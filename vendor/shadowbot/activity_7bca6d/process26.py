import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        账号 = xbot_visual.programing.variable(value=""
        , _block=("测试抖店登录", 1, "设置变量"))
        密码 = xbot_visual.programing.variable(value="Linjj158813"
        , _block=("测试抖店登录", 2, "设置变量"))
        process_result = xbot_visual.process.run(process="process4", package=__name__, inputs={
            "username": 账号,
            "password": 密码,
            "验证邮箱": "",
            "邮箱授权码": "",
            "获取授权码间隔时长": lambda: 20,
            "验证码失败最大重试次数": lambda: 10,
            "退出已登录账户": True,
            "retry_cnt": lambda: 3,
            "网页对象": "",
            }, outputs=[
            "web_page",
        ], _block=("测试抖店登录", 3, "调用流程"))
    finally:
        pass
