import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    try:
        process_result = xbot_visual.process.run(process="get_scaling", package=__name__, inputs={
            }, outputs=[
            "scaling",
        ], _block=("测试-获取屏幕缩放", 1, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result.scaling, _block=("测试-获取屏幕缩放", 2, "打印日志"))
    finally:
        pass
