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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("抖店体验分", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("抖店体验分", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        cookie = xbot_visual.web.browser.execute_javascript(browser=web_page, element=None, argument=None, code="function (element, input) {\r\nreturn document.cookie\r\n}", timeout="20", execution_world="ISOLATED", _block=("抖店体验分", 2, "执行JS脚本"))
    finally:
        pass
