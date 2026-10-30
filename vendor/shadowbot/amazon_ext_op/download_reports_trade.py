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
from ._amazon_api import switch_site, switch_language
from datetime import datetime
from .activities_utils import download_handler
from xbot.web import handle_save_dialog
from .download_utils import find_element_by_text
from xbot.errors import UIAError
from xbot import logging
from xbot_extensions.web_action import select_date
from .get_date import execute_date_selection_workflow
from .create_element import *
from xbot.selector import Selector

#//section/div/form/div[normalize-space(.)="账户类型"]/*[local-name()="kat-dropdown"]
#/xbotShadowRoot//*[local-name()="kat-option"][normalize-space(.)="标准订单"]
#/xbotShadowRoot/div[@class="content-wrapper"]
class Xpath: 
    # 账户类型下拉框
    AccountSelect = "//*[local-name()='kat-dropdown'][@value='PAYABLE' or @value='ALL' or @value='INVOICING']"
    # 交易类型
    TradeType = '//*[local-name()="kat-label"][@text="交易类型" or @text="Transaction Type"]/following-sibling::*[local-name()="kat-dropdown"]'
    #交易状态
    TradeStatus = '//*[local-name()="kat-label"][@text="交易状态" or @text="Transaction Status"]/following-sibling::*[local-name()="kat-dropdown"]'

    # 自定义日期范围选项
    EventDateOption = '//form//div[contains(@class, "main-page")]//input[@role="radio"][@value="CUSTOM"]'
    # 开始日期输入框
    StartDateInput = '(//*[local-name()="kat-date-picker"][@name="startDate"])[1]'
    # 结束日期输入框
    EndDateInput = '(//*[local-name()="kat-date-picker"][@name="endDate"])[1]'
    # 日期shadow内xpath
    DateShadowInput = '//*[local-name()="kat-input"][@type="text"]'
    #日期第三层xpath
    DateThirdInput = '//input[@type="text"]'

    # 请求按钮
    RequestButton = '//*[local-name()="kat-button"][@id="filter-generate-button"]'
    #请求shadow内xpath
    RequestShadowButton = '//button'

    # 刷新按钮
    RefreshButton = '//*[local-name()="kat-table-row"][1][.//*[local-name()="kat-statusindicator" and @variant="loading"]]/*[local-name()="kat-table-cell"][contains(@class, "header-cell-report-action")]//*[local-name()="kat-button"]'


    # 下载按钮
    DownloadButton = '//*[local-name()="kat-table-body"]/*[local-name()="kat-table-row"][1][.//*[local-name()="kat-statusindicator" and @variant="success"]]/*[local-name()="kat-table-cell"][last()]//*[local-name()="kat-button"]'



class Element:
    
    #标准订单 此元素需要手动拼接好xbotshadowroot
    # standard_order = create_selector(Xpath.AccountSelect,Xpath.StandardOrderOption, name = '标准订单')
    standard_order = create_selector_shadow(Xpath.AccountSelect,Xpath.StandardOrderOption, name = '标准订单')
    #全部（联合报告）
    all_order = create_selector_shadow(Xpath.AccountSelect,Xpath.AllOrderOption, name = '全部（联合报告）')
    #发票支付订单
    invoice_order = create_selector_shadow(Xpath.AccountSelect,Xpath.InvoiceOrderOption, name = '发票支付订单')

    #交易
    transaction_order = create_selector_shadow(Xpath.ReportTypeSpan,Xpath.TransactionOrderOption, name = '交易')
    #汇总
    summary = create_selector_shadow(Xpath.ReportTypeSpan,Xpath.SummaryOption, name = '汇总')

    #开始日期输入框
    start_date = create_selector(Xpath.StartDateInput, Xpath.DateShadowInput, name = '开始日期输入框')
    #结束日期输入框
    end_date = create_selector(Xpath.EndDateInput, Xpath.DateShadowInput, name = '结束日期输入框')

    #请求按钮
    request_button = create_selector(Xpath.RequestButton, Xpath.RequestShadowButton, name = '请求按钮')







def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)


def transform_date(date: str):
    # 转换日期格式
    try:
        result = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        return result
    except Exception as e:
        raise Exception(f"日期格式错误：{date}")


def set_filter_params(web_page: WebBrowser, account_type: str, report_type: str,start_date: str, end_date: str):
    # 选择账户类型
    try:
        web_page.find_by_xpath(Xpath.AccountSelect).click() # 点击账户类型下拉框
        
        if account_type in ['标准订单','Order Date']:
            # web_page.find('cs').hover() # 选择标准订单
            web_page.find(Element.standard_order).click()
            # web_page.find('cscs').click()            
        elif account_type in ['全部(联合报告)','全部（联合报告）','全部']:
            print(2)
            web_page.find(Element.all_order).click() # 选择全部（联合报告）
        elif account_type in ['发票支付订单','Invoice Payment Order']:
            web_page.find(Element.invoice_order).click() # 选择发票支付订单
    except Exception as e:
        print(f"选择账户类型失败: {e}")


    # 选择报告类型
    try:
        web_page.find_by_xpath(Xpath.ReportTypeSpan).click() # 点击报告类型下拉框
        if report_type in ['交易','Order Date']:
            web_page.find(Element.transaction_order).click() # 选择交易
        elif report_type in ['汇总','Summary']:
            web_page.find(Element.summary).click() # 选择汇总
    except Exception as e:
        print(f"选择报告类型失败: {e}")

    # 选择自定义日期范围
    try:
        web_page.find_by_xpath(Xpath.EventDateOption).click() # 选择自定义日期范围
        # 输入开始日期
        web_page.find(Element.start_date).input(start_date) # 点击开始日期输入
        # 输入结束日期
        web_page.find(Element.end_date).input(end_date) # 点击结束日期输入
        # 粘贴完日期点击按钮将日历关闭（遮挡了请求按钮）
        web_page.find_by_xpath(Xpath.EventDateOption).click() # 选择自定义日期范围

        #点击请求报告
        web_page.find(Element.request_button).click() # 点击请求按钮

    except Exception as e:
        print(f"输入日期出错: {e}")

    sleep(2)


def wait_download_report(web_page: WebBrowser, file_folder: str, file_name: str, account_type: str, report_type: str, start_date: str, end_date: str):
    # 查看网页是否存在刷新按钮，存在则点击，点击后等待5秒，当下载按钮出现时，点击下载
    # 等待报告状态变化
    for retry in range(50):
        try:
            # 尝试找下载按钮
            web_page.find_by_xpath(Xpath.DownloadButton, timeout=2).click()
            break
        except:
            # 点击刷新按钮
            web_page.find_by_xpath(Xpath.RefreshButton).click()
            sleep(3)

    # 下载报告
    if file_name == '':
        file_name = f"{account_type}_{report_type}_{start_date}_to_{end_date}"
    file_path = download_handler(web_page, file_folder, file_name)
    return file_path


def download_order_report(web_page: WebBrowser,account_type:str, report_type: str,start_date: str, end_date: str, file_folder: str, file_name: str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 进入订单报告页面
    domain = get_domain(web_page)
    url = f"{domain}/payments/reports-repository"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置报告参数
    set_filter_params(web_page,account_type, report_type, transform_date(start_date), transform_date(end_date))

    # 等待并下载报告
    file_path = wait_download_report(web_page, file_folder, file_name, account_type, report_type, start_date, end_date)
    return file_path
    


def test_download_order_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="superbrowser")
    account_type = '标准订单' # 账户类型
    report_type = '汇总' # 报告类型
    start_date = '2024-08-20' # 开始日期
    end_date = '2024-08-26' # 结束日期
    file_folder = r"C:\Users\58204\Desktop\test"  # 下载文件夹路径
    # select_date.select_date(web_page,web_page.find_by_xpath('//div[@role="dialog"][@id="a-popover-4"]'),'2025-09-21','2025-09-21')
    file_name = ""  # 下载文件名
    file_path = download_order_report(web_page, account_type, report_type, start_date, end_date, file_folder, file_name)
    print(file_path)
    exit()


def main(args):
    # 测试代码入口
    test_download_order_report()

    # 业务代码入口
    web_page = args.get('web_page')
    account_type = args.get('账户类型' or '标准订单') # 账户类型
    report_type = args.get('报告类型' or '交易') # 报告类型

    start_date = args.get('开始日期') # 开始日期
    end_date = args.get('结束日期') # 结束日期
    file_folder = args.get('下载文件路径')  # 下载文件夹路径
    file_name = args.get('文件名')  # 下载文件名

    file_path = download_order_report(web_page, account_type, report_type, start_date, end_date, file_folder, file_name)
    print(file_path)
    args['file_path'] = file_path
