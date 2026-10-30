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

def get_quality_data(web_page):
    Tools.check_target_web(web_page, "main/quality/dashboard")
    titles = web_page.find_all_by_xpath("//div[contains(@class,'total-data_container')]//span[not(text()='¥')]")
    values = web_page.find_all_by_xpath("//div[contains(@class,'total-data_container')]//div[contains(@class,'total-item_content')]")
    data_dict = {}
    for title, value in zip(titles, values):
        data_dict[title.get_text()] = value.get_text().strip("¥\n")
    return data_dict

def main(args):
    
    web_page = args.get("web_page")
    # web_page = web.get_active(mode='chrome')
    data_dict = get_quality_data(web_page)
    args["data_dict"] =data_dict
    
