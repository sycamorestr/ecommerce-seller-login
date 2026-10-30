import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    run_status = False
    err_msg = ""
    screenshot_file_name = ""
    currency_total_amount = ""
    if args is None:
        网页对象 = None
        站点名称 = ""
        保存文件夹 = ""
        保存文件名 = ""
        结算周期 = ""
        账户类型 = ""
        截图区域 = ""
    else:
        网页对象 = args.get("网页对象", None)
        站点名称 = args.get("站点名称", "")
        保存文件夹 = args.get("保存文件夹", "")
        保存文件名 = args.get("保存文件名", "")
        结算周期 = args.get("结算周期", "")
        账户类型 = args.get("账户类型", "")
        截图区域 = args.get("截图区域", "")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_payments_api", package=__name__, function="proceeds_screenshot", params={
            "web_page": 网页对象,
            "site_name": 站点名称,
            "save_dir": 保存文件夹,
            "save_name": 保存文件名,
            "cycle": 结算周期,
            "account_type": 账户类型,
            "screenshot_range": 截图区域,
        }, _block=("B3 结算一览截图", 1, "调用模块"))
        run_status = xbot_visual.programing.variable(value=lambda: invoke_result[0]
        , _block=("B3 结算一览截图", 2, "设置变量"))
        err_msg = xbot_visual.programing.variable(value=lambda: invoke_result[1]
        , _block=("B3 结算一览截图", 3, "设置变量"))
        screenshot_file_name = xbot_visual.programing.variable(value=lambda: invoke_result[2]
        , _block=("B3 结算一览截图", 4, "设置变量"))
        currency_total_amount = xbot_visual.programing.variable(value=lambda: invoke_result[3]
        , _block=("B3 结算一览截图", 5, "设置变量"))
    finally:
        args["run_status"] = run_status
        args["err_msg"] = err_msg
        args["screenshot_file_name"] = screenshot_file_name
        args["currency_total_amount"] = currency_total_amount
