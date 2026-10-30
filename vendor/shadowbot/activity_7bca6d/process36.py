import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    有打开的网页 = False
    当前是登录页 = False
    if args is None:
        browser_type = ""
    else:
        browser_type = args.get("browser_type", "")
    try:
        web_page = xbot_visual.programing.variable(value=lambda: None
        , _block=("退出巨量纵横登录", 1, "设置变量"))
        try:
            web_page = xbot_visual.process.invoke_module(module="utils_douyin", package=__name__, function="get_webpage", params={
                "browser_type": browser_type,
                "match_type": "3",
                "title": None,
                "url": None,
                "use_wildcard": None,
            }, _block=("退出巨量纵横登录", 3, "调用模块"))
        except Exception as exception:
            exception = xbot_visual.trace(exception)
            return
        #endtry
        有打开的网页 = xbot_visual.programing.variable(value=True
        , _block=("退出巨量纵横登录", 7, "设置变量"))
        web_url = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("退出巨量纵横登录", 8, "获取网页信息"))
        if xbot_visual.workflow.test(operand1=web_url, operator="in", operand2="business.oceanengine.com/login", operator_options="{\"ignoreCase\":\"True\"}", _block=("退出巨量纵横登录", 9, "IF 条件")):
            当前是登录页 = xbot_visual.programing.variable(value=True
            , _block=("退出巨量纵横登录", 10, "设置变量"))
        #endif
        if xbot_visual.workflow.test(operand1=web_url, operator="in", operand2="business.oceanengine.com/site", operator_options="{\"ignoreCase\":\"True\"}", _block=("退出巨量纵横登录", 12, "IF 条件")):
            # 退出登录
            xbot_visual.web.element.hover(browser=web_page, element=package.selector("巨量纵横_已登录_用户头像"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("退出巨量纵横登录", 14, "鼠标悬停在元素上(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("巨量纵横_已登录_退出登录按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("退出巨量纵横登录", 15, "点击元素(web)"))
            当前是登录页 = xbot_visual.programing.variable(value=True
            , _block=("退出巨量纵横登录", 16, "设置变量"))
        #endif
    finally:
        args["有打开的网页"] = 有打开的网页
        args["当前是登录页"] = 当前是登录页
