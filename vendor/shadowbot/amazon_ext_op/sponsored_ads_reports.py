# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import os

from typing import Optional
import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement
from xbot._core.retry import Retry
from xbot.errors import UIAError

from xbot_extensions.web_action.select_date import select_date

from .utils import get_ad_domain
from .download_utils import download_handler

from datetime import datetime
from pathlib import Path
from ._amazon_api import login

class XPath:
    # 创建报告
    CreateReportBtn = '(//*[@id="application-container"]//button[@data-takt-id="storm-ui-button"])[1]'
    # 报告类别
    # ReportCategory = '//*[@id="report-configuration-form:report-category-control-component-0"]'
    ReportCategory = '//*[@id="report-category"]//button[contains(@id, "report-configuration-form:")]'
    
    # 报告类型
    # ReportType = '//*[@id="report-configuration-form:report-type-control-component-0"]'
    ReportType = '//*[@id="report-type"]//button[contains(@id, "report-configuration-form:")]'
    
    # 国家
    CountryID = '//*[@id="country"]'
    Country = '//*[@id="country"]//button[contains(@data-takt-id, "storm-ui-menu-button")] | //button[contains(@data-takt-id, "marketPlaceIds-multiSelector")]'
    CountryOptions = '//*[@data-takt-id="storm-ui-checkbox"] | //label[contains(@data-takt-id,"storm-ui-report-configuration-form:country-multi-selector")]' # /../..//input'
    CountryLegendOptions = '//legend//*[@data-takt-id="storm-ui-checkbox"]/../..//input'
    ApplyCountryBtn = '//*[@id="report-configuration-form:marketPlaceIds-multiSelector-change-country-button"] | //*[@id="report-configuration-form:country-multi-selector-change-country-button"]'
    # CountryItemCheckBox = '//*[@data-takt-id="storm-ui-checkbox"][text()="{}"]/../..//input'

    # 时间单位: 摘要: summary 每日：day
    TimeUnitItem = '//*[@id="report-configuration-form:time-unit-control-component-0"]//input[@value="{}"]'

    # 报告周期
    ReportPeriod = '//*[@id="report-configuration-form:report-period-control-component-0"]'

    # 下拉框选项
    SelectItem = '//*[@id="portal"]//button[@value="{}"]'
    
    # 日期下拉图标
    DatePickerDown = '//*[@data-takt-id="storm-ui-date-picker-calendar-month-header-calendar-month-header"]//i'

    # 日期选择器
    DatePicker = '//*[@id="portal"]/div[@role="dialog"][1]'

    # 日期选择器确定按钮
    DatePickerSave = '//*[@data-takt-id="storm-ui-date-picker-confirmation-control-save"]'

    # 运行报告按钮
    RunReportBtn = '//*[@id="urc_run_subscription_button"]'

    # 导出失败
    exclamation = '//*[@data-testid="storm-ui-icon-exclamation"]'

    # 报告列表
    DownloadReportBtn = '(//*[@col-id="action"]//a[@data-takt-id="storm-ui-link"])[1]'


def wait_for_element_by_xpath(web_page: WebBrowser, xpath: str, timeout: int = 300):
    try:
        return web_page.find_by_xpath(xpath, timeout=timeout)
    except Exception as e:
        return False


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(url + "/"):
        return
    web_page.navigate(url, load_timeout=300)
    if not wait_for_element_by_xpath(web_page, XPath.CreateReportBtn, timeout=20):
        raise Exception(f"进入报告页面失败，未找到创建报告按钮： {XPath.CreateReportBtn}")


def wait_report_completed(web_page: WebBrowser, timeout: int = 300):
    ''''''
    base_delay = 5  # 初始等待时间（秒）
    max_delay = 30  # 最大等待时间（秒）
    current_delay = base_delay    
    for _ in Retry(timeout):
        try:
            elems = web_page.find_all_by_xpath(XPath.DownloadReportBtn, timeout=1)
            if len(elems) > 0:
                return
            # 使用指数退避增加等待时间
            sleep(current_delay)
            current_delay = min(current_delay * 2, max_delay)            
            web_page.reload()
            login(web_page)
        except UIAError as e:
            pass
    # 最后再检查一次
    elems = web_page.find_all_by_xpath(XPath.DownloadReportBtn, timeout=1)
    if len(elems) > 0:
        return        
    raise Exception(f"等待报告完成超时：{timeout}秒")


def transform_date(date: str):
    """
    转换日期格式
    """
    try:
        result = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        return result
    except Exception as e:
        raise Exception(f"日期格式错误：{date}")
    
def transform_params(report_category: str, report_type: str, time_unit: str, start_date: str, end_date: str, orgins: Optional[list]=None, timeout: int = 300):
    """
    转换报告参数
    """
    report_category_map = {
        "商品推广": "sp",
        "品牌推广": "sb",
        "展示型推广": "sd",
        "Sponsored TV": "st"
    }
    report_type_map = {
        "搜索词": "searchTerms",
        "投放": "keywords",
        "推广的商品": "adProducts",
        "广告活动": "campaigns",
        "预算": "budgets",
        "广告位": "placements",
        "已购买商品": "purchasedProducts",
        "按时间查看效果": "performanceOverTime",
        "搜索词展示量份额": "searchTermsImpressionRank",
        "总流量和无效流量": "grossAndInvalidTraffic",
        "提示词":"prompts",
        "受众":"audience",
        "视频":'videos',

        "关键词": "keywords",
        "关键词广告位": "keywordPlacements",
        "广告活动广告位": "campaignPlacements",
        "品类基准": "peerBenchmark",
        "归因于广告的购买": "attributedPurchases",
        "总流量和无效流量": "grossAndInvalidTraffic",

        "匹配的目标": "matchedTarget",
        "定价透明度": "pricingTransparency"
    }
    time_unit_map = {
        "摘要": "summary",
        "每日": "day",
    }
    if report_category not in report_category_map:
        raise Exception(f"报告类别错误：{report_category}")
    report_category = report_category_map[report_category]
    if report_type not in report_type_map:
        raise Exception(f"报告类型错误：{report_type}")
    need_orgins = ["广告活动", "广告位", "已购买商品", "按时间查看效果", "总流量和无效流量"]
    
    if not orgins:
        orgins = None
    else:
        if isinstance(orgins, str):
            orgins = [orgins]
        if not isinstance(orgins, list):
            raise Exception(f"地区参数错误：{orgins}")
        orgins = list(set(orgins))

    report_type = report_type_map[report_type]
    if time_unit not in time_unit_map:
        raise Exception(f"时间单位错误：{time_unit}")
    time_unit = time_unit_map[time_unit]

    try:
        timeout = int(timeout)
    except Exception as e:
        raise Exception(f"超时时间错误：{timeout}")

    start_date = transform_date(start_date)
    end_date = transform_date(end_date)
    
    return report_category, report_type, time_unit, start_date, end_date, orgins, timeout

def set_report_params(web_page: WebBrowser, report_category: str, report_type: str, time_unit: str, start_date: str, end_date: str, orgins: Optional[list]=None, file_name=None):
    """
    设置报告参数
    """
    # 点击创建报告按钮
    web_page.find_by_xpath(XPath.CreateReportBtn).click(simulative=False)
    
    # 选择报告类别
    web_page.find_by_xpath(XPath.ReportCategory).click(simulative=False)
    web_page.find_by_xpath(XPath.SelectItem.format(report_category)).click(simulative=False)

    # 选择报告类型
    web_page.find_by_xpath(XPath.ReportType).click(simulative=False)
    web_page.find_by_xpath(XPath.SelectItem.format(report_type)).click(simulative=False)

    # 选择地区
    if orgins is not None:
        web_page.find_by_xpath(XPath.CountryID)
        if wait_for_element_by_xpath(web_page, XPath.Country, 2):
            web_page.find_by_xpath(XPath.Country).click(simulative=False)

            # 支持全选
            if "全选" in orgins:
                query_all_xpath = '//button[text()="全选" or text()="Select all"]'
                web_page.find_by_xpath(query_all_xpath ).click(simulative=False)
            
            else:
                for option in web_page.find_all_by_xpath(XPath.CountryOptions):
                    option.find_by_xpath("./../..//input").check(mode="uncheck", delay_after=0)

                # 调整取消权限的逻辑
                query_all_xpath = '//button[text()="全选" or text()="Select all"]'
                web_page.find_by_xpath(query_all_xpath ).click(simulative=False)
                cancel_query_all_xpath = '//button[text()="取消全选" or text()="Deselect all"]'
                web_page.find_by_xpath(cancel_query_all_xpath ).click(simulative=False)

                for option in web_page.find_all_by_xpath(XPath.CountryOptions):
                    if option.get_text() in orgins:
                        # checked = option.find_by_xpath("./../..//input").get_attribute("checked")
                        option.find_by_xpath("./../..//input").check(mode="check", delay_after=0)
                        orgins.remove(option.get_text())
                
                if len(orgins) > 0:
                    raise Exception(f"未找到地区：{'、'.join(orgins)}")
            ApplyCountryBtn = XPath.ApplyCountryBtn
            web_page.find_by_xpath(ApplyCountryBtn).click(simulative=False)

        # 兼容新版
        conuntry_options_xpath = '(//input[contains(@id, "report-configuration-form:inline-country-multi-selector")])[1]'
        if wait_for_element_by_xpath(web_page, conuntry_options_xpath, 2):
            conuntry_options_xpath = '//label[contains(@data-takt-id,"storm-ui-report-configuration-form:inline-country-multi-selecto")]'
            for option in web_page.find_all_by_xpath(conuntry_options_xpath):
                option.find_by_xpath("./../..//input").check(mode="uncheck", delay_after=0.5)

            country_options_label_xpath = '//label[contains(@data-takt-id,"storm-ui-report-configuration-form:inline-country-multi-selecto")]'
            for option in web_page.find_all_by_xpath(country_options_label_xpath):
                if option.get_text() in orgins:
                    # checked = option.find_by_xpath("./../..//input").get_attribute("checked")
                    option.find_by_xpath("./../..//input").check(mode="check", delay_after=0)
                    orgins.remove(option.get_text())

    if report_type != "pricingTransparency":
        # 选择时间单位
        web_page.find_by_xpath(XPath.TimeUnitItem.format(time_unit)).click(simulative=False)

    # 选择报告周期
    web_page.find_by_xpath(XPath.ReportPeriod).click(simulative=False)
    for elem in web_page.find_all_by_xpath(XPath.DatePickerDown):
        elem.execute_javascript('''(elem) => {elem.remove()}''')
    web_page.find_by_xpath(XPath.DatePickerSave).hover()
    date_picker = web_page.find_by_xpath(XPath.DatePicker)
    select_date(web_page, date_picker, start_date, end_date, simulative=True)
    web_page.find_by_xpath(XPath.DatePickerSave).click(simulative=False)    

    # 填写报告名称
    if file_name and len( web_page.find_all_by_xpath('//input[@id="report-settings-card-report-name-input"]')) > 0:
        file_name, _ = os.path.splitext(file_name)
        
        web_page.find_by_xpath('//input[@id="report-settings-card-report-name-input"]').input(file_name)

def test_run():
    if "xbot_extensions" in __file__:
        return
    web_page = xbot.web.get_active(mode="superbrowser")
    report_category = "品牌推广"
    report_type = "搜索词"
    orgins = ["加拿大","美国"]
    time_unit = "摘要"
    start_date = "2025-10-01"
    end_date = "2025-12-08"
    file_folder = r"D:"
    file_name = "adtest.xlsx"
    timeout = "300"
    is_download = False
    params = transform_params(report_category, report_type, time_unit, start_date, end_date, orgins, timeout)
    report_category, report_type, time_unit, start_date, end_date, orgins, timeout = params

    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)
    if "." not in file_name:
        raise Exception(f"文件名错误, 请写上扩展名")

    # 进入报告页面
    domain = get_ad_domain(web_page)
    url = "/reports"
    to_reports_page_if_need(web_page, f"{domain}{url}")

    # 设置报告参数
    set_report_params(web_page, report_category, report_type, time_unit, start_date, end_date, orgins, file_name)

    # # 点击运行报告按钮
    # web_page.find_by_xpath(XPath.RunReportBtn).click(simulative=False)

    # # 根据 is_download 参数决定是否等待和下载
    # if is_download:
    #     # 等待报告完成
    #     wait_report_completed(web_page, timeout=timeout)
    #     # 下载报告
    #     file_path = download_handler(web_page, web_page.find_by_xpath(XPath.DownloadReportBtn), str(file_folder), file_name, timeout, dialog_timeout=20)
    #     print(f"报告下载完成: {file_path}")
    # else:
    #     print("报告已创建，跳过等待和下载步骤")
    #     sleep(2)  # 等待一下确保报告创建请求已发送
    exit()
    
def main(args):
    # test_run()
    web_page = args.get("web_page")
    report_category = args.get("report_category")
    report_type = args.get("report_type")
    orgins = args.get("orgins")
    time_unit = args.get("time_unit")
    start_date = args.get("start_date")
    end_date = args.get("end_date")
    file_folder = args.get("file_folder")
    file_name = args.get("file_name")
    timeout = args.get("timeout")
    is_download = args.get("是否等待下载", True)  # 默认为True，保持向后兼容
    # 处理布尔值转换（可能是字符串 "True"/"False"）
    if isinstance(is_download, str):
        is_download = is_download.lower() in ('true', '1', 'yes', '是')
    elif is_download is None:
        is_download = True  # 默认值
    
    params = transform_params(report_category, report_type, time_unit, start_date, end_date, orgins, timeout)
    report_category, report_type, time_unit, start_date, end_date, orgins, timeout = params

    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)
    if "." not in file_name:
        raise Exception(f"文件名错误, 请写上扩展名")


    for i in range(3):
        # 进入报告页面
        domain = get_ad_domain(web_page)
        url = "/reports"
        to_reports_page_if_need(web_page, f"{domain}{url}")

        # 设置报告参数
        set_report_params(web_page, report_category, report_type, time_unit, start_date, end_date, orgins, file_name)

        # 点击运行报告按钮
        web_page.find_by_xpath(XPath.RunReportBtn).click(simulative=False)

        # 判断是否出现了感叹号
        exclama = web_page.find_all_by_xpath(XPath.exclamation, timeout=5)
        if len(exclama) > 0:
            sleep(10)
            if i == 2:
                raise Exception('报告创建失败，青稍后再试')
            continue

        # 根据 is_download 参数决定是否等待和下载
        if is_download:
            # 等待报告完成
            wait_report_completed(web_page, timeout=timeout)
            # 下载报告
            file_path = download_handler(web_page, web_page.find_by_xpath(XPath.DownloadReportBtn), str(file_folder), file_name, timeout, dialog_timeout=20)
            args['file_path'] = file_path
        else:
            # 只创建报告，不等待和下载
            print("报告已创建，跳过等待和下载步骤")
            sleep(2)  # 等待一下确保报告创建请求已发送
            args['file_path'] = None  # 未下载，返回None
        break

