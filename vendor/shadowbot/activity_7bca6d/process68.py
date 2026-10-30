import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        process_result = xbot_visual.process.run(process="process40", package=__name__, inputs={
            "登录用户名": "",
            "登录密码": "",
            "子平台": "",
            "退出已登录账户": True,
            "短信验证码获取接口": "",
            "识别引擎": "",
            }, outputs=[
            "输出网页对象",
        ], _block=("子流程3", 1, "调用流程"))
    finally:
        pass
