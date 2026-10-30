import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # xbot_extensions.popup_detector.A1 智能屏蔽弹窗(web)
        # programing.log
        # programing.snippet
        # web.get
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("main", 5, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("main", 5,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        process_result = xbot_visual.process.run(process="labor_bill", package=__name__, inputs={
            "web_page": lambda: web_page,
            "start_time": "2026-09-01",
            "end_time": "2026-09-30",
            "financial_type": None,
            "fund_mix": "",
            "fund_max": "",
            "capital_flow": None,
            "file_folder": "C:\\Users\\Administrator\\Desktop\\test",
            "report_type": "",
            "file_name": "",
            "time_out": lambda: 0,
            }, outputs=[
            "save_path_list",
        ], _block=("main", 6, "调用流程"))
    finally:
        pass
