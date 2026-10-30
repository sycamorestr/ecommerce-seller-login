import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    run_status = False
    err_msg = ""
    amount_data = {}
    if args is None:
        网页对象 = None
        站点名称 = ""
        结算周期 = "0"
        切换语言为中文 = "是"
        账户类型 = ""
    else:
        网页对象 = args.get("网页对象", None)
        站点名称 = args.get("站点名称", "")
        结算周期 = args.get("结算周期", "0")
        切换语言为中文 = args.get("切换语言为中文", "是")
        账户类型 = args.get("账户类型", "")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_payments_api", package=__name__, function="get_account_data", params={
            "web_page": 网页对象,
            "site_name": 站点名称,
            "account_type": 账户类型,
            "cycle": 结算周期,
            "switch_zh": 切换语言为中文,
        }, _block=("B4 结算一览账户数据", 1, "调用模块"))
        run_status = xbot_visual.programing.variable(value=lambda: invoke_result[0]
        , _block=("B4 结算一览账户数据", 2, "设置变量"))
        err_msg = xbot_visual.programing.variable(value=lambda: invoke_result[1]
        , _block=("B4 结算一览账户数据", 3, "设置变量"))
        amount_data = xbot_visual.programing.variable(value=lambda: invoke_result[2]
        , _block=("B4 结算一览账户数据", 4, "设置变量"))
    finally:
        args["run_status"] = run_status
        args["err_msg"] = err_msg
        args["amount_data"] = amount_data
