# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.selector import Selector
from . import package

def get_ele(web_page, xpath, ele_name):
    if "iframe" in xpath:
            xpaths = xpath.split(">>")
            data =  {'id': 'ifream-xpath', 'name': ele_name, 'type': 'simple', 'xpath': {'enable': 'true', 'segments': xpaths}}
            selector = Selector(data)
            return selector
    else:
        data =  {'id': 'ifream-xpath', 'name': ele_name, 'type': 'simple', 'xpath': {'enable': 'true', 'segments': [xpath]}}
        selector = Selector(data)
        return selector

def get_web_page_mode(web_page):
    ''' 获取网页mode类型
    '''
    product_name = getattr(web_page, "product_name", "cef" if web_page._controller == "CEFBrowser" else "firefox")
    return product_name

def main(args):
    # for item in dir(package.selector('密码框')):
    #     if item == 'value':
    #         print(type(item))
    pass
