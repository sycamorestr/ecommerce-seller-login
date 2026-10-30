
import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

from xbot.win32 import Win32Element, Win32Window
from xbot.web import WebBrowser, WebElement
from xbot._core.retry import Retry
from xbot.errors import UIAError, UIAErrorCode
from xbot import strings
from xbot import logging
from xbot.selector import Selector
from enum import Enum
import re
import json

from typing import Optional, Union, Pattern, List, Tuple
from pathlib import Path

import xml.etree.ElementTree as ET


def find_element_by_bfs(root, condition_func, skip_condition=None, timeout=30) -> Optional[Win32Element]:
    """
    使用广度优先搜索查找符合条件的元素
    
    参数:
        root: 根元素
        condition_func: 条件函数，接收一个元素参数，返回布尔值
        skip_condition: 跳过条件函数，如果返回True则不遍历该元素的子元素
        timeout: 超时时间（秒），超时后返回None
    
    返回:
        找到的元素，如果没找到返回None
    """
    import time
    if not root:
        return None
    
    # 新增timeout参数，默认None
    import inspect
    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    timeout = values.get('timeout', None)
    if timeout is None:
        timeout = 30  # 默认10秒
    start_time = time.time()
    
    queue = [root]
    
    while queue:
        # 超时判断
        if timeout is not None and (time.time() - start_time) > timeout:
            return None
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


def find_element_by_text(root: Win32Element, text: Union[str, Pattern], no_child: bool=False, timeout=10, times=-1, controlType="") -> Win32Element:
    """
    查找指定文本的元素
    """
    def condition(element: Win32Element):
        elem_text = element.get_text()
        # print(f"elem_text: {elem_text}")
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
            if not result:
                return False
        if controlType:
            if element.get_attribute('ControlType') != controlType:
                return False
        return result
    # root.window.activate()
    for _ in Retry(timeout=timeout, times=times, ignore_exception=True):
        try:
            element = find_element_by_bfs(root, condition)
            if element:
                return element            
        except UIAError:
            pass
    window = root.window
    window_detail = f" {window} {window.get_detail('title')}"
    raise UIAError(strings.Web_Error_Not_Found_Element.format(text) + window_detail, UIAErrorCode.NoSuchElement)


def find_element_by_text2(root: Win32Element, text: str, no_child: bool=False, timeout=10, times=-1) -> Win32Element:
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

        result = elem_text == "关闭"
        if result and no_child:
            result = len(element.children()) == 0
        if result:
            result = text in element.parent().get_text()
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


def wait_element_by_text(root: Win32Element, text: Union[str, Pattern], timeout=10) -> Optional[Win32Element]:
    """
    等待指定文本的元素
    """
    def condition(element: Win32Element):
        elem_text = element.get_text()
        # print(f'elem_text=【{elem_text}】')
        if elem_text is None:
            return False
        left, top, width, height = element.get_bounding()
        if width == 0 or height == 0:
            return False
        
        if isinstance(text, Pattern):
            result = text.match(elem_text)
        else:
            result = elem_text == text
        return result
    
    for _ in Retry(timeout=timeout, ignore_exception=True):
        try:
            element = find_element_by_bfs(root, condition)
            if element:
                return element            
        except UIAError:
            pass
    return None


# 找到满足条件的元素
def find_login_input_elem_v6(root: Win32Element, text: str, timeout: int=5):
    elem = find_element_by_text(root, re.compile(f"请输入.*{text}|企业{text}|{text}"), timeout=timeout)
    elem_text = elem.get_text()
    if elem_text == text:
        return elem.parent().parent().child_at(1)
    if "请输入" in elem_text:
        return elem
    return elem.parent().next_sibling()
    

def retry_input(elem: Win32Element, text: str, times: int = 5):
    """输入文本并校验，
    需要注意的是，这里使用的是动态元素，如果元素结果会变化，会导致前后元素不一致，导致校验错误
    这种情况就不要使用此函数了
    """
    input_text = get_inner_text(elem)
    for retrytime, _ in Retry(times=times, ignore_exception=True):
        elem.click(move_mouse=False, delay_after=0)
        elem.input(text, click_before_input=False, delay_after=0, send_key_delay=10)  
        sleep(0.5)  # 等待输入完成后界面更新
        input_text = get_inner_text(elem)

        # 为防止无法获取到文本的情况导致一致重复输入, 没获取到就不对文本输入做校验, 让流程本身去做
        if not input_text or input_text == text:
            return
        else:
            logging.warning(f"第{retrytime}次输入错误, 输入内容：{text}, 输入框内容：{input_text}")
    
    raise Exception(f"输入失败, 输入内容： {text}, 输入框内容：{input_text}")


def get_inner_text(elem: Win32Element):
    """
    使用深度优先搜索获取内部元素文本
    """
    text = elem.get_text()
    if text is None:
        return ""
    for child in elem.children():
        text += get_inner_text(child)
    return text


class Rect:
    
    def __init__(self, elem: Win32Element) -> None:
        left, top, width, height = elem.get_bounding()
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.center_x = left + width // 2
        self.center_y = top + height // 2
        self.bottom = top + height
    
    def __str__(self) -> str:
        return f"Rect_{id(self)} (left: {self.left}, top: {self.top}, width: {self.width}, height: {self.height})"


class Version(Enum):
    V5 = "V5"
    V6 = "V6"


def get_version():
    """
    获取当前打开的紫鸟版本
    """
    def filter_func(w: Win32Window):
        """筛选紫鸟新版和旧版窗口"""
        process_name = w.get_detail('process_name')
        if process_name != "ziniao" and process_name != "ziniaobrowser" and process_name != "superbrowser":
            return False
        
        title = w.get_detail('title')
        if title != "紫鸟浏览器" and title != "紫鸟浏览器专业版":
            return False
        return True
    
    windows = []
    for _ in Retry(times=1, ignore_exception=True):
        try:
            windows = list(filter(filter_func, xbot.win32.get_list()))
        except UIAError:
            continue
        if not windows:
            continue
        break
    
    if not windows:
        raise Exception("未找到紫鸟浏览器，请先打开")
    has_v6 = next(filter(lambda w: w.get_detail('process_name') in ["ziniao", "ziniaobrowser"], windows), None)
    has_v5 = next(filter(lambda w: w.get_detail('process_name') == "superbrowser", windows), None)
    if has_v5 and has_v6:
        raise Exception("同时存在多个版本紫鸟，无法唯一确定，请先关闭一个不需要操作的版本")
    if has_v5:
        return Version.V5
    elif has_v6:
        return Version.V6
    else:
        raise Exception("未找到紫鸟浏览器，请先打开")


def check_ChromiumBrowser_config() -> bool:
    """
    检查 ChromiumBrowser.config， 判断是否安装了紫鸟V6
    """
    config_path = Path.home() / 'AppData' / 'Local' / 'ShadowBot' / 'ChromiumBrowser.config'
    if config_path.exists():
        tree = ET.parse(config_path)
        root = tree.getroot()
        matching_nodes = root.findall(".//ChromiumBrowserInfo")
        for node in matching_nodes:
            # prod_node = node.find('ProductName')
            # alias_node = node.find('AliasName')
            process_node = node.find('ProcessName')
            if not process_node:
                continue
            if process_node and process_node.text == "ziniaobrowser":
                return True
    return False


def get_active_by_web_page(web_page):
    product_name = getattr(web_page, "product_name", "cef" if web_page._controller == "CEFBrowser" else "firefox")
    return product_name


def main(args):
    pass
