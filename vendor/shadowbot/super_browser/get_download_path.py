import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    download_path = ""
    is_check = False
    try:
        res = xbot_visual.process.invoke_module(module="download_api", package=__name__, function="get_download_path", params={
        }, _block=("A3 获取下载文件保存位置", 1, "调用模块"))
        download_path = xbot_visual.programing.variable(value=res[0]
        , _block=("A3 获取下载文件保存位置", 2, "设置变量"))
        is_check = xbot_visual.programing.variable(value=res[1]
        , _block=("A3 获取下载文件保存位置", 3, "设置变量"))
    finally:
        args["download_path"] = download_path
        args["is_check"] = is_check
