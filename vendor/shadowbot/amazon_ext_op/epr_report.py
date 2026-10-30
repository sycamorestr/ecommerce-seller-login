# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from pathlib import Path
from .utils import get_domain
from .utils import handler_container
from ._amazon_api import switch_site
from .activities_utils import download_handler
from .create_element import create_selector

# --- 1. 定义所有需要用到的 XPath 路径 ---
class Xpath:
    # 下载链接导航
    DownloadLinkNav = "//*[@id='root']//a[@id='reportpage_download_tab']"
    # 请求下载.csv文件按钮
    RequestCsvBtn = "//*[@id='root']//kat-button[@class='download-report-page-kat-button-primary']"
    # 请求.txt下载按钮
    RequestTxtBtn = "//*[@id='root']//kat-button[@class='download-report-page-kat-button-secondary']"
    # 报告类型（动态，需要格式化）
    ReportTypeRadio = "(//input[@type='radio' and @name='report-view-options-radio'])[{report_type}]"
    # 事件年份下拉框触发器
    YearDropdownTrigger = create_selector('//div[1]/*[local-name()="kat-dropdown"]/xbotShadowRoot//div[@class="select-header"]', name='事件年份下拉框')
    # 事件时间段下拉框触发器（仅季度和月）
    TimePeriodDropdownTrigger = create_selector('//div[2]/*[local-name()="kat-dropdown"]/xbotShadowRoot//div[@class="select-header"]', name='事件时间段下拉框')
    # 报告状态项
    ReportStatus = "(((//kat-table[@role='table']//kat-table-row)[2])//kat-table-cell)[last()]"
    # 下载报告按钮
    DownloadButton = "(((//kat-table[@role='table']//kat-table-row)[2])//kat-table-cell)[last()]/kat-button"


def convert_to_int(value, param_name="参数"):
    """
    将值转换为整数
    支持整数或字符串数字（如 "1", "2", "3"）
    """
    if value is None:
        return None
    
    if isinstance(value, int):
        return value
    
    if isinstance(value, str):
        value = value.strip()
        if value.isdigit():
            return int(value)
        else:
            raise ValueError(f"{param_name}必须是数字（整数或字符串数字），当前值: {value}")
    
    raise TypeError(f"{param_name}类型错误，期望 int 或 str，当前类型: {type(value)}")


def convert_time_period_index(time_period_index):
    """
    将时间段索引转换为整数
    支持整数或字符串数字（如 "1", "2", "3"）
    """
    return convert_to_int(time_period_index, "时间段索引")


def input_parameter_valid(web_page: WebBrowser, report_type: int, file_type: str, target_year: str, time_period_index: int = None):
    """
    输入参数校验
    """
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert report_type in [1, 2, 3], f"报告类型必须是 1(季度)、2(月) 或 3(年)，当前值: {report_type}"
    assert file_type in ['csv', 'txt'], f"不支持下载文件类型：{file_type}"
    assert isinstance(target_year, str) and target_year.isdigit(), f"事件年份必须是数字字符串，当前值: {target_year}"
    if report_type in [1, 2]:  # 季度和月需要时间段索引
        assert time_period_index is not None and isinstance(time_period_index, int) and time_period_index > 0, \
            f"季度和月报告类型需要提供有效的时间段索引（正整数），当前值: {time_period_index}"


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    """
    如果当前页面已经是目标报告页面（且不是子页面），直接返回
    否则导航到目标URL
    """
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)


def set_filter_params(web_page: WebBrowser, report_type: int, target_year: str, time_period_index: int = None, file_type: str = 'csv'):
    """
    设置报告参数
    report_type: 1=季度, 2=月, 3=年
    target_year: 事件年份（字符串，如 "2024"）
    time_period_index: 事件时间段索引（仅季度和月需要，整数）
    file_type: 文件类型（'csv' 或 'txt'）
    """
    # 步骤1：点击下载链接导航
    web_page.find_by_xpath(Xpath.DownloadLinkNav).click()
    sleep(1)
    
    # 步骤2：选择报告类型
    report_type_xpath = Xpath.ReportTypeRadio.format(report_type=report_type)
    web_page.find_by_xpath(report_type_xpath).click()
    sleep(0.5)
    print(f"已选择报告类型: {'季度' if report_type == 1 else '月' if report_type == 2 else '年'}")
    
    # 步骤3：选择事件年份
    # 点击年份下拉框触发器
    web_page.find(Xpath.YearDropdownTrigger).click()
    sleep(0.5)
    
    # 选择年份选项
    year_option_xpath = f'//div[1]/*[local-name()="kat-dropdown"]/xbotShadowRoot//*[local-name()="kat-option" and @value="{target_year}"]'
    year_option_selector = create_selector(year_option_xpath, name=f'年份选项-{target_year}')
    web_page.find(year_option_selector).click()
    sleep(0.5)
    print(f"已选择事件年份: {target_year}")
    
    # 步骤4：选择事件时间段（仅季度和月需要）
    if report_type in [1, 2]:  # 季度或月
        if time_period_index is None:
            raise ValueError(f"报告类型为{'季度' if report_type == 1 else '月'}时，必须提供时间段索引")
        
        # 点击时间段下拉框触发器
        web_page.find(Xpath.TimePeriodDropdownTrigger).click()
        sleep(0.5)
        
        # 选择时间段选项（使用索引）
        time_period_option_xpath = f'//div[2]/*[local-name()="kat-dropdown"]/xbotShadowRoot//*[local-name()="kat-option"][{time_period_index}]'
        time_period_option_selector = create_selector(time_period_option_xpath, name=f'时间段选项-索引{time_period_index}')
        web_page.find(time_period_option_selector).click()
        sleep(0.5)
        print(f"已选择事件时间段索引: {time_period_index}")
    
    web_page.find('亚马逊配送报告').click()
    # 步骤5：点击下载按钮
    if file_type == 'csv':
        web_page.find_by_xpath(Xpath.RequestCsvBtn).click()
        print("已点击 CSV 下载按钮")
    elif file_type == 'txt':
        web_page.find_by_xpath(Xpath.RequestTxtBtn).click()
        print("已点击 TXT 下载按钮")


def wait_download_report(web_page: WebBrowser, file_folder: str, file_name: str):
    """
    等待并下载报告
    """
    # 判断是否请求失败
    request_report_error_xpath = '//*[@class="request-report-error"]'
    request_report_error = web_page.find_all_by_xpath(request_report_error_xpath, timeout=5)
    if len(request_report_error) > 0:
        xbot.logging.warning('当前报表请求失败，请查看是否达到每日下载次数上限 或 遇到网络波动')
        return "请求失败"
    # 等待报告状态变化
    for retry in range(5):
        try:
            status_text = web_page.find_by_xpath(Xpath.ReportStatus, timeout=2).get_text()
            if status_text == "进行中":
                break
        except:
            pass
        sleep(2)
    
    # 等待报告生成
    for retry in range(50):
        try:
            # 判断有无报表可以下载
            status_text = web_page.find_by_xpath(Xpath.ReportStatus, timeout=2).get_text()
            
            # 如果报告状态是"已取消"或"无可用数据"，抛出异常
            if status_text == "已取消":
                raise Exception("报告状态为'已取消'，无法下载报告")
            
            if status_text == "无可用数据":
                raise Exception("报告状态为'无可用数据'，无法下载报告")
            
            # 尝试找下载按钮
            web_page.find_by_xpath(Xpath.DownloadButton, timeout=2).click()
            print("已找到并点击下载按钮")
            break
        except Exception as e:
            # 如果是状态异常（已取消或无可用数据），直接抛出
            if "已取消" in str(e) or "无可用数据" in str(e):
                raise
            # 其他异常（如找不到元素），点击下载链接导航刷新
            web_page.find_by_xpath(Xpath.DownloadLinkNav).click()
            sleep(3)
    
    # 下载报告
    file_path = download_handler(web_page, file_folder, file_name)
    return file_path


def return_epr_report(web_page: WebBrowser, file_folder: str, file_name: str, report_type, target_year: str, time_period_index=None, file_type: str = 'csv'):
    """
    下载生产者责任延申报告的主流程函数
    
    参数:
    - web_page: WebBrowser 实例
    - file_folder: 下载文件夹路径
    - file_name: 下载文件名
    - report_type: 报告类型（1=季度, 2=月, 3=年，可以是整数或字符串数字，如 1 或 "1"）
    - target_year: 事件年份（字符串，如 "2024"）
    - time_period_index: 事件时间段索引（仅季度和月需要，可以是整数或字符串数字，如 1 或 "1"）
    - file_type: 文件类型（'csv' 或 'txt'）
    """
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)
    
    # 转换报告类型（支持字符串数字）
    report_type = convert_to_int(report_type, "报告类型")
    
    # 转换时间段索引（支持字符串数字）
    if time_period_index is not None:
        time_period_index = convert_time_period_index(time_period_index)
    
    # 输入参数校验
    input_parameter_valid(web_page, report_type, file_type, target_year, time_period_index)
    
    # 进入 EPR 报告页面
    domain = get_domain(web_page)
    url = f"{domain}/reportcentral/EPR_REPORT/1"
    to_reports_page_if_need(web_page, url)
    
    web_page.wait_load_completed(timeout=30)
    sleep(2)
    
    # 设置报告参数
    set_filter_params(web_page, report_type, target_year, time_period_index, file_type)
    
    # 等待并下载报告
    file_path = wait_download_report(web_page, file_folder, file_name)
    return file_path


def test_return_epr_report():
    """
    测试函数
    """
    if "xbot_extensions" in __file__:
        return
    
    print("--- 开始测试 EPR 报告下载 ---")
    web_page = xbot.web.get_active(mode="superbrowser")
    file_folder = r"D:"  # 下载文件夹路径
    file_name = "epr_report_test"  # 下载文件名
    report_type = "2"  # 1=季度, 2=月, 3=年
    target_year = "2024"  # 事件年份
    time_period_index = "12"  # 时间段索引（仅季度和月需要）
    file_type = 'csv'  # 文件类型
    
    file_path = return_epr_report(
        web_page, 
        file_folder, 
        file_name, 
        report_type, 
        target_year, 
        time_period_index, 
        file_type
    )
    print(f"下载完成，文件路径: {file_path}")
    exit()


def main(args):
    """
    主入口函数
    """
    # 测试代码入口
    test_return_epr_report()
    
    # 业务代码入口
    web_page = args.get('web_page')
    file_folder = args.get('file_folder')  # 下载文件夹路径
    file_name = args.get('file_name')  # 下载文件名
    report_type = args.get('report_type')  # 报告类型（1=季度, 2=月, 3=年）
    target_year = args.get('target_year')  # 事件年份
    time_period_index = args.get('time_period_index')  # 事件时间段索引（仅季度和月需要）
    file_type = args.get('file_type', 'csv')  # 文件类型，默认为 csv
    
    file_path = return_epr_report(
        web_page, 
        file_folder, 
        file_name, 
        report_type, 
        target_year, 
        time_period_index, 
        file_type
    )
    args['file_path'] = file_path

