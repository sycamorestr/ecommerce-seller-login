import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    download_file_path = ""
    if args is None:
        网页对象 = None
        站点名称 = ""
        保存文件夹 = ""
        保存文件名 = ""
        下载类型 = ""
        日期范围 = ""
        等待时间 = ""
    else:
        网页对象 = args.get("网页对象", None)
        站点名称 = args.get("站点名称", "")
        保存文件夹 = args.get("保存文件夹", "")
        保存文件名 = args.get("保存文件名", "")
        下载类型 = args.get("下载类型", "")
        日期范围 = args.get("日期范围", "")
        等待时间 = args.get("等待时间", "")
    try:
        download_file_path = xbot_visual.process.invoke_module(module="_reportcentral_api", package=__name__, function="vat_transaction", params={
            "web_page": 网页对象,
            "site_name": 站点名称,
            "save_dir": 保存文件夹,
            "save_name": 保存文件名,
            "report_type": 下载类型,
            "date_range": 日期范围,
            "wait_time": 等待时间,
        }, _block=("C3 增值税交易报告", 1, "调用模块"))
    finally:
        args["download_file_path"] = download_file_path
