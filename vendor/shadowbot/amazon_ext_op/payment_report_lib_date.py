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


def configure(web_page, report_type, start_time, end_time, file_fold, file_name):
    #查看类型选择
    web_page.find("report_lib_report_type_click").click()
    report_type_list = web_page.find_all("report_lib_report_type_list")
    keyword_list = ['summary', 'transaction', 'delay_transaction']
    select_click(report_type, keyword_list, report_type_list)

    #日期选择
    web_page.find("report_lib_starttime_input").click()
    time_body = web_page.find("report_lib_date_body")
    select_date(web_page, time_body, start_time, '')
    web_page.find("report_lib_endtime_input").click()
    time_body = web_page.find("report_lib_date_body")
    select_date(web_page, time_body, end_time, '')
    
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
    web_page.navigate("https://sellercentral.amazon.com/payments/reports-repository/ref=xx_rrepo_dnav_xx")
    handler_container(web_page)
    configure(web_page, report_type, start_time, end_time, file_fold, file_name)
    return file_fold + '\\' + file_name


def main(args):
    web_page = args.get("web_page")
    report_type = args.get("check_type",'transaction')
    start_time = args.get('start_time','2024-11-10')
    end_time = args.get('end_time','2024-11-15')
    file_fold = args.get("file_fold", r"C:\Users\PC\Desktop")
    file_name = args.get("file_name", r"test.csv")

    web_page = web.get_active(mode='superbrowser')
    file_path = run(web_page, report_type, start_time, end_time, file_fold, file_name)
    args["file_path"] = file_path
