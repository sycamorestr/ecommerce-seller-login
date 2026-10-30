# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
import xbot_visual
import time
from xbot.errors import UIAError
from xbot_extensions.activity_ea8fd401.iframeElement import main as GetElementAcrossDomains



def main(args):
    page = args.get("web_page") or web.get_active(mode="chrome")
    xpath = args.get("xpathSelector")
    text = args.get("输入内容")
    input_type = args.get("模拟人工")
    time_out = args.get("等待元素存在")
    is_iframe = args.get("iframe跨域元素")

    # 获取输入元素
    if is_iframe:
        element = GetElementAcrossDomains({"web_page":page, "xpathSelector": xpath})
    else:
        element = page.find_by_xpath(xpath_selector=xpath, timeout=time_out)

    xbot_visual.web.element.hover(browser=page, element=element, simulate=input_type, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("main", 16, "鼠标悬停在元素上(web)"))
