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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试调用模块", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试调用模块", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("2022年"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("测试调用模块", 2, "获取元素对象(web)"))
        pre_ele = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("pre_year"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("测试调用模块", 3, "获取元素对象(web)"))
        next_ele = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("next_year"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("测试调用模块", 4, "获取元素对象(web)"))
        invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="date_year_select", params={
            "year_ele": web_element,
            "select_text": "2023",
            "year_pre_ele": pre_ele,
            "year_next_ele": next_ele,
        }, _block=("测试调用模块", 5, "调用模块"))
    finally:
        pass
