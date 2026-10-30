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
                web_page = xbot_visual.web.get(web_type="edge", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试登录", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试登录", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # workflow.for
        # programing.sleep
        # programing.sleep
        process_result = xbot_visual.process.run(process="process45", package=__name__, inputs={
            "账号": "",
            "密码": "",
            "web_page": lambda: None,
            }, outputs=[
            "网页对象",
        ], _block=("测试登录", 5, "调用流程"))
        # workflow.endloop
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试登录", 7, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试登录", 7,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("登录页面_滑块验证_div"), _block=("测试登录", 8, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("登录页面_滑块验证_div"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("测试登录", 9, "点击元素(web)"))
            back_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("登录页面_滑块验证_div"), operation="bound", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("测试登录", 10, "获取元素信息(web)"))
            front_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("登录页面_滑块_滑动div"), operation="bound", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("测试登录", 11, "获取元素信息(web)"))
            invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="drag", params={
                "point_x": lambda: back_element_attribute.left + front_element_attribute.width/2,
                "point_y": lambda: back_element_attribute.center_y,
                "distance": lambda: back_element_attribute.width - front_element_attribute.width,
                "move_speed": "middle",
            }, _block=("测试登录", 12, "调用模块"))
        #endif
    finally:
        pass
