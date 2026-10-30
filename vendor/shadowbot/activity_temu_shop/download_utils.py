# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
import xbot_visual
from .import package
from .package import variables as glv
from xbot.selector import Selector  # type: ignore
from xbot.web import WebBrowser, WebElement  # type: ignore
from xbot.web import handle_save_dialog
from xbot.errors import UIAError
from xbot import logging
import time
import threading

# Windows API 相关导入（用于新方法）
try:
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    VK_RETURN = 0x0D
except ImportError:
    user32 = None


def download_handler(web_page:WebBrowser,file_folder:str,file_name:str):
    # ========== 原方法（已注释，保留作为参考） ==========
    # # 下载报告
    # file_path = handle_save_dialog(file_folder=str(file_folder), mode=web_page.product_name, file_name=file_name, wait_complete=False)
    # try:
    #     # 查找下载提示窗口
    #     window = xbot.win32.get_by_selector("下载提示窗口", timeout=0)
    #     if window:
    #         window.activate()  # 激活窗口
    #         client = window.find("下载提示窗口")  # 查找窗口内元素
    #         # 查找并点击"确定"按钮
    #         find_element_by_text(client, "确定").click(
    #             move_mouse=False, delay_after=0
    #         )
    # except UIAError as e:
    #     logging.error("confirm_download_save uia error", e)
    # except Exception as e:
    #     logging.error("confirm_download_save error", e)
    # return file_path
    
    # ========== 新方法：使用 Windows API 处理保存地址弹窗 ==========
    is_completed = False
    
    def wait_and_send_enter(
        window_title_list: list,
        class_name: str = "Chrome_WidgetWin_1",
        timeout: int = 20,
        interval: float = 0.3,
    ):
        """
        循环查找指定窗口，找到后发送回车
        
        参数:
            window_title_list: 窗口标题列表
            class_name: 窗口类名，默认 "Chrome_WidgetWin_1"
            timeout: 超时时间（秒）
            interval: 检查间隔（秒）
        
        返回:
            bool: 如果找到窗口并发送回车返回 True，否则返回 False
        """
        nonlocal is_completed
        if user32 is None:
            return False
        
        end_time = time.time() + timeout + 5
        hwnd = None

        while time.time() < end_time and not is_completed:
            for window_title in window_title_list:
                hwnd = user32.FindWindowW(class_name, window_title)
                if hwnd:
                    # 置前（可选，但强烈建议）
                    user32.SetForegroundWindow(hwnd)

                    # 发送回车
                    user32.SendMessageW(hwnd, WM_KEYDOWN, VK_RETURN, 0)
                    user32.SendMessageW(hwnd, WM_KEYUP, VK_RETURN, 0)

                    return True
            time.sleep(interval)

        return False

    # 启动后台线程处理保存地址弹窗
    confirm_thread = threading.Thread(
        target=wait_and_send_enter,
        kwargs={
            "window_title_list": ["下载保存地址非当前环境指定保存地址", "保存地址非本环境目录"],
            "timeout": 300,
        },
        daemon=True
    )
    confirm_thread.start()
    
    # 下载报告
    file_all_name = f'{file_folder}\{file_name}'
    file_path = handle_save_dialog(file_folder=str(file_folder), mode=web_page.product_name, file_name=file_name,wait_appear_timeout=120,wait_complete=True,wait_complete_timeout=300)
    # 设置完成标志并等待线程结束
    is_completed = True
    confirm_thread.join()
    
    return file_path


def main(args):
    pass
