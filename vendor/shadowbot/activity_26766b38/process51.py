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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("关闭重要消息提示", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("关闭重要消息提示", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("生意参谋_右下角_重要消息提示框"), _block=("关闭重要消息提示", 2, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("生意参谋_右下角_重要消息提示框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("关闭重要消息提示", 3, "点击元素(web)"))
        #endif
    finally:
        pass
