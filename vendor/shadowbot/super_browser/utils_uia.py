# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .uia import auto
import re, time
from collections import deque
from xbot.win32 import Win32Element, Win32Window
from xbot._core.retry import Retry
from xbot.errors import UIAError, UIAErrorCode
from enum import Enum
import ctypes
import ntpath
import time
from ctypes import wintypes
from enum import Enum


print = [lambda *_, **__: None, print][__package__ == 'xbot_robot' or hasattr(xbot, "__log")]

def safe_set_active(window, retry=3):
    from .uia import auto
    for _ in range(retry):
        try:
            window.SetActive(waitTime=0)
            fg = auto.GetForegroundControl()
            if hasattr(window, 'NativeWindowHandle') and hasattr(fg, 'NativeWindowHandle'):
                if window.NativeWindowHandle == fg.NativeWindowHandle:
                    return True
            # 兼容处理：最小化+恢复（已取消置顶）
            window.Minimize()
            window.Restore()
            window.SetActive(waitTime=0)
            fg = auto.GetForegroundControl()
            if hasattr(window, 'NativeWindowHandle') and hasattr(fg, 'NativeWindowHandle'):
                if window.NativeWindowHandle == fg.NativeWindowHandle:
                    return True
        except Exception as e:
            print(f"SetActive失败: {e}")
        sleep(0.5)
    # 可选：用 pywin32 辅助（如需可自行恢复）
    return False


class Version(Enum):
    V5 = "V5"
    V6 = "V6"


def get_version():
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    versions = {
        "superbrowser.exe": Version.V5,
        "ziniao.exe": Version.V6,
        "ziniaobrowser.exe": Version.V6,
    }
    valid_titles = {"紫鸟浏览器", "紫鸟浏览器专业版"}
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    def get_process_name(pid):
        handle = kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION,
            False,
            pid,
        )
        if not handle:
            return None

        try:
            size = wintypes.DWORD(1024)
            buffer = ctypes.create_unicode_buffer(size.value)

            if not kernel32.QueryFullProcessImageNameW(
                handle, 0, buffer, ctypes.byref(size)
            ):
                return None

            return ntpath.basename(buffer.value).lower()
        finally:
            kernel32.CloseHandle(handle)

    def enum_versions():
        found = set()
        callback_type = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes.HWND,
            wintypes.LPARAM,
        )

        @callback_type
        def callback(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True

            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True

            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)

            if buffer.value.strip() not in valid_titles:
                return True

            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            version = versions.get(get_process_name(pid.value))
            if version:
                found.add(version)

            return True

        user32.EnumWindows(callback, 0)
        return found

    found = set()

    for _ in range(3):
        found = enum_versions()
        if found:
            break
        time.sleep(0.5)

    if not found:
        raise Exception("未找到紫鸟浏览器，请先打开")

    if len(found) > 1:
        raise Exception("同时存在多个版本紫鸟，请先关闭一个版本")

    return found.pop()


class ZiniaoNormal:
    def __init__(self):
        pass


    def _find_control(self, control_name: str='', searchDepth: int = 20, control_type: str = 'Control', pattern: str = None, timeout: float = 10.0, root=None):
        """
        查找指定控件，支持正则匹配。

        :param control_name: 控件名称
        :param searchDepth:  搜索深度, 默认为10
        :param control_type: 控件类型，默认为 'Control'
        :param pattern:      正则表达式，匹配控件名称
        :param timeout:      超时时间，默认为5秒
        :param root:         搜索根节点，默认为紫鸟窗口
        :return: auto对象
        """
        # 根节点为空时，默认使用 self.ziniao_window
        if root is None:
            root = self.ziniao_window
        # 如果未传入pattern，按原逻辑查找
        if not pattern:
            try:
                find_control = getattr(root, control_type)(searchDepth=searchDepth, Name=control_name, timeout=timeout)
            except Exception as e:
                print(f"未找到控件 '{control_name}'，错误: {e}")
                return None
            return find_control
        # 如果传入pattern，遍历所有同类型控件，正则匹配Name，并加超时判断
        else:
            def bfs_search(root, control_type, pattern, timeout):
                queue = deque([root])
                start_time = time.time()
                while queue:
                    next_level = []
                    for node in queue:
                        for child in node.GetChildren():
                            if child.ControlTypeName == control_type:
                                if hasattr(child, 'Name') and pattern.search(child.Name):
                                    return child
                            next_level.append(child)
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"正则查找控件超时（>{timeout}s），pattern: {pattern}")
                    queue = next_level
                return None
            found = bfs_search(root, control_type, pattern, timeout)
            if found:
                return found
            else:
                raise Exception(f"未找到符合正则 '{pattern}' 的控件")

    def _click_control(self, control_name: str, searchDepth: int = 10, control_type: str = 'Control'):
        """
        点击指定控件。

        :param control_name: 控件名称
        :param searchDepth:  搜索深度, 默认为10
        :param control_type: 控件类型，默认为 'Control'
        :return: auto对象
        """
        click_control = self._find_control(control_name, searchDepth, control_type)
        click_control.Click(waitTime=0.1)
        return click_control

    def _input_control(self, text_value: str, control_name: str, searchDepth: int = 20, control_type: str = 'EditControl'):
        """
        输入内容到指定控件。

        :param text_value:   输入内容
        :param control_name: 控件名称
        :param searchDepth:  搜索深度, 默认为20
        :param control_type: 控件类型，默认为 'EditControl'
        :return: auto对象
        """
        input_control = self._find_control(control_name, searchDepth, control_type)
        input_control.GetValuePattern().SetValue('')
        input_control.SendKeys(text_value, waitTime=0.01)
        return input_control