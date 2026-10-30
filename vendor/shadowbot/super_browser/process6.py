import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    store_name_list = []
    if args is None:
        所属平台 = ""
    else:
        所属平台 = args.get("所属平台", "")
    try:
        store_name_list = xbot_visual.process.invoke_module(module="api", package=__name__, function="get_store_list", params={
            "selected_platform": 所属平台,
        }, _block=("A6 获取店铺列表", 1, "调用模块"))
    finally:
        args["store_name_list"] = store_name_list
