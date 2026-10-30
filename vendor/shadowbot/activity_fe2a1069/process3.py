import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # process.run
        # programing.log
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试", 3, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试", 3,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        _ = xbot_visual.process.run(process="DataSelection", package=__name__, inputs={
            "日期": "2023-08-31",
            "上一月_xpath": "//*[contains(@class, \"prev-month\")][not(contains(@class, \"hidden\"))]",
            "下一月_xpath": "//*[contains(@class, \"next-month\")][not(contains(@class, \"hidden\"))]",
            "当前年_xpath": "(//*[@class=\"bui-date-panel\"])[1]//span[contains(@class, \"date-header-text\")][1]",
            "目标日期_xpath": "//*[@title=\"2023-08-31\"]",
            "年正则": "(\\d+)年",
            "月正则": "(\\d+)月",
            "当前月_xpath": "(//*[@class=\"bui-date-panel\"])[1]//span[contains(@class, \"date-header-text\")][2]",
            "web_page": web_page,
            "仅切换选择面板": False,
            "模拟人工点击": True,
            }, outputs=[
        ], _block=("测试", 4, "调用流程"))
    finally:
        pass
