# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import Tools

def participage_active(web_page, file_path):
    Tools.check_web(web_page, 'activity/marketing-activity')
    web_page.find_by_xpath("//span[text()='批量报名活动']").click()
    web_page.find_by_xpath("//span[text()='选择文件']").upload(file_names=file_path)
    sleep(2)
    web_page.find_by_xpath("//span[text()='开始导入']").click()
    web_page.find_by_xpath("//span[text()='确认并报名活动']").click()


def main(args):
    web_page = args.get("web_page")
    # web_page = web.get_active(mode='chrome')
    file_path = args.get("file_path",r"C:\Users\11758\Desktop\报名商品信息.xlsx")
    participage_active(web_page, file_path)
