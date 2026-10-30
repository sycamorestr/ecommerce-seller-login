import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        平台名称 = ""
        web_mode = ""
    else:
        平台名称 = args.get("平台名称", "")
        web_mode = args.get("web_mode", "")
    try:
        url_map = {
            "京挑客": "https://jzt.jd.com/jtk/#/index",
            "京准通": "https://jzt.jd.com/home/#/index",
            "京准通-账户中心": "https://jzt.jd.com/account/#/financial",
            "商智-品牌版": "https://ppzh.jd.com/brand/homePage/index.html",
            "商智-商家版": "https://sz.jd.com",
            "京东快车": "https://jzt.jd.com/jdkc/survey.html#/survey",
            "京东联盟": "https://union.jd.com",
            "推荐广告": "https://jzt.jd.com/touch_point/index.html#/survey",
            "互动广告": "https://jzt.jd.com/jdzw/#/index",
            "京东数坊": "",
            "站外广告": "https://jyt.jd.com/jyt/#/accountHome",
            "站外广告-账户中心": "https://jzt.jd.com/zt/#/index",
            "智能投放": "https://jzt.jd.com/jst/#/index",
        }
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type=web_mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京准通登录后跳转", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("京准通登录后跳转", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        url = xbot_visual.programing.variable(value=lambda: url_map.get(平台名称)
        , _block=("京准通登录后跳转", 3, "设置变量"))
        if xbot_visual.workflow.test(operand1=url, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("京准通登录后跳转", 4, "IF 条件")):
            xbot_visual.web.browser.navigate(browser=web_page, mode="url", url=lambda: url_map.get(平台名称), ignore_cache=False, load_timeout="120", _block=("京准通登录后跳转", 5, "跳转至新网址"))
        #endif
    finally:
        pass
