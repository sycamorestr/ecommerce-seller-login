import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    web_page = None
    完整店铺名称 = ""
    if args is None:
        店铺名称 = ""
        匹配类型 = "相等"
        打开账号 = "点击"
        超时时间 = 50
        隐私模式 = False
    else:
        店铺名称 = args.get("店铺名称", "")
        匹配类型 = args.get("匹配类型", "相等")
        打开账号 = args.get("打开账号", "点击")
        超时时间 = args.get("超时时间", 50)
        隐私模式 = args.get("隐私模式", False)
    try:
        # process.invoke_module
        invoke_result = xbot_visual.process.invoke_module(module="api_uia", package=__name__, function="open_store", params={
            "store_name": 店铺名称,
            "match_type": 匹配类型,
            "privacy": lambda: 隐私模式,
            "is_open": lambda: 打开账号,
            "timeout": lambda: 超时时间,
        }, _block=("A2 打开店铺 - uia", 2, "调用模块"))
        完整店铺名称 = xbot_visual.programing.variable(value=invoke_result[0]
        , _block=("A2 打开店铺 - uia", 3, "设置变量"))
        web_page = xbot_visual.programing.variable(value=invoke_result[1]
        , _block=("A2 打开店铺 - uia", 4, "设置变量"))
    finally:
        args["web_page"] = web_page
        args["完整店铺名称"] = 完整店铺名称
