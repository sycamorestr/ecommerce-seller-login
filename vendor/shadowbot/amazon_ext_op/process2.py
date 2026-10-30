import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        站点名称 = ""
    else:
        网页对象 = args.get("网页对象", None)
        站点名称 = args.get("站点名称", "")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_amazon_api", package=__name__, function="switch_site", params={
            "web_page": 网页对象,
            "site_name": 站点名称,
        }, _block=("A2 亚马逊切换站点", 1, "调用模块"))
    finally:
        pass
