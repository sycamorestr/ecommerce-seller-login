# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
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
from xbot_extensions.web_action import select_date
from .get_date import execute_date_selection_workflow


class Xpath:
    # 报告类型单选标签
    ReportTypeSpan = '//span[contains(@class, "radio")]'
    # 事件日期下拉框
    EventDateSelect = '//span[@data-test-id="eventDate-allOrdersReport"]//span[contains(@class, "a-button-dropdown")]'
    # EventDateSelect = '//select[@name="eventDate-allOrdersReport"]'
    # 事件日期选项
    EventDateOption = '//div[contains(@class, "a-popover") and @aria-hidden="false"]//li[@role="presentation"]/a'
    # 开始日期输入框
    StartDateInput = '//*[@id="all-orders-report-start-date"]//input'
    # 结束日期输入框
    EndDateInput = '//*[@id="all-orders-report-end-date"]//input'
    # 请求按钮
    RequestButton = '//input[@name="request"]'
    # 刷新按钮
    RefreshButton = '//*[@id="refreshButton"]//input'
    # 下载报告表格下载项
    DownloadColumn = '//*[contains(@id, "reports")]//tr[2]//td[last()]'
    # 下载按钮
    DownloadButton = '//*[contains(@id, "reports")]//tr[2]//td[last()]//a[@role="button"]'
    # 下载报告表格批编号项
    BatchIdColumn = '//*[contains(@id, "reports")]//tr[2]//td[2]'


class Option:
    # 报告类型选项
    ReportTypeList = ['订单日期', '上次更新日期']
    # 事件日期选项
    EventDateMap = {'最后一天': '日期范围：最后一天', '过去3天': 'Date range: Last 3 days', '过去7天': '日期范围：过去7天', '过去14天': 'Date range: Last 14 days', '过去30天': '日期范围：过去30天', '确切日期': 'Exact dates'}


def input_parameter_valid(web_page: WebBrowser, report_type: str, event_date: str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    # assert fee_month.isdigit() and 1 <= int(fee_month) <= 12, f"收费月份错误：{fee_month}"
    # assert len(fee_year) == 4 and fee_year.isdigit(), f"收费年份错误：{fee_year}"
    # assert (file_type in Option.FileTypeList), f"不支持下载文件类型：{file_type}"


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
    if not web_page.wait_appear(gen_selector(Xpath.RequestButton), timeout=30):
        raise Exception(
            f"进入订单报告页面失败，未找到请求按钮： {Xpath.RequestButton}"
        )


def transform_date(date: str):
    # 转换日期格式
    try:
        result = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        return result
    except Exception as e:
        raise Exception(f"日期格式错误：{date}")


def set_filter_params(web_page: WebBrowser, report_type: str, event_date: str, start_date: str, end_date: str):
    # 选择报告类型
    for btn in web_page.find_all_by_xpath(Xpath.ReportTypeSpan):
        if btn.get_text() == report_type:
            if report_type == Option.ReportTypeList[0]:
                web_page.find_by_xpath('(' + Xpath.ReportTypeSpan + ')[1]/preceding-sibling::input').click()
            elif report_type == Option.ReportTypeList[1]:
                web_page.find_by_xpath('(' + Xpath.ReportTypeSpan + ')[2]/preceding-sibling::input').click()
            break
    # 选择事件日期
    web_page.find_by_xpath(Xpath.EventDateSelect).click() # 点击事件日期下拉框
    for option in web_page.find_all_by_xpath(Xpath.EventDateOption):
        if option.get_text() == Option.EventDateMap.get(event_date):
            if event_date == '确切日期':
                option.click()
                web_page.find_by_xpath(Xpath.StartDateInput).click()
                # web_page.find_by_xpath(Xpath.StartDateInput).clipboard_input(text=transform_date(start_date))
                # web_page.find_by_xpath(Xpath.EndDateInput).click()
                # web_page.find_by_xpath(Xpath.EndDateInput).clipboard_input(text=transform_date(end_date))
                execute_date_selection_workflow(web_page,start_date,end_date)
                web_page.find_by_xpath(Xpath.EndDateInput).click(anchor=('bottomRight', 20, 0))
            else:
                option.click()
    web_page.find_by_xpath(Xpath.RequestButton).click() # 点击请求按钮


def wait_download_report(web_page: WebBrowser, file_folder: str, file_name: str, report_type: str, event_date: str, start_date: str, end_date: str):
    # 等待并下载报告
    # 等待报告状态变化
    for retry in range(5):
        if web_page.find_by_xpath(Xpath.DownloadColumn).get_text()=="未准备好":
            break
        sleep(2)
    # 等待报告生成
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
        if event_date == '确切日期':
            file_name = report_type + '_' + web_page.find_by_xpath(Xpath.BatchIdColumn).get_text() + '_' + start_date + '_' + end_date
        else:
            file_name = report_type + '_' + web_page.find_by_xpath(Xpath.BatchIdColumn).get_text() + '_' + event_date
    file_path = download_handler(web_page, file_folder, file_name)
    return file_path


def download_order_report(web_page: WebBrowser, report_type: str, event_date: str, start_date: str, end_date: str, file_folder: str, file_name: str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page, report_type, event_date)

    # 进入订单报告页面
    domain = get_domain(web_page)
    url = f"{domain}/order-reports-and-feeds/reports/allOrders#"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置报告参数
    set_filter_params(web_page, report_type, event_date, start_date, end_date)

    # 等待并下载报告
    file_path = wait_download_report(web_page, file_folder, file_name, report_type, event_date, start_date, end_date)
    return file_path
    


def test_download_order_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="superbrowser")
    report_type = '订单日期' # 报告类型
    event_date = '确切日期' # 事件日期
    start_date = '2026-02-05' # 开始日期
    end_date = '2026-02-28' # 结束日期
    desktop = os.path.join(os.path.expanduser('~'),'Desktop')
    file_folder = desktop  # 下载文件夹路径
    # select_date.select_date(web_page,web_page.find_by_xpath('//div[@role="dialog"][@id="a-popover-4"]'),'2025-09-21','2025-09-21')
    file_name = ""  # 下载文件名
    file_path = download_order_report(web_page, report_type, event_date, start_date, end_date, file_folder, file_name)
    print(file_path)
    # web_page.find_by_xpath('//select[@name="eventDate-allOrdersReport"]').click()
    exit()


def main(args):
    # 测试代码入口
    test_download_order_report()

    # 业务代码入口
    web_page = args.get('web_page')
    report_type = args.get('report_type') # 报告类型
    event_date = args.get('event_date') # 事件日期
    start_date = args.get('start_date') # 开始日期
    end_date = args.get('end_date') # 结束日期
    file_folder = args.get('file_folder')  # 下载文件夹路径
    file_name = args.get('file_name')  # 下载文件名

    file_path = download_order_report(web_page, report_type, event_date, start_date, end_date, file_folder, file_name)
    args['file_path'] = file_path