import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        process_result = xbot_visual.process.run(process="process12", package=__name__, inputs={
            "username": "",
            "password": "",
            "tj_username": "",
            "tj_password": "",
            "web_type": "0",
            }, outputs=[
            "web_page",
        ], _block=("测试巨量纵横登录", 1, "调用流程"))
    finally:
        pass
