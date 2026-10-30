# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot.errors import UIAError
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from xbot_extensions.activity_ea8fd401.iframeElement import main as GetElementAcrossDomains



def main(args):
    xpath = args.get("xpathSelector")
    time_out = args.get("获取元素超时")
    is_iframe_element = args.get("是否为iframe对象")

    browser = args.get("web_page") or web.get_active(mode="chrome")

    # 跨iframe查找
    try:
        if is_iframe_element:
            GetElementAcrossDomains({"web_page":browser, "xpathSelector": xpath})
        else:
            browser.find_all_by_xpath(xpath, timeout=time_out)[0]
        args["是否存在"] = True
    except:
        args["是否存在"] = False
