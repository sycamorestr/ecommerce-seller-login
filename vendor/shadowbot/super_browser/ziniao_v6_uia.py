import os
import re
import time
import subprocess
import traceback
import winreg

import psutil
import webbrowser
import win32con
import win32gui
import win32process
import xbot
import xbot_visual
from xbot import print

_ZINIAO_PROCESS_NAME = "ziniao"
_ZINIAO_TITLE = ["紫鸟浏览器", "我的账号"] # 紫鸟的窗口标题可能有多个
_UIA_AUTOMATION_ID_PROPERTY = 30011
_UIA_VALUE_VALUE_PROPERTY = 30045
_UIA_IS_KEYBOARD_FOCUSABLE_PROPERTY = 30009
_DEFAULT_ACCOUNT_PAGE_SIZE = 20
PREPARE_TIMEOUT_SECONDS = 600

_LOGIN_PANEL_URL_MARK = "/renderer/workbench/index.html#/login"
_DEBUG = os.getenv("ZINIAO_DEBUG", "").lower() in ("1", "true", "yes", "on")

import ctypes
import time
import win32con
import win32gui
import win32process


user32 = ctypes.windll.user32
oleacc = ctypes.oledll.oleacc


OBJID_CLIENT = -4
WM_GETOBJECT = 0x003D

import ctypes
import ctypes.wintypes as wt

user32 = ctypes.windll.user32
oleacc = ctypes.OleDLL("oleacc")

WM_GETOBJECT = 0x003D
OBJID_CLIENT = 0xFFFFFFFC  # 作为 lParam 传入时为 -4
# IID_IAccessible {618736E0-3C3D-11CF-810C-00AA00389B71} 的内存字节序
_IID_IACCESSIBLE = bytes.fromhex("e03687613d3ccf11810c00aa00389b71")














# 特殊方案激活uia
from .uia import (auto, force_uia, send_message_bounded, budget, phase,
                         check_budget, remaining, pause, OperationTimeout)

def _force_foreground(hwnd):
    """异步显示并尝试前台激活；键盘操作另行验证焦点。"""
    if not win32gui.IsWindow(hwnd):
        return False
    show = ctypes.WinDLL('user32', use_last_error=True).ShowWindowAsync
    show.argtypes, show.restype = (wt.HWND, ctypes.c_int), wt.BOOL
    show(hwnd, win32con.SW_RESTORE if win32gui.IsIconic(hwnd) else win32con.SW_SHOW)
    try:
        if win32gui.GetForegroundWindow() != hwnd:
            user32.keybd_event(0x12, 0, 0, 0)
            user32.keybd_event(0x12, 0, 2, 0)
            win32gui.SetForegroundWindow(hwnd)
    except Exception as exc:
        _debug_log('请求前台激活失败', exc)
    end_time = time.monotonic() + remaining(5)
    while time.monotonic() < end_time:
        check_budget()
        if win32gui.GetForegroundWindow() == hwnd:
            return True
        pause(0.05)
    return win32gui.GetForegroundWindow() == hwnd


def _focus_for_keys(control):
    root = control.GetTopLevelControl()
    if root is None or not _force_foreground(root.NativeWindowHandle):
        raise RuntimeError('紫鸟窗口未取得前台，停止发送键盘输入')
    control.SetFocus()
    end_time = time.monotonic() + remaining(5)
    while time.monotonic() < end_time:
        check_budget()
        if control.HasKeyboardFocus:
            return
        pause(0.1)
    raise RuntimeError('紫鸟输入控件未取得焦点，停止发送键盘输入')



def _poke_accessibility(hwnd):
    try:
        send_message_bounded(hwnd, WM_GETOBJECT, 0, -4, timeout_ms=300)
    except Exception as exc:
        _debug_log('请求 Accessibility 失败', exc)



def _is_window_responding(hwnd):
    """判断窗口是否处于未响应(工作台卡死)状态。

    未响应的窗口(尤其 Electron 工作台主窗口)上调用 UIA 的
    ControlFromHandle / WalkControl 会长时间挂起甚至抛异常。
    在遍历窗口列表或执行 UIA 操作前先过滤未响应窗口。
    """
    if not win32gui.IsWindow(hwnd):
        return False
    try:
        return not bool(user32.IsHungAppWindow(hwnd))
    except Exception as exc:
        _debug_log(f"检查窗口响应状态失败 hwnd={hwnd}", exc)
        return True


def _wait_window_responding(hwnd, timeout=15, interval=0.5):
    """等待指定窗口从未响应状态恢复，返回是否恢复。

    期间每 interval 秒探测一次；超时返回 False，不抛异常。
    """
    end_time = time.monotonic() + timeout
    while time.monotonic() < end_time:
        check_budget()
        if _is_window_responding(hwnd):
            return True
        pause(interval)
    return False


def _enum_child_hwnds(hwnd):
    result = []

    def callback(child_hwnd, _):
        result.append(child_hwnd)
        return True

    try:
        win32gui.EnumChildWindows(hwnd, callback, None)
    except Exception:
        pass

    return result


def start_independent(exe_path: str, *args: str):
    exe_path = os.path.abspath(exe_path)

    if not os.path.isfile(exe_path):
        raise FileNotFoundError(f"程序不存在: {exe_path}")

    first_arg = args[0]

    subprocess.Popen(
        ["explorer.exe", exe_path + first_arg, ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )



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


def _normalize_url(url):
    """标准化 URL，统一路径分隔符和大小写，便于后续匹配。"""
    return str(url or "").replace("\\", "/").lower()


def _url_match(mark, url):
    """匹配紫鸟页面 URL。"""
    return _normalize_url(url).endswith(_normalize_url(mark))


def set_control_text(control, text):
    """通过 ValuePattern 设置输入框文本。"""
    for _ in range(5):
        check_budget()
        try:
            value_pattern = control.GetValuePattern()
            if value_pattern and not value_pattern.IsReadOnly:
                value_pattern.SetValue(text)
                return
        except Exception as exc:
            _debug_log("ValuePattern.SetValue 失败", exc)

    raise Exception("输入框不支持 ValuePattern.SetValue")


def click_control(control):
    """统一触发控件，优先使用 UIA Pattern，尽量避免鼠标移动。"""
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
        _debug_log(legacy_pattern)
        if legacy_pattern:
            legacy_pattern.DoDefaultAction()
            return
    except Exception as exc:
        _debug_log("LegacyIAccessible 触发失败，尝试键盘或窗口消息", exc)

    if control.GetPropertyValue(_UIA_IS_KEYBOARD_FOCUSABLE_PROPERTY):
        _focus_for_keys(control)
        control.SendKeys("{Enter}")
        _debug_log("尝试通过发送回车触发点击元素")
        return

    rect = control.BoundingRectangle
    x = (rect.left + rect.right) // 2
    y = (rect.top + rect.bottom) // 2
    hwnd = win32gui.WindowFromPoint((x, y))
    if not hwnd:
        raise Exception("未找到控件所在窗口")

    client_x, client_y = win32gui.ScreenToClient(hwnd, (x, y))
    lparam = (client_y << 16) | (client_x & 0xFFFF)
    send_message_bounded(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    send_message_bounded(hwnd, win32con.WM_LBUTTONUP, 0, lparam)


class ZiNiao:
    def __init__(self, debug=None):
        """初始化紫鸟操作对象，可通过 debug 开启调试日志。"""
        if debug is not None:
            set_ziniao_debug(debug)

    def _get_exe_path(self):
        default_path = r"C:\Program Files\ziniao\ziniao.exe"

        registry_key = (
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            r"\8c327052-d9e8-5248-931f-e5b8c47f82b5"
        )

        for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY):
            check_budget()
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
                _debug_log("读取紫鸟注册表路径失败", exc)

        return default_path if os.path.isfile(default_path) else ""
    
    def _visible_hwnds(self):
        """获取紫鸟主程序的可见顶层窗口。"""
        return [
            hwnd
            for hwnd in _visible_hwnds_by_process(f"{_ZINIAO_PROCESS_NAME}.exe")
            if win32gui.GetWindowText(hwnd) in _ZINIAO_TITLE
        ]

    def _launch(self, timeout=30):
        """启动紫鸟并等待主窗口可见。"""
        if self._visible_hwnds():
            return

        process_info = xbot_visual.system.run_or_open(application_path=self._get_exe_path(), command_line_arguments= "--force-renderer-accessibility", working_folder=None, after_application_launch="continue", is_waitexit_not_more_than=False, timeout_for_exit="30", is_waithwnd_not_more_than=False, timeout_for_hwnd="30", start_as_admin=False, window_style="normal")

        # start_independent(self._get_exe_path(), "--force-renderer-accessibility")
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            check_budget()
            if self._visible_hwnds():
                return
            pause(0.2)

        raise Exception("启动紫鸟浏览器超时，未找到可见窗口")

    def _wait_document_by_url(self, url, timeout=10):
        """等待指定 URL 的紫鸟 Document 就绪。"""
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            check_budget()
            document = self._document_by_url(url)
            if document:
                return document
            pause(0.2)

        raise Exception(f"未找到紫鸟浏览器页面: {url}")

    def _panel_type(self, document):
        """通过固定 UIA 特征判断紫鸟面板类型。"""

        # 有刷新图标的是完整面板
        reload_button = document.ImageControl(Name="reload", searchDepth=8)
        has_reload = reload_button.Exists(0, 0)
        if has_reload:
            return "full"

        login_button = document.Control(Name="企业登录", searchDepth=15)
        if login_button.Exists(0, 0):
            return "login"

        account_button = document.Control(Name="账号", searchDepth=15)
        caret_down = document.ImageControl(Name="caret-down", searchDepth=8)
        if account_button.Exists(0, 0) and caret_down.Exists(0, 0):
            return "basic"
        return ""

    def _account_pagination(self, document):
        """通过账号表格相邻区域定位分页栏。"""
        control = document.Control(Name="上一页", searchDepth=30)

        if control.Exists(0, 0):
            parent = control.GetParentControl()
        else:
            control = document.Control(Name="left", searchDepth=30)
            parent = control.GetParentControl() if control.Exists(0, 0) else None
        return parent

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
        """获取账号列表的数据表控件。

        不同紫鸟版本/面板结构下，账号表格的层级路径不同：
        - 路径A: ...GetPreviousSiblingControl() 后直接 7 层 GetLastChildControl()
        - 路径B: ...GetPreviousSiblingControl().GetPreviousSiblingControl() 后 7 层 GetLastChildControl()
        先尝试路径A，取不到表格时再回退到路径B。
        """
        base = (
            document.Control(Name="search", searchDepth=30)
            .GetParentControl()
            .GetParentControl()
            .GetParentControl()
            .GetLastChildControl()
            .GetPreviousSiblingControl()
        )

        # 路径A
        try:
            table = base
            for _ in range(7):
                check_budget()
                table = table.GetLastChildControl()
            if table is not None:
                return table
        except Exception as exc:
            _debug_log("按路径A定位账号表格失败，尝试路径B", exc)

        # 路径B
        try:
            table = base.GetPreviousSiblingControl()
            for _ in range(7):
                check_budget()
                table = table.GetLastChildControl()
            if table is not None:
                return table
        except Exception as exc:
            _debug_log("按路径B定位账号表格失败", exc)

        raise Exception("未找到账号列表数据表格")

    def _document_from_hwnd(self, hwnd, timeout=5):
        """
        激活紫鸟/Chromium Accessibility，
        然后从顶层 HWND + 所有子 HWND 中寻找真正的 UIA Document。
        """

        if not hwnd or not win32gui.IsWindow(hwnd):
            return None
        if not _is_window_responding(hwnd):
            return None

        # --------------------------------------------------
        # 1. 真正把窗口拉到前台
        # --------------------------------------------------
        _force_foreground(hwnd)
        force_uia(hwnd)

        pause(0.2)

        # --------------------------------------------------
        # 2. 主动唤醒 Accessibility Provider
        # --------------------------------------------------
        _poke_accessibility(hwnd)

        child_hwnds = _enum_child_hwnds(hwnd)

        for child in child_hwnds:
            check_budget()
            _poke_accessibility(child)

        pause(0.3)

        # --------------------------------------------------
        # 3. 不要只搜索顶层 hwnd
        # Chromium UIA Provider 很可能挂在某个 child hwnd
        # --------------------------------------------------
        end_time = time.monotonic() + remaining(timeout)
        while time.monotonic() < end_time:

            check_budget()
            hwnds = [hwnd] + _enum_child_hwnds(hwnd)

            for current_hwnd in hwnds:
                check_budget()
                try:
                    if not _is_window_responding(current_hwnd):
                        continue
                    control = auto.ControlFromHandle(current_hwnd)

                    if not control:
                        continue

                    # 真正访问 Element，迫使 uiautomation 请求 UIA Provider
                    try:
                        _ = control.Name
                        _ = control.ControlType
                    except Exception:
                        pass

                    # 先看这个 HWND 自己是不是 Document
                    try:
                        if control.ControlType == auto.ControlType.DocumentControl:
                            return control
                    except Exception:
                        pass

                    # 再从此 HWND 向下找 Document
                    document = control.DocumentControl(
                        searchDepth=20
                    )

                    if document.Exists(0.2, 0.05):
                        return document

                except Exception as exc:
                    _debug_log(
                        f"等待 UIA Document: "
                        f"root={hwnd}, child={current_hwnd}",
                        exc,
                    )

            # 再 poke 一次
            _poke_accessibility(hwnd)

            pause(0.2)

        return None

        
    def _wait_any_panel(self, panel_types, timeout=10, login_document=None):
        """等待指定面板，并按 panel_types 顺序选择。"""
        end_time = time.monotonic() + timeout
        login_error = None
        if login_document:
            login_error = login_document.TextControl(
                RegexName=r"用户名.*密码错误",
                searchDepth=10,
            )

        while time.monotonic() < end_time:
            check_budget()
            if login_error and login_error.Exists(0, 0):
                raise Exception(login_error.Name or "用户名或者密码错误")

            documents = {}
            for hwnd in self._visible_hwnds():
                check_budget()
                try:
                    document = self._document_from_hwnd(hwnd, timeout=1)
                    if document:
                        panel_type = self._panel_type(document)
                        if panel_type in panel_types:
                            documents.setdefault(panel_type, document)
                except Exception as exc:
                    _debug_log(f"等待面板时读取窗口失败: hwnd={hwnd}", exc)

            for panel_type in panel_types:
                check_budget()
                if panel_type in documents:
                    return documents[panel_type], panel_type

            pause(0.2)

        raise Exception(f"未找到紫鸟面板: {', '.join(panel_types)}")

    def _document_by_url(self, url):
        """根据 URL 获取紫鸟浏览器的 Document。"""
        for hwnd in self._visible_hwnds():
            check_budget()
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
        """登录紫鸟，可选使用页面已保存的企业账号。"""
        # 已有紫鸟窗口且不在登录页时，说明存在登录态，必须先退出再重新登录。
        self._visible_hwnds()
        self._document_by_url(_LOGIN_PANEL_URL_MARK)        # 第一次去寻找login页面的时候，可能ui树没有激活，先找一次，确保后续的判断能够正常
        if self._visible_hwnds() and not self._document_by_url(_LOGIN_PANEL_URL_MARK):
            if not is_close:
                print("当前店铺已登录")
                return
            self.exit_app(timeout=max(timeout, 120))
        

        self._launch(timeout=timeout)

        document = self._wait_document_by_url(
            _LOGIN_PANEL_URL_MARK,
            timeout=timeout,
        )

        click_control(document.Control(Name="企业登录"))

        if is_fill:
            if not company_name:
                raise ValueError("企业名称不能为空")
            if not company_username:
                raise ValueError("企业用户名不能为空")

            company_ele = (
                document.Control(RegexName=r".*公司名.*")
                .GetParentControl()
                .GetNextSiblingControl()  # type: ignore
                .EditControl(searchDepth=10)  # type: ignore
            )
            set_control_text(company_ele, company_name)

            account_ele = (
                document.Control(RegexName=r".*企业用户名.*")
                .GetParentControl()
                .GetNextSiblingControl()  # type: ignore
                .EditControl(searchDepth=10)  # type: ignore
            )
            set_control_text(account_ele, company_username)

            # 密码为空时保留页面中已记住的密码。
            if password:
                password = xbot_visual.decrypt(password)
                password_ele = (
                    document.Control(RegexName=r".*企业.*密码.*")
                    .GetParentControl()
                    .GetNextSiblingControl()  # type: ignore
                    .EditControl(searchDepth=10)  # type: ignore
                )
                set_control_text(password_ele, password)

        error = "" # 错误信息

        for _ in range(5):
            check_budget()
            click_control(document.Control(Name="登 录"))

            try:
                self._wait_any_panel(
                    ("full", "basic"),
                    timeout=timeout,
                    login_document=document,
                )
                return

            except Exception as e:
                error = e
                print("尝试登录中.....")
        raise error

    def exit_app(self, timeout=20):
        """退出当前紫鸟登录态"""
        webbrowser.open("superbrowser://exit")
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            check_budget()
            if not self._visible_hwnds():
                pause(3)
                return
            pause(0.5)
        raise Exception("退出紫鸟浏览器超时")

    def open_store(
        self,
        store_name,
        *,
        privacy=False,
        match_type="相等",
        is_open="点击",
        timeout=20,
        user_limit="取 消",
    ):
        if match_type not in ["模糊", "相等"]:
            raise ValueError("匹配类型输入有误，仅支持： 模糊、相等")
        if is_open not in ["点击", "不点击"]:
            raise ValueError("打开账号输入有误，仅支持： 点击、不点击")

        store_name = store_name.strip()
        auto._AutomationClient.instance()  # 先选后端，再关闭任何店铺。
        for attempt in range(2):
            try:
                with budget(max(timeout, PREPARE_TIMEOUT_SECONDS), "打开店铺准备阶段"):
                    document, start_btn = self._prepare_store(store_name, match_type, timeout)
                break
            except OperationTimeout as exc:
                if attempt:
                    raise
                _debug_log("准备阶段超时，向紫鸟控制台发送唤醒输入后重试一次", exc)
                self._revive_console()
        self._start_store(document, start_btn, privacy)

        if self._handle_online_limit_dialog(document, user_limit):
            raise Exception(
                f"店铺[{store_name}]触发在线人数上限弹窗，"
                f"已按配置选择'{user_limit}'，本次启动终止"
            )
        
        # 针对申请访问名额情况,等待120s
        if user_limit == "申请访问名额":
            store_hwnd = self._wait_store_window(document, timeout=120)
        else:
            store_hwnd = self._wait_store_window(document, timeout=45)
        
        # 店铺窗口可能刚启动时工作台短暂未响应，等待其恢复再继续，避免下方 GetWindowText / UIA 挂起。
        force_uia(store_hwnd)
        _wait_window_responding(store_hwnd, timeout=max(timeout, 20))
        full_store_name = win32gui.GetWindowText(store_hwnd)
        web_page = None
        last_exc = None
        if is_open == "点击":
            for attempt in range(3):
                check_budget()
                try:
                    self._click_open_account(store_hwnd, timeout=30)
                    try:
                        web_page = self._wait_store_web_page(timeout=max(timeout, 10))
                    except Exception:
                        if not self._click_continue_account(store_hwnd):
                            raise
                        web_page = self._wait_store_web_page(timeout=max(timeout, 10))
                    if web_page is not None:
                        break
                except Exception as exc:
                    last_exc = exc
                    _debug_log(f"第 {attempt + 1} 次打开店铺账号页失败", exc)
            if web_page is None:
                raise Exception("打开店铺账号失败, 获取网页对象失败, 请检查浏览器插件是否正常安装启用") from last_exc
        return full_store_name, web_page

    def _prepare_store(self, store_name, match_type, timeout):
        with phase("关闭已有店铺"):
            self._close_store()
        with phase("进入账号面板"):
            document = self._open_full_panel(timeout=remaining(max(timeout, 120)))
        # self._close_dialog(document)


        # 清空和搜索使用 UIA Pattern，不受独立广告窗口遮盖影响。
        self._clear_account_search(document, timeout=timeout)
        with phase("搜索店铺"):
            self._search_store(document, store_name)

        self._click_account_first_page(document)
        self._require_account_page_size_20(document)

        if "," in store_name:
            target_name = store_name.casefold()
            start_btn = None
            for records in self._iter_account_pages(document, timeout=timeout):
                check_budget()
                if any(
                    target_name in account_name.casefold()
                    if match_type == "模糊"
                    else target_name == account_name.casefold()
                    for account_name, _, _ in records
                ):
                    start_btn = self._find_store_start_button(
                        document,
                        store_name,
                        match_type,
                        timeout=timeout,
                    )
                    break
            if start_btn is None:
                raise Exception(f"未搜索到指定店铺：{store_name}")
        else:
            start_btn = self._find_store_start_button(
                document,
                store_name,
                match_type,
                timeout=timeout,
            )
            print(start_btn)
        return document, start_btn

    def _revive_console(self):
        """准备阶段超时后的无害唤醒：向控制台窗口投递 Shift 按键、鼠标移动并重新敲门。

        不点按钮、不发 F5；PostMessage 异步投递，对窗口无实质副作用，也不会阻塞。
        """
        for hwnd in self._visible_hwnds():
            try:
                win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_SHIFT, 0)
                win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_SHIFT, 0)
                win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, 0)
                _poke_accessibility(hwnd)
            except Exception as exc:
                _debug_log(f"唤醒紫鸟控制台窗口失败 hwnd={hwnd}", exc)
        pause(5)

    def _close_dialog(self, document):
        """关闭可能遮挡账号操作区域的紫鸟弹窗。"""
        # 精简面板提示使用 HyperlinkControl，不能按 ButtonControl 定位。
        know_button = document.HyperlinkControl(
            Name="知道了",
            searchDepth=30,
        )
        if know_button.Exists(0, 0):
            click_control(know_button)

        # 关闭升级提醒弹窗。
        search_button = document.ButtonControl(Name="search", searchDepth=30)
        search_close_id = None
        if search_button.Exists(0, 0):
            search_close_button = search_button.GetParentControl().ButtonControl(
                Name="close-circle",
                searchDepth=5,
            )
            if search_close_button.Exists(0, 0):
                search_close_id = search_close_button.GetRuntimeId()

        for button, _ in auto.WalkControl(document, includeTop=False, maxDepth=30):
            check_budget()
            if button.ControlTypeName != "ButtonControl" or button.Name != "close-circle":
                continue
            if search_close_id is not None and button.GetRuntimeId() == search_close_id:
                continue
            click_control(button)
            break

        # 关闭资源到期提醒弹窗。
        expiration_close_button = document.ButtonControl(
            Name="close",
            searchDepth=30,
        )
        if expiration_close_button.Exists(0, 0):
            # click_control(expiration_close_button)
            pass

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
                kernel_title.GetParentControl().GetParentControl().GetParentControl()
            )
            cancel_button = kernel_dialog.ButtonControl(
                RegexName=r"取\s*消",
                searchDepth=5,
            )
        except Exception as e:
            # 工作台可能短暂未响应，UIA 调用会抛 COM 错误(0x80040201)。
            _debug_log("处理启动店铺后弹窗失败, 影响较小, 忽略异常", e)
            return

        if not cancel_button.Exists(1, 0):
            raise Exception("下载内核弹窗未找到取消按钮")

        click_control(cancel_button)
        raise Exception("启动店铺失败，请下载指定内核，下载升级内核后即可启动")

    def _handle_online_limit_dialog(self, document, action, timeout=1):
        """处理在线人数上限弹窗，返回是否应终止打开店铺流程。"""
        if not action:
            return False

        try:
            micro_slot = document.Control(
                AutomationId="microSlot",
                searchDepth=10,
            )
            if not micro_slot.Exists(0, 0):
                return False
        except Exception as exc:
            _debug_log("处理在线人数弹窗失败(可能工作台未响应)", exc)
            return False

        try:
            dialog = micro_slot.CustomControl(
                SubName="当前在线人员",
                searchDepth=3,
                timeout=1
            )
            if not dialog.Exists(timeout, 0.2):
                return False
        except Exception as exc:
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

    def _search_store(self, document, store_name):
        """输入店铺名称并校验输入值后执行搜索。"""
        search_button = document.ButtonControl(Name="search", searchDepth=30)
        if not search_button.Exists(1, 0):
            raise Exception("未找到店铺搜索按钮")

        search_input = search_button.GetParentControl().EditControl(searchDepth=5)
        if not search_input.Exists(1, 0):
            raise Exception("未找到店铺搜索输入框")

        # 输入框用 Legacy 唤起下拉框；Invoke 可能返回成功但不展开。

        first_option = document.TextControl(
            Name="全局搜索", searchDepth=30,
            Compare=lambda control, depth: not control.IsOffscreen and control.IsEnabled,
        )

        for _ in range(5):
            check_budget()
            _focus_for_keys(search_input)
            if not first_option.Exists(0, 0):
                input_action = search_input.GetPattern(auto.PatternId.LegacyIAccessiblePattern)
                if input_action:
                    input_action.DoDefaultAction()
            if str(search_input.GetPropertyValue(_UIA_VALUE_VALUE_PROPERTY) or "") != store_name:
                auto.SendKeys("{Ctrl}a{Delete}", waitTime=0.05)
                auto.SendKeys(store_name, interval=0.2, waitTime=0.5)
            pause(3)
            current_value = str(
                search_input.GetPropertyValue(_UIA_VALUE_VALUE_PROPERTY) or ""
            )
            if current_value != store_name:
                continue

            if not first_option.Exists(3, 0.2):
                continue

            # 选择搜索范围时页面会直接执行查询，不需要再次点击搜索按钮。
            click_control(first_option)
            applied_scope = search_input.GetParentControl().TextControl(
                Name="全局搜索包含：", searchDepth=5,
                Compare=lambda control, depth: not control.IsOffscreen,
            )
            if applied_scope.Exists(3, 0.2):
                return
            # 未应用搜索条件时，下一轮只重新唤起下拉框；输入值正确则不重输。
        raise Exception("填写店铺名称异常或未触发搜索下拉框导致输入搜索店铺失败")


    @staticmethod
    def _account_row_texts(row_control):
        """读取账号行第2列店铺名称/店铺类型、第3列真实平台名称。"""
        children = row_control.GetChildren()
        if len(children) < 3:
            return []

        def collect_texts(cell):
            return [
                text
                for item, _ in auto.WalkControl(
                    cell,
                    includeTop=True,
                    maxDepth=5,
                )
                if item.ControlTypeName == "TextControl"
                for text in [(item.Name or "").strip()]
                if text
            ]

        account_texts = collect_texts(children[1])
        if not account_texts:
            return []
        store_name = account_texts[0]
        store_type = account_texts[1] if len(account_texts) > 1 else ""

        platform_texts = collect_texts(children[2])
        platform_name = platform_texts[0] if platform_texts else ""

        return [store_name, store_type, platform_name]

    def _find_store_start_button(
        self,
        document,
        store_name,
        match_type="相等",
        timeout=10,
    ):
        """在当前账号表格中定位匹配店铺的启动或切换按钮。"""
        target_name = store_name.casefold()
        end_time = time.monotonic() + timeout
        last_operation = ""

        while time.monotonic() < end_time:
            check_budget()
            matched_rows = []
            try:
                for row_control in self._account_data_table(document).GetChildren():
                    # print(row_control)

                    check_budget()
                    texts = self._account_row_texts(row_control)
                    if not texts:
                        continue

                    account_name = texts[0]
                    matched = (
                        target_name in account_name.casefold()
                        if match_type == "模糊"
                        else target_name == account_name.casefold()
                    )
                    if matched:
                        matched_rows.append(row_control)
            except Exception as exc:
                _debug_log("读取账号表格失败", exc)
                # 工作台可能短暂未响应导致 UIA COM 错误(0x80040201)，等待恢复后重试
                for hwnd in self._visible_hwnds():
                    check_budget()
                    if not _is_window_responding(hwnd):
                        _wait_window_responding(hwnd, timeout=5)
                        break
                pause(0.2)
                continue

            if match_type == "相等" and len(matched_rows) > 1:
                raise Exception("找到多个匹配的店铺，无法唯一确定")

            # print("matched_rows", matched_rows)

            for row_control in matched_rows:
                check_budget()
                start_button = row_control.ButtonControl(
                    RegexName=r"^(启动|切换)$",
                    searchDepth=8,
                )
                if start_button.Exists(0, 0):
                    return start_button
                last_operation = (
                    row_control.GetLastChildControl().Name or "未找到启动按钮"
                )

            if matched_rows and last_operation:
                raise Exception(f"店铺当前无法启动: {last_operation}")
            pause(0.2)

        raise Exception(f"未搜索到指定店铺：{store_name}")

    def _start_store(self, document, start_button, privacy):
        """按隐私或正常模式启动已定位的店铺。"""
        if privacy:
            self._close_dialog(document)
            
            more_button = start_button.GetParentControl().GetParentControl().GetNextSiblingControl()
            if not more_button.Exists(1, 0):
                raise Exception("未找到隐私模式更多操作按钮")
            auto.MoveTo(0, 0)
            # print(more_button)
            rect = more_button.BoundingRectangle
            auto.Click(rect.xcenter(), rect.ycenter())
            # operation_menu = document.Control(
            #     AutomationId="currentMoreOperationPopover",
            #     searchDepth=30,
            # )
            # if not operation_menu.Exists(1, 0):
            #     raise Exception("未找到账号更多操作菜单")

            temporary_mode_item = document.TextControl(
                Name="临时模式启动",
                searchDepth=20,
            )
            if not temporary_mode_item.Exists(1, 0):
                raise Exception("未找到临时模式启动菜单项")

            click_control(temporary_mode_item.GetParentControl())

            temporary_dialog = document.Control(
                Name="本次临时启动配置",
                searchDepth=30,
            )
            if not temporary_dialog.Exists(1, 0):
                raise Exception("未找到临时启动配置弹窗")

            load_plugins_checkbox = temporary_dialog.CheckBoxControl(
                RegexName=r"加载插件\s*",
                searchDepth=10,
            )
            if not load_plugins_checkbox.Exists(1, 0):
                raise Exception("未找到加载插件复选框")
            toggle_pattern = load_plugins_checkbox.GetTogglePattern()
            if not toggle_pattern:
                raise Exception("加载插件复选框不支持 TogglePattern")
            if toggle_pattern.ToggleState == auto.ToggleState.Off:
                toggle_pattern.Toggle()
            if toggle_pattern.ToggleState != auto.ToggleState.On:
                raise Exception("加载插件复选框未选中")

            temporary_start_button = temporary_dialog.ButtonControl(
                RegexName=r"启\s*动",
                searchDepth=10,
            )
            if not temporary_start_button.Exists(1, 0):
                raise Exception("未找到临时启动确认按钮")
            click_control(temporary_start_button)
            self._handle_kernel_download_dialog(document, timeout=1)
            return

        if start_button.Name == "切换":
            click_control(start_button)
        elif start_button.Name != "启动":
            raise Exception(f"启动按钮文字不是启动：{start_button.Name}")
        else:
            start_exc = None
            started = False
            known_hwnds = set(_visible_hwnds_by_process("ziniaobrowser.exe"))
            # 启动是第一次页面跳转：每次尝试轮换触发方式并校验生效信号，
            # 避免 Invoke 假成功被当作已启动。
            methods = ("invoke", "legacy", "mouse", "enter")
            for attempt in range(5):
                check_budget()
                method = methods[attempt % len(methods)]
                try:
                    if start_button.Name != "启动":
                        started = True
                        break
                    self._fire_button(start_button, method)
                    self._handle_kernel_download_dialog(document, timeout=0.5)
                    if self._start_took_effect(start_button, known_hwnds):
                        started = True
                        break
                    raise Exception(f"启动按钮 {method} 触发后无跳转信号")
                except Exception as exc:
                    start_exc = exc
                    _debug_log(f"点击启动第 {attempt + 1} 次失败({method})", exc)
                    # 工作台可能短暂未响应，等待恢复后重试
                    try:
                        hwnd = start_button.NativeWindowHandle or 0
                    except Exception:
                        hwnd = 0
                    _wait_window_responding(hwnd, timeout=8)
            if not started and start_exc is not None:
                raise start_exc

    def _wait_store_window(self, document, timeout=20):
        """等待店铺窗口的 UIA Document 出现，并返回窗口句柄。"""
        end_time = time.monotonic() + timeout
        next_kernel_check = time.monotonic()

        while time.monotonic() < end_time:
            check_budget()
            if time.monotonic() >= next_kernel_check:
                self._handle_kernel_download_dialog(document)
                next_kernel_check = time.monotonic() + 1

            saw_unresponsive = False
            for hwnd in _visible_hwnds_by_process("ziniaobrowser.exe"):
                check_budget()
                if not _is_window_responding(hwnd):
                    saw_unresponsive = True
                    continue
                title = win32gui.GetWindowText(hwnd)
                if title in ["紫鸟浏览器", "另存为", "提示", "翻译此页？"]:
                    continue
                if "影刀RPA网页自动化" in title:
                    continue

                try:
                    root = auto.ControlFromHandle(hwnd)
                    if not root:
                        continue
                    store_document = root.DocumentControl(searchDepth=10)
                    if store_document.Exists(0, 0):
                        return hwnd
                except Exception as exc:
                    _debug_log(f"检查店铺窗口 Document 失败 hwnd={hwnd}", exc)
                    continue

            if saw_unresponsive:
                remaining = end_time - time.monotonic()
                if remaining <= 0:
                    break
                for hwnd in _visible_hwnds_by_process("ziniaobrowser.exe"):
                    check_budget()
                    if not _is_window_responding(hwnd):
                        _wait_window_responding(hwnd, timeout=min(5.0, remaining))
                        break
                continue

            pause(0.2)

        raise Exception("店铺浏览器窗口未出现")

    def _fire_button(self, control, method):
        """按指定方式触发一次按钮动作；调用本身失败时抛异常。"""
        if method == "invoke":
            pattern = control.GetPattern(auto.PatternId.InvokePattern)
            if not pattern:
                pattern = control.GetInvokePattern()
            pattern.Invoke()
            return
        if method == "legacy":
            pattern = control.GetPattern(auto.PatternId.LegacyIAccessiblePattern)
            if not pattern:
                raise Exception("控件不支持 LegacyIAccessible")
            pattern.DoDefaultAction()
            return
        if method == "enter":
            if not control.GetPropertyValue(_UIA_IS_KEYBOARD_FOCUSABLE_PROPERTY):
                raise Exception("控件不可聚焦")
            _focus_for_keys(control)
            control.SendKeys("{Enter}")
            return
        if method == "mouse":
            rect = control.BoundingRectangle
            x = (rect.left + rect.right) // 2
            y = (rect.top + rect.bottom) // 2
            hwnd = win32gui.WindowFromPoint((x, y))
            if not hwnd:
                raise Exception("未找到控件所在窗口")
            client_x, client_y = win32gui.ScreenToClient(hwnd, (x, y))
            lparam = (client_y << 16) | (client_x & 0xFFFF)
            send_message_bounded(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
            send_message_bounded(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
            return
        raise ValueError(f"未知点击方式: {method}")

    @staticmethod
    def _active_document_url(root):
        try:
            doc = root.DocumentControl(searchDepth=20)
            if doc.Exists(0, 0):
                return str(
                    doc.GetPropertyValue(_UIA_VALUE_VALUE_PROPERTY) or ""
                )
        except Exception:
            pass
        return ""

    @staticmethod
    def _document_count(root, cap=3):
        """统计窗口内 Document 控件数（页签数），早退限节点扫描量。"""
        count, stack, seen = 0, [root], 0
        while stack and count < cap and seen < 200:
            control = stack.pop()
            seen += 1
            try:
                if control.ControlType == auto.ControlType.DocumentControl:
                    count += 1
                stack.extend(control.GetChildren() or [])
            except Exception:
                continue
        return count


    def _open_account_took_effect(self, store_hwnd, base_url="", base_docs=1,
                                  timeout=6):
        """打开账号点击的生效信号：新文档页出现、活动页 URL 变化、
        按钮消失/置灰，或出现"继续"确认。"""
        end_time = time.monotonic() + timeout
        while time.monotonic() < end_time:
            check_budget()
            try:
                root = auto.ControlFromHandle(store_hwnd)
                if not root:
                    pause(0.3)
                    continue
                url = self._active_document_url(root)
                if url and url != base_url:
                    return True
                if self._document_count(root, cap=base_docs + 1) > base_docs:
                    return True
                button = root.ButtonControl(Name="打开账号")
                if not button.Exists(0.3, 0.1):
                    return True
                try:
                    if not button.IsEnabled:
                        return True
                except Exception:
                    pass
                continue_button = root.ButtonControl(
                    RegexName=r"^继\s*续$", searchDepth=30
                )
                if continue_button.Exists(0, 0):
                    # "继续"本来就是生效后要点的确认，提前点掉省去等待网页超时。
                    try:
                        click_control(continue_button)
                        _debug_log("打开账号后出现继续确认，已提前点击")
                    except Exception as exc:
                        _debug_log("提前点击继续确认失败，留待延迟路径处理", exc)
                    return True
            except Exception:
                # 页面跳转中窗口可能短暂不可读，继续探测
                pause(0.3)
                continue
            pause(0.3)
        return False

    def _start_took_effect(self, start_button, known_hwnds, timeout=10):
        """启动按钮点击的生效信号：按钮文字变化、店铺新窗口出现。"""
        end_time = time.monotonic() + timeout
        excluded = {"紫鸟浏览器", "另存为", "提示", "翻译此页？"}
        while time.monotonic() < end_time:
            check_budget()
            try:
                if start_button.Name != "启动":
                    return True
            except Exception:
                pass
            for hwnd in _visible_hwnds_by_process("ziniaobrowser.exe"):
                check_budget()
                if hwnd in known_hwnds:
                    continue
                title = win32gui.GetWindowText(hwnd)
                if title and title not in excluded and "影刀RPA网页自动化" not in title:
                    return True
            pause(0.4)
        return False


    def _click_open_account(self, store_hwnd, timeout=30):
        """在指定店铺窗口中点击"打开账号"。"""
        end_time = time.monotonic() + timeout
        saw_button = False
        click_no_effect = False
        disabled_reads = 0

        # 循环内每次都重新获取 root，工作台未响应恢复后 Chromium 会替换 Document，
        # 缓存的控件引用会失效，必须重新定位。
        while time.monotonic() < end_time:
            check_budget()
            if not _is_window_responding(store_hwnd):
                _wait_window_responding(store_hwnd, timeout=5)
                continue
            try:
                force_uia(store_hwnd)
                root = auto.ControlFromHandle(store_hwnd)
                if not root:
                    pause(0.2)
                    continue

                open_account = root.ButtonControl(Name="打开账号")
                if not open_account.Exists(0, 0):
                    # 自动进入网页时先切回第一个浏览器 Tab，打开账号页才会出现。
                    new_tab_button = root.ButtonControl(Name="新标签页", searchDepth=15)
                    if new_tab_button.Exists(0, 0):
                        tab_control = new_tab_button.GetParentControl()
                        first_tab = tab_control.TabItemControl(searchDepth=10)
                        if first_tab.Exists(0, 0):
                            click_control(first_tab)
                    pause(0.2)
                    continue
                saw_button = True

                try:
                    if not open_account.IsEnabled or open_account.IsOffscreen:
                        disabled_reads += 1
                        if disabled_reads < 3:
                            _debug_log("打开账号按钮不可用，等待环境检查完成后重试")
                            pause(0.5)
                            continue
                        _debug_log("打开账号按钮状态持续不可用，按旧行为照常触发")
                    else:
                        disabled_reads = 0
                except Exception:
                    pass  # 状态读不出时保持宽松，照常尝试

                # 打开账号是第二次页面跳转：每次触发必须看到跳转信号；
                # Invoke 假成功（有返回无效果）时依次换 Legacy/鼠标/回车。
                pause(3)
                base_url = self._active_document_url(root)
                base_docs = self._document_count(root)
                took_effect = False
                for method in ("invoke", "legacy", "mouse", "enter"):
                    try:
                        self._fire_button(open_account, method)
                    except Exception as exc:
                        _debug_log(f"打开账号 {method} 调用失败", exc)
                        continue
                    if self._open_account_took_effect(
                        store_hwnd, base_url, base_docs
                    ):
                        took_effect = True
                        break
                    _debug_log(f"打开账号 {method} 调用后无跳转，换方式重试")
                if not took_effect:
                    click_no_effect = True
                    _debug_log("打开账号多次触发均未产生跳转，等待后整轮重试")
                    pause(0.5)
                    continue

                for _ in range(5):
                    check_budget()
                    save_as_hwnd = win32gui.FindWindow("#32770", "另存为")
                    if save_as_hwnd:
                        win32gui.PostMessage(save_as_hwnd, win32con.WM_CLOSE, 0, 0)
                        break
                    pause(0.3)
                return
            except Exception as exc:
                _debug_log("点击打开账号失败(可能工作台未响应)", exc)
                pause(0.3)

        if saw_button and click_no_effect:
            raise Exception("打开账号按钮已触发但未产生页面跳转")
        raise Exception("未找到店铺窗口中的打开账号按钮")

    def _click_continue_account(self, store_hwnd):
        """网页对象未就绪时，单次查找并点击"继续"确认按钮。"""
        if not _wait_window_responding(store_hwnd, timeout=5):
            return False
        root = auto.ControlFromHandle(store_hwnd)
        if not root:
            raise Exception("未找到店铺窗口 UIA 根节点")

        continue_button = root.ButtonControl(
            RegexName=r"^继\s*续$",
            searchDepth=30,
        )
        if not continue_button.Exists(0, 0):
            return False

        click_control(continue_button)
        return True

    def _wait_store_web_page(self, timeout=30):
        """等待影刀接入当前店铺的活动网页。"""
        end_time = time.monotonic() + timeout

        while time.monotonic() < end_time:
            check_budget()
            try:
                # get_all 建立插件连接，get_active 返回当前打开的账号页面。
                xbot.web.get_all(mode="ziniaobrowser")  # type: ignore
                return xbot.web.get_active(  # type: ignore
                    mode="ziniaobrowser",
                    load_timeout=0,
                )
            except Exception:
                pause(0.2)

        # 再调用一次，向上抛出影刀提供的真实错误码和调用栈。
        xbot.web.get_all(mode="ziniaobrowser")  # type: ignore
        return xbot.web.get_active(  # type: ignore
            mode="ziniaobrowser",
            load_timeout=0,
        )

    def _close_store(self):
        """关闭店铺浏览器，不能直接强制杀死进程，会有风控提示"""

        def is_store_hwnd(hwnd):
            """判断窗口是否为实际运行中的店铺浏览器窗口。"""
            title = win32gui.GetWindowText(hwnd)
            if title in {"紫鸟浏览器", "另存为", "提示", "翻译此页？"}:
                return False
            if "影刀RPA网页自动化" in title:
                return False

            return bool(title)

        def store_hwnds():
            """获取当前可见的店铺浏览器窗口。"""
            return [
                hwnd
                for hwnd in _visible_hwnds_by_process("ziniaobrowser.exe")
                if is_store_hwnd(hwnd)
            ]

        def confirm_tip_window():
            """确认关闭店铺时出现的提示窗口。"""
            for hwnd in _visible_hwnds_by_process("ziniaobrowser.exe"):
                check_budget()
                if not _is_window_responding(hwnd):
                    continue
                if win32gui.GetWindowText(hwnd) != "提示":
                    continue

                root = auto.ControlFromHandle(hwnd)
                ok_button = root.ButtonControl(Name="确定", searchDepth=12)  # type: ignore
                if not ok_button.Exists(1, 0):
                    continue

                click_control(ok_button)
                return True
            return False

        

        hwnds = store_hwnds()
        if not hwnds:
            return

        for hwnd in hwnds:
            check_budget()
            if not win32gui.IsWindow(hwnd):
                continue
            try:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            except Exception as exc:
                _debug_log(f"关闭店铺窗口失败: hwnd={hwnd}", exc)

        end_time = time.monotonic() + 8
        while time.monotonic() < end_time:
            check_budget()
            confirm_tip_window()
            if all(not win32gui.IsWindow(hwnd) for hwnd in hwnds):
                return
            pause(0.2)

        if all(not win32gui.IsWindow(hwnd) for hwnd in hwnds):
            return
        raise Exception("关闭店铺超时")

    def _click_account_button(self, document, timeout=10):
        """点击账号菜单，并等待完整面板进入账号页面。"""
        account_button = document.Control(Name="账号", searchDepth=30)
        if not account_button.Exists(1, 0):
            raise Exception("未找到紫鸟账号按钮")

        click_target = account_button
        try:
            click_target = (
                account_button.GetParentControl().GetParentControl()  # type: ignore
            )
        except Exception as exc:
            _debug_log("获取账号按钮父级点击目标失败，使用账号文本控件", exc)

        # 父级容器点击已验证可稳定触发 Electron 菜单。
        click_control(click_target)

        # 有可能紫鸟网络问题, 账号页面不能正常加载, 需要额外的判断
        for attempt in range(5):
            check_budget()
            document, panel_type = self._wait_any_panel(
                ("full",),
                timeout=timeout,
            )
            account_layout = document.Control(
                LocalizedControlType="菜单",
                searchDepth=25,
            )
            reload_button = document.ImageControl(Name="reload", searchDepth=8)

            if account_layout.Exists(timeout, 0.2):
                return document
            
            if not reload_button.Exists(timeout, 0.2):
                continue

            click_control(reload_button)
            pause(1)


        raise Exception("未找到紫鸟账号面板")

    def _open_full_panel(self, timeout=5):
        """打开完整账号面板，并返回完整面板的 document 节点。并保证当前面板停留在账号页面。"""
        if not self._visible_hwnds():
            raise Exception("未打开紫鸟浏览器")

        document, panel_type = self._wait_any_panel(
            ("full", "basic", "login"),
            timeout=timeout,
        )

        if panel_type == "login":
            raise Exception("紫鸟浏览器未登录，请先登录")
        if panel_type == "full":
            return self._click_account_button(document, timeout=timeout)

        full_panel_button = (
            document.ImageControl(Name="caret-down", searchDepth=8)
            .GetNextSiblingControl()
            .GetNextSiblingControl()  # type: ignore
        )
        click_control(full_panel_button)
        full_document = self._wait_any_panel(("full",), timeout=timeout)[0]
        return self._click_account_button(
            full_document,
            timeout=timeout,
        )

    def _clear_account_search(self, document, timeout=5):
        """等待账号列表加载后清空搜索条件。"""
        search_button = document.ButtonControl(Name="search", searchDepth=30)

        if not search_button.Exists(timeout, 0.2):
            raise Exception("未找到可见的搜索按钮")

        search_parent = search_button.GetParentControl()
        close_button = search_parent.ButtonControl(  # type: ignore
            Name="close-circle",
            searchDepth=5,
        )
        if not close_button.Exists(0, 0):
            return

        click_control(close_button)

        end_time = time.monotonic() + 5
        while time.monotonic() < end_time:
            check_budget()
            if not search_parent.ButtonControl(  # type: ignore
                Name="close-circle",
                searchDepth=5,
            ).Exists(0, 0):
                return
            pause(0.2)

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
        layout = document.Control(Name="什么是账号？", searchDepth=25)
        # 有账号列表时会拆成左侧筛选栏、分隔条、右侧内容区；无账号引导页只有一个内容区。
        return layout.Exists(1, 0.2)

    def _require_account_page_size_20(self, document):
        """确保账号列表分页大小为 20。建议固定使用 20 条/页；50 条/页时账号表格元素结构会变化。"""
        if self._account_page_size(document) == _DEFAULT_ACCOUNT_PAGE_SIZE:
            return

        # 复用分页栏最后一个元素定位页大小控件，避免全页面搜索"xx 条/页"。
        pagination = self._account_pagination(document)
        if not pagination.Exists(2, 0.2):
            raise Exception("未找到账号分页大小控件")

        page_size_area = pagination.GetLastChildControl()
        combo = page_size_area.ComboBoxControl(Name="页码", searchDepth=5)
        # ComboBox 本身可触发下拉，但点击外层页码区域更快。
        # click_control(combo.GetParentControl().GetParentControl())
        _focus_for_keys(combo)
        combo.SendKeys("{Alt}{Down}", waitTime=0.1)

        # Ant Design Select 的下拉列表 AutomationId 由 ComboBox 的 AutomationId 派生：
        # rc_select_2 -> rc_select_2_list_1，其中 _list_1 对应"20 条/页"。
        page_size_option = document.ListItemControl(
            AutomationId=f"{combo.AutomationId}_list_1",
            searchDepth=35,
        )
        if not page_size_option.Exists(3, 0.2):
            raise Exception("未找到20条/页选项")
        click_control(page_size_option)

        end_time = time.monotonic() + 8
        while time.monotonic() < end_time:
            check_budget()
            try:
                if self._account_page_size(document) == _DEFAULT_ACCOUNT_PAGE_SIZE:
                    return
            except Exception as exc:
                _debug_log("等待账号分页大小切换失败", exc)
            pause(0.2)

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
            check_budget()
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

            pause(0.2)

        if last_error:
            raise Exception(f"等待账号页店铺数据超时: {last_error}")
        raise Exception("等待账号页店铺数据超时")

    def _extract_store_records_from_account_table(self, document):
        """从账号列表表格提取账号名称和平台名称。"""
        try:
            data_table = self._account_data_table(document)
        except Exception as exc:
            _debug_log("定位账号表格失败", exc)
            return []

        store_records = []
        for row_control in data_table.GetChildren():
            check_budget()
            texts = self._account_row_texts(row_control)
            if len(texts) < 3:
                continue
            store_name, store_type, platform_name = texts
            store_records.append((store_name, platform_name, store_type))

        return store_records

    def _iter_account_pages(self, document, timeout=8):
        """按页面总数设置硬页数边界；业务预算覆盖所有翻页。"""
        total = self._account_total_record(document)
        size = self._account_page_size(document)
        if total < 0 or size <= 0:
            raise RuntimeError('账号分页数量无效')
        max_pages = (total + size - 1) // size
        if not max_pages:
            return
        previous_records = None
        for page_index in range(max_pages):
            check_budget()
            records = self._wait_account_page_records(document, previous_records, timeout=remaining(timeout))
            yield records
            next_page = document.ListItemControl(RegexName=r"^(下一页|right)$", searchDepth=30)
            if not next_page.Exists(remaining(2), 0.2) or not next_page.IsEnabled:
                return
            if page_index + 1 >= max_pages:
                raise RuntimeError('账号分页超过页面总数对应的页数上限')
            click_control(next_page)
            pause(2)
            previous_records = records


    def get_store_list(self, selected_platform=None, timeout=30):
        """获取紫鸟中的店铺列表"""
        document = self._open_full_panel(timeout=timeout)
        # print("self._is_empty_account_page(document)", self._is_empty_account_page(document))
        if self._is_empty_account_page(document):
            return []

        self._clear_account_search(document, timeout=timeout)
        self._click_account_first_page(document)

        self._require_account_page_size_20(document)
        total_record = self._account_total_record(document)
        if total_record == 0:
            return []

        store_names = []
        fetched_record_count = 0
        for page_records in self._iter_account_pages(document, timeout=timeout):
            check_budget()
            fetched_record_count += len(page_records)
            for store_name, platform_name, store_type in page_records:
                check_budget()
                if selected_platform:
                    sel = selected_platform.upper()
                    if (
                        sel != platform_name.split("-")[0].upper()
                        and sel != store_type.upper()
                    ):
                        continue
                if store_name not in store_names:
                    store_names.append(store_name)

        if fetched_record_count != total_record:
            raise Exception(
                f"账号列表数量不一致: 页面显示{total_record}条, "
                f"实际获取{fetched_record_count}条"
            )
        return store_names


def main(args):
    raise RuntimeError('此模块为底层实现，请运行原打开店铺入口或 test_uia')

    # print(f"打开店铺: {full_store_name}")
    # print(f"web_page: {web_page}")
    # ziniao.get_store_list()

