# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,win32
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from pathlib import Path
from .activities_utils import get_shadowroot_element,gen_selector
from .utils import get_domain, handler_container
from ._amazon_api import switch_site
from datetime import datetime
from .activities_utils import download_handler
from xbot.web import handle_save_dialog
from .download_utils import find_element_by_text
from xbot.errors import UIAError
from xbot import logging
from .create_element import create_selector
from xbot._core.retry import Retry


class Xpath:
    # 下载链接导航
    DownloadLinkNav = "//*[@id='root']//a[@id='reportpage_download_tab']"
    # 请求下载.csv文件按钮
    RequestCsvBtn = "//*[@id='root']//kat-button[@class='download-report-page-kat-button-primary']"
    # 请求.txt下载按钮
    RequestTxtBtn = "//*[@id='root']//kat-button[@class='download-report-page-kat-button-secondary']"
    # 事件日期
    ReportDate = create_selector('//*[local-name()="kat-dropdown"]/xbotShadowRoot//div[@class="select-header"]',name ='事件日期')
    # 确切日期
    ExactDate = create_selector('//*[local-name()="kat-dropdown"]/xbotShadowRoot//kat-option[@value="-1"]',name='确切日期')
    # 报告状态项
    ReportStatus = "(((//kat-table[@role='table']//kat-table-row)[2])//kat-table-cell)[last()]"
    # 下载报告按钮
    DownloadButton = "(((//kat-table[@role='table']//kat-table-row)[2])//kat-table-cell)[last()]/kat-button"
    # 报告类型
    ReportClass = '//*[local-name()="kat-table-cell"][@role="columnheader"][1]'

    StartDate = create_selector('//*[local-name()="kat-date-range-picker"]/xbotShadowRoot/*[local-name()="kat-date-picker"][@class="start"]/xbotShadowRoot//*[@class="input"]',name = '开始日期')
    EndDate = create_selector('//*[local-name()="kat-date-range-picker"]/xbotShadowRoot/*[local-name()="kat-date-picker"][@class="end"]/xbotShadowRoot//*[@class="input"]',name='结束日期')


def input_parameter_valid(web_page: WebBrowser, file_type: str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (file_type in ['csv', 'txt']), f"不支持下载文件类型：{file_type}"


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)


def set_filter_params(web_page: WebBrowser, file_type: str,start_date,end_date):
    # 设置报告参数
    web_page.find_by_xpath(Xpath.DownloadLinkNav).click()
    web_page.find(Xpath.ReportDate).click()
    web_page.find(Xpath.ExactDate).click()
    start_date_element = web_page.find(Xpath.StartDate)
    placeholder = start_date_element.get_attribute("placeholder") or ""
    if "MM/DD/YYYY" in placeholder:
        parts = start_date.split("-")
        start_date = f"{parts[1]}/{parts[2]}/{parts[0]}"
        parts = end_date.split("-")
        end_date = f"{parts[1]}/{parts[2]}/{parts[0]}"
    else:
        start_date = start_date.replace("-", "/")
        end_date = end_date.replace("-", "/")
    start_date_element.input(start_date)
    web_page.find(Xpath.EndDate).input(end_date)
    web_page.find('亚马逊配送报告').click()
    # 点击下载文件类型按钮
    if file_type == 'csv':
        web_page.find_by_xpath(Xpath.RequestCsvBtn).click()
    elif file_type == 'txt':
        web_page.find_by_xpath(Xpath.RequestTxtBtn).click()


def wait_download_report(web_page:WebBrowser,file_folder:str,file_name:str, wait_timeout_appear):
    # 等待并下载报告
    # 判断是否请求失败
    request_report_error_xpath = '//*[@class="request-report-error"]'
    request_report_error = web_page.find_all_by_xpath(request_report_error_xpath, timeout=5)
    if len(request_report_error) > 0:
        xbot.logging.warning('当前报表请求失败，请查看是否达到每日下载次数上限 或 遇到网络波动')
        return "请求失败"
    # 等待报告状态变化
    for retry in range(5):
        if web_page.find_by_xpath(Xpath.ReportStatus).get_text()=="进行中":
            break
        sleep(2)
    # 等待报告生成
    for retry in Retry(timeout=wait_timeout_appear):
        try:
            # 判断有无报表可以下载
            if web_page.find_by_xpath(Xpath.ReportStatus).get_text()=="无可用数据":
                return "无可用数据"
            # 尝试找下载按钮
            web_page.find_by_xpath(Xpath.DownloadButton, timeout=2).click()
            break
        except:
            # 点击下载链接导航刷新
            web_page.find_by_xpath(Xpath.DownloadLinkNav).click()
            sleep(10)
    # 下载报告
    file_path = download_handler(web_page, file_folder, file_name, wait_timeout_appear=wait_timeout_appear)
    return file_path


def return_processing_report(web_page: WebBrowser,file_folder: str, file_name: str, file_type: str,start_date,end_date, wait_timeout_appear):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page,file_type)

    # 进入亚马逊配送货件
    domain = get_domain(web_page)
    url = f"{domain}/reportcentral/AFNShipmentReport/1"
    to_reports_page_if_need(web_page, url)
    
    web_page.wait_load_completed(timeout=30)
    # 设置报告参数
    set_filter_params(web_page,file_type,start_date,end_date)

    # 等待并下载报告
    file_path = wait_download_report(web_page, file_folder, file_name, wait_timeout_appear)
    return file_path
    


def test_return_processing_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="superbrowser")
    file_folder = r"C:\Users\58204\Desktop"  # 下载文件夹路径
    file_name = "111"  # 下载文件名
    file_type = 'csv' # 下载文件类型
    start_date = '2025-10-01'
    end_date ='2025-10-20'
    file_path = return_processing_report(web_page,file_folder, file_name, file_type,start_date,end_date)
    print(file_path)

    exit()


def main(args):
    # 测试代码入口
    # test_return_processing_report()

    # 业务代码入口
    web_page = args.get('web_page')
    file_folder = args.get('file_folder')  # 下载文件夹路径
    file_name = args.get('file_name')  # 下载文件名
    file_type = args.get('file_type') # 下载文件类型
    start_date = args.get('start_date')
    end_date = args.get('end_date') 
    wait_timeout_appear = args.get('wait_timeout_appear') or 300   


    file_path = return_processing_report(web_page,file_folder, file_name, file_type,start_date,end_date, wait_timeout_appear)
    args['file_path'] = file_path
