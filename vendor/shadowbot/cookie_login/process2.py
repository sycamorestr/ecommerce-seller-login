import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    if args is None:
        网页对象 = None
        Cookie文件路径 = ""
        添加本地存储 = False
    else:
        网页对象 = args.get("网页对象", None)
        Cookie文件路径 = args.get("Cookie文件路径", "")
        添加本地存储 = args.get("添加本地存储", False)
    try:
        _ = xbot_visual.process.invoke_module(module="_core", package=__name__, function="login", params={
            "web_page": 网页对象,
            "cookie_file_path": Cookie文件路径,
            "add_local_storage": 添加本地存储,
        }, _block=("A2 Cookie登录", 1, "调用模块"))
    finally:
        pass
