import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        保存文件夹 = xbot_visual.programing.variable(value="C:\\Users\\45124\\Desktop"
        , _block=("测试-", 1, "设置变量"))
        查询日期 = xbot_visual.programing.variable(value="2025-01-01"
        , _block=("测试-", 2, "设置变量"))
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="edge", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试-", 3, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试-", 3,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        process_result3 = xbot_visual.process.run(process="process6", package=__name__, inputs={
            "查询日期": 查询日期,
            "类目选择": "导购类目",
            "保存文件夹": 保存文件夹,
            "开启页面统计时间校验": True,
            "网页对象": None,
            }, outputs=[
            "输出文件路径",
            "执行状态",
        ], _block=("测试-", 4, "调用流程"))
        # process.run
        # process.run
        # process.run
        # programing.log
    finally:
        pass
