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
        站点名称 = ""
        报告类型 = "汇总"
        报告标签 = ""
        日期范围 = ""
        保存文件夹 = ""
        保存文件名 = ""
        超时时间 = "300"
        账户类型 = "标准订单"
    else:
        网页对象 = args.get("网页对象", None)
        站点名称 = args.get("站点名称", "")
        报告类型 = args.get("报告类型", "汇总")
        报告标签 = args.get("报告标签", "")
        日期范围 = args.get("日期范围", "")
        保存文件夹 = args.get("保存文件夹", "")
        保存文件名 = args.get("保存文件名", "")
        超时时间 = args.get("超时时间", "300")
        账户类型 = args.get("账户类型", "标准订单")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_payments_api", package=__name__, function="reports_download", params={
            "web_page": 网页对象,
            "site_name": 站点名称,
            "account_type": 账户类型,
            "report_type": 报告类型,
            "report_tag": 报告标签,
            "date_range": 日期范围,
            "save_dir": 保存文件夹,
            "save_name": 保存文件名,
            "wait_time": 超时时间,
        }, _block=("B1 付款报告下载", 1, "调用模块"))
        run_status = xbot_visual.programing.variable(value=lambda: invoke_result[0]
        , _block=("B1 付款报告下载", 2, "设置变量"))
        err_msg = xbot_visual.programing.variable(value=lambda: invoke_result[1]
        , _block=("B1 付款报告下载", 3, "设置变量"))
        download_file_path = xbot_visual.programing.variable(value=lambda: invoke_result[2]
        , _block=("B1 付款报告下载", 4, "设置变量"))
    finally:
        args["run_status"] = run_status
        args["err_msg"] = err_msg
        args["download_file_path"] = download_file_path
