import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        process_result = xbot_visual.process.run(process="process43", package=__name__, inputs={
            "账号": "",
            "密码": "",
            "短信验证码接口": "123",
            "是否退出已登录账户": True,
            }, outputs=[
            "web_page",
        ], _block=("测试拼多多登录", 1, "调用流程"))
    finally:
        pass
