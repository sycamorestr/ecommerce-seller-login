import xbot
import xbot_visual
from xbot import print, sleep
from .import package
from .package import variables as glv

from xbot._core.retry import Retry
from xbot.selector import Selector
from xbot import strings
from xbot.web import WebBrowser, WebElement
from xbot.win32 import Win32Element
from xbot.win32 import UIAError, UIAErrorCode
from xbot import logging

from typing import Union, Optional, Pattern
import time
import os
from os.path import join
import json
import re

import glob
import threading

import ctypes
from ctypes import wintypes        
user32 = ctypes.windll.user32

# Win32 常量
WM_KEYDOWN = 0x0100
WM_KEYUP   = 0x0101
VK_RETURN  = 0x0D


import xml.etree.ElementTree as ET


print = [lambda *_, **__: None, print][__package__ == "xbot_robot" or hasattr(xbot, "__log")]




def is_file_locked(file_path):
    """
    判断文件是否被其他程序锁定
    """
    try:
        # 尝试以写入模式打开文件
        with open(file_path, 'a') as f:
            pass
        # 文件未被锁定
        time.sleep(3)
        return False
    except IOError:
        # 文件被锁定
        return True


def wait_for_file_unlock(file_path, timeout=100):
    """
    等待文件被解锁
    """
    print("file_path", file_path)
    start_time = time.time()
    while is_file_locked(file_path):
        # 文件仍被锁定
        if time.time() - start_time >= timeout:
            # 超过指定的超时时间，退出等待
            raise TimeoutError(f"等待文件下载超时：{file_path}")

        time.sleep(1)  # 等待一段时间再重新检查

    # 文件已解锁
    print("文件已解锁")


def get_download_path_():
    """
    获取下载保存位置和下载方式
    """

    file_path = join(os.path.expanduser("~"),
                     r"AppData\Local\SuperBrowser\User Data\BrowserWorkbench_1\Default\Preferences")

    if not os.path.exists(file_path):
        # 用户更改了缓存路径，从 BROWSER_DATATEMP_FOLDER.data 文件读取

        tmp_path = glob.glob(join(os.path.expanduser("~"),
                                  r"AppData\Local\SuperBrowserClient\SuperBrowser\*\AsyncStorage"
                                  r"\BROWSER_DATATEMP_FOLDER.data"))[-1]
        print(tmp_path)
        with open(tmp_path, 'r', encoding="u8") as f:
            temp_folder = f.read()

        print(temp_folder)
        file_path = join(temp_folder, r"User Data\BrowserWorkbench_1\Default\Preferences")

    with open(file_path, "r", encoding="u8") as f:
        content = json.load(f)
    content_json = content['download']
    download_path, is_check = content_json["default_directory"], content_json["prompt_for_download"]
    download_path = os.path.dirname(download_path)
    return download_path, is_check


def super_browser_download(web_page, selector_or_element, save_file_dir, save_file_name, wait_time):
    """
    紫鸟下载处理

    :param web_page: 网页对象
    :param selector_or_element: 下载按钮元素
    :param save_file_dir: 保存文件夹
    :param save_file_name: 保存文件名称
    :param wait_time: 等待文件加载时间
    :return: 下载的完整文件路径
    """
    download_path, is_check = get_download_path_()

    if bool(save_file_name) and "." not in save_file_name:
        raise Exception("请填写完整文件名（需要加上文件后缀名）")

    if isinstance(selector_or_element, xbot.selector.Selector):
        download_ele = web_page.find(selector_or_element)
    if isinstance(selector_or_element, str):
        download_ele = web_page.find_by_xpath(selector_or_element)
    else:
        download_ele = selector_or_element

    def get_store_name():
        window = xbot.win32.get_by_selector(package.selector("打开账号_v1"))
        title = window.get_detail("title")
        if title.strip() != "":
            return title

        windows = xbot.win32.get_list()
        for window in windows:
            try:
                if window.get_detail('process_name') != "superbrowser":
                    continue

                title = window.get_detail('title')
                if title == "紫鸟浏览器专业版":
                    continue
                if title.strip() == "":
                    continue

                return title
            except:
                pass
        raise Exception("获取当前店铺名称失败")

    store_name = get_store_name()

    tmp_dir = join(download_path, store_name)  # 临时保存文件夹
    if is_check:
        # 弹出对话框下载
        download_file_name = download_ele.download(tmp_dir, file_name=save_file_name)

        # 等待文件
        file_wait_result = xbot_visual.file.wait(path=download_file_name, desired_state="created", is_wait=True,
                                                 timeout_seconds=wait_time)
        if not file_wait_result:
            raise FileExistsError("长时间等待文件下载失败")

        sleep(2)

    else:
        # 不弹出对话框下载

        file_paths = xbot_visual.dir.find_files(path=tmp_dir, patterns="*.*", find_subdir=False, skip_hidden_file=True,
                                                is_sort=False, sort_by="name", sort_way="increase")

        download_ele.click()

        # 等待文件夹新增文件
        start_time = time.time()
        while True:
            new_file_paths = xbot_visual.dir.find_files(path=tmp_dir, patterns="*.*", find_subdir=False,
                                                        skip_hidden_file=True, is_sort=False, sort_by="name",
                                                        sort_way="increase")
            if len(file_paths) != len(new_file_paths):
                break
            if time.time() - start_time > 10:
                raise Exception("下载文件失败, 点击下载文件后未等到文件出现")

        download_file_name = xbot_visual.list.remove_list(lst1=new_file_paths, lst2=file_paths)[0]

        # 等待文件解锁
        wait_for_file_unlock(download_file_name, timeout=wait_time)

        # 获取新的文件路径
        new_file_paths = xbot_visual.dir.find_files(path=tmp_dir, patterns="*.*", find_subdir=False,
                                                    skip_hidden_file=True, is_sort=False, sort_by="name",
                                                    sort_way="increase")
        download_file_name = xbot_visual.list.remove_list(lst1=new_file_paths, lst2=file_paths)[0]

        # 修改临时文件名
        download_file_name = xbot_visual.file.rename(path=download_file_name, new_name=save_file_name)

    # 复制文件到保存文件夹
    file_list = xbot_visual.file.copy(source_file_paths=download_file_name, copyto_dir_path=save_file_dir,
                                      copy_way="save_as")
    # 删除临时文件
    os.remove(download_file_name)
    return file_list[0]


def download_file(web_page, selector_or_element, save_dir, save_name, wait_time):
    """下载文件"""

    product_name = web_page.product_name
    if isinstance(selector_or_element, xbot.selector.Selector):
        download_ele = web_page.find(selector_or_element)
    if isinstance(selector_or_element, str):
        download_ele = web_page.find_by_xpath(selector_or_element)
    else:
        download_ele = selector_or_element

    if product_name == "superbrowser":
        args = [web_page, download_ele, save_dir, save_name, wait_time]
        download_file_path = super_browser_download(*args)
        return download_file_path

    download_file_path = download_ele.download(save_dir, file_name=save_name)
    assert xbot_visual.file.wait(path=download_file_path, desired_state="created", is_wait=True, timeout_seconds=wait_time), "长时间等待文件下载失败"

    return download_file_path


def find_element_by_bfs(root, condition_func, skip_condition=None) -> Optional[Win32Element]:
    """
    使用广度优先搜索查找符合条件的元素
    
    参数:
        root: 根元素
        condition_func: 条件函数，接收一个元素参数，返回布尔值
        skip_condition: 跳过条件函数，如果返回True则不遍历该元素的子元素
    
    返回:
        找到的元素，如果没找到返回None
    """
    if not root:
        return None
        
    # 使用队列进行BFS
    queue = [root]
    
    while queue:
        current = queue.pop(0)  # 从队列头部取出元素
        
        # 检查当前元素是否符合条件
        if condition_func(current):
            return current
            
        # 如果设置了跳过条件且当前元素满足跳过条件，则跳过其子元素
        if skip_condition and skip_condition(current):
            continue
            
        # 将子元素添加到队列尾部
        children = current.children()
        queue.extend(children)  # 添加到队列尾部
            
    return None


def find_element_by_text(root: Win32Element, text: Union[str, Pattern], no_child: bool=False, timeout=10, times=-1) -> Win32Element:
    """
    查找指定文本的元素
    """
    def condition(element: Win32Element):
        elem_text = element.get_text()
        if elem_text is None:
            return False

        left, top, width, height = element.get_bounding()
        if width == 0 or height == 0:
            return False

        if isinstance(text, Pattern):
            result = text.match(elem_text)
        else:
            result = elem_text == text
        if result and no_child:
            result = len(element.children()) == 0
        return result
    # root.window.activate()
    for _ in Retry(timeout=timeout, times=times, ignore_exception=True):
        try:
            element = find_element_by_bfs(root, condition)
            if element:
                return element            
        except UIAError:
            pass
    
    raise UIAError(strings.Web_Error_Not_Found_Element.format(text), UIAErrorCode.NoSuchElement)


def download_handler(web_page: xbot.web.WebBrowser, element: Union[WebElement, Selector, str], file_folder: str, file_name: str, wait_time: int = 300, dialog_timeout=20) -> str:
    
    is_completed = False
    wait_time = int(wait_time)
    dialog_timeout = int(dialog_timeout)
    
    if isinstance(element, xbot.selector.Selector) or isinstance(element, str):
        element = web_page.find(element, timeout=5)

    assert isinstance(element, xbot.web.WebElement), Exception("传入的元素类型不正确")  

    def wait_and_send_enter(
        window_title_list: list,
        class_name: str = "Chrome_WidgetWin_1",
        timeout: int = 20,
        interval: float = 0.3,
        ):
        """
        循环查找指定窗口，找到后发送回车
        """
        nonlocal is_completed
        end_time = time.time() + timeout + 5
        hwnd = None

        while time.time() < end_time and not is_completed :
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

                
    confirm_thread = threading.Thread(
        target=wait_and_send_enter,
        kwargs={
            "window_title_list": ["下载保存地址非当前环境指定保存地址", "保存地址非本环境目录"],
            "timeout": dialog_timeout,
        },
        daemon=True
    )
    confirm_thread.start()

    # TODO: 不带文件扩展名的时候无法通过等待文件完成进行创建
    file_path = element.download(file_folder, file_name=file_name, wait_complete=True, wait_complete_timeout=wait_time, dialog_timeout=dialog_timeout)
    is_completed = True
    confirm_thread.join()
    return file_path

