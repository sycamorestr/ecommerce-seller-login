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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("子流程4", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("子流程4", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # xbot_extensions.cookie_login.A1 保存Cookie
        loop_index = -1
        while True:
            loop_index += 1
            _ = xbot_visual.process.run(process="process11", package=__name__, inputs={
                "web_page": lambda: web_page,
                "drag_start_element": package.selector("_1"),
                "background_element": package.selector("向右滑动验证_2"),
                }, outputs=[
            ], _block=("子流程4", 4, "调用流程"))
            try:
                web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("块元素_`nc_1_refresh1`"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("子流程4", 5, "获取元素对象(web)"))
            except Exception as e:
                pass
                web_element = None
            if xbot_visual.workflow.test(operand1=web_element, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("子流程4", 6, "IF 条件")):
                break
            #endif
            xbot_visual.web.element.click(browser=web_page, element=web_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("子流程4", 9, "点击元素(web)"))
        #endloop
    finally:
        pass
