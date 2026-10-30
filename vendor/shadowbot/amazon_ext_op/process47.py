import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    提现结果 = ""
    if args is None:
        网页对象 = None
        站点 = ""
        最小提现金额 = ""
        银行卡尾号 = ""
        提现类型 = []
    else:
        网页对象 = args.get("网页对象", None)
        站点 = args.get("站点", "")
        最小提现金额 = args.get("最小提现金额", "")
        银行卡尾号 = args.get("银行卡尾号", "")
        提现类型 = args.get("提现类型", [])
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_payments_api", package=__name__, function="process_custom_payment", params={
            "web_page": 网页对象,
            "site_name": 站点,
            "minimum_amount": 最小提现金额,
            "account_tail": 银行卡尾号,
            "payment_types": 提现类型,
        }, _block=("B2.0自定义类型提现", 1, "调用模块"))
        提现结果 = xbot_visual.programing.variable(value=lambda: invoke_result[2]
        , _block=("B2.0自定义类型提现", 2, "设置变量"))
        # programing.log
    finally:
        args["提现结果"] = 提现结果
