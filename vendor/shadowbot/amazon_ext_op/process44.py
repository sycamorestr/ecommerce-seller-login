import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    运行结果 = ""
    错误信息 = ""
    发票支付订单金额 = ""
    if args is None:
        网页对象 = None
        站点 = ""
        最小提现金额 = ""
        银行卡尾号 = ""
    else:
        网页对象 = args.get("网页对象", None)
        站点 = args.get("站点", "")
        最小提现金额 = args.get("最小提现金额", "")
        银行卡尾号 = args.get("银行卡尾号", "")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_payments_api", package=__name__, function="process_standard_payment", params={
            "web_page": 网页对象,
            "site_name": 站点,
            "minimum_amount": 最小提现金额,
            "account_tail": 银行卡尾号,
        }, _block=("B2.2发票支付订单提现", 1, "调用模块"))
        运行结果 = xbot_visual.programing.variable(value=lambda: invoke_result[0]
        , _block=("B2.2发票支付订单提现", 2, "设置变量"))
        错误信息 = xbot_visual.programing.variable(value=lambda: invoke_result[1]
        , _block=("B2.2发票支付订单提现", 3, "设置变量"))
        发票支付订单金额 = xbot_visual.programing.variable(value=lambda: invoke_result[2]
        , _block=("B2.2发票支付订单提现", 4, "设置变量"))
        # programing.log
    finally:
        args["运行结果"] = 运行结果
        args["错误信息"] = 错误信息
        args["发票支付订单金额"] = 发票支付订单金额
