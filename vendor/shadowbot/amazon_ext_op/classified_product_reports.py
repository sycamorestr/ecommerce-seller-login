# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot  # type: ignore
import re  # type: ignore
from xbot import print, sleep  # type: ignore
from xbot import logging  # type: ignore
from xbot.selector import Selector  # type: ignore
from xbot.web import WebBrowser, WebElement  # type: ignore
from xbot.errors import UIAError  # type: ignore
from xbot._core.retry import Retry  # type: ignore
from .package import variables as glv  # type: ignore
from .utils import get_domain
from .utils import handler_container
from datetime import datetime
from typing import Union
from pathlib import Path
from ._amazon_api import switch_site
from ._amazon_api import switch_language
from .create_element import create_selector
from .activities_utils import download_handler as activities_download_handler


class XPath:
    # 报告类型（包含 Shadow DOM）
    ReportCategory = '//*[local-name()="kat-dropdown"][1]/xbotShadowRoot//div[@class="select-header"]'
    # 类型选项（包含 Shadow DOM）
    CategoryItem = '//*[local-name()="kat-dropdown"][1]/xbotShadowRoot//*[local-name()="kat-option"]'
    # 创建日期（包含 Shadow DOM）
    CreateDate = '//*[local-name()="kat-date-picker"]/xbotShadowRoot//*[local-name()="kat-input"][@type="text"]'
    # 状态筛选（包含 Shadow DOM）
    StateFilter = '//*[local-name()="kat-dropdown"][@class="filter-dropdown"]/xbotShadowRoot//div[@class="kat-select-container"]'
    # 状态选项（包含 Shadow DOM）
    StateItem = '//*[local-name()="kat-dropdown"][@class="filter-dropdown"]/xbotShadowRoot//*[local-name()="kat-option"]'
    # 请求报告
    RequestReportBtn = '//*[@data-testid="request-report-testid"]'
    # 批次编号
    BatchId = '//tbody/tr[1]/td[2]'
    # 报告生成状态（kat-badge 元素，包含 Shadow DOM）
    ReportState = '//tbody/tr[1]/td[3]//kat-badge'
    # 下载报告按钮
    DownloadReport = '//tbody/tr[1]/td[4]//kat-button'
    # 无任何下载报告标识（您尚未请求任何报告。）
    NoReportFlag = '//*[@id="empty-table-no-files-uploaded-report_type"]//span[@class="mt-text-content"]'


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


def validate_date_format(date_str: str) -> str:
    """
    验证日期字符串是否符合 'YYYY-MM-DD' 格式且为有效日期，不符合时抛出异常
    如果日期为空字符串或None，直接返回空字符串
    :param date_str: 待验证的日期字符串（如 "2025-12-30"），可为空字符串或None
    :return: 验证通过的日期字符串（格式不变），如果为空则返回空字符串
    :raises ValueError: 格式错误或日期无效时抛出
    """
    # 如果日期为空，直接返回
    if not date_str or date_str.strip() == '':
        return ''
    
    # 步骤1：正则校验格式（YYYY-MM-DD）
    pattern = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'
    if not re.fullmatch(pattern, date_str):
        raise ValueError(
            f"日期格式错误，需为 'YYYY-MM-DD'（年-月-日，横杠分隔）。当前值：'{date_str}'"
        )
    # 步骤2：校验日期有效性（月份和日期是否真实存在）
    try:
        # 解析时自动校验月份（1-12）和日期（如2月无30日）
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError as e:
        raise ValueError(f"日期无效：{str(e)}。当前值：'{date_str}'") from e


def convert_date_format(date_str: str) -> str:
    """
    将日期字符串从 'YYYY-MM-DD' 格式转换为 'MM/DD/YYYY' 格式
    :param date_str: 日期字符串（如 "2025-12-30"）
    :return: 转换后的日期字符串（如 "12/30/2025"）
    """
    try:
        # 解析 YYYY-MM-DD 格式
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        # 转换为 MM/DD/YYYY 格式
        return date_obj.strftime("%m/%d/%Y")
    except ValueError as e:
        raise ValueError(f"日期转换失败：{str(e)}。当前值：'{date_str}'") from e


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)

        

def wait_for_element_by_xpath(web_page: WebBrowser, xpath: str, timeout: int = 300):
    try:
        return web_page.find_by_xpath(xpath, timeout=timeout)
    except Exception as e:
        return False


def set_report_params(
    web_page: WebBrowser,
    report_category: str,  # 报告类型
    create_date: str,  # 商品创建时间
    state_filter: str # 状态筛选条件
):
    """设置报告参数"""
    # 如果未找到无报告标识，则获取目前批次编号，否则目前批次编号为空
    if not wait_for_element_by_xpath(web_page, XPath.NoReportFlag, timeout=5):
        # 获取目前批次编号
        current_bid = web_page.find_by_xpath(XPath.BatchId).get_text()
    else:
        current_bid = ''
    # 选择报告类型（使用 create_selector 处理 Shadow DOM）
    report_category_selector = create_selector(XPath.ReportCategory, name='报告类型下拉框')
    web_page.find(report_category_selector).click()
    sleep(0.5)  # 等待下拉选项出现
    category_item_selector = create_selector(XPath.CategoryItem, name='报告类型选项')
    for option in web_page.find_all(category_item_selector):
        if option.get_text() == report_category:
            option.click()
            break
    
    if report_category == '分类商品报告':
        # 选择状态筛选条件（使用 create_selector 处理 Shadow DOM）
        state_filter_selector = create_selector(XPath.StateFilter, name='状态筛选下拉框')
        web_page.find(state_filter_selector).click()
        sleep(0.5)  # 等待下拉选项出现
        state_item_selector = create_selector(XPath.StateItem, name='状态筛选选项')
        for option in web_page.find_all(state_item_selector):
            if option.get_text() == state_filter:
                option.click()
                break
        # 选择商品创建日期（使用 create_selector 处理 Shadow DOM）
        # 只有当日期不为空时才输入日期
        if create_date and create_date.strip() != '':
            # 将日期从 YYYY-MM-DD 格式转换为 MM/DD/YYYY 格式
            date_for_input = convert_date_format(create_date)
            create_date_selector = create_selector(XPath.CreateDate, name='创建日期输入框')
            web_page.find(create_date_selector).input(date_for_input)
    return current_bid


def wait_report_completed(web_page: WebBrowser, current_bid: str, timeout: int = 300):
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
            # 1. 尝试查找下载报告按钮和报告生成状态和最新报告批次编号
            elems = web_page.find_all_by_xpath(XPath.DownloadReport, timeout=1)
            # kat-badge 元素需要使用 get_attribute('label') 获取文本
            report_state_selector = create_selector(XPath.ReportState, name='报告状态')
            state = web_page.find(report_state_selector, timeout=1).get_attribute('label')
            new_bid = web_page.find_by_xpath(XPath.BatchId, timeout=1).get_text()

            # 2. 如果找到按钮并且状态为完成，说明报告已生成
            if len(elems) > 0 and state == "完成" and new_bid!=current_bid:
                return state, new_bid # 成功返回

            # 3. 使用指数退避策略增加等待时间
            sleep(current_delay)
            current_delay = min(current_delay * 2, max_delay)

            # 4. 刷新页面获取最新状态
            # web_page.reload()

        # 5. 忽略UI查找错误（继续重试）
        except UIAError as e:
            pass

    # 6. 超时后最后检查一次
    elems = web_page.find_all_by_xpath(XPath.DownloadReport, timeout=1)
    # kat-badge 元素需要使用 get_attribute('label') 获取文本
    report_state_selector = create_selector(XPath.ReportState, name='报告状态')
    state = web_page.find(report_state_selector, timeout=1).get_attribute('label')
    new_bid = web_page.find_by_xpath(XPath.BatchId, timeout=1).get_text()

    if len(elems) > 0 and state == "完成" and new_bid!=current_bid:
        return state, new_bid # 成功返回

    # 7. 最终失败抛出异常
    raise Exception(f"等待报告完成超时：{timeout}秒")




def download_classified_product_report(
    web_page: WebBrowser,
    site_name:str,
    report_category: str,
    create_date: str,
    state_filter: str = "",
    file_folder: str = "",
    file_name: str = "",
    timeout: int = 300,
    is_download: bool = True
) -> str:
    """下载分类商品报告"""
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert str(timeout).isdigit(), "timeout 必须是整数"
    # 验证日期格式（如果日期为空则跳过验证）
    if create_date and create_date.strip() != '':
        create_date = validate_date_format(create_date)
    else:
        create_date = ''  # 确保空日期统一为空字符串
    # 设置默认报告类型
    if report_category == '':
        report_category = '分类商品报告'
    report_category_list = [
        '大批量商品报告',
        '销售佣金折扣报告',
        '库存报告',
        '在售商品报告',
        '每月库存历史记录',
        '卖家自配送可售商品报告精简版',
        '卖家自配送可售商品报告精简升级版',
        '分类商品报告',
        '卖家自配送可售商品报告',
        '非在售商品报告',
        '所有商品报告',
        '已取消的商品报告',
        '已售商品报告',
        '卖家处理出口资格报告',
        '佣金预览报告'
    ]
    if report_category not in report_category_list:
        raise Exception(f"报告类型错误：{report_category}")
    state_filter_list = [
        '全部',
        '在售',
        '不可售',
        '不完整',
        '不可售（缺货）'
    ]
    if state_filter not in state_filter_list:
        raise Exception(f"状态筛选条件错误：{state_filter}")

    # TODO: 对数据进行处理
    timeout = int(timeout)
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 站点切换
    switch_site(web_page, site_name)

    # 进入报告页面
    domain = get_domain(web_page)
    url = f"{domain}/listing/reports"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置报告参数
    current_bid = set_report_params(
        web_page=web_page,
        report_category=report_category,
        create_date=create_date,
        state_filter=state_filter
    )
    file_path = ''

    # 点击请求报告按钮
    web_page.find_by_xpath(XPath.RequestReportBtn, timeout=30).click()

    if is_download == True:
        # 等待报告生成
        state, new_bid = wait_report_completed(web_page, current_bid=current_bid, timeout=timeout)
        # 设置默认文件名
        if file_name == '':
            file_name = site_name + '_' + report_category + '_' + new_bid + '_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if state == '完成':
            # 点击下载按钮
            download_selector = create_selector(XPath.DownloadReport, name='下载报告按钮')
            web_page.find(download_selector).click()
            sleep(1)  # 等待下载对话框出现
            # 使用 activities_utils 中的 download_handler 处理下载
            file_path = activities_download_handler(
                web_page,
                str(file_folder),
                file_name
            )
    return file_path


def test_download_classified_product_report():
    if "xbot_extensions" in __file__:
        return

    web_page = xbot.web.get_active(mode="ziniaobrowser") 
    site_name = '美国' # 站点名称 支持中文和英文简写，例：1.美国、2.US
    report_category = "分类商品报告" # 报告类型
    create_date = "2025-11-30" # 商品创建日期（格式：年-月-日，会自动转换为月/日/年）
    timeout = 300  # 等待报告超时时间
    file_folder = r"C:\Users\58204\Desktop\亚马逊"  # 下载文件夹路径
    file_name = ""  # 下载文件名
    state_filter = "在售" # 状态筛选条件
    is_download = True # 是否下载
    download_classified_product_report(
        web_page,site_name, report_category, create_date, state_filter, file_folder, file_name, timeout, is_download
    )
    exit()
def main(args):

    # 测试代码入口
    test_download_classified_product_report()

    # 业务代码入口
    web_page = args.get("web_page")
    site_name = args.get("site_name") # 站点名称
    report_category = args.get("report_category") # 报告类型
    create_date = args.get("create_date") # 商品创建日期
    state_filter = args.get("state_filter") # 状态筛选条件
    file_folder = args.get("file_folder") # 下载文件夹路径
    file_name = args.get("file_name") # 下载文件名
    timeout = args.get("timeout") # 等待报告下载时间
    is_download = args.get("is_download") # 是否下载

    file_path = download_classified_product_report(
        web_page,site_name, report_category, create_date, state_filter, file_folder, file_name, timeout, is_download
    )
    args["file_path"] = file_path
