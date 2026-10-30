import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        _ = xbot_visual.process.run(process="process1", package=__name__, inputs={
            "邮箱账号": "songpengfei1210@outlook.com",
            "邮箱密码": "1qaz@WSX3edc",
            "图鉴账号": lambda: None,
            "图鉴密码": lambda: None,
            "是否退出已登录": False,
            }, outputs=[
        ], _block=("main", 1, "调用流程"))
    finally:
        pass
