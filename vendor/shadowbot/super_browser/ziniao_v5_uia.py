import os
import re
import time
import traceback
import webbrowser
import winreg
import xbot

import psutil
import uiautomation as auto
import win32con
import win32gui
import win32process

_SUPERBROWSER_PROCESS_NAME = "superbrowser"
_SUPERBROWSER_MAIN_TITLES = {
    "紫鸟浏览器专业版",
    "管理系统 - Chromium",
    "运营工作台 - Chromium",
}

_UIA_AUTOMATION_ID_PROPERTY = 30011
_UIA_VALUE_VALUE_PROPERTY = 30045
_UIA_IS_KEYBOARD_FOCUSABLE_PROPERTY = 30009
_DEFAULT_ACCOUNT_PAGE_SIZE = 20
_LOGIN_PANEL_URL_MARK = "/renderer/workbench/index.html#/login"
_DEBUG = os.getenv("ZINIAO_DEBUG", "").lower() in ("1", "true", "yes", "on")

auto.uiautomation.SetGlobalSearchTimeout(5)

def set_ziniao_debug(enabled=True):
    """设置紫鸟调试日志开关。"""
    global _DEBUG
    _DEBUG = bool(enabled)


def _debug_log(message, exc=None):
    """调试开关开启时输出被忽略的异常和运行细节。"""
    if not _DEBUG:
        return
    print(f"[ziniao debug] {message}")
    if exc:
        traceback.print_exception(type(exc), exc, exc.__traceback__)


def _visible_hwnds_by_process(process_name):
    """按进程名获取可见顶层窗口句柄列表。"""
    result = []
    expected_name = process_name.lower()

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if not pid:
            return True
        try:
            actual_name = psutil.Process(pid).name().lower()
        except psutil.Error as exc:
            _debug_log(f"读取进程名称失败: hwnd={hwnd}, pid={pid}", exc)
            return True
        if actual_name == expected_name:
            result.append(hwnd)
        return True

    win32gui.EnumWindows(callback, None)
    return result


def set_control_text(control, text):
    """设置输入框文本，ValuePattern 优先，失败则 SendKeys 回退。"""
    try:
        value_pattern = control.GetValuePattern()
        if value_pattern and not value_pattern.IsReadOnly:
            value_pattern.SetValue(text)
            if str(value_pattern.Value or "") == text:
                return
    except Exception as exc:
        _debug_log("ValuePattern.SetValue 失败，回退 SendKeys", exc)

    try:
        control.SendKeys("{Ctrl}a{Delete}", waitTime=0.05)
        control.SendKeys(text, interval=0.05, waitTime=0.1)
    except Exception as exc:
        _debug_log("SendKeys 输入也失败", exc)
        raise Exception(f"无法设置输入框文本: {exc}")


def click_control(control):
    """统一触发控件，依次尝试 InvokePattern → LegacyIAccessible → 键盘 → win32gui 鼠标消息。"""
    get_pattern = getattr(control, "GetPattern", None)

    try:
        if get_pattern:
            invoke_pattern = get_pattern(auto.PatternId.InvokePattern)
        else:
            invoke_pattern = control.GetInvokePattern()
        if invoke_pattern:
            invoke_pattern.Invoke()
            return
    except Exception as exc:
        _debug_log("InvokePattern 触发失败，尝试 LegacyIAccessible", exc)

    try:
        if get_pattern:
            legacy_pattern = get_pattern(auto.PatternId.LegacyIAccessiblePattern)
        else:
            legacy_pattern = control.GetLegacyIAccessiblePattern()
        if legacy_pattern:
            legacy_pattern.DoDefaultAction()
            return
    except Exception as exc:
        _debug_log("LegacyIAccessible 触发失败，尝试键盘或窗口消息", exc)

    if control.GetPropertyValue(_UIA_IS_KEYBOARD_FOCUSABLE_PROPERTY):
        control.SetFocus()
        control.SendKeys("{Enter}")
        return

    rect = control.BoundingRectangle
    x = (rect.left + rect.right) // 2
    y = (rect.top + rect.bottom) // 2
    hwnd = win32gui.WindowFromPoint((x, y))
    if not hwnd:
        raise Exception("未找到控件所在窗口")
    client_x, client_y = win32gui.ScreenToClient(hwnd, (x, y))
    lparam = (client_y << 16) | (client_x & 0xFFFF)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)


def _normalize_url(url):
    """标准化 URL，统一路径分隔符和大小写，便于后续匹配。"""
    return str(url or "").replace("\\", "/").lower()


def _url_match(mark, url):
    """匹配紫鸟页面 URL。"""
    return _normalize_url(url).endswith(_normalize_url(mark))


# ---------------------------------------------------------------------------
# SuperBrowser（v5 紫鸟浏览器专业版，架构与 v6 ZiNiao 对齐）
# ---------------------------------------------------------------------------

class SuperBrowser:
    def __init__(self, debug=None):
        if debug is not None:
            set_ziniao_debug(debug)

    # ------------------------------------------------------------------
    # 通用工具
    # ------------------------------------------------------------------

    @staticmethod
    def _wait_control(find_fn, timeout=10, interval=0.3, description=""):
        """重试查找 UIA 控件，直到找到或超时。

        用于替代单次 Exists() 调用，解决页面加载/网络波动
        导致控件暂时不可用的问题。
        """
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            try:
                control = find_fn()
                if control and control.Exists(0, 0):
                    return control
            except Exception:
                pass
            time.sleep(interval)
        raise Exception(
            f"等待控件超时({timeout}s): {description or '未找到指定控件'}"
        )

    # ------------------------------------------------------------------
    # 窗口查找（与 v6 一致）
    # ------------------------------------------------------------------

    def _visible_hwnds(self):
        """获取 SuperBrowser 主程序的可见顶层窗口。"""
        return [
            hwnd
            for hwnd in _visible_hwnds_by_process(f"{_SUPERBROWSER_PROCESS_NAME}.exe")
            if win32gui.GetWindowText(hwnd) in _SUPERBROWSER_MAIN_TITLES
        ]

    def _all_candidate_hwnds(self):
        """获取所有可能包含 UIA Document 的 superbrowser 窗口句柄。

        不只看 IsWindowVisible，因为 Chromium 的渲染窗口可能被标记为不可见。
        按优先级：可见主窗口 > 有 Document 的大尺寸隐藏窗口。
        """
        all_hwnds = _visible_hwnds_by_process(
            f"{_SUPERBROWSER_PROCESS_NAME}.exe"
        )
        candidates = []
        for hwnd in all_hwnds:
            rect = win32gui.GetWindowRect(hwnd)
            w, h = rect[2] - rect[0], rect[3] - rect[1]
            title = win32gui.GetWindowText(hwnd)
            visible = win32gui.IsWindowVisible(hwnd)
            candidates.append((hwnd, title, visible, w * h))

        # 排序：可见+大尺寸 优先
        candidates.sort(key=lambda x: (x[2], x[3]), reverse=True)
        return [c[0] for c in candidates if c[3] > 10000]  # 面积 > 100x100

    def _require_main_window(self):
        """确保主窗口存在并返回句柄，不存在则抛异常。

        优先返回有可用 UIA Document 的窗口，而非简单取第一个。
        """
        for hwnd in self._all_candidate_hwnds():
            doc = self._document_from_hwnd(hwnd, timeout=2)
            if doc is not None:
                return hwnd

        raise Exception("未找到紫鸟浏览器(SuperBrowser)，请确保其已打开")

    def _document_from_hwnd(self, hwnd, timeout=5):
        """激活窗口到前台，并等待可用的 UIA Document。"""
        root = auto.ControlFromHandle(hwnd)
        if not root:
            return None

        # 强制激活到前台
        if win32gui.GetForegroundWindow() != hwnd:
            try:
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)
            except Exception as exc:
                _debug_log(f"激活窗口失败: hwnd={hwnd}", exc)

        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            try:
                root = auto.ControlFromHandle(hwnd)
                root.GetPropertyValue(_UIA_AUTOMATION_ID_PROPERTY)
                document = root.DocumentControl(searchDepth=20)
                if document.Exists(0, 0):
                    return document
            except Exception as exc:
                _debug_log(f"等待 UIA 树就绪: hwnd={hwnd}", exc)
            time.sleep(0.2)
        return None

    @staticmethod
    def _is_store_hwnd(hwnd, skip_title_check=False):
        """判断 hwnd 是否为实际运行中的店铺浏览器窗口。

        先检查是否包含 Chrome_RenderWidgetHostHWND Document（所有浏览器窗口共有的特征），
        再通过标题区分主窗口和店铺窗口。

        :param skip_title_check: True 时不检查标题（用于店铺刚启动标题还在加载中的场景）
        """
        # 先检查是否有浏览器 Document（快速排除非浏览器窗口）
        try:
            root = auto.ControlFromHandle(hwnd)
            if not root:
                return False
            document = root.DocumentControl(searchDepth=10)
            if not document.Exists(0.5, 0):
                return False
        except Exception as exc:
            _debug_log(f"判断店铺窗口失败: hwnd={hwnd}", exc)
            return False

        if skip_title_check:
            return True

        # 有浏览器 Document，通过标题区分：主窗口标题在 _SUPERBROWSER_MAIN_TITLES 中
        title = win32gui.GetWindowText(hwnd)
        if "影刀RPA网页自动化" in title:
            return False
        # 主窗口标题 → 不是店铺窗口；其他标题 → 是店铺窗口
        return title not in _SUPERBROWSER_MAIN_TITLES

    # ------------------------------------------------------------------
    # 关闭店铺（与 v6 _close_store 架构一致）
    # ------------------------------------------------------------------

    def _close_store(self):
        """关闭店铺浏览器，不能直接强制杀死进程，会有风控提示"""

        def is_store_hwnd(hwnd):
            """判断窗口是否为实际运行中的店铺浏览器窗口。"""
            title = win32gui.GetWindowText(hwnd)
            if title in {"紫鸟浏览器专业版", "另存为", "提示", "翻译此页？"}:
                return False
            if "影刀RPA网页自动化" in title:
                return False

            # 方案A：通过类名判断
            class_name = win32gui.GetClassName(hwnd)
            if class_name == "Chrome_WidgetWin_1":
                return True  # 紫鸟V5的浏览器窗口

            try:
                root = auto.ControlFromHandle(hwnd)
                root.SetActive(waitTime=0.2)
                document = root.DocumentControl()  # type: ignore
                return document.Exists(1, 0)
            except Exception as exc:
                _debug_log(f"判断店铺窗口失败: hwnd={hwnd}", exc)
                return False

        def store_hwnds():
            """获取当前可见的店铺浏览器窗口。"""
            return [
                hwnd
                for hwnd in _visible_hwnds_by_process("superbrowser.exe")
                if is_store_hwnd(hwnd)
            ]

        def confirm_tip_window():
            """确认关闭店铺时出现的提示窗口。"""
            for hwnd in _visible_hwnds_by_process("superbrowser.exe"):
                if win32gui.GetWindowText(hwnd) != "提示":
                    continue

                root = auto.ControlFromHandle(hwnd)
                ok_button = root.ButtonControl(Name="确定", searchDepth=12)  # type: ignore
                if not ok_button.Exists(1, 0):
                    continue

                click_control(ok_button)
                return True
            return False

        def close_window(hwnd):
            """向店铺窗口发送关闭消息。"""
            if not win32gui.IsWindow(hwnd):
                return
            try:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            except Exception as exc:
                _debug_log(f"关闭店铺窗口失败: hwnd={hwnd}", exc)
            confirm_tip_window()

        hwnds = store_hwnds()
        if not hwnds:
            return

        for hwnd in hwnds:
            close_window(hwnd)

        # 已定位到店铺窗口后，只检查句柄是否已销毁，避免关闭过程中反复遍历 UIA 树。
        end_time = time.time() + 3
        while time.time() < end_time:
            confirm_tip_window()
            if all(not win32gui.IsWindow(hwnd) for hwnd in hwnds):
                return
            time.sleep(0.1)

        if all(not win32gui.IsWindow(hwnd) for hwnd in hwnds):
            return
        raise Exception("关闭店铺超时")

    # ------------------------------------------------------------------
    # 弹窗处理（与 v6 _close_dialog 一致）
    # ------------------------------------------------------------------

    def _close_dialogs(self, document):
        """关闭可能遮挡账号操作区域的紫鸟弹窗。"""
        # 精简面板提示使用 HyperlinkControl，不能按 ButtonControl 定位。
        know_button = document.HyperlinkControl(
            Name="知道了",
            searchDepth=30,
        )
        if know_button.Exists(0, 0):
            click_control(know_button)

        # 关闭升级提醒弹窗。
        update_close_button = document.ButtonControl(
            Name="close-circle",
            searchDepth=30,
        )
        if update_close_button.Exists(0, 0):
            click_control(update_close_button)

        # 关闭资源到期提醒弹窗。
        expiration_close_button = document.ButtonControl(
            Name="close",
            searchDepth=30,
        )
        if expiration_close_button.Exists(0, 0):
            click_control(expiration_close_button)

    def _handle_kernel_download_dialog(self, document, timeout=0):
        """启动店铺后取消内核下载弹窗，并抛出明确的启动失败异常。"""
        try:
            micro_slot = document.Control(
                AutomationId="microSlot",
                searchDepth=10,
            )
            if not micro_slot.Exists(0, 0):
                return

            kernel_title = micro_slot.TextControl(
                Name="请下载指定内核",
                searchDepth=6,
            )
            if not kernel_title.Exists(timeout, 0.2):
                return

            kernel_dialog = (
                kernel_title.GetParentControl()
                .GetParentControl()
                .GetParentControl()
            )
            cancel_button = kernel_dialog.ButtonControl(
                RegexName=r"取\s*消",
                searchDepth=5,
            )
        except Exception:
            _debug_log("处理启动店铺后弹窗失败, 影响较小, 忽略异常")
            return

        if not cancel_button.Exists(1, 0):
            raise Exception("下载内核弹窗未找到取消按钮")

        click_control(cancel_button)
        raise Exception("启动店铺失败，请下载指定内核，下载升级内核后即可启动")

    def _handle_online_limit_dialog(self, document, action, timeout=1):
        """处理在线人数上限弹窗，返回是否应终止打开店铺流程。"""
        if not action:
            return False

        micro_slot = document.Control(
            AutomationId="microSlot",
            searchDepth=10,
        )
        if not micro_slot.Exists(0, 0):
            return False

        dialog = micro_slot.CustomControl(
            Name="当前在线人员",
            searchDepth=3,
        )
        if not dialog.Exists(timeout, 0.2):
            return False

        action_button = dialog.ButtonControl(
            Name=action,
            searchDepth=5,
        )
        if not action_button.Exists(1, 0):
            raise Exception(f"未找到在线人数上限操作按钮: {action}")

        # 该 Electron 按钮的 InvokePattern 调用成功但页面无响应，Legacy 实测有效。
        legacy_pattern = action_button.GetPattern(
            auto.PatternId.LegacyIAccessiblePattern
        )
        if not legacy_pattern:
            raise Exception(f"在线人数上限操作按钮不支持 Legacy: {action}")
        legacy_pattern.DoDefaultAction()
        return action != "申请访问名额"

    # ------------------------------------------------------------------
    # 启动 / 退出（移植自 v6）
    # ------------------------------------------------------------------

    def _get_exe_path(self):
        """从注册表读取 SuperBrowser 安装路径。"""
        default_path = r"C:\Program Files\superbrowser\superbrowser.exe"

        registry_key = (
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            r"\SuperBrowser"
        )

        for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
            try:
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    registry_key,
                    0,
                    winreg.KEY_READ | view,
                ) as key:
                    icon = str(
                        winreg.QueryValueEx(key, "DisplayIcon")[0]
                    )

                    exe_path = re.sub(
                        r",\s*-?\d+\s*$",
                        "",
                        icon,
                    ).strip().strip('"')

                    if os.path.isfile(exe_path):
                        return exe_path

            except OSError as exc:
                _debug_log("读取 SuperBrowser 注册表路径失败", exc)

        return default_path if os.path.isfile(default_path) else ""

    def _launch(self, timeout=30):
        """启动 SuperBrowser 并等待主窗口可见。"""
        if self._visible_hwnds():
            return

        exe_path = self._get_exe_path()
        if not exe_path:
            raise Exception("未找到 SuperBrowser 可执行文件路径")
        os.startfile(exe_path)

        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            if self._visible_hwnds():
                return
            time.sleep(0.2)

        raise Exception("启动 SuperBrowser 超时，未找到可见窗口")

    def _wait_document_by_url(self, url, timeout=10):
        """等待指定 URL 的 SuperBrowser Document 就绪。"""
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            document = self._document_by_url(url)
            if document:
                return document
            time.sleep(0.2)

        raise Exception(f"未找到 SuperBrowser 页面: {url}")

    def _panel_type(self, document):
        """通过固定 UIA 特征判断 SuperBrowser 面板类型。

        "环境管理"和"账号管理"在窗口侧边栏（root）中，不在 Document 中，
        必须从 root 搜索。
        """
        # 从 root 获取控件树
        root = document.GetParentControl()

        # 检查环境管理菜单（主面板特征）
        env_menu = root.Control(RegexName=r".*环境管理.*", searchDepth=12)
        has_env_menu = env_menu.Exists(0, 0)

        # 检查账号管理
        account_ctrl = root.Control(RegexName=r".*账号管理.*", searchDepth=12)
        has_account = account_ctrl.Exists(0, 0)

        if has_env_menu and has_account:
            return "full"
        if has_env_menu or has_account:
            return "basic"

        # 登录页特征
        login_button = document.Control(Name="企业登录", searchDepth=15)
        if login_button.Exists(0, 0):
            return "login"

        return ""

    def _wait_any_panel(self, panel_types, timeout=10):
        """等待指定面板，并按 panel_types 顺序选择。

        每次循环都从当前窗口重新获取 Document 并检查登录错误，
        避免使用已失效的旧 Document 引用。
        """
        end_time = time.monotonic() + timeout

        while time.monotonic() < end_time:
            for hwnd in self._visible_hwnds():
                try:
                    document = self._document_from_hwnd(hwnd, timeout=1)
                    if not document:
                        continue
                    panel_type = self._panel_type(document)

                    # 登录失败 → 还在登录页，检查当前页面是否有密码错误提示
                    if panel_type == "login":
                        login_error = document.TextControl(
                            RegexName=r"用户名.*密码错误",
                            searchDepth=10,
                        )
                        if login_error.Exists(0, 0):
                            raise Exception(
                                login_error.Name or "用户名或者密码错误"
                            )

                    if panel_type in panel_types:
                        return document, panel_type
                except Exception as exc:
                    # 如果是我们主动抛出的密码错误异常，继续向上传播
                    err_msg = str(exc)
                    if "用户名" in err_msg and "密码错误" in err_msg:
                        raise
                    _debug_log(f"等待面板时读取窗口失败: hwnd={hwnd}", exc)

            time.sleep(0.2)

        raise Exception(f"未找到 SuperBrowser 面板: {', '.join(panel_types)}")

    def _document_by_url(self, url):
        """根据 URL 获取 SuperBrowser 的 Document。"""
        for hwnd in self._visible_hwnds():
            try:
                document = self._document_from_hwnd(hwnd)
                if document and _url_match(
                    url,
                    document.GetPropertyValue(_UIA_VALUE_VALUE_PROPERTY),
                ):
                    return document
            except Exception as exc:
                _debug_log(
                    f"根据 URL 查找 document 失败: hwnd={hwnd}, url={url}",
                    exc,
                )
        return None

    def login(
        self,
        company_name: str = "",
        company_username: str = "",
        password: str = "",
        is_fill: bool = False,
        is_close: bool = True,
        *,
        timeout: int = 20,
    ):
        """登录 SuperBrowser。

        通过「登录」HyperlinkControl（ControlType=50005）判断登录状态：
          - 控件存在 → 未登录，执行登录流程
          - 控件不存在 → 已登录，提示后返回

        所有控件查找优先使用 root（ControlFromHandle），
        只在需要填表时才获取 Document，避免频繁 SetForegroundWindow。
        """

        # 1. 获取主窗口
        hwnd = self._require_main_window()
        # 2. 从 root 判断是否需要登录（不调 _document_from_hwnd，避免
        #    SetForegroundWindow 开销）
        root = auto.ControlFromHandle(hwnd)
        try:
            self._wait_control(
                lambda: root.HyperlinkControl(Name="登录", searchDepth=10),
                timeout=min(timeout, 5),
                interval=0.3,
                description="等待登录按钮出现",
            )
            need_login = True
        except Exception:
            need_login = False

        if not need_login:
            # 已登录状态
            if not is_close:
                return

            # is_close=True → 先关闭店铺，再退出登录
            self._close_store()

            # 关闭店铺后重新激活工作台窗口
            try:
                hwnd = self._require_main_window()
                root = auto.ControlFromHandle(hwnd)
            except Exception:
                pass

            # 退出登录（只用 root，不用 document）
            logout_deadline = time.monotonic() + 10
            logged_out = False
            while time.monotonic() < logout_deadline:
                try:
                    root = auto.ControlFromHandle(hwnd)

                    # 查找并点击 down 下拉按钮
                    down_btn = root.Control(Name="down", searchDepth=15)
                    if not down_btn.Exists(1, 0):
                        time.sleep(0.3)
                        continue

                    rect = down_btn.BoundingRectangle
                    x = (rect.left + rect.right) // 2
                    y = (rect.top + rect.bottom) // 2
                    click_hwnd = win32gui.WindowFromPoint((x, y)) or hwnd
                    client_x, client_y = win32gui.ScreenToClient(
                        click_hwnd, (x, y)
                    )
                    lparam = (client_y << 16) | (client_x & 0xFFFF)
                    win32gui.SendMessage(
                        click_hwnd, win32con.WM_LBUTTONDOWN,
                        win32con.MK_LBUTTON, lparam
                    )

                    time.sleep(0.5)
                    # 轮询搜索"退出登录"（不重试 down，避免关闭下拉框）
                    logout_btn = None
                    poll_end = time.monotonic() + 3
                    while time.monotonic() < poll_end:
                        fresh_root = auto.ControlFromHandle(hwnd)
                        try:
                            for ctrl, _ in auto.WalkControl(
                                fresh_root, includeTop=False, maxDepth=30
                            ):
                                if (ctrl.Name or "").strip() == "退出登录":
                                    logout_btn = ctrl
                                    break
                        except Exception:
                            pass
                        if logout_btn is not None:
                            break
                        time.sleep(0.2)

                    if logout_btn is None:
                        continue
                    click_control(logout_btn)

                    # 等待"登录"超链接重新出现
                    self._wait_control(
                        lambda: auto.ControlFromHandle(hwnd).HyperlinkControl(
                            Name="登录", searchDepth=10
                        ),
                        timeout=5,
                        interval=0.3,
                        description="等待登录按钮重新出现",
                    )
                    logged_out = True
                    break
                except Exception:
                    time.sleep(0.3)
                    continue

            if not logged_out:
                raise Exception("退出登录超时(10s)：未能完成退出登录操作")

        # 2. 点击"登录"按钮进入登录页
        login_link = self._wait_control(
            lambda: auto.ControlFromHandle(hwnd).HyperlinkControl(
                Name="登录", searchDepth=10
            ),
            timeout=min(timeout, 5),
            interval=0.3,
            description="等待登录按钮出现",
        )
        click_control(login_link)

        document = self._document_from_hwnd(hwnd, timeout=timeout)
        if document is None:
            raise Exception("点击登录后无法获取登录页 Document")

        # 3. 点击「企业登录」切换到企业登录表单
        click_control(document.Control(Name="企业登录"))

        # 4. 填表
        if is_fill:
            if not company_name:
                raise ValueError("企业名称不能为空")
            if not company_username:
                raise ValueError("企业用户名不能为空")

            company_ele = (
                document.Control(RegexName=r".*公司名.*")
                .GetParentControl()
                .GetNextSiblingControl()
                .EditControl(searchDepth=10)
            )
            set_control_text(company_ele, company_name)

            account_ele = (
                document.Control(RegexName=r".*企业用户名.*")
                .GetParentControl()
                .GetNextSiblingControl()
                .EditControl(searchDepth=10)
            )
            set_control_text(account_ele, company_username)

            # 密码为空时保留页面中已记住的密码。
            if password:
                password_ele = (
                    document.Control(RegexName=r".*企业.*密码.*")
                    .GetParentControl()
                    .GetNextSiblingControl()
                    .EditControl(searchDepth=10)
                )
                set_control_text(password_ele, password)

        # 4. 点击「登 录」并等待进入面板
        click_control(document.Control(Name="登 录"))
        self._wait_any_panel(("full", "basic"), timeout=timeout)


    def exit_app(self, timeout=20):
        """退出当前 SuperBrowser 登录态"""
        webbrowser.open("superbrowser://exit")
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            if not self._visible_hwnds():
                return
            time.sleep(0.5)
        raise Exception("退出 SuperBrowser 超时")

    # ------------------------------------------------------------------
    # 账号列表分页 / 数据提取（移植自 v6，适配 v5 UI 结构）
    # ------------------------------------------------------------------

    def _account_pagination(self, document):
        """通过账号表格相邻区域定位分页栏。"""
        return (
            document.Control(AutomationId="account-table", searchDepth=30)
            .GetParentControl()
            .GetNextSiblingControl()
            .GetFirstChildControl()
        )

    def _account_total_record(self, document):
        """读取账号列表总记录数。"""
        total_name = (
            self._account_pagination(document)
            .GetFirstChildControl()
            .TextControl(searchDepth=3)
            .Name
        )
        return int(re.sub(r"\D", "", total_name or ""))

    def _account_page_size(self, document):
        """读取账号列表每页显示数量。"""
        page_size_name = (
            self._account_pagination(document)
            .GetLastChildControl()
            .GroupControl(RegexName=r"(\d+)\s*条/页", searchDepth=5)
            .Name
        )
        return int(re.sub(r"\D", "", page_size_name or ""))

    def _account_data_table(self, document):
        """获取账号列表的数据表控件。"""
        return (
            document.Control(AutomationId="account", searchDepth=30)
            .GetFirstChildControl()
            .GetLastChildControl()
            .GetFirstChildControl()
        )

    def _clear_account_search(self, document, timeout=5):
        """等待账号列表加载后清空搜索条件。"""
        search_button = document.ButtonControl(Name="search", searchDepth=30)
        if not search_button.Exists(timeout, 0.2):
            raise Exception("未找到账号列表搜索按钮")

        search_parent = search_button.GetParentControl()
        close_button = search_parent.ButtonControl(
            Name="close-circle",
            searchDepth=5,
        )
        if not close_button.Exists(0, 0):
            return

        click_control(close_button)

        end_time = time.monotonic() + 5
        while time.monotonic() < end_time:
            if not search_parent.ButtonControl(
                Name="close-circle",
                searchDepth=5,
            ).Exists(0, 0):
                return
            time.sleep(0.2)

        raise Exception("清空账号列表搜索条件失败")

    def _click_account_first_page(self, document):
        """点击账号列表分页的第一页按钮。"""
        pagination = self._account_pagination(document)
        previous_page_button = pagination.ListItemControl(
            RegexName=r"^(上一页|left)$",
            searchDepth=10,
        )
        if not previous_page_button.IsEnabled:
            return

        first_page_button = pagination.ListItemControl(Name="1", searchDepth=10)
        if getattr(first_page_button, "Name", "") != "1":
            raise Exception("未找到账号第一页按钮")

        click_control(first_page_button)

    def _is_empty_account_page(self, document):
        """判断当前账号页是否为无账号引导页。"""
        # 尝试通过 AutomationId 定位 SuperManager 布局。
        layout = document.Control(
            AutomationId="superManagerLayout", searchDepth=25
        )
        if layout.Exists(0, 0):
            return len(layout.GetChildren()) == 1

        # fallback：检查是否有"暂无数据"提示。
        empty = document.Control(Name="暂无数据", searchDepth=20)
        return empty.Exists(0, 0)

    def _require_account_page_size_20(self, document):
        """确保账号列表分页大小为 20。建议固定使用 20 条/页。"""
        if self._account_page_size(document) == _DEFAULT_ACCOUNT_PAGE_SIZE:
            return

        pagination = self._account_pagination(document)
        if not pagination.Exists(2, 0.2):
            raise Exception("未找到账号分页大小控件")

        page_size_area = pagination.GetLastChildControl()
        combo = page_size_area.ComboBoxControl(Name="页码", searchDepth=5)
        click_control(combo.GetParentControl().GetParentControl())

        page_size_option = document.ListItemControl(
            AutomationId=f"{combo.AutomationId}_list_1",
            searchDepth=35,
        )
        if not page_size_option.Exists(3, 0.2):
            raise Exception("未找到20条/页选项")
        click_control(page_size_option)

        end_time = time.monotonic() + 8
        while time.monotonic() < end_time:
            try:
                if self._account_page_size(document) == _DEFAULT_ACCOUNT_PAGE_SIZE:
                    return
            except Exception as exc:
                _debug_log("等待账号分页大小切换失败", exc)
            time.sleep(0.2)

        raise Exception("账号分页大小切换超时")

    def _wait_account_page_records(
        self,
        document,
        previous_records=None,
        timeout=8,
    ):
        """等待账号列表数据加载完成。"""
        end_time = time.monotonic() + timeout
        last_error = None

        while time.monotonic() < end_time:
            try:
                records = tuple(
                    self._extract_store_records_from_account_table(document)
                )
                if records and (
                    previous_records is None or records != previous_records
                ):
                    return records
            except Exception as exc:
                last_error = exc
                _debug_log("等待账号页店铺数据失败", exc)

            time.sleep(0.2)

        if last_error:
            raise Exception(f"等待账号页店铺数据超时: {last_error}")
        raise Exception("等待账号页店铺数据超时")

    def _extract_store_records_from_account_table(self, document):
        """从账号列表表格提取账号名称和平台名称。"""
        try:
            data_table = self._account_data_table(document)
        except Exception as exc:
            _debug_log("定位账号表格失败，尝试 fallback", exc)
            # fallback：使用 v5 原有的 start 按钮定位行容器
            return self._extract_store_records_fallback(document)

        store_records = []
        for row_control in data_table.GetChildren():
            texts = self._row_texts(row_control)
            if len(texts) < 2:
                continue
            account_name, platform_name = texts[0], texts[1]
            store_records.append((account_name, platform_name))

        return store_records

    def _extract_store_records_fallback(self, document):
        """v5 fallback：通过「启动」按钮定位店铺行容器并提取数据。"""
        start_ctrl = document.Control(Name="启动", searchDepth=25)
        if not start_ctrl.Exists(2, 0.2):
            return []

        group_items = start_ctrl.GetParentControl().GetParentControl()
        store_records = []
        for row in group_items.GetChildren():
            texts = self._row_texts(row)
            if len(texts) < 2:
                continue
            store_records.append((texts[0], texts[1]))
        return store_records

    def _iter_account_pages(self, document, timeout=8):
        """从当前页开始遍历账号列表，直到下一页不存在或不可点击。"""
        previous_records = None
        while True:
            records = self._wait_account_page_records(
                document,
                previous_records,
                timeout=timeout,
            )
            yield records

            next_page_button = document.ListItemControl(
                RegexName=r"^(下一页|right)$",
                searchDepth=30,
            )
            if not next_page_button.Exists(2, 0.2):
                return
            if not next_page_button.IsEnabled:
                return

            click_control(next_page_button)
            previous_records = records

    def get_store_list(self, selected_platform=None, timeout=30):
        """获取 SuperBrowser 中的店铺列表"""
        hwnd = self._require_main_window()
        document = self._document_from_hwnd(hwnd, timeout=timeout)
        if document is None:
            raise Exception("无法获取 SuperBrowser 主窗口 UIA Document")

        document = self._to_account_page(timeout=timeout)
        self._close_dialogs(document)

        if self._is_empty_account_page(document):
            return []

        self._clear_account_search(document, timeout=timeout)
        self._click_account_first_page(document)

        try:
            self._require_account_page_size_20(document)
            total_record = self._account_total_record(document)
        except Exception:
            # 如果 v6 风格的分页/总数定位失败（v5 UI 不同），则退化到纯遍历模式
            total_record = 0

        if total_record == 0:
            # 尝试通过遍历确定是否有数据
            pass

        store_names = []
        fetched_record_count = 0
        for page_records in self._iter_account_pages(document, timeout=timeout):
            fetched_record_count += len(page_records)
            for store_name, platform_name in page_records:
                if selected_platform and (
                    selected_platform.upper() != platform_name.upper()
                ):
                    continue
                if store_name not in store_names:
                    store_names.append(store_name)

        if total_record and fetched_record_count != total_record:
            raise Exception(
                f"账号列表数量不一致: 页面显示{total_record}条, "
                f"实际获取{fetched_record_count}条"
            )
        return store_names

    # ------------------------------------------------------------------
    # 账号页面导航（v5 特有 UI 结构）
    # ------------------------------------------------------------------

    def _to_account_page(self, timeout=5):
        """打开账号管理页面。

        "环境管理"和"账号管理"在窗口侧边栏中，是 root 控件的子孙节点，
        不在 Document（网页内容）中。控件类型为 MenuItemControl 或 TabItemControl。
        """
        hwnd = self._require_main_window()
        root = auto.ControlFromHandle(hwnd)
        if not root:
            raise Exception("无法获取 SuperBrowser 窗口根控件")

        # 关闭可能遮挡的弹窗
        document = self._document_from_hwnd(hwnd, timeout=timeout)
        if document:
            self._close_dialogs(document)

        # 1) 从 root 搜索"账号管理"（可能是 MenuItemControl 或 TabItemControl）
        account_ctrl = root.Control(
            RegexName=r".*账号管理.*", searchDepth=12
        )
        if account_ctrl.Exists(2, 0.2):
            click_control(account_ctrl)
            return document

        # 2) 从 root 搜索"环境管理" → 点击 → 再找"账号管理"
        env_menu = root.Control(
            RegexName=r".*环境管理.*", searchDepth=12
        )
        if not env_menu.Exists(3, 0.2):
            raise Exception("未找到环境管理菜单")
        click_control(env_menu)

        # 点击后重新获取 root
        root = auto.ControlFromHandle(hwnd)
        account_ctrl = root.Control(
            RegexName=r".*账号管理.*", searchDepth=12
        )
        if not account_ctrl.Exists(3, 0.2):
            raise Exception("未找到账号管理")
        click_control(account_ctrl)
        return document

    # ------------------------------------------------------------------
    # 店铺搜索（与 v6 _search_store 逻辑一致）
    # ------------------------------------------------------------------

    def _search_store(self, document, store_name, timeout=15):
        """输入店铺名称并触发搜索。

        使用 _wait_control 重试查找控件，应对页面加载延迟。
        """
        # 重试查找搜索按钮（页面可能还在加载）
        search_button = self._wait_control(
            lambda: document.ButtonControl(Name="search", searchDepth=30),
            timeout=timeout,
            description="店铺搜索按钮",
        )
        search_input = self._wait_control(
            lambda: search_button.GetParentControl().EditControl(searchDepth=5),
            timeout=5,
            description="店铺搜索输入框",
        )

        for _ in range(10):
            click_control(search_input)
            auto.SendKeys("{Ctrl}a{Delete}", waitTime=0.05)
            auto.SendKeys(store_name, interval=0.2, waitTime=0.5)

            current_value = str(
                search_input.GetPropertyValue(_UIA_VALUE_VALUE_PROPERTY) or ""
            )
            if current_value != store_name:
                _debug_log(
                    f"输入值校验失败：期望={store_name}, 实际={current_value}，重试"
                )
                continue

            first_option = document.TextControl(Name="全局搜索", searchDepth=30)
            if not first_option.Exists(3, 0.2):
                _debug_log("未找到全局搜索下拉选项，重试")
                continue

            click_control(first_option)
            time.sleep(0.3)
            if search_button.Exists(0, 0):
                click_control(search_button)
            return

        raise Exception("填写店铺名称异常或未触发搜索下拉框导致输入搜索店铺失败")

    # ------------------------------------------------------------------
    # 店铺列表匹配（v6 _account_row_texts + _find_store_start_button 风格）
    # ------------------------------------------------------------------

    @staticmethod
    def _row_texts(row_control):
        """读取行内的文本控件，返回 [店铺名称, 平台名称]（与 v6 _account_row_texts 一致）。"""
        return [
            (item.Name or "").strip()
            for item, _ in auto.WalkControl(
                row_control,
                includeTop=True,
                maxDepth=6,
            )
            if item.ControlTypeName == "TextControl" and (item.Name or "").strip()
        ]

    def _find_store_start_button(self, document, store_name, match_type, timeout=10):
        """在店铺列表中定位匹配店铺的启动按钮（与 v6 _find_store_start_button 一致）。"""
        target_name = store_name.casefold()
        end_time = time.monotonic() + timeout
        last_operation = ""

        while time.monotonic() < end_time:
            # 定位店铺列表容器
            start_ctrl = document.Control(Name="启动", searchDepth=25)
            if not start_ctrl.Exists(1, 0.2):
                time.sleep(0.2)
                continue

            group_control_items = start_ctrl.GetParentControl().GetParentControl()
            if not group_control_items:
                time.sleep(0.2)
                continue

            # 先收集所有匹配行，再做重复检查和按钮定位（与 v6 一致）
            matched_rows = []
            try:
                for row in group_control_items.GetChildren():
                    texts = self._row_texts(row)
                    if len(texts) < 2:
                        continue

                    account_name = texts[0]
                    _debug_log(f"行文本: 店铺={account_name}, 平台={texts[1]}")

                    matched = (
                        target_name in account_name.casefold()
                        if match_type == "模糊"
                        else target_name == account_name.casefold()
                    )
                    if matched:
                        matched_rows.append(row)
            except Exception as exc:
                _debug_log("读取账号表格失败", exc)
                time.sleep(0.2)
                continue

            # 精确匹配时，多个同名店铺说明数据异常（与 v6 一致）
            if match_type == "相等" and len(matched_rows) > 1:
                raise Exception("找到多个匹配的店铺，无法唯一确定")

            for row in matched_rows:
                start_button = row.ButtonControl(
                    RegexName=r"^(启动|切换)$",
                    searchDepth=8,
                )
                if start_button.Exists(0, 0):
                    return start_button
                last_operation = (
                    row.GetLastChildControl().Name or "未找到启动按钮"
                )

            if matched_rows and last_operation:
                raise Exception(f"店铺当前无法启动: {last_operation}")

            time.sleep(0.2)

        raise Exception(f"未搜索到指定店铺：{store_name}")

    # ------------------------------------------------------------------
    # 启动店铺（与 v6 _start_store 逻辑一致）
    # ------------------------------------------------------------------

    def _start_store(self, document, start_button, privacy):
        """按隐私或正常模式启动店铺（与 v6 _start_store 完全一致）。"""
        if privacy:
            more_button = start_button.GetParentControl().GetNextSiblingControl()
            if not more_button or not more_button.Exists(1, 0):
                raise Exception("未找到隐私模式更多操作按钮")
            auto.MoveTo(0, 0)
            click_control(more_button)

            operation_menu = document.Control(
                Name="当前更多操作",
                searchDepth=30,
            )
            if not operation_menu.Exists(1, 0):
                raise Exception("未找到账号更多操作菜单")

            temporary_mode = operation_menu.TextControl(
                Name="临时模式启动",
                searchDepth=10,
            )
            if not temporary_mode.Exists(1, 0):
                raise Exception("未找到临时模式启动菜单项")
            click_control(temporary_mode.GetParentControl())

            temp_dialog = document.Control(
                Name="本次临时启动配置",
                searchDepth=30,
            )
            if not temp_dialog.Exists(1, 0):
                raise Exception("未找到临时启动配置弹窗")

            # 处理加载插件复选框（移植自 v6）
            load_plugins_checkbox = temp_dialog.CheckBoxControl(
                RegexName=r"加载插件\s*",
                searchDepth=10,
            )
            if load_plugins_checkbox.Exists(0.5, 0):
                toggle_pattern = load_plugins_checkbox.GetTogglePattern()
                if toggle_pattern:
                    if toggle_pattern.ToggleState == auto.ToggleState.Off:
                        toggle_pattern.Toggle()
                    if toggle_pattern.ToggleState != auto.ToggleState.On:
                        raise Exception("加载插件复选框未选中")

            close_btn = temp_dialog.ButtonControl(Name="关闭", searchDepth=10)
            if close_btn.Exists(0.5, 0):
                click_control(close_btn)

            start_btn = temp_dialog.ButtonControl(
                RegexName=r"启\s*动",
                searchDepth=10,
            )
            if not start_btn.Exists(1, 0):
                raise Exception("未找到临时启动确认按钮")
            click_control(start_btn)
            self._handle_kernel_download_dialog(document, timeout=1)
            return

        # 正常启动：与 v6 完全一致的逻辑
        btn_name = start_button.Name
        if btn_name == "切换":
            click_control(start_button)
        elif btn_name != "启动":
            raise Exception(f"启动按钮文字不是启动：{btn_name}")
        else:
            for _ in range(3):
                try:
                    current_name = start_button.Name
                except Exception:
                    break
                if current_name != "启动":
                    break
                try:
                    click_control(start_button)
                except Exception:
                    break
                self._handle_kernel_download_dialog(document, timeout=0.5)
                time.sleep(0.5)

    # ------------------------------------------------------------------
    # 等待店铺窗口（与 v6 _wait_store_window 一致）
    # ------------------------------------------------------------------

    def _wait_store_window(self, document, existing_hwnds, timeout=20):
        """等待**新的**店铺浏览器窗口出现（与 v6 一致）。

        :param document: 主窗口 UIA Document，用于检测内核下载弹窗
        :param existing_hwnds: 启动前已存在的窗口句柄集合，这些会被跳过
        """
        end_time = time.monotonic() + timeout
        next_kernel_check = time.monotonic()

        while time.monotonic() < end_time:
            if time.monotonic() >= next_kernel_check:
                self._handle_kernel_download_dialog(document)
                next_kernel_check = time.monotonic() + 1

            for hwnd in _visible_hwnds_by_process(
                f"{_SUPERBROWSER_PROCESS_NAME}.exe"
            ):
                if hwnd in existing_hwnds:
                    continue
                # 新窗口跳过标题检查（店铺刚启动时标题可能还在加载中）
                if not self._is_store_hwnd(hwnd, skip_title_check=True):
                    continue
                return hwnd
            time.sleep(0.2)

        raise Exception("店铺浏览器窗口未出现")

    # ------------------------------------------------------------------
    # 打开账号 + 验证网页加载（与 v6 _click_open_account / _wait_store_web_page 一致）
    # ------------------------------------------------------------------

    def _click_open_account(self, store_hwnd, timeout=30):
        """在店铺窗口中点击"打开账号"。

        与 v6 一致：等待按钮可点击后才点击，标签切换后重新获取 root。
        """
        end_time = time.monotonic() + timeout

        # 等待窗口 UIA 树就绪
        root = auto.ControlFromHandle(store_hwnd)
        if not root:
            raise Exception("未找到店铺窗口 UIA 根节点")

        # 检查"打开账号"是否存在；不存在则切回第一个标签页
        open_account = root.ButtonControl(Name="打开账号", searchDepth=15)
        if not open_account.Exists(0, 0):
            new_tab_button = root.ButtonControl(Name="新标签页", searchDepth=15)
            while time.monotonic() < end_time:
                if new_tab_button.Exists(0, 0):
                    tab_control = new_tab_button.GetParentControl()
                    first_tab = tab_control.TabItemControl(searchDepth=10)
                    if first_tab.Exists(0, 0):
                        click_control(first_tab)
                        break
                time.sleep(0.2)
            else:
                raise Exception("未找到店铺窗口中的浏览器首个 Tab")

            # 标签切换后 Chromium 会替换 Document，重新获取 root
            root = auto.ControlFromHandle(store_hwnd)
            if not root:
                raise Exception("标签切换后无法获取店铺窗口 UIA 根节点")

        # 等待按钮出现并点击（每轮重新查询，防止 UIA 引用失效）
        while time.monotonic() < end_time:
            # 重新获取 root（Chromium 可能在等待过程中替换 Document）
            root = auto.ControlFromHandle(store_hwnd)
            if not root:
                time.sleep(0.2)
                continue
            open_account = root.ButtonControl(Name="打开账号", searchDepth=15)
            if open_account.Exists(0.5, 0):
                # 确认按钮可交互（不是 disabled 状态）
                if open_account.IsEnabled:
                    click_control(open_account)
                    return
                else:
                    _debug_log("打开账号按钮存在但被禁用，等待启用")
            time.sleep(0.3)

        raise Exception("未找到店铺窗口中的打开账号按钮")

    def _click_continue_account(self, store_hwnd):
        """点击"继续"确认按钮（与 v6 一致）。"""
        root = auto.ControlFromHandle(store_hwnd)
        if not root:
            return False
        continue_button = root.ButtonControl(
            RegexName=r"^继\s*续$",
            searchDepth=30,
        )
        if not continue_button.Exists(1, 0):
            return False
        if not continue_button.IsEnabled:
            _debug_log("继续按钮存在但被禁用")
            return False
        click_control(continue_button)
        return True

    def _wait_store_web_page(self, timeout=30):
        """等待影刀接入当前店铺的活动网页（与 v6 一致）。"""
        end_time = time.monotonic() + timeout

        while time.monotonic() < end_time:
            try:
                xbot.web.get_all(mode="superbrowser")
                return xbot.web.get_active(mode="superbrowser", load_timeout=0)
            except Exception:
                time.sleep(0.2)

        # 再调用一次，向上抛出影刀提供的真实错误码和调用栈。
        xbot.web.get_all(mode="superbrowser")
        return xbot.web.get_active(mode="superbrowser", load_timeout=0)


    def open_store(
        self,
        store_name,
        *,
        match_type="相等",
        privacy=False,
        is_open="点击",
        timeout=20,
        user_limit="取 消",
    ):
        """打开指定店铺（与 v6 open_store 架构一致）。

        :return: (full_store_name, web_page) 或 None（隐私模式或 is_open 不为点击时）
        """
        if match_type not in ("模糊", "相等"):
            raise ValueError("匹配类型输入有误，仅支持： 模糊、相等")
        if is_open not in ("点击", "不点击"):
            raise ValueError("打开账号输入有误，仅支持： 点击、不点击")

        store_name = store_name.strip()

        # 1. 关闭已有店铺
        self._close_store()

        # 2. 进入账号管理页面
        document = self._to_account_page(timeout=5)

        # 3. 关闭弹窗
        self._close_dialogs(document)

        # 4. 搜索店铺
        self._clear_account_search(document, timeout=timeout)
        self._search_store(document, store_name)

        # 5. 检查空结果
        error_control = document.Control(Name="暂无数据", searchDepth=20)
        if error_control.Exists(1, 0):
            raise ValueError(f"没有包含{store_name}这个店铺")

        # 6. 逐页定位店铺启动按钮
        self._click_account_first_page(document)
        self._require_account_page_size_20(document)
        target_name = store_name.casefold()
        start_button = None
        for records in self._iter_account_pages(document, timeout=timeout):
            if any(
                target_name in name.casefold()
                if match_type == "模糊"
                else target_name == name.casefold()
                for name, _ in records
            ):
                start_button = self._find_store_start_button(
                    document, store_name, match_type, timeout=timeout
                )
                break
        if start_button is None:
            raise Exception(f"未搜索到指定店铺：{store_name}")

        # 7. 记录启动前已有窗口，启动店铺
        existing_hwnds = set(
            _visible_hwnds_by_process(f"{_SUPERBROWSER_PROCESS_NAME}.exe")
        )
        self._start_store(document, start_button, privacy)

        # 8. 处理在线人数上限弹窗
        if self._handle_online_limit_dialog(document, user_limit):
            return None

        if privacy or is_open != "点击":
            return None

        # 9. 等待新的店铺窗口 → 打开账号 → 获取网页对象（与 v6 完全一致）
        store_hwnd = self._wait_store_window(
            document, existing_hwnds, timeout=timeout
        )
        full_store_name = win32gui.GetWindowText(store_hwnd)
        web_page = None
        if is_open == "点击":
            for attempt in range(3):
                try:
                    self._click_open_account(store_hwnd, timeout=10)
                    try:
                        web_page = self._wait_store_web_page(timeout=max(timeout, 10))
                    except Exception:
                        if not self._click_continue_account(store_hwnd):
                            raise
                        web_page = self._wait_store_web_page(timeout=max(timeout, 10))
                    break
                except Exception as exc:
                    _debug_log(f"第 {attempt + 1} 次打开店铺账号页失败", exc)
        return full_store_name, web_page


def main(args):
    sb = SuperBrowser()
    # 示例：获取店铺列表
    # stores = sb.get_store_list()
    # print(f"店铺列表: {stores}")

    # sb.login(
    # )

    # 示例：打开店铺
    name, web_page = sb.open_store(
        "美国亚马逊",
        match_type="相等",
        privacy=False,
        is_open="点击",
        timeout=60,
    )
    xbot.print(name)
    xbot.print(web_page)

    # 进行登录

    # sb._to_account_page()
