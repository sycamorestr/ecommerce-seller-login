import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        切换语言 = ""
    else:
        网页对象 = args.get("网页对象", None)
        切换语言 = args.get("切换语言", "")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_amazon_api", package=__name__, function="switch_language", params={
            "web_page": 网页对象,
            "language": 切换语言,
        }, _block=("A3 亚马逊-切换语言", 1, "调用模块"))
    finally:
        pass
