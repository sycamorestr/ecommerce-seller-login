import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        invoke_result = xbot_visual.process.invoke_module(module="GetDownloadPath", package=__name__, function="close_prompt_download", params={
        }, _block=("打开下载文件询问", 1, "调用模块"))
        xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("打开下载文件询问", 2, "等待"))
    finally:
        pass
