import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    try:
        for _xbot_retry_time in range(4):
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=True, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试-京东风控滑动验证", 1, "获取已打开的网页对象"))
                break
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试-京东风控滑动验证", 1,"获取已打开的网页对象"))
            time.sleep(3)
        _ = xbot_visual.process.run(process="process35", package=__name__, inputs={
            "图块所在背景": package.selector("京东风控背景"),
            "目标图块": package.selector("目标图块"),
            "拖拽元素": package.selector("拖拽"),
            "网页对象": lambda: web_page,
            "缺口or单缺口": "缺口识别",
            "图鉴帐号": "",
            "图鉴密码": "",
            "重试次数": lambda: 5,
            "偏移距离": lambda: 0,
            "识别引擎": "YD",
            "移动速度": "slow",
            }, outputs=[
        ], _block=("测试-京东风控滑动验证", 2, "调用流程"))
    finally:
        pass
