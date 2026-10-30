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
from .download_utils import find_element_by_text
from datetime import datetime
from typing import Union
from dateutil.relativedelta import relativedelta
from pathlib import Path
from ._amazon_api import switch_site,switch_language
from xbot_extensions.iframe2 import init_iframe, find_ele, find_all_ele, click_by_xpath
from .classified_product_reports import gen_selector
from .payments_past_settlements import get_shadowroot_element
from .create_element import create_selector

class Xpath:
    # 国家名称下拉框
    CountrySelect= '//kat-dropdown[@id="myq-merchant-marketplace-picker"]'
    # 国家名称下拉选项
    CountryItem = '//*[@id="myq-merchant-marketplace-picker"]/kat-option'
    # 截图区域元素
    # ScreenshotXpath = '//*[@id="container"]'
    # 元素更新
    ScreenshotXpath = '//*[local-name()="kat-tabs"][@class="myq_quote_marketplace_tabs"]'
    # 日本区截图区域元素
    JapanScreenshot = '//*[@id="bulk-genie-tab"]//div[@class="row text-left"]'
    # 下一页按钮
    NextButton = '(//*[@id="bulk-genie-tab"]//li)[last()]'
    # 关闭弹窗
    Close_Button = create_selector('//*[local-name()="kat-modal"][@role="dialog"]/xbotShadowRoot//button[@aria-label="关闭"]',name ="关闭弹窗")





class Option:
    CountryMap = {'美国':'United States','日本':'Japan','英国':'United Kingdom','德国':'Germany','法国':'France','意大利':'Italy','西班牙':'Spain'}
    CountryList = ['美国','日本','英国', '德国', '法国', '意大利', '西班牙']


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(Xpath.CountrySelect), timeout=30):
        raise Exception(
            f"进入管理报价页面失败，未找到国家名称下拉框： {Xpath.CountrySelect}"
        )


def input_parameter_valid(web_page:WebBrowser,country_name:str):
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (country_name in Option.CountryList), f"国家名称错误：{country_name}"


def screenshot_manage_quote(web_page:WebBrowser,country_name:str,site_name:str,file_folder:str,file_name:str):
    # 管理报价截图
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page,country_name)

    # 站点切换
    switch_site(web_page, site_name)

    # 进入管理报价页面
    domain = get_domain(web_page)
    url = f"{domain}/business/manage-quotes"
    to_reports_page_if_need(web_page, url)
    has_win = web_page.wait_appear(Xpath.Close_Button , timeout = 3)
    if has_win:
        web_page.find(Xpath.Close_Button,timeout = 2).click()
    # 切换语言
    switch_language(web_page, 'zh_CN')
    
    # 选择国家选项
    web_page.find_by_xpath(Xpath.CountrySelect).click()
    for option in web_page.find_all_by_xpath(Xpath.CountryItem):
        if option.get_text() == Option.CountryMap.get(country_name):
            option.click()
            break
    # print([option.get_text() for option in web_page.find_all_by_xpath(Xpath.CountryItem)])

    # 管理报价查询结果区域截图
    if country_name=='日本':
        web_page.find_by_xpath(Xpath.JapanScreenshot).screenshot(str(file_folder), filename=file_name)
    else:
        web_page.find_by_xpath(Xpath.ScreenshotXpath).screenshot(str(file_folder), filename=file_name)
    return str(file_folder)


def test_screenshot_manage_quote():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="chrome")
    site_name = '日本' # 站点名称
    country_name = '日本' # 国家名称
    file_folder = r"C:\Users\Administrator\Desktop\测试"  # 截图文件夹路径
    file_name = "测试.png"  # 截图文件名

    file_path = screenshot_manage_quote(web_page,country_name,site_name,file_folder,file_name)
    print(file_path)


def main(args):
    # 测试代码入口
    # test_screenshot_manage_quote()

    # 业务代码入口
    web_page = args.get('web_page')
    site_name = args.get('site_name') # 站点名称
    country_name =args.get('country_name') # 国家名称
    file_folder = args.get('file_folder')  # 截图文件夹路径
    file_name = args.get('file_name')  # 截图文件名
    file_path = screenshot_manage_quote(web_page,country_name,site_name,file_folder,file_name)
    args['file_path'] = file_path
