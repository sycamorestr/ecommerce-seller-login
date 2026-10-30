import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # programing.variable
        # workflow.forin
        # process.run
        # web.get
        # programing.sleep
        # web.browser.navigate
        # web.get
        # web.element.click
        # workflow.endloop
        # web.get
        # workflow.for
        # web.get
        # web.element.click
        # programing.log
        # process.run
        # workflow.endloop
        # web.get
        # xbot_extensions.activity_jfbym.jd_click_select_captcha
        # process.run
        process_result3 = xbot_visual.process.run(process="process6", package=__name__, inputs={
            "username": "",
            "password": "",
            "web_mode": "chrome",
            "tj_username": "",
            "tj_password": "",
            "rec_count": lambda: 5,
            "login_url": "",
            }, outputs=[
            "web_page",
        ], _block=("测试_京东登录", 20, "调用流程"))
    finally:
        pass
