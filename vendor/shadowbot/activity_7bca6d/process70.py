import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        _ = xbot_visual.process.run(process="process62", package=__name__, inputs={
            "账号": lambda: 123123123123,
            "密码": "",
            "重试次数": "3",
            "浏览器类型": "chrome",
            }, outputs=[
        ], _block=("千牛登录测试", 1, "调用流程"))
    finally:
        pass
