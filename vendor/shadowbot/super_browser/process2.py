import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    download_file_name = ""
    if args is None:
        网页对象 = None
        保存文件夹 = ""
        保存文件名 = ""
        超时时间 = "100"
        下载按钮 = None
        等待对话框出现 = "20"
    else:
        网页对象 = args.get("网页对象", None)
        保存文件夹 = args.get("保存文件夹", "")
        保存文件名 = args.get("保存文件名", "")
        超时时间 = args.get("超时时间", "100")
        下载按钮 = args.get("下载按钮", None)
        等待对话框出现 = args.get("等待对话框出现", "20")
    try:
        download_file_name = xbot_visual.process.invoke_module(module="download_api", package=__name__, function="download_handler", params={
            "web_page": 网页对象,
            "selector_or_element": 下载按钮,
            "save_file_dir": 保存文件夹,
            "save_file_name": 保存文件名,
            "wait_time": 超时时间,
            "dialog_timeout": 等待对话框出现,
        }, _block=("A5 紫鸟文件下载", 1, "调用模块"))
    finally:
        args["download_file_name"] = download_file_name
