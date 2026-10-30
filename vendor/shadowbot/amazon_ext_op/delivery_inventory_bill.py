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
from ._amazon_api import switch_site
import time
from datetime import datetime
from .activities_utils import download_handler
from .create_element import create_selector,create_selector_shadow

LOCATION_TYPE_MAP = {
    "国家/地区":"COUNTRY",
    "亚马逊运营中心":"FC"
}

ORDER_OPTION_MAP = {
    "每天": "DAILY",
    "每周": "WEEKLY",
    "每月": "MONTHLY"
}

# 详细视图中「事件类型」下拉选项 value 映射（与一览视图中按时段汇总报告对应）
EVENT_TYPE_MAP = {
    "任何状况": "ANY",
    "盘点": "Adjustments",
    "买家退货": "CustomerReturns",
    "接收": "Receipts",
    "货件": "Shipments",
    "供应商退货": "VendorReturns",
    "库房转移": "WhseTransfers",
}
class Xpath:
    # 下载链接导航
    DownloadLinkNav = "//*[@id='root']//a[@id='reportpage_download_tab']"
    # 请求下载.csv文件按钮
    RequestCsvBtn = "//*[@id='root']//kat-button[@class='download-report-page-kat-button-primary']"
    # 请求.txt下载按钮
    RequestTxtBtn = "//*[@id='root']//kat-button[@class='download-report-page-kat-button-secondary']"
    # 事件日期
    ReportDate = create_selector('//div/div/div/*[local-name()="kat-dropdown"]/xbotShadowRoot//div[@class="select-header"]',name ='事件日期')
    # 确切日期
    ExactDate = create_selector('//div/div/div/*[local-name()="kat-dropdown"]/xbotShadowRoot//kat-option[@value="-1"]',name='确切日期')
    # 报告状态项
    ReportStatus = "(((//kat-table[@role='table']//kat-table-row)[2])//kat-table-cell)[last()]"
    # 下载报告按钮
    DownloadButton = "(((//kat-table[@role='table']//kat-table-row)[2])//kat-table-cell)[last()]/kat-button"
    # 报告类型：一览视图（按时段汇总）
    ReportClass = '//*[local-name()="kat-radiobutton"][1][@name="report-view-options-radio"]'
    # 报告类型：详细视图
    DetailView = '//*[local-name()="kat-radiobutton"][2][@name="report-view-options-radio"]'
    # 一览视图 - 按时段汇总报告下拉
    SumReport = create_selector('//*[local-name()="kat-box"]/div/div/*[local-name()="kat-dropdown"]/xbotShadowRoot//div[@class="select-header"]', name='汇总报告')
    # 详细视图 - 事件类型下拉
    EventTypeDropdown = create_selector('//*[local-name()="kat-box"]/div/div/*[local-name()="kat-dropdown"]/xbotShadowRoot//div[@class="select-header"]', name='事件类型')
    #按位置汇总报告


    StartDate = create_selector('//*[local-name()="kat-date-range-picker"]/xbotShadowRoot/*[local-name()="kat-date-picker"][@class="start"]/xbotShadowRoot//*[@class = "input"]',name = '开始日期')
    EndDate = create_selector('//*[local-name()="kat-date-range-picker"]/xbotShadowRoot/*[local-name()="kat-date-picker"][@class="end"]/xbotShadowRoot//*[@class = "input"]',name='结束日期')


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


def set_filter_params(web_page: WebBrowser, file_type: str, location_report: str, start_date, end_date,
                      report_view: str = "一览", sum_report: str = "每天", event_type: str = None):
    # 设置报告参数
    web_page.find_by_xpath(Xpath.DownloadLinkNav).click()
    # 点击报告类型：一览 或 详细
    if report_view == "详细":
        web_page.find_by_xpath(Xpath.DetailView).click()
    else:
        web_page.find_by_xpath(Xpath.ReportClass).click()
    
    # 一览：先选位置，再选按时间段汇总（仅支持每日，默认每天）；详细：选择事件类型
    if report_view == "详细":
        if event_type:
            try:
                value_to_select = EVENT_TYPE_MAP[event_type]
                web_page.find(Xpath.EventTypeDropdown).click()
                sleep(0.5)
                full_shadow_path = f'//*[local-name()="kat-box"]/div/div/*[local-name()="kat-dropdown"]/xbotShadowRoot//*[local-name()="kat-option"][@value="{value_to_select}"]/xbotShadowRoot/div[@class="content-wrapper"]'
                option_selector = create_selector(full_shadow_path, name=event_type)
                web_page.find(option_selector).click()
            except KeyError:
                raise KeyError(f"映射失败: 事件类型 '{event_type}' 在 EVENT_TYPE_MAP 中不存在。")
            except Exception as e:
                raise Exception(f"选择事件类型 '{event_type}' 时失败: {e}")
    else:
        # 一览视图：位置仅在此视图中有，选完位置再选按时间段汇总（默认每天）
        location_to_select = LOCATION_TYPE_MAP[location_report]
        web_page.find_by_xpath(f'//*[local-name()="kat-radiobutton"][@name="location-aggregation-radio"][@value="{location_to_select}"]').click()
        sum_report_val = sum_report or "每天"
        try:
            value_to_select = ORDER_OPTION_MAP[sum_report_val]
            web_page.find(Xpath.SumReport).click()
            sleep(0.5)
            full_shadow_path = f'//*[local-name()="kat-box"]/div/div/*[local-name()="kat-dropdown"]/xbotShadowRoot//*[local-name()="kat-option"][@value="{value_to_select}"]/xbotShadowRoot/div[@class="content-wrapper"]'
            option_selector = create_selector(full_shadow_path, name=sum_report_val)
            web_page.find(option_selector).click()
        except KeyError:
            raise KeyError(f"映射失败: 时间段 '{sum_report_val}' 在 ORDER_OPTION_MAP 中不存在。")
        except Exception as e:
            raise Exception(f"选择时间段 '{sum_report_val}' 时失败: {e}")

    web_page.find(Xpath.ReportDate).click()
    web_page.find(Xpath.ExactDate).click()
    start_date_element = web_page.find(Xpath.StartDate)
    placeholder = start_date_element.get_attribute("placeholder") or ""
    if "MM/DD/YYYY" in placeholder:
        parts = start_date.split("-")
        start_date = f"{parts[1]}/{parts[2]}/{parts[0]}"
        parts = end_date.split("-")
        end_date = f"{parts[1]}/{parts[2]}/{parts[0]}"
    elif "DD/MM/YYYY" in placeholder:
        parts = start_date.split("-")
        start_date = f"{parts[2]}/{parts[1]}/{parts[0]}"
        parts = end_date.split("-")
        end_date = f"{parts[2]}/{parts[1]}/{parts[0]}"
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


def wait_download_report(web_page: WebBrowser, file_folder: str, file_name: str, wait_timeout: int = 300):
    # 等待并下载报告，wait_timeout 为最长等待时间（秒），默认 300s
    start_time = time.time()

    # 判断是否请求失败
    request_report_error_xpath = '//*[@class="request-report-error"]'
    request_report_error = web_page.find_all_by_xpath(request_report_error_xpath, timeout=5)
    if len(request_report_error) > 0:
        xbot.logging.warning('当前报表请求失败，请查看是否达到每日下载次数上限 或 遇到网络波动')
        return "请求失败"

    # 等待报告状态变化
    for retry in range(5):
        if time.time() - start_time >= wait_timeout:
            return "等待超时"
        if web_page.find_by_xpath(Xpath.ReportStatus).get_text() == "进行中":
            break
        sleep(2)
    # 等待报告生成
    for retry in range(50):
        if time.time() - start_time >= wait_timeout:
            return "等待超时"
        try:
            if web_page.find_by_xpath(Xpath.ReportStatus).get_text() == "无可用数据":
                return "无可用数据"
            web_page.find_by_xpath(Xpath.DownloadButton, timeout=2).click()
            break
        except Exception:
            web_page.find_by_xpath(Xpath.DownloadLinkNav).click()
            sleep(3)
    if time.time() - start_time >= wait_timeout:
        return "等待超时"
    file_path = download_handler(web_page, file_folder, file_name)
    return file_path


def return_processing_report(web_page: WebBrowser, file_folder: str, file_name: str, file_type: str,
                             location_report: str, start_date, end_date,
                             report_view: str = "一览", sum_report: str = "每天", event_type: str = None,
                             wait_timeout: int = 300):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page,file_type)

    # 进入亚马逊配送货件
    domain = get_domain(web_page)
    url = f"{domain}/reportcentral/LEDGER_REPORT/1"
    to_reports_page_if_need(web_page, url)
    
    web_page.wait_load_completed(timeout=30)
    # 设置报告参数（report_view: 一览/详细，详细视图时用 event_type，一览时用 sum_report）
    set_filter_params(web_page, file_type, location_report, start_date, end_date,
                      report_view=report_view, sum_report=sum_report, event_type=event_type)

    # 等待并下载报告
    file_path = wait_download_report(web_page, file_folder, file_name, wait_timeout=wait_timeout)
    return file_path
    


def test_return_processing_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    file_folder = r"D:"  # 下载文件夹路径
    file_name = "111"  # 下载文件名
    file_type = 'csv' # 下载文件类型
    start_date = '2026-01-01'
    end_date ='2026-01-07'
    location_report = "国家/地区"
    report_view = "一览"   # 或 "详细"
    sum_report = "每天"   # 一览时有效，仅支持每日
    event_type = "库房转移"     # 详细时传如 "任何状况"、"盘点" 等
    file_path = return_processing_report(web_page, file_folder, file_name, file_type,
                                         location_report, start_date, end_date,
                                         report_view=report_view, sum_report=sum_report, event_type=event_type)
    print(file_path)
    # web_page.find(Xpath.OrderClass).click()


    exit()


def main(args):
    # 测试代码入口
    test_return_processing_report()

    # 业务代码入口
    web_page = args.get('web_page')
    file_folder = args.get('file_folder')  # 下载文件夹路径
    file_name = args.get('file_name')  # 下载文件名
    file_type = args.get('file_type') # 下载文件类型
    start_date = args.get('start_date')
    end_date = args.get('end_date')    
    location_report = args.get('location_report')  # 按位置
    report_view = args.get('report_view', '一览')   # 一览 / 详细
    sum_report = args.get('sum_report', '每天')    # 一览时按时间段，仅支持每日，默认每天
    event_type = args.get('event_type')            # 详细时事件类型：任何状况/盘点/买家退货等
    wait_timeout = args.get('wait_timeout', 300)   # 等待报告生成的最长时间（秒），默认 300

    file_path = return_processing_report(web_page, file_folder, file_name, file_type,
                                         location_report, start_date, end_date,
                                         report_view=report_view, sum_report=sum_report, event_type=event_type,
                                         wait_timeout=wait_timeout)
    args['file_path'] = file_path
