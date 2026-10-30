import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        店铺ID = ""
        全局超时时间 = "20"
    else:
        网页对象 = args.get("网页对象", None)
        店铺ID = args.get("店铺ID", "")
        全局超时时间 = args.get("全局超时时间", "20")
    try:
        _ = xbot_visual.process.run(process="process36", package=__name__, inputs={
            "网页对象": lambda: 网页对象,
            "店铺ID": 店铺ID,
            "全局超时时间": 全局超时时间,
            }, outputs=[
        ], _block=("抖店店铺切换(ID)", 1, "调用流程"))
    finally:
        pass
