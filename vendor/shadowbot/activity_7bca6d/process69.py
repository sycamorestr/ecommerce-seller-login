import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        process_result = xbot_visual.process.run(process="process39", package=__name__, inputs={
            "用户名": "测试",
            "密码": "",
            }, outputs=[
            "process_result",
        ], _block=("测试-旺铺登录", 1, "调用流程"))
    finally:
        pass
