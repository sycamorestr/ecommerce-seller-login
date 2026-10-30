import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        data = xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_alphanum_captcha", package=__name__, inputs={
            "web_page": "",
            "engine": "xbot",
            "captcha_type": "10110",
            "ele": lambda: None,
            "token": "",
            "timeout": lambda: 20,
            "is_trim": False,
            }, outputs=[
            "data",
        ], _block=("子流程1", 1, "通用数英验证码"))
    finally:
        pass
