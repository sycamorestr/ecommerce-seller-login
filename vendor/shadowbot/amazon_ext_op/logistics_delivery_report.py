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
from .activities_utils import get_shadowroot_element
from xbot.web import handle_save_dialog
from .download_utils import find_element_by_text
from xbot.errors import UIAError
from xbot import logging

class Xpath:
    # 下载链接导航
    DownloadLinkNav = "//*[@id='root']//a[@id='reportpage_download_tab']"
    # 事件日期下拉框
    EventDateSelect = "//*[@id='root']//kat-dropdown"
    # 请求下载.csv文件按钮
    RequestCsvBtn = "//*[@id='root']//kat-button[@class='download-report-page-kat-button-primary']"
    # 请求.txt下载按钮
    RequestTxtBtn = "//*[@id='root']//kat-button[@class='download-report-page-kat-button-secondary']"
    # 报告状态项
    ReportStatus = "(((//kat-table[@role='table']//kat-table-row)[2])//kat-table-cell)[last()]"
    # 下载报告按钮
    DownloadButton = "(((//kat-table[@role='table']//kat-table-row)[2])//kat-table-cell)[last()]/kat-button"
    # 日期选择框
    DateSelectFrame = '//*[@id="daily-time-picker-kat-date-range-picker"]'


class Option:
    # 事件日期选项
    EventDateItem = ['前一天（昨天）', '最近3天', '最近7天', '最近14天', '最近30天', '最近90天', '最近180天', '最近365天', '确切日期']
    # 下载文件类型列表
    FileTypeList = ['csv', 'txt']


def transform_date(date: str):
    # 转换日期格式
    try:
        result = datetime.strptime(date, "%Y-%m-%d").strftime("%Y/%m/%d")
        return result
    except Exception as e:
        raise Exception(f"日期格式错误：{date}")


def input_parameter_valid(web_page:WebBrowser, event_date:str, file_type:str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (event_date in Option.EventDateItem), f"事件日期名称错误：{event_date}"
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
            f"进入亚马逊配送报告页面失败，未找到下载链接导航： {Xpath.DownloadLinkNav}"
        )


def set_filter_params(web_page:WebBrowser,event_date:str,start_date:str,end_date:str,file_type:str):
    # 设置报告参数
    # 选择事件日期选项
    web_page.find_by_xpath(Xpath.EventDateSelect).click()
    for option in web_page.find_all(get_shadowroot_element(web_page,"logistics_delivery_report_事件日期选项")):
        option_text = option.get_text().replace(' ', '')
        if option_text == event_date:
            if option_text!='确切日期':
                option.click()
            else:
                option.click()
                web_page.find(get_shadowroot_element(web_page, "logistics_delivery_report_开始日期输入框")).input(transform_date(start_date))
                web_page.find_by_xpath(Xpath.DateSelectFrame).click(anchor=('topCenter',0,-20))
                web_page.find(get_shadowroot_element(web_page, "logistics_delivery_report_结束日期输入框")).input(transform_date(end_date))
                web_page.find_by_xpath(Xpath.DateSelectFrame).click(anchor=('topCenter',0,-20))

    # 点击下载文件类型按钮
    if file_type == 'csv':
        web_page.find_by_xpath(Xpath.RequestCsvBtn).click()
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
            web_page.find_by_xpath(Xpath.DownloadButton, timeout=2).click()
            break
        except:
            # 点击下载链接导航刷新
            web_page.find_by_xpath(Xpath.DownloadLinkNav).click()
            sleep(3)

    # 下载报告
    handle_save_dialog(file_folder=str(file_folder), mode=web_page.product_name, file_name=file_name, wait_complete=False)
    try:
        # 查找下载提示窗口
        window = xbot.win32.get_by_selector("下载提示窗口", timeout=0)
        if window:
            window.activate()  # 激活窗口
            client = window.find("下载提示窗口")  # 查找窗口内元素
            # 查找并点击"确定"按钮
            find_element_by_text(client, "确定").click(
                move_mouse=False, delay_after=0
            )
    except UIAError as e:
        logging.error("confirm_download_save uia error", e)
    except Exception as e:
        logging.error("confirm_download_save error", e)
    return str(file_folder) + '\\' + file_name


def logistics_delivery_report(web_page:WebBrowser, event_date:str,start_date:str,end_date:str, file_folder:str, file_name:str, file_type:str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page, event_date, file_type)

    # 进入亚马逊配送报告页面
    domain = get_domain(web_page)
    url = f"{domain}/reportcentral/INBOUND_PLACEMENT_FEES_CHARGES/1"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置报告参数
    web_page.wait_load_completed(timeout=20)
    sleep(5)
    set_filter_params(web_page,event_date,start_date,end_date,file_type)

    # 等待并下载报告
    file_path = wait_download_report(web_page,file_folder,file_name)
    return file_path
    


def test_logistics_delivery_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="superbrowser")
    event_date = '确切日期' # 事件日期名称
    start_date = '2025-08-01' # 开始日期
    end_date = '2025-08-10' # 结束日期
    file_folder = r"C:\Users\58204\Desktop\配送报告"  # 下载文件夹路径
    file_name = "111"  # 下载文件名
    file_type = 'txt' # 下载文件类型

    file_path = logistics_delivery_report(web_page, event_date,start_date,end_date, file_folder, file_name, file_type)
    print(file_path)
    exit()


def main(args):
    # 测试代码入口
    test_logistics_delivery_report()

    # 业务代码入口
    web_page = args.get('web_page')
    event_date = args.get('event_date') # 事件日期名称
    start_date = args.get('start_date') # 开始日期
    end_date = args.get('end_date') # 结束日期
    file_folder = args.get('file_folder')  # 下载文件夹路径
    file_name = args.get('file_name')  # 下载文件名
    file_type = args.get('file_type') # 下载文件类型

    file_path = logistics_delivery_report(web_page, event_date,start_date,end_date, file_folder, file_name, file_type)
    args['file_path'] = file_path
