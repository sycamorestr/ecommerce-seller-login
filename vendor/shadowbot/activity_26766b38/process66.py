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
        # process.run
        process_result2 = xbot_visual.process.run(process="process14", package=__name__, inputs={
            "查询日期": "2026-07-24_2026-07-27",
            "保存文件夹": "C:\\Users\\Administrator\\Desktop\\test",
            "售后分析类型": "售后解决分析",
            "开启页面统计时间校验": False,
            }, outputs=[
            "输出文件路径",
            "执行状态",
        ], _block=("T SD测试", 3, "调用流程"))
    finally:
        pass
