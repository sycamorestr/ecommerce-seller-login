import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    try:
        # 暂时无测试网址
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试-图片旋转验证", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试-图片旋转验证", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
    finally:
        pass
