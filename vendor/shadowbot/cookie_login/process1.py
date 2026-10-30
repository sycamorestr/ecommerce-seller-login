import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    if args is None:
        网页对象 = None
        保存路径 = ""
        partition_key = ""
    else:
        网页对象 = args.get("网页对象", None)
        保存路径 = args.get("保存路径", "")
        partition_key = args.get("partition_key", "")
    try:
        Cookie信息 = xbot_visual.process.invoke_module(module="_core", package=__name__, function="save_login_info", params={
            "web_page": 网页对象,
            "save_path": 保存路径,
            "partition_key": partition_key,
        }, _block=("A1 保存Cookie", 1, "调用模块"))
    finally:
        pass
