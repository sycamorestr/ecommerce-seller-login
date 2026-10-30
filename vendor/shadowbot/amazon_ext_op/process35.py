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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("TEST E4 发送POST", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("TEST E4 发送POST", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        _ = xbot_visual.process.run(process="process34", package=__name__, inputs={
            "网页对象": web_page,
            "品牌帖子网址": "https://advertising.amazon.com/brand-content-manager/profiles/d09ce62e-5bb0-4524-b9cf-6eb9c0afed78",
            "文件路径": "C:\\Users\\Administrator\\Desktop\\G1.jpg",
            "标题": "One",
            "asin列表": lambda: ["B08FHS3537", "B0BGMJDBFT"],
            "开始时间": "2024-02-29 07:00",
            "结束时间": "",
            }, outputs=[
        ], _block=("TEST E4 发送POST", 2, "调用流程"))
    finally:
        pass
