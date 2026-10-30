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
from .activities_utils import download_handler
from xbot.web import handle_save_dialog
from .download_utils import find_element_by_text
from xbot.errors import UIAError
from xbot import logging
from .create_element import create_selector,create_selector_shadow

VALUE_MAP = {
        '默认': 'DEFAULT',
        '所有列': 'ALL_COLUMNS',
        'B2B': 'B2B'
    }
class Xpath:
    # 下载链接导航
    DownloadLinkNav = create_selector("//strong",name ='业务报告')
    # 请求下载.csv文件按钮
    RequestCsvBtn = '//*[@data-testid="BR_TABLE_BAR_DOWNLOAD_BUTTON"]'

    # 事件日期
    ReportDate = create_selector('(//*[local-name()="kat-dropdown"][@data-testid="selection-box-dropdown"])[1]/xbotShadowRoot//div[@part="dropdown-header"]',name ='日期选择')
    # 确切日期
    ExactDate = create_selector('(//*[local-name()="kat-dropdown"][@data-testid="selection-box-dropdown"])[1]/xbotShadowRoot//*[local-name()="kat-option"][@value="CUSTOM"]/div[contains(@class, "standard-option-content")]',name='确切日期')
    # 控制面板视图
    ReportView = create_selector('(//*[local-name()="kat-dropdown"][@data-testid="selection-box-dropdown"])[2]/xbotShadowRoot//div[@part="dropdown-header"]',name ='视图选择')
    # 应用按钮
    ChooseButton = create_selector('//*[local-name()="kat-button"][@type="submit"]/xbotShadowRoot/button',name ="应用")

    StartDate = create_selector('(//*[local-name()="kat-date-picker"])[1]/xbotShadowRoot//*[local-name()="kat-input"]',name = '开始日期')
    EndDate = create_selector('(//*[local-name()="kat-date-picker"])[2]/xbotShadowRoot//*[local-name()="kat-input"]',name='结束日期')


def input_parameter_valid(web_page: WebBrowser):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)


def select_start_time(web_page, start_date):
    # 选择开始时间
    #点击开始日期
    web_page.wait_appear(Xpath.DownloadLinkNav,timeout =30)
    web_page.find(Xpath.StartDate).input(start_date)
    web_page.find(Xpath.DownloadLinkNav).click()

def select_end_time(web_page, end_date):
    # 选择结束时间
    web_page.wait_appear(Xpath.DownloadLinkNav,timeout =30)
    web_page.find(Xpath.EndDate).input(end_date)
    web_page.find(Xpath.DownloadLinkNav).click()

def time_compare(web_page, start_date, end_date):
    # 进行时间比较
    web_start_date = web_page.find(Xpath.StartDate).get_attribute('value').strip()
    web_end_date = web_page.find(Xpath.EndDate).get_attribute('value').strip()
    try:
        # 进行网页时间格式化
        web_start_date = datetime.strptime(web_start_date, "%Y/%m/%d")
        web_end_date = datetime.strptime(web_end_date, "%Y/%m/%d")
        # 进行目标时间格式化
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except:
        return 'start_first'

    if web_start_date > end_date:
        return 'start_first'
    elif web_end_date < start_date:
        return 'end_first'
    else:
        return 'start_first'

def set_filter_params(web_page: WebBrowser, file_type: str,control_view:str,start_date,end_date,file_folder:str,file_name:str):
    # 等待元素出现
    web_page.wait_appear(Xpath.DownloadLinkNav,timeout =30)
    web_page.find(Xpath.ReportDate).click()
    web_page.find(Xpath.ExactDate).click()
    # 进行时间判断
    compare_res = time_compare(web_page, start_date, end_date)
    if compare_res == 'start_first':
        # 进行开始时间选择
        select_start_time(web_page, start_date)
        sleep(1)
        # 进行结束时间选择
        select_end_time(web_page, end_date)
    elif compare_res == 'end_first':
        # 进行结束时间选择
        select_end_time(web_page, end_date)
        sleep(1)
        # 进行开始时间选择
        select_start_time(web_page, start_date)

    web_page.find(Xpath.ReportView).click()
    #点击位置
    view_to_select = VALUE_MAP[control_view]
    Control_view = create_selector(f'(//*[local-name()="kat-dropdown"][@data-testid="selection-box-dropdown"])[2]/xbotShadowRoot//*[local-name()="kat-option"][@value="{view_to_select}"]',name = '面板选项')
    web_page.find(Control_view).click()
    #点击应用
    web_page.find(Xpath.ChooseButton).click()
    web_page.wait_appear(Xpath.DownloadLinkNav,timeout =30)

    #点击下载
    web_page.find_by_xpath(Xpath.RequestCsvBtn).click()
    file_path = download_handler(web_page, file_folder, file_name)
    return file_path



def return_processing_report(web_page: WebBrowser, file_type: str,control_view:str,start_date,end_date,file_folder:str,file_name:str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page)

    # 进入亚马逊配送货件
    domain = get_domain(web_page)
    url = f"{domain}/business-reports/ref=xx_sitemetric_dnav_xx#/report?id=102:DetailSalesTrafficByChildItem"
    to_reports_page_if_need(web_page, url)
    
    # 切换语言
    switch_language(web_page, 'zh_CN')
    web_page.wait_load_completed(timeout=30)
    # 设置报告参数
    file_path = set_filter_params(web_page, file_type,control_view,start_date,end_date,file_folder,file_name)

    return file_path
    


def test_return_processing_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    file_folder = r"D:"  # 下载文件夹路径
    file_name = "111"  # 下载文件名
    file_type = 'csv' # 下载文件类型
    start_date = '2026-05-02'
    end_date ='2026-05-02'
    control_view = "所有列"
    file_path = return_processing_report(web_page, file_type,control_view,start_date,end_date,file_folder,file_name)

    print(file_path)

    exit()


def main(args):
    # 测试代码入口
    test_return_processing_report()

    # 业务代码入口
    web_page = args.get('web_page')
    file_folder = args.get('file_folder')  # 下载文件夹路径
    file_name = args.get('file_name')  # 下载文件名
    file_type = args.get('file_type','csv') # 下载文件类型
    start_date = args.get('start_date')
    end_date = args.get('end_date')    
    control_view = args.get('control_view')

    file_path = return_processing_report(web_page, file_type,control_view,start_date,end_date,file_folder,file_name)
    args['file_path'] = file_path
