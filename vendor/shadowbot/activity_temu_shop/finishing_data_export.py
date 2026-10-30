# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os

import xbot
import xbot_visual
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import Tools
from .download_utils import download_handler

def export_data(web_page, file_path, file_name):

    # 获取浏览器名称
    web_type = Tools.get_web_page_product_name(web_page)

    Tools.check_target_web(web_page, 'labor/settle')
    web_page.find_by_xpath("//*[text()='结算中款项']/..//following-sibling::*").click()#点击导出数据
    
    next_xpath = '//span[text()="下一条"]'# 下一条元素
    next_sel   = Tools.gen_selector(next_xpath)
    confirm_export_xpath = '//span[text()="确认导出并继续"]'    # 确认导出元素
    confirm_export_sel   = Tools.gen_selector(confirm_export_xpath)

    if web_page.wait_appear(next_sel, timeout=1):
        # 循环匹配出现的元素并进行点击
        while True:

            # 点击下一条
            if web_page.wait_appear(next_sel, timeout=1):
                web_page.find_by_xpath(next_xpath).click()
                continue
            # 点击确认导出并继续
            if web_page.wait_appear(confirm_export_sel, timeout=1):
                web_page.find_by_xpath(confirm_export_xpath).click()
                break

    for retry in range(100):
        target_report = web_page.find_by_xpath("//div[contains(@class,'exportHistoryList')]/div[1]//button//span[1]")
        if '生成中' in target_report.get_text():
            sleep(2)
            web_page.find_by_xpath("//span[text()='刷新']").click()
            continue
        else:
            target_report.click()
            download_handler(web_page=web_page, file_folder=file_path, file_name=file_name)
            break
    return file_path + '\\' + file_name

def main(args):
    
    web_page = args.get("web_page")
    folder_path = args.get("folder_path", r"C:\Users\11758\Desktop\test")
    file_name = args.get("file_name", 'test.xlsx')

    # web_page = web.get_active(mode='chrome')

    file_path = export_data(web_page, folder_path, file_name)
    args["file_path"] = file_path

