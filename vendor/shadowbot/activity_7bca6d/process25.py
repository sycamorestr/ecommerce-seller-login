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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试_电商罗盘", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试_电商罗盘", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # web.element.input
        process_result = xbot_visual.process.run(process="process15", package=__name__, inputs={
            "网页对象": lambda: web_page,
            "username": "",
            "password": "",
            "tj_username": "123",
            "tj_password": "",
            "登录的店铺名称": "BLUE ERDOS官方旗舰店",
            "是否要退出已登录账号": True,
            "wait_time": "",
            }, outputs=[
            "web_page",
        ], _block=("测试_电商罗盘", 3, "调用流程"))
        # xbot_extensions.activity_jfbym.std_slider_captcha
        # programing.variable
        # workflow.forin
        # workflow.endloop
        # process.run
    finally:
        pass
