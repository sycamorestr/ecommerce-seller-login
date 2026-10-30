# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import select_click, handler_container
from xbot_extensions.web_action.select_date import select_date
from .import data_report_utils


def configure(web_page, transaction_type, start_time, end_time, file_fold, file_name):
    #查看类型选择
    web_page.find("report_lib_report_type_click").click()
    report_type_list = web_page.find_all("report_lib_report_type_list")
    keyword_list = ['所有交易类型', '临时付款', '订单付款', '退款',
                '信用卡拒付退款', '清算', '清仓盘点', '亚马逊商城交易保障退款',
                '服务费用', '临时付款', '订单付款', '退款',]
    select_click(report_type, keyword_list, report_type_list)

    #月选择
    web_page.find("report_lib_month").click()
    web_page.find("report_lib_month_select").click()
    month_elem_list = web_page.find_all("report_lib_month_list")
    keyword_list = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
    select_click(month, keyword_list, month_elem_list)

    #年选择
    web_page.find("report_lib_year_select").click()
    year_elem_list = web_page.find_all("report_lib_year_list")
    for year_elem in year_elem_list:
        if year_elem.get_text() == year:
            year_elem.click()
            break
    
    #点击请求报告
    web_page.find("res_report").click()
    
    #验证是否可下载
    for retry in range(100):
        try:
            web_page.find("report_lib_download_mark",timeout=2)
            break
        except:
            web_page.find("report_lib_download").click()
            continue
    web_page.find("report_lib_download").click()  
    web.handle_save_dialog(file_folder = file_fold, mode=web_page.product_name, file_name=file_name)


def run(web_page, report_type, start_time, end_time, file_fold, file_name):
    web_page.navigate("https://sellercentral.amazon.com/payments/event/view")
    handler_container(web_page)
    configure(web_page, report_type, start_time, end_time, file_fold, file_name)
    return file_fold + '\\' + file_name


def main(args):
    web_page = args.get("web_page")
    report_type = args.get("check_type",'summary')
    month = args.get('month','April')
    year = args.get('year','2020')
    file_fold = args.get("file_fold", r"C:\Users\11758\Desktop")
    file_name = args.get("file_name", r"test.csv")

    web_page = web.get_active(mode='superbrowser')
    file_path = run(web_page, report_type, month, year, file_fold, file_name)
    args["file_path"] = file_path
