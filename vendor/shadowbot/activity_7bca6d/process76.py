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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("T SD测试", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("T SD测试", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.process.run(process="xbot_extensions.activity_jfbym.dy_slider_captcha", package=__name__, inputs={
            "web_page": web_page,
            "engine": "xbot",
            "background_ele": package.selector("电商罗盘_背景元素"),
            "slider_ele": package.selector("罗盘-拖拽元素"),
            "refresh_ele": package.selector("抖店_验证码刷新元素"),
            "offset": lambda: 0,
            "token": "",
            "retry_count": lambda: 5,
            }, outputs=[
        ], _block=("T SD测试", 2, "抖音滑块验证"))
        # process.run
    finally:
        pass
