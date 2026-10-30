import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    if args is None:
        网页对象 = None
        删除本地存储 = False
    else:
        网页对象 = args.get("网页对象", None)
        删除本地存储 = args.get("删除本地存储", False)
    try:
        _ = xbot_visual.process.invoke_module(module="_core", package=__name__, function="logout", params={
            "web_page": 网页对象,
            "del_local_storage": 删除本地存储,
        }, _block=("A3 Cookie退出登录", 1, "调用模块"))
    finally:
        pass
