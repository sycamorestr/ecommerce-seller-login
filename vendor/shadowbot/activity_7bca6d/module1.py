# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv

def run(web_page, down_elem):
    elem = web_page.find(down_elem)
    elem.hover()
    win32.mouse_click(click_type='down')
    sleep(7)
    win32.mouse_click(click_type='up')
 
def main(args):
    web_page = args.get('web_page')
    down_elem = args.get('down_elem')
    # web_page = web.get_active(mode='chrome')
    run(web_page, down_elem)
