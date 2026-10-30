import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        全局超时时间 = "20"
    else:
        网页对象 = args.get("网页对象", None)
        全局超时时间 = args.get("全局超时时间", "20")
    try:
        if xbot_visual.web.browser.contains_element_or_text(browser=网页对象, content_type="contains_element", selector=package.selector("飞鸽工作台_广告"), text="", _block=("飞鸽工作台去除开屏广告", 1, "IF 网页包含")):
            web_js_result = xbot_visual.web.browser.execute_javascript(browser=网页对象, element=package.selector("飞鸽工作台_广告"), argument=None, code="function (element, input) {\r\n    // 在此处编写您的Javascript代码\r\n    // element表示选择的操作目标(HTML元素)\r\n    // input表示输入的参数(字符串)\r\n    \r\n    if (element.parentElement.nodeName == 'DIV'){\r\n        element.parentElement.remove()\r\n    }else{\r\n        element.remove()\r\n    }\r\n}", timeout=全局超时时间, execution_world="ISOLATED", _block=("飞鸽工作台去除开屏广告", 2, "执行JS脚本"))
            return
        #endif
        if xbot_visual.web.browser.contains_element_or_text(browser=网页对象, content_type="contains_element", selector=package.selector("弹窗"), text="", _block=("飞鸽工作台去除开屏广告", 5, "IF 网页包含")):
            web_js_result = xbot_visual.web.browser.execute_javascript(browser=网页对象, element=package.selector("弹窗"), argument=None, code="function (element, input) {\r\n    // 在此处编写您的Javascript代码\r\n    // element表示选择的操作目标(HTML元素)\r\n    // input表示输入的参数(字符串)\r\n    \r\n    if (element.parentElement.nodeName == 'DIV'){\r\n        element.parentElement.remove()\r\n    }else{\r\n        element.remove()\r\n    }\r\n}", timeout=全局超时时间, execution_world="ISOLATED", _block=("飞鸽工作台去除开屏广告", 6, "执行JS脚本"))
            return
        #endif
        xbot_visual.programing.log(type="info", text="未检测到广告，或未支持的广告类型 ~", _block=("飞鸽工作台去除开屏广告", 9, "打印日志"))
    finally:
        pass
