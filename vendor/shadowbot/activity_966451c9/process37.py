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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试 SD抖店售后工作台时间选择", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试 SD抖店售后工作台时间选择", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # process.run
        _ = xbot_visual.process.run(process="process4", package=__name__, inputs={
            "网页对象": lambda: web_page,
            "筛选类别": "付款时间",
            "时间类别": "近30日",
            "开始日期": "",
            "结束日期": "",
            }, outputs=[
        ], _block=("测试 SD抖店售后工作台时间选择", 3, "调用流程"))
        # process.run
        # process.run
        # process.run
        # process.run
        # web.element.get_element
        # web.element.get_element
        # process.run
    finally:
        pass
