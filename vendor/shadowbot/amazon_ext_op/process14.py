import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    run_status = False
    err_msg = ""
    download_file_path = ""
    if args is None:
        网页对象 = None
        保存文件夹 = ""
        保存文件名 = ""
        下载类型 = ""
        下载年月 = ""
        等待时间 = ""
    else:
        网页对象 = args.get("网页对象", None)
        保存文件夹 = args.get("保存文件夹", "")
        保存文件名 = args.get("保存文件名", "")
        下载类型 = args.get("下载类型", "")
        下载年月 = args.get("下载年月", "")
        等待时间 = args.get("等待时间", "")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_reportcentral_api", package=__name__, function="monthly_storage_fees", params={
            "web_page": 网页对象,
            "save_dir": 保存文件夹,
            "save_name": 保存文件名,
            "report_type": 下载类型,
            "year_month": 下载年月,
            "wait_time": 等待时间,
        }, _block=("C2 月度仓储费", 1, "调用模块"))
        run_status = xbot_visual.programing.variable(value=lambda: invoke_result[0]
        , _block=("C2 月度仓储费", 2, "设置变量"))
        err_msg = xbot_visual.programing.variable(value=lambda: invoke_result[1]
        , _block=("C2 月度仓储费", 3, "设置变量"))
        download_file_path = xbot_visual.programing.variable(value=lambda: invoke_result[2]
        , _block=("C2 月度仓储费", 4, "设置变量"))
    finally:
        args["run_status"] = run_status
        args["err_msg"] = err_msg
        args["download_file_path"] = download_file_path
