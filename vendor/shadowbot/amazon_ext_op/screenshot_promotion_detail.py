# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot  # type: ignore
import re  # type: ignore
import threading
import math
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


class Xpath:
    # 促销页面_状态下拉框
    StatusSelect = '(//*[@id="search-and-filters"]//kat-icon[contains(@name, "chevron")])[1]'
    # 促销页面_类型/持续时间下拉框
    CategorySelect = '(//*[@id="search-and-filters"]//kat-icon[contains(@name, "chevron")])[2]'
    # 促销页面_日期下拉框
    DateSelect = '(//*[@id="search-and-filters"]//kat-icon[contains(@name, "chevron")])[3]'
    # 促销页面_Amazon Stores下拉框
    StoreSelect = '(//*[@id="search-and-filters"]//kat-icon[contains(@name, "chevron")])[4]'
    # 促销页面_状态下拉框选项
    StatusOptions = '((//*[@id="search-and-filters"]//ul)[1])/li/kat-checkbox'
    # 促销页面_类型/持续时间下拉框选项
    CategoryOptions = '((//*[@id="search-and-filters"]//ul)[2])/li/kat-checkbox'
    # 促销页面_日期下拉框选项
    DateOptions = '((//*[@id="search-and-filters"]//ul)[3])/li'
    # 促销页面_Amazon Stores下拉框选项
    StoreOptions = '((//*[@id="search-and-filters"]//ul)[4])/li'
    # 促销页面_Amazon Stores下拉框选项所有
    StoreOptionAll = '((//*[@id="search-and-filters"]//ul)[4])/li[1]'
    # 促销页面_状态应用按钮
    StatusApplyBtn = '(//*[@id="search-and-filters"]//kat-button)[1]'
    # 促销页面_类型/持续时间应用按钮
    CategoryApplyBtn = '(//*[@id="search-and-filters"]//kat-button)[2]'
    # 促销页面_日期应用按钮
    DateApplyBtn = '(//*[@id="search-and-filters"]//kat-button)[3]'
    # 促销页面_Amazon Stores应用按钮
    StoreApplyBtn = '(//*[@id="search-and-filters"]//kat-button)[4]'
    # 促销页面_状态清空无链接
    StatusClearLink = '(//*[@id="search-and-filters"]//a)[1]'
    # 促销页面_类型/持续时间清空无链接
    CategoryClearLink = '(//*[@id="search-and-filters"]//a)[2]'
    # 促销页面_日期清空无链接
    DateClearLink = '(//*[@id="search-and-filters"]//a)[3]'
    # 促销页面_消费群体状态标签：//*[@class="manage-table"]//kat-table-body//kat-table-cell[2]//kat-badge
    # 促销页面_（正在进行、即将推出、需要注意）消费群体状态标签：//*[@class="manage-table"]//kat-table-body//kat-table-cell[2]//kat-badge[@label="正在进行" or @label="即将推出" or @label="需要注意"]
    # 促销页面_（正在进行、即将推出、需要注意）消费群体状态标签对应的促销详情页链接：//*[@class="manage-table"]//kat-table-body//kat-table-cell[2]//kat-badge[@label="正在进行" or @label="即将推出" or @label="需要注意"]/parent::div/parent::kat-table-cell/preceding-sibling::kat-table-cell//a
    PromotionDetailLinks = '//*[@class="manage-table"]//kat-table-body//kat-table-cell[2]//kat-badge[@label="正在进行" or @label="即将推出" or @label="需要注意"]/parent::div/parent::kat-table-cell/preceding-sibling::kat-table-cell//a'
    # 促销页面_分页导航组
    PageNavigation = "//*[contains(@class, manage-footer)]//kat-pagination"
    # 促销详情页面_商品类别筛选按钮
    DetailProductBtn = '//*[@id="search-and-filters"]//kat-button'
    # 促销详情页面_截图区域
    ScreenshotArea = '//*[@id="smui-root"]'
    # 促销详情页面_促销名称
    DetailPromotionName = '//*[@id="deal-summary-display-name"]'
    # 促销详情页面_分页导航组
    DetailPageNavigation = '//*[contains(@class, manage-footer)]//kat-pagination'


class Option:
    # 状态选项列表
    StatusOptionList = ['正在进行', '即将推出', '需要注意', '已结束', '已取消', '未定']
    # 类型选项列表
    CategoryOptionList = ['Z划算', '秒杀', '精选优惠']
    # 日期选项列表
    DateOptionList = ['过去30天', '最近6个月', '确切日期']
    # 商城选项列表
    StoreOptionList = ['新加坡','澳大利亚','美国', '加拿大', '墨西哥', '巴西', '日本','比利时', '爱尔兰', '英国', '德国', '法国', '意大利', '西班牙', '荷兰', '瑞典', '波兰', '土耳其', '南非']
    # 商品类别项列表
    ProductTypeList = ['所有商品', '参与的商品', '出错的参与商品']


def transform_date(date: str):
    # 转换日期格式
    try:
        result = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        return result
    except Exception as e:
        raise Exception(f"日期格式错误：{date}")


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(Xpath.StatusSelect), timeout=30):
        raise Exception(
            f"进入促销页面失败，未找到状态下拉框： {Xpath.StatusSelect}"
        )


def input_parameter_valid(web_page: WebBrowser, status_name: list, category_name: list, date_name: str, store_name: list, product_type: str):
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert all(item in Option.StatusOptionList for item in status_name), f"状态名称有误：{status_name}"
    assert all(item in Option.CategoryOptionList for item in category_name), f"类型名称有误：{category_name}"
    assert (date_name in Option.DateOptionList), f"日期范围有误：{date_name}"
    assert all(item in Option.StoreOptionList for item in store_name), f"商城名称有误：{store_name}"
    assert (product_type in Option.ProductTypeList), f"商品类别有误：{product_type}"


def set_filter_parameters(web_page: WebBrowser, status_name: list, category_name: list, date_name: str, start_date: str, end_date: str, store_name: list):
    # 选择状态
    web_page.find_by_xpath(Xpath.StatusSelect).click() # 点击状态下拉框
    web_page.find_by_xpath(Xpath.StatusClearLink).click() # 点击无清空状态选项
    for option in web_page.find_all_by_xpath(Xpath.StatusOptions):
        if option.get_attribute('label') in status_name:
            option.click()
    web_page.find_by_xpath(Xpath.StatusApplyBtn).click() # 点击状态应用按钮
    # 选择类型/持续时间
    web_page.find_by_xpath(Xpath.CategorySelect).click() # 点击类型下拉框
    web_page.find_by_xpath(Xpath.CategoryClearLink).click() # 点击无清空类型选项
    for option in web_page.find_all_by_xpath(Xpath.CategoryOptions):
        if option.get_attribute('label').replace(' ', '') in category_name:
            option.click()
    web_page.find_by_xpath(Xpath.CategoryApplyBtn).click() # 点击类型应用按钮
    # 选择日期
    web_page.find_by_xpath(Xpath.DateSelect).click() # 点击日期下拉框
    for option in web_page.find_all_by_xpath(Xpath.DateOptions):
        option_name = option.get_text().replace(' ', '')
        if option_name == date_name:
            option.click() # 如果日期范围名称是'过去30天'或者'最近6个月'，直接点击选项
            break
        elif date_name == Option.DateOptionList[2]:
            # 如果日期范围名称是'确切日期'，输入开始日期和结束日期
            web_page.find("screenshot_promotion_detail_开始日期输入框").clipboard_input(text=transform_date(start_date))
            web_page.find("screenshot_promotion_detail_开始日期输入框").click(anchor=('topRight', 5, 0))
            web_page.find("screenshot_promotion_detail_结束日期输入框").clipboard_input(text=transform_date(end_date))
            web_page.find("screenshot_promotion_detail_结束日期输入框").click(anchor=('topRight', 5, 0))
            web_page.find_by_xpath(Xpath.DateApplyBtn).click() # 点击日期应用按钮
            break
    # 选择Amazon Stores
    web_page.find_by_xpath(Xpath.StoreSelect).click() # 点击Amazon Stores下拉框
    web_page.find_by_xpath(Xpath.StoreOptionAll).click() # 点击Amazon Stores下拉框选项所有，清空商城选项
    for option in web_page.find_all_by_xpath(Xpath.StoreOptions):
        if option.get_text() in store_name:
            option.click()
    web_page.find_by_xpath(Xpath.StoreApplyBtn).click() # 点击商城应用按钮


def screenshot_pages(web_page:WebBrowser, file_name:str, file_folder:str, domain:str, product_type:str):
    # 获取总行数
    total_items = web_page.find_by_xpath(Xpath.PageNavigation).get_attribute('total-items')
    # 获取每页总行数
    page_items = web_page.find_by_xpath(Xpath.PageNavigation).get_attribute('items-per-page')
    pages = math.ceil(int(total_items)/int(page_items))
    # print(pages)
    result_list = []
    promotion_detail_link_list = [] # "正在进行"、"即将推出"、"需要注意"消费群体状态标签的促销详情页链接列表
    for index in range(pages):
        # 获取每页中的"正在进行"、"即将推出"、"需要注意"消费群体状态标签的促销详情页链接
        for item in web_page.find_all_by_xpath(Xpath.PromotionDetailLinks):
            promotion_detail_link_list.append(domain + item.get_attribute("href"))
        # 点击下一页
        web_page.find("screenshot_promotion_detail_下一页按钮").click()
        sleep(2)
        index += 1
    # 遍历"正在进行"、"即将推出"、"需要注意"消费群体状态标签的促销详情页链接列表，截图促销详情和参与的商品
    for item_link in promotion_detail_link_list:
        web_page.navigate(item_link)
        web_page.wait_load_completed()
        sleep(5)
        # 点击商品类别的筛选按钮
        for item_button in web_page.find_all_by_xpath(Xpath.DetailProductBtn):
            # 正则匹配所有中文字符（\u4e00-\u9fa5 是中文Unicode范围），提取后拼接
            item_button_label = ''.join(re.findall(r'[\u4e00-\u9fa5]+', item_button.get_attribute('label')))
            if item_button_label == product_type:
                item_button.click()
                # 获取总行数
                detail_total_items = web_page.find_by_xpath(Xpath.DetailPageNavigation).get_attribute('total-items')
                # 获取每页总行数
                detail_page_items = web_page.find_by_xpath(Xpath.DetailPageNavigation).get_attribute('items-per-page')
                detail_pages = math.ceil(int(detail_total_items)/int(detail_page_items))
                # print(detail_pages)
                # 如果未找到任何结果，也截取空结果图
                if detail_pages == 0:
                    detail_pages = 1
                for detail_index in range(detail_pages):
                    file_name = web_page.find_by_xpath(Xpath.DetailPromotionName).get_text() + '_' + product_type + '_第' + str(detail_index+1) + '页_促销详情和参与的商品截图.png'
                    # 移除文件名中的非法字符
                    file_name = re.sub(r'[\\/:*?"<>|]', '', file_name)
                    web_page.scroll_to(location='top')
                    sleep(2)
                    web_page.find_by_xpath(Xpath.ScreenshotArea).screenshot(str(file_folder), filename=file_name)
                    result_list.append(str(file_folder) + '\\' + file_name)
                    web_page.find("screenshot_promotion_detail_促销详情页下一页按钮").click() # 点击促销详情页下一页
                    sleep(2)
                    detail_index += 1
                break
    return result_list


def screenshot_promotion_detail(web_page: WebBrowser, status_name: list, category_name: list, date_name: str, start_date: str, end_date: str, store_name: list, product_type: str, file_folder: str, file_name: str):
    # 促销价格报错信息整理
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page, status_name, category_name, date_name, store_name, product_type)

    # 进入管理报价页面
    domain = get_domain(web_page)
    url = f"{domain}/merchandising-new"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')
    
    # 设置过滤参数
    web_page.wait_load_completed(timeout=20)
    sleep(5)
    set_filter_parameters(web_page, status_name, category_name, date_name, start_date, end_date, store_name)

    # 截图促销详情和参与的商品
    result_list = screenshot_pages(web_page, file_name, file_folder, domain, product_type)
    return result_list


def test_screenshot_promotion_detail():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="superbrowser")
    status_name = ['正在进行', '即将推出', '需要注意'] # 状态名称
    category_name = ['Z划算', '秒杀', '精选优惠'] # 类型名称
    date_name = '确切日期' # 日期名称
    start_date = '2025-03-10' # 开始日期
    end_date = '2025-09-08' # 结束日期
    store_name = ['英国'] # 商城名称
    product_type = '出错的参与商品' # 商品类别
    
    file_folder = r"D:\\"  # 截图文件夹路径
    file_name = ""  # 截图文件名

    file_path = screenshot_promotion_detail(web_page, status_name, category_name, date_name, start_date, end_date, store_name, product_type, file_folder, file_name)
    print(file_path)
    exit()


def main(args):
    # 测试代码入口
    test_screenshot_promotion_detail()

    # 业务代码入口
    web_page = args.get('web_page')
    status_name = args.get('status_name') # 状态名称
    category_name = args.get('category_name') # 类型名称
    date_name = args.get('date_name') # 日期名称
    start_date = args.get('start_date') # 开始日期
    end_date = args.get('end_date') # 结束日期
    store_name = args.get('store_name') # 商城名称
    product_type = args.get('product_type') # 商品类别
    
    file_folder = args.get('file_folder')  # 截图文件夹路径
    file_name = args.get('file_name')  # 截图文件名
    file_path = screenshot_promotion_detail(web_page, status_name, category_name, date_name, start_date, end_date, store_name, product_type, file_folder, file_name)
    args['file_path'] = file_path
