# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot  # type: ignore
import re  # type: ignore
from xbot import print, sleep  # type: ignore
from xbot.selector import Selector  # type: ignore
from xbot.web import WebBrowser  # type: ignore
from xbot.errors import UIAError  # type: ignore
from xbot._core.retry import Retry  # type: ignore
from .package import variables as glv  # type: ignore
from .utils import get_domain, handler_container
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
from ._amazon_api import switch_site, switch_language
from .import package
from .activities_utils import download_handler


class Xpath:
    # 账户类型
    AccountTypeSelect = "//form[@class='date-range-form']/kat-dropdown[@class='account-type-dropdown']"
    # 开始日期选择
    StartDateSelect = "//form[@class='date-range-form']/kat-date-picker[1]"
    # 结束日期选择
    EndDateSelect = "//form[@class='date-range-form']/kat-date-picker[2]"
    # 搜索按钮
    SearchButton = "//form[@class='date-range-form']/kat-button[@class='form-search-button']"
    # 下载结算周期列
    BillingPeriodCols= "//*[@id='financialEventGroupList']//td[8]//kat-dropdown-button/parent::*/parent::*/parent::*/preceding-sibling::*[7]"
    # 下载按钮列
    DownloadButtons = "//*[@id='financialEventGroupList']//td[8]//kat-dropdown-button"
    # 请求按钮列
    RequestButtons = "//*[@id='financialEventGroupList']//td[8]//kat-button"
    # 所有结算表格周期列
    AllBillingCols = "//*[@id='financialEventGroupList']//td[1]"

# 模拟滚动页面触发页面的懒加载
def scroll_and_load(web_page:WebBrowser):
    # 获取初始页面高度
    last_height = web_page.execute_javascript("""function (element, args) {return document.body.scrollHeight;}""")
    while True:
        # 向下滚动页面
        web_page.execute_javascript("""function (element, args) {window.scrollTo(0, document.body.scrollHeight);}""")
        # 等待页面加载
        sleep(2)
        # 计算新的页面高度并与之前的页面高度进行比较
        new_height = web_page.execute_javascript("""function (element, args) {return document.body.scrollHeight;}""")
        if new_height == last_height:
            break
        last_height = new_height


# 获取shadowroot内的网页元素
def get_shadowroot_element(web_page:WebBrowser,selector_str:str):
    # 传入参数selector_str：影刀捕获的元素；返回Selector选择器
    data = {}
    for item in dir(package.selector(selector_str)):
        if item == 'value':
            # print(f'{item} -> {getattr(package.selector(selector_str), item)}')
            data['id'] = getattr(package.selector(selector_str), item)['id']
            data['name'] = getattr(package.selector(selector_str), item)['name']
            data['type'] = getattr(package.selector(selector_str), item)['type']
            data['framework'] = getattr(package.selector(selector_str), item)['framework']
            try:
                data['version'] = getattr(package.selector(selector_str), item)['version']
            except:
                data['version'] = '2'
            data['xpath'] = getattr(package.selector(selector_str), item)['xpath']
    # print(data)
    return Selector(data)


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

    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(Xpath.SearchButton), timeout=30):
        raise Exception(
            f"进入所有结算页面失败，未找到搜索按钮： {Xpath.SearchButton}"
        )


def wait_report_completed(web_page: WebBrowser,table_rows:int, timeout: int = 1200):
    """等待报告生成完成"""
    base_delay = 5 # 初始等待时间（秒）
    max_delay = 30 # 最大等待时间（秒）
    current_delay = base_delay # 当前等待时间从初始值开始
    # 使用重试机制（在指定超时时间内循环）
    for _ in Retry(timeout):
        try:
            # 如果刷新后捕获到的下载按钮数量等于之前查询的结算表格行数，则说明之前请求的文件生成完成，则退出等待
            if len(web_page.find_all_by_xpath(Xpath.DownloadButtons)) == table_rows:
                return
            # 使用指数退避策略增加等待时间
            sleep(current_delay)
            current_delay = min(current_delay * 2, max_delay)
            # web_page.reload() # 刷新页面获取最新状态
            web_page.find_by_xpath(Xpath.SearchButton).click()
            # 模拟滚动页面触发页面的懒加载
            scroll_and_load(web_page)
        # 忽略UI查找错误（继续重试）
        except UIAError as e:
            pass
    raise Exception(f"等待报告生成超时：{timeout}秒") # 最终失败抛出异常


def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%Y/%m/%d")


def sanitize_filename(filename):
    # 替换非法字符
    filename = re.sub(r'[\\/:\*\?"<>\|\s]', '_', filename)  # 替换为下划线或连字符
    filename = re.sub(r'[–—]', '-', filename)  # 统一破折号为短横线
    filename = re.sub(r'-+', '-', filename)    # 合并多个短横线
    filename = filename.strip('.- _')          # 去除首尾空字符
    return filename


def payments_past_settlements(web_page:WebBrowser,account_type:str,start_date:str,end_date:str,site_name:str,file_folder:str,file_name:str):
    # 获取账号状态数据
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    if account_type == '':
        account_type = '标准订单' # 设置默认账户类型
    account_type_list = [
        '标准订单',
        '发票支付订单'
    ]
    if account_type not in account_type_list:
        raise Exception(f"账户类型错误：{account_type}")

    # 站点切换
    switch_site(web_page, site_name)

    # 进入所有结算页面
    domain = get_domain(web_page)
    url = f"{domain}/payments/past-settlements"
    to_reports_page_if_need(web_page, url)

    # 0.切换语言
    switch_language(web_page, 'zh_CN')

    # 选择账户类型
    web_page.find_by_xpath(Xpath.AccountTypeSelect).click()
    for option in web_page.find_all(get_shadowroot_element(web_page,"payments_past_settlements_账户类型选项")):
        if option.get_text() == account_type:
            option.click()
    
    # 选择开始日期
    web_page.find_by_xpath(Xpath.StartDateSelect).click()
    web_page.find(get_shadowroot_element(web_page,"payments_past_settlements_开始日期输入框")).input(convert_date_format(start_date))

    # 选择结束日期
    web_page.find_by_xpath(Xpath.EndDateSelect).click()
    web_page.find(get_shadowroot_element(web_page,"payments_past_settlements_结束日期输入框")).input(convert_date_format(end_date))

    # 点击搜索按钮
    web_page.find_by_xpath(Xpath.SearchButton).click()

    # 模拟滚动页面触发页面的懒加载
    scroll_and_load(web_page)

    # 先循环点击请求按钮并等待文件生成
    request_ele_list = web_page.find_all_by_xpath(Xpath.RequestButtons)
    if len(request_ele_list)>0:
        for option in request_ele_list:
            option.click()
    
    # 计算结算表格行数，除开现在周期日期行，并记录查询的结算周期
    table_rows = 0
    period_texts = []
    for option in web_page.find_all_by_xpath(Xpath.AllBillingCols):
        if "现在" not in option.get_text():
            table_rows += 1
            period_texts.append(option.get_text())
    print(table_rows)
    print(period_texts)

    # 等待文件生成完成
    wait_report_completed(web_page,table_rows)

    # 获取下载结算周期
    period_text_list = []
    for col in web_page.find_all_by_xpath(Xpath.BillingPeriodCols):
        period_text_list.append(col.get_text())
    file_path_list = []
    i=0
    # 循环点击下载按钮并下载文件
    download_ele_list = web_page.find_all_by_xpath(Xpath.DownloadButtons)
    for option in download_ele_list:
        # 点击下载
        option.click()
        # 设置下载文件名：用户传入的 file_name + 周期 + .txt 后缀（file_name 为空时用 site_name 作为前缀）
        base_name = (file_name[:-4] if file_name and file_name.endswith('.txt') else file_name) or site_name
        download_file_name = sanitize_filename(str(base_name) + '_' + period_text_list[i] + '.txt')
        # 下载文件（使用 activities_utils.download_handler，与 SC 其他下载指令一致）
        file_path = download_handler(
            web_page,
            str(file_folder),
            download_file_name,
            wait_time=300,
        )
        file_path_list.append(file_path)
        i+=1
    return file_path_list


def test_payments_past_settlements():
    if "xbot_extensions" in __file__:
        return

    web_page = xbot.web.get_active(mode="ziniaobrowser")
    site_name = '美国' # 站点名称
    account_type = '发票支付订单' # 账户类型
    start_date = '2025-11-03' # 开始日期
    end_date = '2025-12-08' # 结束日期
    file_folder = r"C:\Users\58204\Desktop"  # 下载文件夹路径
    file_name = ""  # 下载文件名
    payments_past_settlements(
        web_page,account_type,start_date,end_date,site_name,file_folder,file_name
    )
    exit()

def main(args):
    # 测试代码入口
    test_payments_past_settlements()

    # 业务代码入口
    web_page = args.get("web_page")
    site_name = args.get("site_name") # 站点名称
    account_type = args.get("account_type") # 账户类型
    start_date = args.get("start_date") # 开始日期
    end_date = args.get("end_date") # 结束日期
    file_folder = args.get("file_folder")  # 下载文件夹路径
    file_name = args.get("file_name")  # 下载文件名
    file_path_list = payments_past_settlements(
        web_page,account_type,start_date,end_date,site_name,file_folder,file_name
    )
    args["file_path"] = ','.join(file_path_list)
