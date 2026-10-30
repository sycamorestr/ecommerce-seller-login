import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        process_result = xbot_visual.process.run(process="process6", package=__name__, inputs={
            "平台名称": "品销宝",
            "账户": "123123123",
            "密码": "",
            "浏览器类型": "chrome",
            }, outputs=[
            "web_page",
        ], _block=("main", 1, "调用流程"))
    finally:
        pass
