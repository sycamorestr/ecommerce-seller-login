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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试-验证码", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试-验证码", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.process19", package=__name__, inputs={
            "网页对象": web_page,
            "识别引擎": "YD",
            "缺口or单缺口": "缺口识别",
            "图块所在背景": package.selector("图形"),
            "目标图块": package.selector("图片"),
            "拖拽元素": package.selector("滑块"),
            "图鉴帐号": "",
            "图鉴密码": "",
            "重试次数": lambda: 0,
            "偏移距离": lambda: 0,
            "移动速度": "instant",
            }, outputs=[
        ], _block=("测试-验证码", 2, "滑动拼图验证"))
    finally:
        pass
