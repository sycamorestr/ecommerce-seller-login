import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        chrome_login_result = xbot_visual.process.run(process="login_tmall_supermarket", package=__name__, inputs={
            "username": "",
            "password": "",
            "shop_name": "安徽徽盛堂商贸有限公司——新商家仓 -- 寄售",
            "mode": "chrome",
            "timeout": lambda: 60,
            "verification_timeout": lambda: 120,
            }, outputs=[
            "web_page",
        ], _block=("天猫测试", 1, "调用流程"))
        edge_login_result = xbot_visual.process.run(process="login_tmall_supermarket", package=__name__, inputs={
            "username": "",
            "password": "",
            "shop_name": "安徽徽盛堂商贸有限公司——新商家仓 -- 寄售",
            "mode": "edge",
            "timeout": lambda: 60,
            "verification_timeout": lambda: 120,
            }, outputs=[
            "web_page",
        ], _block=("天猫测试", 2, "调用流程"))
        cef_login_result = xbot_visual.process.run(process="login_tmall_supermarket", package=__name__, inputs={
            "username": "",
            "password": "",
            "shop_name": "安徽徽盛堂商贸有限公司——新商家仓 -- 寄售",
            "mode": "cef",
            "timeout": lambda: 60,
            "verification_timeout": lambda: 120,
            }, outputs=[
            "web_page",
        ], _block=("天猫测试", 3, "调用流程"))
    finally:
        pass
