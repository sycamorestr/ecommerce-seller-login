import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        process_result = xbot_visual.process.run(process="process20", package=__name__, inputs={
            "浏览器类型": "chrome",
            "登录账号": "",
            "登录密码": "",
            "重试次数": lambda: 5,
            }, outputs=[
            "web_page",
        ], _block=("测试_支付宝登录", 1, "调用流程"))
        # web.get
        # xbot_extensions.activity_bintuo.zfb_click
        # xbot_extensions.activity_jfbym.std_slider_captcha
        # xbot_extensions.activity_jfbym.std_slider_captcha
        # web.get
        # programing.variable
        # xbot_extensions.activity_jfbym.std_click_select_captcha_plus
        # xbot_extensions.activity_jfbym.std_click_select_captcha
    finally:
        pass
