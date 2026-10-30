import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    run_status = False
    err_msg = ""
    coupons = []
    header_fields = []
    if args is None:
        网页对象 = None
        站点名称 = ""
    else:
        网页对象 = args.get("网页对象", None)
        站点名称 = args.get("站点名称", "")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_ad_api", package=__name__, function="get_coupons", params={
            "web_page": 网页对象,
            "site_name": 站点名称,
            "has_header": False,
        }, _block=("E1 查询优惠券", 1, "调用模块"))
        # programing.variable
        # programing.variable
        header_fields = xbot_visual.programing.variable(value=lambda: invoke_result[0]
        , _block=("E1 查询优惠券", 4, "设置变量"))
        coupons = xbot_visual.programing.variable(value=lambda: invoke_result[1]
        , _block=("E1 查询优惠券", 5, "设置变量"))
    finally:
        args["run_status"] = run_status
        args["err_msg"] = err_msg
        args["coupons"] = coupons
        args["header_fields"] = header_fields
