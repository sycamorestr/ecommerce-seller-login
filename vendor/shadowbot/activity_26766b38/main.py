import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        dir_path = xbot_visual.dir.get_special_dir(special_dir_name="DesktopDirectory", _block=("main", 1, "获取系统文件夹路径"))
        xbot_visual.process.run(process="xbot_extensions.popup_detector.process1", package=__name__, inputs={
            }, outputs=[
        ], _block=("main", 2, "智能屏蔽弹窗(web)"))
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("main", 3, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("main", 3,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # process.run
        # process.run
        # programing.log
        # process.run
        # process.run
        # process.run
        # process.run
        # programing.log
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # xbot_extensions.activity_7bca6d.滑块拖动
    finally:
        pass
