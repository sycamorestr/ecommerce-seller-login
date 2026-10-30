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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # process.run
        _ = xbot_visual.process.run(process="slider_captcha", package=__name__, inputs={
            "web_page": lambda: web_page,
            "background_ele": package.selector("删除 - 抖音背景"),
            "slider_ele": package.selector("删除 - 抖音滑块"),
            "drag_ele": package.selector("删除 - 抖音拖拽"),
            "retry_count": lambda: 5,
            "offset": lambda: 0,
            "move_speed": "fast",
            }, outputs=[
        ], _block=("测试", 3, "调用流程"))
        # process.run
        # process.run
        # process.run
        # system.take_screenshot
        # process.run
        # win32.window.get_window
        # process.run
        # web.element.screenshot
        # file.write
    finally:
        pass
