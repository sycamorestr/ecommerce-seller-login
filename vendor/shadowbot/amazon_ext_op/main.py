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
                web_page = xbot_visual.web.get(web_type="ziniaobrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("main", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("main", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        process_result6 = xbot_visual.process.run(process="process47", package=__name__, inputs={
            "网页对象": web_page,
            "站点": "美国",
            "最小提现金额": "0",
            "银行卡尾号": "1234",
            "提现类型": "发票支付订单",
            }, outputs=[
            "提现结果",
        ], _block=("main", 2, "调用流程"))
        # process.run
        # process.run
        # programing.log
        # process.invoke_module
        # win32.element.click
        # process.run
        # process.run
        # process.run
        # programing.snippet
    finally:
        pass
