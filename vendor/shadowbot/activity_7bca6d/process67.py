import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        invoke_result = xbot_visual.process.invoke_module(module="qn_login", package=__name__, function="login", params={
            "mode": "chrome",
            "username": "",
            "password": "",
            "token": "",
            "retry_count": "2",
        }, _block=("子流程2", 1, "调用模块"))
    finally:
        pass
