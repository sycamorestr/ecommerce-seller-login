import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="cef", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试悬停", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试悬停", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # web.element.hover
        # web.element.hover
        web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("抖店_目标滑块_ifream"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("测试悬停", 4, "获取元素对象(web)"))
        web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=web_element, operation="bound", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("测试悬停", 5, "获取元素信息(web)"))
        xbot_visual.win32.move_mouse(point_x=web_element_attribute.center_x, point_y=web_element_attribute.center_y, relative_to="screen", move_speed="middle", delay_after="1", _block=("测试悬停", 6, "移动鼠标"))
        xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("测试悬停", 7, "等待"))
    finally:
        pass
