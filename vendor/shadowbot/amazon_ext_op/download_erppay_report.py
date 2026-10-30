# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import re
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser,WebElement
from pathlib import Path
from .utils import get_domain
from .utils import handler_container
from .activities_utils import gen_selector
from ._amazon_api import switch_language
from math import ceil
from xbot.web import handle_save_dialog
from .download_utils import find_element_by_text
from xbot.errors import UIAError
from xbot import logging


class Xpath:
    # 国家导航组
    CountryTabs = "//kat-tabs//kat-tab/span"
    # 生态费下载表格
    ErpPayTable = "(//table)[3]//tr"
    # 分页导航组
    PageNavigation = '//*[@class="eco-contribution-container"]//kat-pagination'
    # 当前订阅分类
    SubscribeTable = '//table//tr[contains(@class, "data")]'


class Option:
    # 国家缩写映射
    CountryMap = {'美国':'US','英国':'UK','德国':'DE','法国':'FR','日本':'JP','加拿大':'CA','意大利':'IT','西班牙':'ES','荷兰':'NL','墨西哥':'MX','瑞典':'SE','波兰':'PL'}


def input_parameter_valid(web_page:WebBrowser,year_num:str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert len(year_num) == 4 and year_num.isdigit(), f"年份格式错误：{year_num}"


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
    if not web_page.wait_appear(gen_selector(Xpath.CountryTabs), timeout=30):
        raise Exception(
            f"进入亚马逊生产者责任延申代理付费页面失败，未找到国家导航组： {Xpath.CountryTabs}"
        )


def download_handler(web_page:WebBrowser,file_folder:str,file_name:str):
    # 下载报告
    file_path = handle_save_dialog(file_folder=str(file_folder), mode=web_page.product_name, file_name=file_name, wait_complete=False)
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
    return file_path


def download_report(web_page:WebBrowser,year_num:str,file_folder:str,file_name:str):
    result_list = []
    # 循环国家站点tab
    for i, tab in enumerate(web_page.find_all_by_xpath(Xpath.CountryTabs)):
        tab.click()
        tab_name = tab.get_text().split()[0] # 获取国家tab名称
        # 获取当前订阅表中分类名称
        type_list = [] # 存放当前国家站点的分类
        subscribe_xpath = '(//kat-tab[' + str(i+1) + '])' + Xpath.SubscribeTable # 不同tab的订阅表Xpath
        for r in range(1, len(web_page.find_all_by_xpath(subscribe_xpath))+1):
            subscribe_type_text = (web_page.find_by_xpath(subscribe_xpath + '[' + str(r) + ']' + '//td[1]')).get_text().replace(' ', '')
            type_list.append(subscribe_type_text)
        # 获取生态费表中总行数
        total_items = web_page.find_by_xpath(Xpath.PageNavigation).get_attribute('total-items')
        # 获取生态费表中每页总行数
        page_items = web_page.find_by_xpath(Xpath.PageNavigation).get_attribute('items-per-page')
        pages = ceil(int(total_items)/int(page_items))
        print(pages)
        # 循环生态费表中每页
        for index in range(pages):
            rows = len(web_page.find_all_by_xpath(Xpath.ErpPayTable))
            # 循环生态费表中每行
            for row in range(1, rows):
                # 获取生态费表中生产者责任延申分类文本
                type_text = (web_page.find_by_xpath(Xpath.ErpPayTable + '[' + str(row) + ']' + '//td[3]').get_text()).replace(' ', '')
                # 获取生态费表中报告期文本
                date_text = (web_page.find_by_xpath(Xpath.ErpPayTable + '[' + str(row) + ']' + '//td[5]').get_text()).replace(' ', '')
                year_pos = date_text.find('年')
                if year_pos != -1:
                    year_text = date_text[year_pos -4 : year_pos] # 提取年份文本
                else:
                    year_text = ''
                # 获取生态费表中国家/地区文本
                country_text = web_page.find_by_xpath(Xpath.ErpPayTable + '[' + str(row) + ']' + '//td[2]').get_text()
                # 下载对应国家、分类和年份的生态费报告
                if type_text in type_list and Option.CountryMap.get(tab_name)==country_text and year_text == year_num:
                    if file_name == '':
                        file_name = tab_name + '_' + date_text + '_' + type_text # 设置默认文件名
                    # 点击报告下载按钮
                    web_page.find_by_xpath(Xpath.ErpPayTable + '[' + str(row) + ']' + '//td[7]').click()
                    # 下载报告
                    file_path = download_handler(web_page,file_folder,file_name)
                    result_list.append(file_path)
            # 点击下一页
            web_page.find("download_erppay_report_下一页按钮").click()
    return result_list


def download_erppay_report(web_page:WebBrowser,year_num:str,file_folder:str,file_name:str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page,year_num)

    # 进入批量管理您的采购页面
    domain = get_domain(web_page)
    url = f"{domain}/epr-payonbehalf/dashboard"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 下载生态费报告
    result_list = download_report(web_page,year_num,file_folder,file_name)
    return result_list


def test_download_erppay_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="auto")
    year_num = '2024' # 年份
    file_folder = r"C:\Users\Administrator\Desktop\test" # 保存文件夹路径
    file_name = "" # 保存文件名

    file_list = download_erppay_report(web_page,year_num,file_folder,file_name)
    print(file_list)


def main(args):
    # 测试代码入口
    # test_download_erppay_report()

    # 业务代码入口
    web_page = args.get('web_page')
    year_num = args.get('year_num') # 年份
    file_folder = args.get('file_folder') # 保存文件夹路径
    file_name = args.get('file_name') # 保存文件名

    file_list = download_erppay_report(web_page,year_num,file_folder,file_name)
    args['file_list'] = file_list
