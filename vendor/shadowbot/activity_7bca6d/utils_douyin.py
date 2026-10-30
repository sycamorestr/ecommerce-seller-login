# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot import web


def open_webpage(browser_type, url, load_timeout=20, stop_if_timeout=False):
    """打开网页"""
    load_timeout = int(load_timeout)
    browser_name = {
        '0': 'chrome',
        '1': 'edge',
        '2': 'ie',
        '3': '360se',
        '4': 'cef',
    }.get(str(browser_type), 'cef')
    web_page = web.create(url, mode=browser_name, load_timeout=load_timeout, stop_if_timeout=stop_if_timeout, 
                arguments=None)
    return web_page


def get_webpage(browser_type, match_type, title, url, use_wildcard=False):
    """获取网页对象
        browser_type
        match_type 1:根据标题|2:根据url|3:当前
    """

    browser_name = {
        '0': 'chrome',
        '1': 'edge',
        '2': 'ie',
        '3': '360se',
        '4': 'cef',
    }.get(browser_type, 'cef')
    if match_type == '3':
        return web.get_active(mode=browser_name, load_timeout=20)

    args = {
        "mode": browser_name,
        "load_timeout": 20,
        "use_wildcard": use_wildcard,
    }
    if match_type == '1':
        args["title"] = title
    elif match_type == '2':
        args["url"] = url
    return web.get(**args)


def main(args):
    # url = 'https://www.baidu.com'
    # open_webpage(url, browser_type='4')
    web_page = get_webpage('0', '1', "百度一下", "baidu")
    print(web_page)
