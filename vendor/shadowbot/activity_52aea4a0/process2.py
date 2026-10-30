import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        _ = xbot_visual.process.run(process="process1", package=__name__, inputs={
            "邮箱账号": "12345",
            "邮箱密码": "12345",
            "图鉴账号": lambda: None,
            "图鉴密码": lambda: None,
            "是否退出已登录": True,
            }, outputs=[
        ], _block=("测试_jc", 1, "调用流程"))
    finally:
        pass
