import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
    else:
        网页对象 = args.get("网页对象", None)
    try:
        invoke_result2 = xbot_visual.process.invoke_module(module="_amazon_api", package=__name__, function="login", params={
            "web_page": 网页对象,
        }, _block=("A1 亚马逊店铺登录", 1, "调用模块"))
    finally:
        pass
