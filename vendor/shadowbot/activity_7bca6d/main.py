import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # web.get
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        process_result = xbot_visual.process.run(process="process20", package=__name__, inputs={
            "浏览器类型": "chrome",
            "登录账号": "",
            "登录密码": "",
            "重试次数": lambda: 5,
            }, outputs=[
            "web_page",
        ], _block=("main", 9, "调用流程"))
    finally:
        pass
