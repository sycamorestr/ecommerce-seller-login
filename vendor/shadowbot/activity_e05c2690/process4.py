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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试_jc", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试_jc", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        _ = xbot_visual.process.run(process="orangebank_load", package=__name__, inputs={
            "web_page": lambda: web_page,
            "ai_engine": "",
            "username": "",
            "password": "",
            "ym_token": "",
            "drag_distance": lambda: 0,
            }, outputs=[
        ], _block=("测试_jc", 2, "调用流程"))
        # process.run
        # process.run
        # process.run
    finally:
        pass
