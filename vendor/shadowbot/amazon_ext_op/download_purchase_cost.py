# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import re
from math import ceil
from xbot import print, sleep,win32
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from pathlib import Path
from .activities_utils import scroll_and_load, gen_selector
from .utils import get_domain
from .utils import handler_container
from ._amazon_api import switch_site, switch_language
from datetime import datetime
from xbot.web import handle_save_dialog
from .download_utils import find_element_by_text
from xbot.errors import UIAError
from xbot import logging, excel


class Xpath:
    # 国家市场下拉框
    MarketSelect = "//app-marketplace-selector[@class='marketplace-selector']/kat-dropdown"
    # 国家市场选项
    MarketItems = "//app-marketplace-selector[@class='marketplace-selector']//kat-option"
    # 下载采购成本按钮
    DownloadButton = "//*[@id='container']//kat-button[@variant='secondary']"
    # 等待下载弹窗
    WaitDownloadToast = "//*[@id='container']//kat-toast-group[@id='manufacturing_cost_bulk_update_page_download_toast_group']"
    # 批量更新按钮
    BatchUpdateBtn = "//kat-button[@class='bulk-update-button']"
    # 表格数据行
    TableRows = "//kat-data-table//tbody/tr"
    # 分页导航组
    PageNavigation = '//*[@class="pagination-footer"]//kat-pagination'
    # 搜索按钮
    SearchButton = "//kat-button[contains(@class, 'search')]"


class Option:
    # 国家市场选项列表
    MarketItemList = ['US市场', 'UK市场', 'DE市场', 'FR市场', 'JP市场', 'CA市场', 'IT市场', 'ES市场', 'NL市场', 'MX市场', 'SE市场', 'PL市场']
    CountryList = ['美国', '英国', '德国', '法国', '日本', '加拿大', '意大利', '西班牙', '荷兰', '墨西哥', '瑞典', '波兰']
    CountryMarketMap = {'美国':'US市场','英国':'UK市场','德国':'DE市场','法国':'FR市场','日本':'JP市场','加拿大':'CA市场','意大利':'IT市场','西班牙':'ES市场','荷兰':'NL市场','墨西哥':'MX市场','瑞典':'SE市场','波兰':'PL市场'}


def input_parameter_valid(web_page:WebBrowser, market_name:str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (market_name in Option.CountryList), f"国家市场名称错误：{market_name}"


def to_reports_page_if_need(web_page: WebBrowser, url: str, method_name: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)
    # 使用构建 selector 的方式来等待元素
    if method_name == '下载报告':
        if not web_page.wait_appear(gen_selector(Xpath.DownloadButton), timeout=30):
            raise Exception(f"进入亚马逊批量管理您的采购成本页面失败，未找到下载采购成本按钮： {Xpath.DownloadButton}")
    elif method_name == '人工抓取':
        if not web_page.wait_appear(gen_selector(Xpath.BatchUpdateBtn), timeout=30):
            raise Exception(f"进入亚马逊管理您的获物成本页面失败，未找到批量更新按钮： {Xpath.BatchUpdateBtn}")


def set_filter_params(web_page: WebBrowser, market_name: str, method_name: str):
    # 设置报告参数
    # 选择国家市场
    web_page.find_by_xpath(Xpath.MarketSelect).click()
    for option in web_page.find_all_by_xpath(Xpath.MarketItems):
        if option.get_text().replace(' ', '') == Option.CountryMarketMap.get(market_name):
            option.click()
            break
    # 如果是人工抓取方式，点击搜索按钮
    if method_name == '人工抓取':
        web_page.find_by_xpath(Xpath.SearchButton).click()


def download_handler(web_page:WebBrowser,file_folder:str,file_name:str):
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
        
    return str(Path(file_folder) / f"{file_name}")


def wait_download_report(web_page: WebBrowser, file_folder: str, file_name: str, time_out: int=300):
    # 等待并下载报告
    # 点击下载按钮
    web_page.find_by_xpath(Xpath.DownloadButton).click()
    # 等待下载等待弹窗出现
    if web_page.wait_appear("download_purchase_cost_下载等待弹窗",timeout=10):
        # 等待下载等待弹窗消失
        if web_page.wait_disappear("download_purchase_cost_下载等待弹窗",timeout=time_out):
            web_page.find_by_xpath(Xpath.DownloadButton).click()
            file_path = download_handler(web_page,file_folder,file_name)
        else:
            raise Exception(f"等待报告完成超时：{time_out}秒")
    else:
        file_path = download_handler(web_page,file_folder,file_name)
    return file_path


def get_table_data(web_page: WebBrowser, file_folder: str, file_name: str):
    # 创建excel表格
    file_path = str(file_folder) + '\\' + file_name + '.xlsx'
    work_book = excel.create(kind='auto_check')
    work_sheet = work_book.get_active_sheet()
    work_sheet.append_row(['商品SKU', '上次更新成本的日期', '亚马逊预估的获物成本', '更新状态']) # 添加标题行
    # 获取表中总行数
    total_items = web_page.find_by_xpath(Xpath.PageNavigation).get_attribute('total-items')
    # 获取表中每页总行数
    page_items = web_page.find_by_xpath(Xpath.PageNavigation).get_attribute('items-per-page')
    pages = ceil(int(total_items)/int(page_items))
    print(pages)
    # 循环表中每页
    for index in range(pages):
        # 人工抓取表格数据
        scroll_and_load(web_page)
        table_rows = len(web_page.find_all_by_xpath(Xpath.TableRows))
        for row in range(1, table_rows+1):
            # 获取商品列SKU数据
            sku_name = web_page.find_by_xpath(Xpath.TableRows + '[' + str(row) + ']/td[1]//kat-link').get_attribute('label')
            # 获取上次更新列数据
            last_update = web_page.find_by_xpath(Xpath.TableRows + '[' + str(row) + ']/td[2]').get_text()
            # 获取获物成本列数据
            cost_text = web_page.find_by_xpath(Xpath.TableRows + '[' + str(row) + ']/td[3]').get_text()
            # 获取更新状态列数据
            update_status = web_page.find_by_xpath(Xpath.TableRows + '[' + str(row) + ']/td[4]').get_text()
            # 正则匹配：提取所有数字（包括整数和小数），去除可能存在的逗号
            clean_text = cost_text.replace(',', '')
            match_text = re.search(r'\d+\.?\d*', clean_text)
            if match_text:
                cost_value = match_text.group()
            else:
                cost_value = '-'
            work_sheet.append_row([sku_name, last_update, cost_value, update_status]) # 添加数据行
        web_page.find("download_purchase_cost_下一页按钮").click() # 点击下一页
    work_book.save_as(file_path)
    work_book.close()
    return file_path


def download_purchase_cost(web_page:WebBrowser, market_name: str, method_name: str, file_folder: str, file_name: str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)
    if file_name == '':
        file_name = market_name + '_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # 输入参数校验
    input_parameter_valid(web_page,market_name)

    # 进入批量管理您的采购页面
    domain = get_domain(web_page)
    if method_name == '下载报告':
        url = f"{domain}/inventory-reimbursement/cost-management/bulk-update"
    elif method_name == '人工抓取':
        url = f"{domain}/inventory-reimbursement/cost-management"
    to_reports_page_if_need(web_page, url, method_name)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置报告参数
    set_filter_params(web_page, market_name, method_name)

    if method_name == '下载报告':
        # 等待并下载报告
        file_path = wait_download_report(web_page, file_folder, file_name, time_out=300)
    elif method_name == '人工抓取':
        # 人工抓取
        file_path = get_table_data(web_page, file_folder, file_name)
    return file_path
    


def test_download_purchase_cost():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="superbrowser")
    market_name = '美国' # 国家市场名称
    file_folder = r"C:\Users\10577\Desktop\test" # 保存文件夹路径
    file_name = "" # 保存文件名
    method_name = "人工抓取" # 获取方法：下载报告/人工抓取

    file_path = download_purchase_cost(web_page, market_name, method_name, file_folder, file_name)
    print(file_path)
    exit()


def main(args):
    # 测试代码入口
    test_download_purchase_cost()

    # 业务代码入口
    web_page = args.get('web_page')
    market_name = args.get('market_name') # 国家市场名称
    file_folder = args.get('file_folder') # 保存文件夹路径
    file_name = args.get('file_name') # 保存文件名
    method_name = args.get('method_name') # 获取方法：下载报告/人工抓取

    file_path = download_purchase_cost(web_page, market_name, method_name, file_folder, file_name)
    args['file_path'] = file_path
