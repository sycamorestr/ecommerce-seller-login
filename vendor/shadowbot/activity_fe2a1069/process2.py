import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        web_page = None
        url = ""
        跳转最大次数 = 5
    else:
        web_page = args.get("web_page", None)
        url = args.get("url", "")
        跳转最大次数 = args.get("跳转最大次数", 5)
    try:
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=跳转最大次数, step="1", _block=("URL检查", 1, "For次数循环")):
            web_page_attribute = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("URL检查", 2, "获取网页信息"))
            if xbot_visual.workflow.test(operand1=web_page_attribute, operator="not in", operand2=url, operator_options="{\"ignoreCase\":\"False\"}", _block=("URL检查", 3, "IF 条件")):
                xbot_visual.web.browser.navigate(browser=web_page, mode="url", url=url, ignore_cache=False, load_timeout="120", _block=("URL检查", 4, "跳转至新网址"))
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("URL检查", 5, "等待"))
                if xbot_visual.workflow.test(operand1=loop_index, operator="==", operand2=跳转最大次数, operator_options="{}", _block=("URL检查", 6, "IF 条件")):
                    raise Exception("超过最大跳转次数后url仍不正确：url > " + xbot_visual.sh_str(web_page_attribute))
                #endif
            else:
                break
            #endif
        #endloop
    finally:
        pass
