# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import random
import time
import xbot
from xbot import print, sleep,win32
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from pathlib import Path
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language
from datetime import datetime
from .activities_utils import download_handler
from .create_element import *

#//section/div/form/div[normalize-space(.)="账户类型"]/*[local-name()="kat-dropdown"]
#/xbotShadowRoot//*[local-name()="kat-option"][normalize-space(.)="标准订单"]
#/xbotShadowRoot/div[@class="content-wrapper"]
class Xpath:
    # 账户类型下拉框
    AccountSelect = "//*[local-name()='kat-dropdown'][@value='PAYABLE' or @value='ALL' or @value='INVOICING']"
    # 标准订单
    StandardOrderOption = '//*[local-name()="kat-option"][@value="PAYABLE"]'
    ThirdInput = "//div[contains(@class, 'content-wrapper')]"
    #全部（联合报告）
    AllOrderOption = '//*[local-name()="kat-option"][@value="ALL"]'
    #发票支付订单
    InvoiceOrderOption = '//*[local-name()="kat-option"][@value="INVOICING"]'

    # 报告类型单选标签
    ReportTypeSpan = "(//div[contains(@class, 'report-type-selection')]//*[local-name()='kat-dropdown'][not(ancestor::*[@hidden or contains(@style, 'display: none')])])[1]"
    # 交易
    TransactionOrderOption = '//*[local-name()="kat-option"][@value="SELLER_TRANSACTION_DATE_RANGE"]'
    # 汇总
    SummaryOption = '//*[local-name()="kat-option"][@value="SELLER_SUMMARY_DATE_RANGE"]'
    # 延迟交易
    Delayed_trading = '//*[local-name()="kat-option"][@value="SELLER_HOLD_DATE_RANGE"]'

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
    # 延迟交易
    delay = create_selector_shadow(Xpath.ReportTypeSpan,Xpath.Delayed_trading, name='延迟交易')

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
        account_select_element = web_page.find_by_xpath(Xpath.AccountSelect, timeout=5)
        # 检查账户类型下拉框是否可点击
        if not account_select_element.is_enabled():
            print(f"[跳过] 账户类型下拉框不可点击，跳过账户类型选择步骤")
        else:
            account_select_element.click() # 点击账户类型下拉框
            
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

    time_select = False
    # 选择报告类型
    try:
        report_type_element = web_page.find_by_xpath(Xpath.ReportTypeSpan, timeout=5)
        # 检查报告类型下拉框是否可点击
        if not report_type_element.is_enabled():
            print(f"[跳过] 报告类型下拉框不可点击，跳过报告类型选择步骤")
        else:
            report_type_element.click() # 点击报告类型下拉框
            if report_type in ['交易','Transaction']:
                web_page.find(Element.transaction_order).click() # 选择交易
                time_select = True
            elif report_type in ['汇总','Summary']:
                web_page.find(Element.summary).click() # 选择汇总
                time_select = True
            elif report_type in ['延迟交易','Deferred transaction']:
                web_page.find(Element.delay, timeout=2).click() # 选择延迟交易
    except Exception as e:
        print(f"选择报告类型失败: {e}")
        return False

    # 选择自定义日期范围
    try:
        if time_select is True:
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
        return False
    return True


def wait_download_report(web_page: WebBrowser, file_folder: str, file_name: str, account_type: str, report_type: str, start_date: str, end_date: str, wait_timeout: int = 300, wait_timeout_appear: int = 120):
    """等待下载按钮出现后点击并下载报告。wait_timeout 为等待秒数，超时未出现则报错。"""
    end_time = time.time() + wait_timeout
    while time.time() < end_time:
        try:
            web_page.find_by_xpath(Xpath.DownloadButton, timeout=2).click()
            break
        except Exception:
            try:
                web_page.find_by_xpath(Xpath.RefreshButton).click()
                sleep(random.random() * 10)
            except Exception:
                raise Exception('未找到刷新按钮，请检查筛选日期是否正确')
    else:
        raise Exception(f'等待下载按钮超时（{wait_timeout} 秒），报表可能尚未生成，可增大「超时时间」参数后重试')

    if not file_name:
        file_name = f"{account_type}_{report_type}_{start_date}_to_{end_date}"
    file_path = download_handler(web_page, str(file_folder), file_name, wait_timeout_appear=wait_timeout_appear)
    return file_path


def download_order_report(web_page: WebBrowser, account_type: str, report_type: str, start_date: str, end_date: str, file_folder: str, file_name: str, switch_languages: bool, wait_timeout: int = 300, wait_timeout_appear: int = 120):
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    domain = get_domain(web_page)
    url = f"{domain}/payments/reports-repository"
    to_reports_page_if_need(web_page, url)

    if switch_languages:
        switch_language(web_page, 'zh_CN')

    download_state = set_filter_params(web_page, account_type, report_type, transform_date(start_date), transform_date(end_date))

    if download_state is True:
        file_path = wait_download_report(web_page, file_folder, file_name, account_type, report_type, start_date, end_date, wait_timeout=wait_timeout, wait_timeout_appear=wait_timeout_appear)
        return file_path
    


def test_download_order_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    account_type = '标准订单' # 账户类型
    report_type = '汇总' # 报告类型
    start_date = '2024-08-20' # 开始日期
    end_date = '2024-08-26' # 结束日期
    file_folder = r"D:"  # 下载文件夹路径
    # select_date.select_date(web_page,web_page.find_by_xpath('//div[@role="dialog"][@id="a-popover-4"]'),'2025-09-21','2025-09-21')
    file_name = ""  # 下载文件名
    switch_languages = True
    file_path = download_order_report(web_page, account_type, report_type, start_date, end_date, file_folder, file_name, switch_languages, 300)
    print(file_path)
    # print(web_page.find_by_xpath(Xpath.AccountSelect).is_enabled())
    exit()


def main(args):
    test_download_order_report()
    # 兼容英文参数名（block 配置）与中文参数名（旧版/表单）
    web_page = args.get('web_page')
    account_type = args.get('account_type') or '标准订单'
    report_type = args.get('report_type') or '交易'
    start_date = args.get('start_date')
    end_date = args.get('end_date')
    file_folder = args.get('download_path')
    file_name = args.get('download_name') or ''
    wait_timeout_appear = args.get('wait_timeout_appear') or 120
    wait_timeout_appear = int(wait_timeout_appear)
    if file_name and '.' not in file_name:
        raise Exception('请在文件名中添加扩展名后缀，如 .csv')
    if 'PDF' in file_name or 'CSV' in file_name:
        file_name.replace('PDF', 'pdf').replace('CSV', 'csv')
    switch_languages = args.get('is_chinese') if args.get('is_chinese') is not None else args.get('是否使用中文')
    if switch_languages is None:
        switch_languages = True
    wait_timeout = args.get('timeout') or args.get('超时时间') or 300
    try:
        wait_timeout = int(wait_timeout) if wait_timeout not in (None, '') else 300
    except (TypeError, ValueError):
        wait_timeout = 300

    if not file_folder:
        raise ValueError('未传入下载文件路径（download_path / 下载文件路径），请检查指令参数。')
    if not start_date or not end_date:
        raise ValueError('未传入开始日期或结束日期（start_date/end_date 或 开始日期/结束日期），请检查指令参数。')

    file_path = download_order_report(web_page, account_type, report_type, start_date, end_date, file_folder, file_name, switch_languages, wait_timeout, wait_timeout_appear)
    print(file_path)
    args['file_path'] = file_path
