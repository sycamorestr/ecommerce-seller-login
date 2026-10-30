import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        店铺名称 = ""
        网页对象 = None
        全局超时时间 = "20"
    else:
        店铺名称 = args.get("店铺名称", "")
        网页对象 = args.get("网页对象", None)
        全局超时时间 = args.get("全局超时时间", "20")
    try:
        _ = xbot_visual.process.run(process="process17", package=__name__, inputs={
            "网页对象": 网页对象,
            "目标店铺名称": 店铺名称,
            "全局超时时间": 全局超时时间,
            }, outputs=[
        ], _block=("抖店店铺切换", 1, "调用流程"))
    finally:
        pass
