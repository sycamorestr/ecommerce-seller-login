import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    run_status = False
    err_msg = ""
    asin_data = []
    not_exist_asin_list = []
    if args is None:
        网页对象 = None
        站点名称 = ""
        ASIN列表 = []
        上次更新天数 = ""
    else:
        网页对象 = args.get("网页对象", None)
        站点名称 = args.get("站点名称", "")
        ASIN列表 = args.get("ASIN列表", [])
        上次更新天数 = args.get("上次更新天数", "")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_performance_api", package=__name__, function="get_voice_customer_data", params={
            "web_page": 网页对象,
            "site_name": 站点名称,
            "asin_list": ASIN列表,
            "ret_type": "1",
            "time_days": 上次更新天数,
        }, _block=("D1 买家之声", 1, "调用模块"))
        run_status = xbot_visual.programing.variable(value=lambda: invoke_result[0]
        , _block=("D1 买家之声", 2, "设置变量"))
        err_msg = xbot_visual.programing.variable(value=lambda: invoke_result[1]
        , _block=("D1 买家之声", 3, "设置变量"))
        asin_data = xbot_visual.programing.variable(value=lambda: invoke_result[2]
        , _block=("D1 买家之声", 4, "设置变量"))
        not_exist_asin_list = xbot_visual.programing.variable(value=lambda: invoke_result[3]
        , _block=("D1 买家之声", 5, "设置变量"))
    finally:
        args["run_status"] = run_status
        args["err_msg"] = err_msg
        args["asin_data"] = asin_data
        args["not_exist_asin_list"] = not_exist_asin_list
