# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, win32
from .import package
from .package import variables as glv
from xbot.selector import Selector
import uuid

def drag(point_x, point_y, distance, move_speed):
    """拖动滑块
    :param poit_x: 鼠标开始拖动的 x 坐标
    :param point_y: 鼠标开始拖动的 y 坐标
    :param distance: 鼠标拖动的距离
    :param move_speed: 移动速度, instant, fast, middle, slow
    """
    win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=1,max_time=5)
    win32.mouse_move(point_x=point_x, point_y=point_y, move_speed=move_speed)
    poit_x, point_y = win32.get_mouse_position(relative_to="screen")
    win32.mouse_click(button="left", click_type="down")
    win32.mouse_move(point_x+ distance, point_y, move_speed=move_speed,)
    win32.mouse_click(button="left", click_type="up")
    win32.manual_motion_off()

def get_active_by_web_page(web_page):
    product_name = getattr(web_page, "product_name", "cef" if web_page._controller == "CEFBrowser" else "firefox")
    return product_name

def get_select(xpath, name):
    if isinstance(xpath, str):
        xpath = xpath.split(">>")
    data = {
        "id": str(uuid.uuid4()),
        "name": name,
        "framework": "chrome",
        "type": "simple",
        "version": 2,
        "xpath": {"enable": "true", "segments": xpath},
    }
    selector = Selector(data)
    return selector

def drag_mover(web_page: xbot.web.WebBrowser, drag_ele: xbot.web.WebElement, long_ele: xbot.web.WebElement):
    '''
    拖动元素
    :param web_page: 网页对象
    :param drag_ele: 要拖动的元素
    :param long_ele: 长元素
    '''
    


def main(args):
    a = [['', 1, 2], [21212, 1, 2], ['', 2,3]]
    for jishu_, i in enumerate(a):
        i[0] = jishu_ + 1
    print(a)
    pass
