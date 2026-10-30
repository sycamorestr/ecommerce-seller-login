import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        web_page = None
        隐藏显示 = ""
    else:
        web_page = args.get("web_page", None)
        隐藏显示 = args.get("隐藏显示", "")
    try:
        # web.get
        # 图标隐藏
        if xbot_visual.workflow.test(operand1=隐藏显示, operator="==", operand2="隐藏", operator_options="{}", _block=("抖店商家助手隐藏显示", 3, "IF 条件")):
            web_js_result = xbot_visual.web.browser.execute_javascript(browser=web_page, element=package.selector("商家助手"), argument=None, code="function (element, input) {\r\n    \r\n    element.setAttribute('hidden','hidden')\r\n    return null;\r\n}", timeout="20", execution_world="ISOLATED", _block=("抖店商家助手隐藏显示", 4, "执行JS脚本"))
        else:
            try:
                web_js_result = xbot_visual.web.browser.execute_javascript(browser=web_page, element=package.selector("商家助手"), argument=None, code="function (element, input) {\r\n    \r\n    element.removeAttribute('hidden')\r\n    return null;\r\n}", timeout="20", execution_world="ISOLATED", _block=("抖店商家助手隐藏显示", 6, "执行JS脚本"))
            except Exception as e:
                pass
                web_js_result = None
        #endif
    finally:
        pass
