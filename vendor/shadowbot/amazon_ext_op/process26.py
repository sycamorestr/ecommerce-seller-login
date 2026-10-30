import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    run_status = False
    err_msg = ""
    campaign_data = []
    if args is None:
        网页对象 = None
        站点名称 = ""
    else:
        网页对象 = args.get("网页对象", None)
        站点名称 = args.get("站点名称", "")
    try:
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                网页对象 = xbot_visual.web.get(web_type="superbrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("E3 广告爆款超预算数据抓取", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("E3 广告爆款超预算数据抓取", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        站点名称 = xbot_visual.programing.variable(value="美国"
        , _block=("E3 广告爆款超预算数据抓取", 2, "设置变量"))
        invoke_result = xbot_visual.process.invoke_module(module="_ad_api", package=__name__, function="get_campaigns", params={
            "web_page": 网页对象,
            "site_name": 站点名称,
        }, _block=("E3 广告爆款超预算数据抓取", 3, "调用模块"))
        run_status = xbot_visual.programing.variable(value=lambda: invoke_result[0]
        , _block=("E3 广告爆款超预算数据抓取", 4, "设置变量"))
        err_msg = xbot_visual.programing.variable(value=lambda: invoke_result[1]
        , _block=("E3 广告爆款超预算数据抓取", 5, "设置变量"))
        campaign_data = xbot_visual.programing.variable(value=lambda: invoke_result[2]
        , _block=("E3 广告爆款超预算数据抓取", 6, "设置变量"))
    finally:
        args["run_status"] = run_status
        args["err_msg"] = err_msg
        args["campaign_data"] = campaign_data
