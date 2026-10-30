import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # 品类-商品排行-全部商品 测试
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试专用-肯尼", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试专用-肯尼", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        process_result = xbot_visual.process.run(process="process3", package=__name__, inputs={
            "保存文件夹": "C:\\Users\\78130\\Desktop",
            "查询日期": "2023-12-24",
            "开启页面统计时间校验": True,
            "网页对象": web_page,
            }, outputs=[
            "输出文件路径",
            "执行状态",
            "数据集对象列表",
        ], _block=("测试专用-肯尼", 3, "调用流程"))
    finally:
        pass
