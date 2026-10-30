import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    run_status = ""
    err_msg = ""
    wd_amount = ""
    standard_current_balance = 0
    invoice_payment_current_balance = 0
    total_amount = 0
    if args is None:
        网页对象 = None
        站点名称 = ""
        最小提现金额 = "0"
        逗号处理 = False
    else:
        网页对象 = args.get("网页对象", None)
        站点名称 = args.get("站点名称", "")
        最小提现金额 = args.get("最小提现金额", "0")
        逗号处理 = args.get("逗号处理", False)
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_payments_api", package=__name__, function="payment_request", params={
            "web_page": 网页对象,
            "site_name": 站点名称,
            "minimum_amount": 最小提现金额,
            "is_comma_decimal": 逗号处理,
        }, _block=("B2 自动提现", 1, "调用模块"))
        run_status = xbot_visual.programing.variable(value=lambda: invoke_result[0]
        , _block=("B2 自动提现", 2, "设置变量"))
        err_msg = xbot_visual.programing.variable(value=lambda: invoke_result[1]
        , _block=("B2 自动提现", 3, "设置变量"))
        wd_amount = xbot_visual.programing.variable(value=lambda: invoke_result[2]
        , _block=("B2 自动提现", 4, "设置变量"))
        standard_current_balance = xbot_visual.programing.variable(value=lambda: invoke_result[3]
        , _block=("B2 自动提现", 5, "设置变量"))
        invoice_payment_current_balance = xbot_visual.programing.variable(value=lambda: invoke_result[4]
        , _block=("B2 自动提现", 6, "设置变量"))
        total_amount = xbot_visual.programing.variable(value=lambda: invoke_result[5]
        , _block=("B2 自动提现", 7, "设置变量"))
        # programing.log
    finally:
        args["run_status"] = run_status
        args["err_msg"] = err_msg
        args["wd_amount"] = wd_amount
        args["standard_current_balance"] = standard_current_balance
        args["invoice_payment_current_balance"] = invoice_payment_current_balance
        args["total_amount"] = total_amount
