import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        parameter = ""
    else:
        parameter = args.get("parameter", "")
    try:
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试专用-文武", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试专用-文武", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        整体看板框架 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("首页-整体看板父元素"), css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("测试专用-文武", 2, "获取元素对象(web)"))
        try:
            整体看板右滑动按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("首页_运营视窗_整体看板_右滑动按钮"), css_selector="", xpath_selector="", is_related_parent=True, parent=整体看板框架, timeout="20", _block=("测试专用-文武", 3, "获取元素对象(web)"))
        except Exception as e:
            xbot_visual.programing.log(type='info',text=e,_block=("测试专用-文武", 3,"获取元素对象(web)"))
            整体看板右滑动按钮 = None
        loop_index = -1
        while True:
            loop_index += 1
            # web.element.data_scraping
            # workflow.forin
            # dictionary.set
            # workflow.endloop
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=整体看板右滑动按钮, _block=("测试专用-文武", 9, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=整体看板右滑动按钮, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("测试专用-文武", 10, "点击元素(web)"))
            else:
                break
            #endif
        #endloop
    finally:
        pass
