import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        上传按钮 = None
        上传文件路径 = ""
        等待对话框超时时间 = "20"
    else:
        网页对象 = args.get("网页对象", None)
        上传按钮 = args.get("上传按钮", None)
        上传文件路径 = args.get("上传文件路径", "")
        等待对话框超时时间 = args.get("等待对话框超时时间", "20")
    try:
        store_name_list = xbot_visual.process.invoke_module(module="download_api", package=__name__, function="upload_handler", params={
            "web_page": 网页对象,
            "selector_or_element": 上传按钮,
            "file_names": 上传文件路径,
            "simulative": False,
            "dialog_timeout": 等待对话框超时时间,
        }, _block=("A7 上传文件到紫鸟", 1, "调用模块"))
    finally:
        pass
