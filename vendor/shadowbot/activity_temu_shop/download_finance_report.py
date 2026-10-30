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

def download(web_page, date, file_folder):
    """下载逻辑"""
    Tools.check_web(web_page, 'labor/bill')  
    web_page.find_by_xpath("//span[text()='导出历史']").click()
    total_page = web_page.find_by_xpath("//ul/li[last()-1]").get_text()  #得到总页数
    quit = True #用于退出外圈循环
    for page in total_page:
        financial_reports = web_page.find_all_by_xpath("//div[contains(@class,'exportHistoryList')]/div")
        for financial_report in financial_reports:
            info = financial_report.find_by_xpath("./div[1]/div[1]").get_text()
            report_date = info.split('时间')[1]
            if report_date > date:
                status = financial_report.find_by_xpath(".//button//span[1]")
                try:
                    keyword = financial_report.find_by_xpath(".//div[contains(@class,'export-history_right')]/div[2]",timeout=2).get_text()
                except:
                    continue
                if status.get_text() == '下载数据报表' and "失效" in keyword:
                    file_name = report_date.replace(' ', '_').replace(':', '-') + "财务明细报表.xlsx"
                    status.click(simulative=False)  
                    web.handle_save_dialog(file_folder=file_folder, file_name=file_name, mode=web_page.product_name,wait_appear_timeout=120)
            else:
                quit = False
                break
        if quit == False:
            break
        web_page.find_by_xpath("//ul/li[last()]").click()

def main(args):
    
    web_page = args.get("web_page", '')
    # web_page = web.get_active(mode='chrome')
    date = args.get("date", '2025-01-03')
    file_folder = args.get("file_folder", r'C:\Users\11758\Desktop\test')
    download(web_page, date, file_folder)

