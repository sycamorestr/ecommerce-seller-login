# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot  # type: ignore
import re  # type: ignore
import threading

from xbot import print, sleep  # type: ignore
from xbot import logging  # type: ignore
from xbot.selector import Selector  # type: ignore
from xbot.web import WebBrowser, WebElement  # type: ignore
from xbot.errors import UIAError  # type: ignore
from xbot._core.retry import Retry  # type: ignore

from .package import variables as glv  # type: ignore
from .utils import get_domain
from .utils import handler_container, handler_feedback
from .download_utils import find_element_by_text, download_handler

from datetime import datetime
from typing import Union
from dateutil.relativedelta import relativedelta
from pathlib import Path
from xbot_extensions.web_action.select_date import select_date
from ._amazon_api import switch_language
from .payments_past_settlements import get_shadowroot_element


class XPath:
    # 商城
    ShoppingCentre = '//*[@data-testid="marketplace-dropdown"]'
    # 商城选项
    SC_SelectItem = '//*[@data-testid="marketplace-dropdown"]//kat-option'
    # 数据汇总级别
    DataLevel = '//*[@data-testid="data-aggregation-dropdown"]'
    # 日期范围
    DateRange = '//*[@data-testid="daterange-dropdown"]'
    # 选择年份
    SelectedYear = '//*[@class="select-year-dropdown dateRange-component"]'
    # 选择年份选项
    SY_SelectItem = '//*[@class="select-year-dropdown dateRange-component"]/kat-option'
    # 选择月份
    SelectedMonth = '//*[@class="select-month-dropdown dateRange-component"]'
    # 选择月份选项
    SM_SelectItem = '//*[@class="select-month-dropdown dateRange-component"]/kat-option'
    # 选择季度
    SelectedQuarter = '//*[@class="select-quarter-dropdown dateRange-component"]'
    # 选择季度选项
    SQ_SelectItem = '//*[@class="select-quarter-dropdown dateRange-component"]/kat-option'
    # 自定义日期范围-开始日期
    StartDateRange = '(//kat-date-picker[@class="dateRange-component"])[1]'
    # 自定义日期范围-结束日期
    EndDateRange = '(//kat-date-picker[@class="dateRange-component"])[2]'
    # 简化的报告配置选项
    ReportConfiguration = '//*[@id="root"]//kat-checkbox'
    # 生成报告按钮
    GenerateReport = '//*[@data-testid="generate-report-button"]'
    # 报告生成日期
    GenerateDate = '(//kat-table-row[@class="report-record-row"]//kat-table-cell)[2]'
    # 报告生成状态
    ReportState = '(//kat-table-row[@class="report-record-row"]//kat-table-cell)[3]'
    # 下载报告按钮
    DownloadReport = '(//*[@role="table"]//kat-button)[1]'


def gen_selector(xpath):
    xpaths = xpath.split(">>")
    data = {
        "id": "xbot-xpath",
        "name": "动态元素",
        "type": "simple",
        "xpath": {"enable": "true", "segments": xpaths},
    }
    selector = Selector(data)
    return selector


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)
    handler_feedback(web_page)

    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(XPath.GenerateReport), timeout=30):
        raise Exception(
            f"进入报告页面失败，未找到生成报告按钮： {XPath.GenerateReport}"
        )


def wait_for_element_by_xpath(web_page: WebBrowser, xpath: str, timeout: int = 300):
    try:
        return web_page.find_by_xpath(xpath, timeout=timeout)
    except Exception as e:
        return False


def convert_date_format(date:str):
    # 转换日期格式
    try:
        result = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        return result
    except Exception as e:
        raise Exception(f"日期格式错误：{date}")


def set_report_params(
    web_page: WebBrowser,
    date: str,  # 日期范围
    report_configuration: list,  # 简化报告配置列表
    shopping_names: list, # 商城列表
    data_level: str # 数据汇总级别
):
    """设置报告参数"""
    # 获取当前已生成报告的最新生成日期
    if not wait_for_element_by_xpath(web_page, XPath.GenerateDate, timeout=5):
        date_flag = ''
    else:
        date_flag = web_page.find_by_xpath(XPath.GenerateDate).get_text()
    shopping_names_map = {
        '美国':'US',
        '加拿大':'CA',
        '墨西哥':'MX',
        '英国':'GB',
        '德国':'DE',
        '法国':'FR',
        '意大利':'IT',
        '西班牙':'ES',
        '日本':'JP',
        '澳大利亚':'AU',
        '比利时':'BE',
        '瑞典':'SE',
        '波兰':'PL',
        '荷兰':'NL',
        '阿拉伯联合酋长国':'AE',
        '土耳其':'TR',
        '巴西':'BR',
        '沙特阿拉伯':'SA',
        '新加坡共和国':'SG',
        '印度':'IN',
        '爱尔兰':'IE'
    }
    # TODO: 判断是否全选, 取消勾选全选, 然后选择目标
    # 点击商城按钮, 选择MSKU对应的城市
    web_page.find_by_xpath(XPath.ShoppingCentre).click()
    for option in web_page.find_all_by_xpath(XPath.SC_SelectItem):
        if option.get_attribute('aria-selected') == 'true':
            option.click()
    for option in web_page.find_all_by_xpath(XPath.SC_SelectItem):
        if option.get_text() in [shopping_names_map[name] for name in shopping_names]:
            option.click()
    
    # 选择数据汇总级别
    web_page.find_by_xpath(XPath.DataLevel).click()
    for option in web_page.find_all(get_shadowroot_element(web_page,"sku_cost_report_数据汇总级别选项")):
        if option.get_text() == data_level:
            option.click()

    # 选择日期范围, 根据不同的日期格式解析
    # 月份格式正则：YYYY-MM（MM范围01-12）
    month_pattern = r'^\d{4}-(0[1-9]|1[0-2])$'
    # 季度格式正则：YYYY-QN（N范围1-4）
    quarter_pattern = r'^\d{4}-Q[1-4]$'
    # 年份格式正则
    year_pattern = r'^\d{4}$'
    # 自定义日期范围正则
    customize_pattern = r'(?P<start>\d{4}[-]\d{2}[-]\d{2})~(?P<end>\d{4}[-]\d{2}[-]\d{2})'
    if date == "过去7天":
        web_page.find_by_xpath(XPath.DateRange).click()
        for option in web_page.find_all(get_shadowroot_element(web_page,"sku_cost_report_日期范围选项")):
            if option.get_text() == '过去 7 天':
                option.click()

    elif date == "过去30天":
        web_page.find_by_xpath(XPath.DateRange).click()
        for option in web_page.find_all(get_shadowroot_element(web_page,"sku_cost_report_日期范围选项")):
            if option.get_text() == '过去30天':
                option.click()

    elif re.match(month_pattern, date):
        date_year, date_month = date.split('-')
        month_map = {
            '01': '一月', '02': '二月', '03': '三月', '04': '四月',
            '05': '五月', '06': '六月', '07': '七月', '08': '八月',
            '09': '九月', '10': '十月', '11': '十一月', '12': '十二月'
        }
        date_month = month_map[date_month]
        web_page.find_by_xpath(XPath.DateRange).click()
        for option in web_page.find_all(get_shadowroot_element(web_page,"sku_cost_report_日期范围选项")):
            if option.get_text() == '按月份选择':
                option.click()
        # print(web_page.find_by_xpath(XPath.DateRange).get_attribute('options'))
        # web_page.find_by_xpath(XPath.DateRange).set_attribute('value', date_range)
        # 选择年份
        web_page.find_by_xpath(XPath.SelectedYear).click()
        # 设置年份
        for option in web_page.find_all_by_xpath(XPath.SY_SelectItem):
            # print(option.get_text())
            if option.get_text() == date_year:
                option.click()
        # 选择月份
        web_page.find_by_xpath(XPath.SelectedMonth).click()
        # 设置月份
        for option in web_page.find_all_by_xpath(XPath.SM_SelectItem):
            # print(option.get_text())
            if option.get_text() == date_month:
                option.click()
    elif re.match(quarter_pattern, date):
        date_year, date_quarter = date.split("-")
        web_page.find_by_xpath(XPath.DateRange).click()
        for option in web_page.find_all(get_shadowroot_element(web_page,"sku_cost_report_日期范围选项")):
            if option.get_text() == '按季度选择':
                option.click()
        # 选择年份
        web_page.find_by_xpath(XPath.SelectedYear).click()
        # 设置年份
        for option in web_page.find_all_by_xpath(XPath.SY_SelectItem):
            # print(option.get_text())
            if option.get_text() == date_year:
                option.click()
        # 选择季度
        web_page.find_by_xpath(XPath.SelectedQuarter).click()
        # 设置季度
        for option in web_page.find_all_by_xpath(XPath.SQ_SelectItem):
            # print(option.get_text())
            if option.get_text() == date_quarter:
                option.click()
    elif re.match(year_pattern, date):
        web_page.find_by_xpath(XPath.DateRange).click()
        for option in web_page.find_all(get_shadowroot_element(web_page,"sku_cost_report_日期范围选项")):
            if option.get_text() == '按年份选择':
                option.click()
        # 选择年份
        web_page.find_by_xpath(XPath.SelectedYear).click()
        # 设置年份
        for option in web_page.find_all_by_xpath(XPath.SY_SelectItem):
            # print(option.get_text())
            if option.get_text() == date:
                option.click()
    elif re.match(customize_pattern, date):
        web_page.find_by_xpath(XPath.DateRange).click()
        for option in web_page.find_all(get_shadowroot_element(web_page,"sku_cost_report_日期范围选项")):
            if option.get_text() == '自定义日期范围':
                option.click()
        # TODO: 支持自定义区间
        matchs = re.search(customize_pattern, date)
        start_date = matchs.group("start")
        end_date = matchs.group("end")
        web_page.find(get_shadowroot_element(web_page,"sku_cost_report_开始日期输入框")).input(convert_date_format(start_date))
        web_page.find(get_shadowroot_element(web_page,"sku_cost_report_结束日期输入框")).input(convert_date_format(end_date))
    else:
        raise Exception(f"日期范围错误：{date}")

    # 配置简化报告
    configuration_checks = web_page.find_all_by_xpath(XPath.ReportConfiguration)
    for option in configuration_checks:
        if option.get_attribute('checked') == 'true':
            option.click()
    for option in configuration_checks:
        # print(option.get_attribute("label"))
        if option.get_attribute("label") in report_configuration:
            option.click()
    return date_flag


def wait_report_completed(web_page: WebBrowser,date_flag: str, timeout: int = 300):
    """等待报告生成完成"""
    # 初始等待时间（秒）
    base_delay = 5
    # 最大等待时间（秒）
    max_delay = 30
    # 当前等待时间从初始值开始
    current_delay = base_delay

    # 使用重试机制（在指定超时时间内循环）
    for _ in Retry(timeout):
        try:
            # 1. 尝试查找下载报告按钮和报告生成状态和报告生成日期
            elems = web_page.find_all_by_xpath(XPath.DownloadReport, timeout=1)
            state = web_page.find_by_xpath(XPath.ReportState, timeout=1).get_text()
            dflag = web_page.find_by_xpath(XPath.GenerateDate, timeout=1).get_text()

            # 2. 如果找到按钮并且状态为准备就绪并且是最新生成日期，说明报告已生成
            if len(elems) > 0 and state == "准备就绪" and dflag!=date_flag:
                return state # 成功返回
            elif state == "已完成，无数据":
                return state
            elif state == "已取消":
                return state

            # 3. 使用指数退避策略增加等待时间
            sleep(current_delay)
            current_delay = min(current_delay * 2, max_delay)

            # 4. 刷新页面获取最新状态
            web_page.reload()

        # 5. 忽略UI查找错误（继续重试）
        except UIAError as e:
            pass

    # 6. 超时后最后检查一次
    elems = web_page.find_all_by_xpath(XPath.DownloadReport, timeout=1)
    state = web_page.find_by_xpath(XPath.ReportState, timeout=1).get_text()
    dflag = web_page.find_by_xpath(XPath.GenerateDate, timeout=1).get_text()
    if len(elems) > 0 and state == "准备就绪" and dflag!=date_flag:
        return state # 最后时刻成功
    elif state == "已完成，无数据":
        return state
    elif state == '已取消':
        return state

    # 7. 最终失败抛出异常
    raise Exception(f"等待报告完成超时：{timeout}秒")


def download_sku_cost_report(
    web_page: WebBrowser,
    shopping_names: str,
    data_level: str,
    report_configuration: str,
    file_folder: str = "",
    file_name: str = "",
    date: str = "",
    timeout: str = '300',
) -> str:
    """
    下载SKU成本报告
    :param args: 参数字典，包含以下键：
        - web_page: WebBrowser实例
        - report_configuration: 报告配置选项列表
        - timeout: 等待报告超时时间（秒）
        - file_folder: 下载文件夹路径
        - file_name: 下载文件名
    :return: None
    """

    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert str(timeout).isdigit(), "timeout 必须是整数"
    if data_level == '':
        data_level = 'MSKU'
    data_levels = ['MSKU', '父 ASIN', '子 ASIN']
    if data_level not in data_levels:
        raise Exception(f"数据汇总级别错误：{data_level}")

    # TODO: 对数据进行处理
    timeout = int(timeout)
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)
    if file_name == "":
        file_name = '-'.join([s.strip() for s in shopping_names.split(',')])+'-'+date
    if not isinstance(shopping_names, list):
        shopping_names = re.split(r'\s*,\s*', shopping_names.strip())
    if not isinstance(report_configuration, list):
        report_configuration = re.split(r'\s*,\s*', report_configuration.strip())

    # 进入报告页面
    domain = get_domain(web_page)
    url = f"{domain}/sereport"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置报告参数
    # month_value=get_last_month_cn() 针对这个客户, 是选择上个月, 其他客户需要自定义,
    date_flag = set_report_params(
        web_page=web_page,
        date=date,
        report_configuration=report_configuration,
        shopping_names=shopping_names,
        data_level = data_level
    )
    file_path = ''
    # 点击生成报告按钮
    web_page.find_by_xpath(XPath.GenerateReport).click()

    # 等待报告生成
    state = wait_report_completed(web_page,date_flag, timeout=timeout)

    if state == '准备就绪':
        # 下载报告（需要传入下载按钮元素）
        download_btn = web_page.find_by_xpath(XPath.DownloadReport)
        file_path = download_handler(
            web_page=web_page,
            element=download_btn,
            file_folder=str(file_folder),
            file_name=file_name,
        )
    elif state == '已完成，无数据':
        pass
    elif state == '已取消':
        pass

    return file_path


def test_download_sku_cost_report(web_page:WebBrowser):
    if "xbot_extensions" in __file__:
        return

    web_page = xbot.web.get_active(mode="ziniaobrowser")
    shopping_names = "美国,墨西哥,加拿大" # 商城 多选
    report_configuration = "销售数据,仓储费基础费用和附加费,费用数据,配送基础费用和附加费,广告支出数据,净收入,亚马逊以外的费用" # 报告配置 多选
    timeout = 300  # 等待报告超时时间
    file_folder = r"C:\Users\10577\Desktop"  # 下载文件夹路径
    file_name = "SKU成本报告"  # 下载文件名
    date = "2025-06" # 日期范围
    data_level = 'MSKU' # 数据汇总级别 MSKU/父 ASIN/子 ASIN
    for option in [[web_page, "美国,墨西哥,加拿大", 'MSKU', "销售数据,仓储费基础费用和附加费,费用数据,配送基础费用和附加费,广告支出数据,净收入,亚马逊以外的费用", r"C:\Users\10577\Desktop", "SKU成本报告", '过去7天', 300],
    [web_page, "美国,墨西哥,加拿大", '父 ASIN', "销售数据,仓储费基础费用和附加费,费用数据,配送基础费用和附加费,广告支出数据,净收入,亚马逊以外的费用", r"C:\Users\10577\Desktop", "SKU成本报告", '过去30天', 300],
    [web_page, "美国,墨西哥,加拿大", '子 ASIN', "销售数据,仓储费基础费用和附加费,费用数据,配送基础费用和附加费,广告支出数据,净收入,亚马逊以外的费用", r"C:\Users\10577\Desktop", "SKU成本报告", '2024-06', 300],
    [web_page, "美国,墨西哥,加拿大", 'MSKU', "销售数据,仓储费基础费用和附加费,费用数据,配送基础费用和附加费,广告支出数据,净收入,亚马逊以外的费用", r"C:\Users\10577\Desktop", "SKU成本报告", '2024-Q2', 300],
    [web_page, "美国,墨西哥,加拿大", '父 ASIN', "销售数据,仓储费基础费用和附加费,费用数据,配送基础费用和附加费,广告支出数据,净收入,亚马逊以外的费用", r"C:\Users\10577\Desktop", "SKU成本报告", '2024', 300],
    [web_page, "美国,墨西哥,加拿大", '子 ASIN', "销售数据,仓储费基础费用和附加费,费用数据,配送基础费用和附加费,广告支出数据,净收入,亚马逊以外的费用", r"C:\Users\10577\Desktop", "SKU成本报告", '从2024-04-01到2025-07-15', 300],
    [web_page, "美国,墨西哥,加拿大", 'MSKU', "销售数据,仓储费基础费用和附加费,费用数据,配送基础费用和附加费,广告支出数据,净收入,亚马逊以外的费用", r"C:\Users\10577\Desktop", "SKU成本报告", '过去7天', 300]]:
        download_sku_cost_report(
            web_page=option[0],
            shopping_names=option[1],
            data_level=option[2],
            report_configuration=option[3],
            file_folder=option[4],
            file_name=option[5],
            date=option[6],
            timeout=option[7],
        )
    exit()


def main(args):
    # TODO:
    # 1. 商场应该支持传参, 传参要求 支持列表, 支持 "BR,US"
    # 2. 日期范围支持传参, 过去7天, 过去30天, "2025-05" -> 按月份选择, "2025-05-01~2025-05-10" -> 按自定义日期范围
    # 3. 报表配置支持传参, ["销售数据", "仓储费基础费用和附加费", "费用数据", "配送基础费用和附加费", "广告支出数据", "净收入", "亚马逊以外的费用"], "净收入,亚马逊以外的费用"

    # 测试代码入口
    # test_download_sku_cost_report()

    # 业务代码入口
    web_page = args.get("web_page")
    shopping_names = args.get("shopping_name")
    report_configuration = args.get("report_configuration")
    timeout = args.get("timeout")  # 等待报告超时时间
    file_folder = args.get("file_folder")  # 下载文件夹路径
    file_name = args.get("file_name")  # 下载文件名
    date = args.get("date")  # 日期范围, 如 "2025-05" 或 "过去7天"
    data_level = args.get("data_level") # 数据汇总级别，如MSKU

    file_path = download_sku_cost_report(
        web_page,
        shopping_names,
        data_level,
        report_configuration,
        file_folder,
        file_name,
        date,
        timeout,
    )
    args["file_path"] = file_path
