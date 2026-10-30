import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        _ = xbot_visual.process.invoke_module(module="api", package=__name__, function="to_account_page", params={
        }, _block=("A1 进入账号管理页面", 1, "调用模块"))
    finally:
        pass
