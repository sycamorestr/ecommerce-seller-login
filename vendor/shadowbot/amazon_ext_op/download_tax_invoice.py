# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser,WebElement
from pathlib import Path
from datetime import datetime
from .utils import get_domain, handler_container
from .activities_utils import gen_selector, download_handler
from ._amazon_api import switch_language


class Xpath:
    # 墨西哥税务发票标题
    TaxInvoiceTitle = '//*[@id="taxstiapp-secondarynav"]//h2'
    # 墨西哥税务发票内容行
    InvoiceTableRow = '//*[@id="invoiceDownloadRequestRow"]'


def input_parameter_valid(web_page: WebBrowser, file_format: str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (file_format in ['pdf', 'xml']), f"不支持下载发票文件类型：{file_format}"


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
    if not web_page.wait_appear(gen_selector(Xpath.TaxInvoiceTitle), timeout=30):
        raise Exception(
            f"进入亚马逊墨西哥税务发票页面失败，未找到墨西哥税务发票标题： {Xpath.TaxInvoiceTitle}"
        )


def is_date_range_included(input_start: str, input_end: str, current_start: str, current_end: str):
    """
    判断当前日期范围是否在输入日期范围内
    参数:
        input_start (str): 输入的开始日期，格式为"yyyy-mm-dd"
        input_end (str): 输入的结束日期，格式为"yyyy-mm-dd"
        current_start (str): 当前的开始日期，格式为"yyyy年m月d日"
        current_end (str): 当前的结束日期，格式为"yyyy年m月d日"
    返回:
        bool: 如果当前日期范围在输入日期范围内返回True，否则返回False
    """
    try:
        # 解析输入的日期（yyyy-mm-dd格式）
        input_start_date = datetime.strptime(input_start, "%Y-%m-%d")
        input_end_date = datetime.strptime(input_end, "%Y-%m-%d")
        # 解析当前的日期（yyyy年m月d日格式）
        current_start_date = datetime.strptime(current_start, "%Y年%m月%d日")
        current_end_date = datetime.strptime(current_end, "%Y年%m月%d日")
        # 检查当前开始日期是否在输入开始日期之后或等于，且当前结束日期是否在输入结束日期之前或等于
        return (input_start_date <= current_start_date) and (current_end_date <= input_end_date)
    except ValueError as e:
        # 处理日期格式错误
        raise ValueError(f"日期格式错误: {str(e)}")


def transform_date(date: str):
    """
    转换日期格式
    """
    try:
        result = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        return result
    except Exception as e:
        raise Exception(f"日期格式错误：{date}")


def download_mexico_tax_invoice(web_page: WebBrowser, invoice_type: str, start_date: str, end_date: str, file_format: str, file_folder: str, file_name: str):
    """
    下载墨西哥税务发票
    """
    file_path_list = []
    total_rows = len(web_page.find_all_by_xpath(Xpath.InvoiceTableRow)) # 获取墨西哥税务发票内容行数
    # 遍历墨西哥税务发票内容行
    for row in range(1, total_rows+1):
        # 获取每行内容中的发票类型
        invoice_type_cell = web_page.find_by_xpath('(' + Xpath.InvoiceTableRow + ')[' + str(row) + ']//td[1]').get_text()
        # 获取每行内容中的发票编号
        invoice_id_cell = web_page.find_by_xpath('(' + Xpath.InvoiceTableRow + ')[' + str(row) + ']//td[2]').get_text()
        # 获取每行内容中的开始日期
        start_date_cell = web_page.find_by_xpath('(' + Xpath.InvoiceTableRow + ')[' + str(row) + ']//td[6]').get_text()
        # 获取每行内容中的结束日期
        end_date_cell = web_page.find_by_xpath('(' + Xpath.InvoiceTableRow + ')[' + str(row) + ']//td[7]').get_text()
        # 如果发票类型等于输入的发票类型，并且开始日期到结束日期的范围是在输入的开始日期到输入的结束日期范围内，就下载发票
        if invoice_type_cell == invoice_type and is_date_range_included(start_date, end_date, start_date_cell, end_date_cell):
            if file_format == 'pdf':
                web_page.find_by_xpath('(' + Xpath.InvoiceTableRow + ')[' + str(row) + ']//td[8]/a').click()
            elif file_format == 'xml':
                web_page.find_by_xpath('(' + Xpath.InvoiceTableRow + ')[' + str(row) + ']//td[9]/a').click()
            file_name = invoice_type_cell + '_' + invoice_id_cell + '_' + start_date_cell + '_' + end_date_cell
            file_path = download_handler(web_page, file_folder, file_name)
            file_path_list.append(file_path)
    return file_path_list


def download_tax_invoice(web_page: WebBrowser, invoice_type: str, start_date: str, end_date: str, file_format: str, file_folder: str, file_name: str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)
    start_date = transform_date(start_date)
    end_date = transform_date(end_date)
    if invoice_type == '':
        invoice_type = '墨西哥卖家费用发票'

    # 输入参数校验
    input_parameter_valid(web_page, file_format)

    # 进入批量管理您的采购页面
    domain = get_domain(web_page)
    url = f"{domain}/sellertaxinvoice/displaySellerTaxInvoices"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 下载墨西哥税务发票
    file_path_list = download_mexico_tax_invoice(web_page, invoice_type, start_date, end_date, file_format, file_folder, file_name)
    return file_path_list


def test_download_tax_invoice():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="chrome")
    invoice_type = '' # 发票类型，默认：墨西哥卖家费用发票
    start_date = '2025-03-01' # 开始日期
    end_date = '2025-03-31' # 结束日期
    file_format = 'xml' # 文件格式，pdf，xml
    file_folder = r"C:\Users\Administrator\Desktop\test" # 保存文件夹路径
    file_name = "" # 保存文件名，默认：发票类型+发票编号+开始日期+结束日期

    file_path_list = download_tax_invoice(web_page, invoice_type, start_date, end_date, file_format, file_folder, file_name)
    print(file_path_list)
    exit()


def main(args):
    # 测试代码入口
    test_download_tax_invoice()

    # 业务代码入口
    web_page = args.get("web_page")
    invoice_type = args.get("invoice_type") # 发票类型，默认：墨西哥卖家费用发票
    start_date = args.get("start_date") # 开始日期
    end_date = args.get("end_date") # 结束日期
    file_format = args.get("file_format") # 文件格式，pdf，xml
    file_folder = args.get("file_folder") # 保存文件夹路径
    file_name = args.get("file_name") # 保存文件名

    file_path_list = download_tax_invoice(web_page, invoice_type, start_date, end_date, file_format, file_folder, file_name)
    args["file_path_list"] = file_path_list
