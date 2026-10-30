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
from .utils import get_domain
from .utils import handler_container
from ._amazon_api import switch_site, switch_language
from datetime import datetime
from .activities_utils import download_handler
from xbot.web import handle_save_dialog
from .download_utils import find_element_by_text
from xbot.errors import UIAError
from xbot import logging


class Xpath:
    # 下载链接导航
    DownloadLinkNav = "//*[@id='root']//a[@id='reportpage_download_tab']"
    # 请求下载.csv文件按钮
    RequestCsvBtn = "//*[@id='root']//kat-button[@class='download-report-page-kat-button-primary']"
    # 请求.txt下载按钮
    RequestTxtBtn = "//*[@id='root']//kat-button[@class='download-report-page-kat-button-secondary']"
    # 报告状态项
    ReportStatus = "(((//kat-table[@role='table']//kat-table-row)[2])//kat-table-cell)[last()]"
    # 下载报告按钮
    DownloadButton = "(((//kat-table[@role='table']//kat-table-row)[2])//kat-table-cell)[last()]/kat-button"
    # 收费月份下拉框
    MonthSelect = "//*[@id='root']//kat-dropdown[contains(@class, 'month-select')]"
    # 收费年份下拉框
    YearSelect = "//*[@id='root']//kat-dropdown[contains(@class, 'year-select')]"


class Option:
    # 收费月份选项
    MonthMap = {'1':'1月', '2':'2月', '3':'3月', '4':'4月', '5':'5月', '6':'6月', '7':'7月', '8':'8月', '9':'9月', '10':'10月', '11':'11月', '12':'12月'}
    # 下载文件类型列表
    FileTypeList = ['csv', 'txt']


def input_parameter_valid(web_page: WebBrowser, fee_month: str, fee_year: str, file_type: str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert fee_month.isdigit() and 1 <= int(fee_month) <= 12, f"收费月份错误：{fee_month}"
    assert len(fee_year) == 4 and fee_year.isdigit(), f"收费年份错误：{fee_year}"
    assert (file_type in Option.FileTypeList), f"不支持下载文件类型：{file_type}"


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)
    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(Xpath.DownloadLinkNav), timeout=30):
        raise Exception(
            f"进入亚马逊退货处理费（非服装和非鞋靴类商品）页面失败，未找到下载链接导航： {Xpath.DownloadLinkNav}"
        )


def set_filter_params(web_page: WebBrowser, fee_month: str, fee_year: str, file_type: str):
    # 设置报告参数
    # 选择收费年份
    web_page.find_by_xpath(Xpath.YearSelect).click()
    for option in web_page.find_all("download_returnfee_report_收费年份选项"):
        if option.get_text() == fee_year:
            option.click()
            break

    # 选择收费月份
    web_page.find_by_xpath(Xpath.MonthSelect).click()
    for option in web_page.find_all("download_returnfee_report_收费月份选项"):
        if option.get_text().replace(' ', '') == Option.MonthMap.get(fee_month):
            option.click()
            break

    # 点击下载文件类型按钮
    if file_type == 'csv':
        web_page.find_by_xpath(Xpath.RequestCsvBtn).click()
        pass
    elif file_type == 'txt':
        web_page.find_by_xpath(Xpath.RequestTxtBtn).click()


def wait_download_report(web_page:WebBrowser,file_folder:str,file_name:str):
    # 等待并下载报告
    # 等待报告状态变化
    for retry in range(5):
        if web_page.find_by_xpath(Xpath.ReportStatus).get_text()=="进行中":
            break
        sleep(2)
    # 等待报告生成
    for retry in range(50):
        try:
            # 判断有无报表可以下载
            if web_page.find_by_xpath(Xpath.ReportStatus).get_text()=="无可用数据":
                return "无可用数据"
            # 尝试找下载按钮
            download_sel = web_page.find_by_xpath(Xpath.DownloadButton, timeout=2)
            download_sel.click()
            break
        except:
            # 点击下载链接导航刷新
            web_page.find_by_xpath(Xpath.DownloadLinkNav).click()
            sleep(3)
    # 下载报告
    file_path = download_handler(web_page, file_folder, file_name)
    return file_path


def return_processing_fee_report(web_page: WebBrowser, fee_month: str, fee_year: str, file_folder: str, file_name: str, file_type: str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page, fee_month, fee_year, file_type)
    # 进入亚马逊退货处理费（非服装和非鞋靴类商品）页面
    domain = get_domain(web_page)
    url = f"{domain}/reportcentral/HIGH_RETURN_RATE_FEES/1"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置报告参数
    set_filter_params(web_page, fee_month, fee_year, file_type)

    # 等待并下载报告
    file_path = wait_download_report(web_page, file_folder, file_name)
    return file_path
    


def test_return_processing_fee_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="superbrowser")
    fee_month = '7' # 收费月份
    fee_year = '2025' # 收费年份
    file_folder = r"C:\Users\10577\Desktop\test"  # 下载文件夹路径
    file_name = "111"  # 下载文件名
    file_type = 'csv' # 下载文件类型

    file_path = return_processing_fee_report(web_page, fee_month, fee_year, file_folder, file_name, file_type)
    print(file_path)
    exit()


def main(args):
    # 测试代码入口
    # test_return_processing_fee_report()

    # 业务代码入口
    web_page = args.get('web_page')
    fee_month = args.get('fee_month') # 收费月份
    fee_year = args.get('fee_year') # 收费年份
    file_folder = args.get('file_folder')  # 下载文件夹路径
    file_name = args.get('file_name')  # 下载文件名
    file_type = args.get('file_type') # 下载文件类型

    file_path = return_processing_fee_report(web_page, fee_month, fee_year, file_folder, file_name, file_type)
    args['file_path'] = file_path
