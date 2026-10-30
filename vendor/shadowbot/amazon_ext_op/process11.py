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
                web_page = xbot_visual.web.get(web_type="superbrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("TEST D1买家之声", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("TEST D1买家之声", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # web.browser.start_monitor_network
        # web.browser.get_responses
        # web.browser.stop_monitor_network
        process_result = xbot_visual.process.run(process="process10", package=__name__, inputs={
            "网页对象": web_page,
            "站点名称": glv['测试_站点'],
            "ASIN列表": "",
            "上次更新天数": "2",
            }, outputs=[
            "run_status",
            "err_msg",
            "asin_data",
            "not_exist_asin_list",
        ], _block=("TEST D1买家之声", 5, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result.run_status, _block=("TEST D1买家之声", 6, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.err_msg, _block=("TEST D1买家之声", 7, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.asin_data, _block=("TEST D1买家之声", 8, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.not_exist_asin_list, _block=("TEST D1买家之声", 9, "打印日志"))
    finally:
        pass
