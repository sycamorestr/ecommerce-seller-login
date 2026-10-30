# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web, win32
from .import package
from .package import variables as glv
from .utils import select_click
from .utils import handler_container
from urllib.parse import urlparse
from .activities_utils import download_handler

def select_date(web_page, date):
    mapping = {
        "一月": 1,
        "二月": 2,
        "三月": 3,
        "四月": 4,
        "五月": 5,
        "六月": 6,
        "七月": 7,
        "八月": 8,
        "九月": 9,
        "十月": 10,
        "十一月": 11,
        "十二月": 12,
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }

    target_month = date.split("-")[1]
    month_year = web_page.find("亚马逊配送报告_移除订单详情_当前年月")
    month = month_year.get_text().split(" ")[0]
    convert_month = mapping[month]

    while convert_month != int(target_month):
        if convert_month > int(target_month):
            web_page.find("亚马逊配送报告_移除订单详情_日期往前").click()
        else:
            web_page.find("亚马逊配送报告_移除订单详情_日期往后").click()

        month_year = web_page.find("亚马逊配送报告_移除订单详情_当前年月")
        month = month_year.get_text().split(" ")[0]
        convert_month = mapping[month]

    all_day = web_page.find_all("亚马逊配送报告_移除订单详情_具体日期")
    for day in all_day:
        if int(day.get_text()) == int(date.split("-")[2]):
            day.click()

def excute(web_page, order_type, order_status, date, start_time, end_time, download_type, folder_path, file_name):

    if "/reportcentral/REMOVAL_ORDER_DETAIL/1" not in web_page.get_url():
        domain = urlparse(web_page.get_url()).netloc
        url = f"{domain}/reportcentral/REMOVAL_ORDER_DETAIL/1"
        web_page.navigate(url)
        handler_container(web_page)

    sleep(3)

    web_page = web.get_active(mode=web_page.product_name)

    web_page.find("亚马逊配送报告_移除订单详情_订单类型下拉框").click()
    check_type_list = web_page.find_all('亚马逊配送报告-移除订单详情-下拉框选项')
    
    keyword_list = ['任何状况', '退货', '弃置', "取件", '批量清货', '评级和转销']
    select_click(order_type, keyword_list, check_type_list)

    web_page.find("亚马逊配送报告_移除订单详情_订单状态下拉框").click()
    check_type_list = web_page.find_all('亚马逊配送报告-移除订单详情-下拉框选项')
    keyword_list = ['任何状况', '待处理', '已完成', "已取消"]
    select_click(order_status, keyword_list, check_type_list)

    web_page.find("亚马逊配送报告_移除订单详情_日期下拉框").click()
    check_type_list = web_page.find_all('亚马逊配送报告-移除订单详情-下拉框选项')
    keyword_list = ['昨天', '最近3天', '最近7天', "最近14天", "最近30天", "自定义"]
    select_click(date, keyword_list, check_type_list) 

    if date == '自定义':
        mapping = {
            "一月": 1,
            "二月": 2,
            "三月": 3,
            "四月": 4,
            "五月": 5,
            "六月": 6,
            "七月": 7,
            "八月": 8,
            "九月": 9,
            "十月": 10,
            "十一月": 11,
            "十二月": 12,
            "January": 1,
            "February": 2,
            "March": 3,
            "April": 4,
            "May": 5,
            "June": 6,
            "July": 7,
            "August": 8,
            "September": 9,
            "October": 10,
            "November": 11,
            "December": 12
        }
        #新直接输入
        start_date_element = web_page.find("亚马逊配送报告_移除订单详情_开始日期点击框")
        placeholder = start_date_element.get_attribute("placeholder") or ""

        if "MM/DD/YYYY" in placeholder:
            # 将 YYYY-MM-DD 转换为 MM/DD/YYYY
            parts = start_time.split("-")
            start_time = f"{parts[1]}/{parts[2]}/{parts[0]}"
            parts = end_time.split("-")
            end_time = f"{parts[1]}/{parts[2]}/{parts[0]}"
        else:
            # YYYY/MM/DD 格式，将 - 替换为 /
            start_time = start_time.replace("-", "/")
            end_time = end_time.replace("-", "/")

        start_date_element.clipboard_input(start_time)

        # select_date(web_page, start_time)

        web_page.find("亚马逊配送报告_移除订单详情_结束日期点击框").clipboard_input(end_time)
        # select_date(web_page, end_time)
    
    # 点击事件
    web_page.find("亚马逊配送报告").click()

    if download_type == 'csv':
        web_page.find("亚马逊配送报告_移除订单详情_下载csv文件").click()
    elif download_type == 'txt':
        web_page.find("亚马逊配送报告_移除订单详情_下载txt文件").click()
    else:
        return "文件格式不正确 请重新输入"

    # 判断是否请求失败
    request_report_error_xpath = '//*[@class="request-report-error"]'
    request_report_error = web_page.find_all_by_xpath(request_report_error_xpath, timeout=5)
    if len(request_report_error) > 0:
        xbot.logging.warning('当前报表请求失败，请查看是否达到每日下载次数上限 或 遇到网络波动')
        return "请求失败"

    for retry in range(120):
        try:
            # 判断有无报表可以下载
            xpath = '(//kat-table-row)[2]/*[local-name()="kat-table-cell"][normalize-space(.)="无可用数据" or normalize-space(.)="No Data Available"]'
            if len(web_page.find_all_by_xpath(xpath)) >= 1:
                return "无可用数据"
            # 尝试找下载按钮

            download_button = web_page.find_all("亚马逊配送报告_移除订单详情_下载按钮", timeout=3)
            print(download_button)
            if len(download_button) > 0:
                sleep(5)
                download_button[0].click()
            break
        except Exception as e:
            print(e)
            web_page.find("亚马逊配送报告_移除订单详情_下载刷新", timeout=5).click()
            sleep(3)
    try:
        file_path = download_handler(web_page, folder_path, file_name,wait_time=600,wait_timeout_appear=30)
    except:
        download_button = web_page.find_all("亚马逊配送报告_移除订单详情_下载按钮", timeout=2)
        download_button[0].click()
        file_path = download_handler(web_page, folder_path, file_name,wait_time=600,wait_timeout_appear=30)
    return file_path
    

def main(args):
    test_run()
    web_page = args.get("web_page", "")
    order_type = args.get("order_type", "任何状况")
    order_status = args.get("order_status", "任何状况")
    date = args.get("date", "自定义")
    start_time = args.get("start_time", "2025-02-02")
    end_time = args.get("end_time", "2025-02-07")
    download_type = args.get("download_type", "csv")
    folder_path = args.get("folder_path", r'C:\Users\Administrator\Desktop\test')
    file_name = args.get("file_name", r'test.csv')

    # # web_page = web.get_active(mode='superbrowser')
    # web_page = web.get_active(mode='chrome')
    # print()
    file_path = excute(web_page, order_type, order_status, date, start_time, end_time, download_type, folder_path, file_name)
    args["file_path"] = file_path

def test_run():
    if "xbot_extensions" in __file__:
        return
    
    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    order_type = "任何状况"
    order_status = "任何状况"
    date = "自定义"
    start_time = "2025-06-01"
    end_time = "2026-07-21"
    download_type =  "csv"
    folder_path =  r'D:'
    file_name = 'test.csv'

    # # web_page = web.get_active(mode='superbrowser')
    # web_page = web.get_active(mode='chrome')
    # print()
    file_path = excute(web_page, order_type, order_status, date, start_time, end_time, download_type, folder_path, file_name)
    print(file_path)
    exit()