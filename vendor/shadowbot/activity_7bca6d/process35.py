import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # process.run
        # process.run
        process_result3 = xbot_visual.process.run(process="process1", package=__name__, inputs={
            "username": "",
            "password": "",
            "tj_username": "",
            "tj_password": "",
            "web_type": "0",
            "status": False,
            }, outputs=[
            "web_page",
        ], _block=("测试巨量登录", 3, "调用流程"))
        # win32.send_keys
        # win32.send_keys
    finally:
        pass
