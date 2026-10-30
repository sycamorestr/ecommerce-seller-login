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
                web_page = xbot_visual.web.get(web_type="ziniaobrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("TEST B2 自动提现", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("TEST B2 自动提现", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # process.run
        # programing.log
        # process.invoke_module
        # programing.log
        process_result = xbot_visual.process.run(process="process4", package=__name__, inputs={
            "网页对象": web_page,
            "站点名称": glv['测试_站点'],
            "最小提现金额": "0",
            }, outputs=[
            "run_status",
            "err_msg",
            "wd_amount",
            "standard_current_balance",
            "invoice_payment_current_balance",
            "total_amount",
        ], _block=("TEST B2 自动提现", 6, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result, _block=("TEST B2 自动提现", 7, "打印日志"))
    finally:
        pass
