import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        loop_index = -1
        while True:
            loop_index += 1
            账号 = xbot_visual.programing.variable(value=""
            , _block=("测试抖店循环登录", 2, "设置变量"))
            密码 = xbot_visual.programing.variable(value="Linjj158813"
            , _block=("测试抖店循环登录", 3, "设置变量"))
            process_result = xbot_visual.process.run(process="process4", package=__name__, inputs={
                "username": 账号,
                "password": 密码,
                }, outputs=[
                "web_page",
            ], _block=("测试抖店循环登录", 4, "调用流程"))
        #endloop
    finally:
        pass
