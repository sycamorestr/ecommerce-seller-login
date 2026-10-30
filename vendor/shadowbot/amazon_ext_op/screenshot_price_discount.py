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
from .activities_utils import download_handler


class Xpath:
    # 大区切换按钮组
    RegionButtons = "//*[@id='root']//kat-button-group[@class='region-button']/kat-button"
    # 事件切换按钮组
    EventButtons = "//*[@class='event-button-group']/kat-button-group/kat-button"
    # 国家/地区下拉框
    CountySelect = "//*[@class='filters-container']/kat-region-selector"
    # 状态下拉框
    StatusSelect = "//*[@class='filters-container']/kat-dropdown[@class='status-filter']"
    # 运行日期下拉框
    RunDateSelect = "//*[@class='filters-container']//kat-dropdown[@class='date-range-filter']"
    # 运行日期应用按钮
    RunDateApply = '//*[local-name()="kat-button"][contains(@class, "apply-button")]'
    # 运行日期下拉项
    RunDateItem = "//*[@class='filters-container']//div[@class='date-range-wrapper']"
    # 消费群体类型下拉框
    CustomerTypeSelect = "//*[@class='filters-container']/kat-dropdown[2]"
    # 搜索按钮
    SearchButton = "//*[@id='root']//kat-button[@class='search-button']"
    # 截图区域元素
    ScreenshotXpath = '//*[@id="root"]//div[@role="treegrid"]'
    # 分页导航组
    PageNavigation = "//*[@id='root']//kat-pagination"
    # "进行中"状态的商品详情页链接
    ProgressProductLink = '//*[contains(@id, "cell-promotionTitle")]//kat-badge[@type="success"]/parent::div/preceding-sibling::kat-link'
    # 商品详情页链接
    ProductDetailLink = '//*[contains(@id, "cell-promotionTitle")]//kat-link'
    # 编辑下拉框按钮
    EditSelectBtn = '//*[@class="dashboard"]//kat-dropdown-button[@class="action-dropdown"]'
    # 价格折扣商品详情页_促销标题
    DetailPromotionTitle = '//kat-panel-wrapper//div[@class="promotion-title"]'
    # 价格折扣商品详情页_导出到模板链接按钮
    DetailDownloadBtn = '(//*[@class="bulk-options"]//kat-link)[1]'


class Option:
    # 大洲地区列表
    region_list = ["美洲","亚太地区","中东和北非","欧洲","印度"]
    # 事件名称列表
    event_list = ["非动作","动作"]
    # 国家/地区名称列表（待补充）
    country_list = ['美洲', '加拿大', '墨西哥', '美国',
                    '欧洲', '比利时', '法国', '德国', '意大利', '荷兰', '波兰', '西班牙', '瑞典', '英国', '']
    # 状态名称列表
    status_list = ['全选', '即将开始', '处理中', '进行中', '已取消', '失败', '已结束', '注意事项', '']
    # 消费群体类型列表
    custom_list = ['全选', '所有买家', 'Prime买家', '']


def transform_date(date: str):
    # 转换日期格式
    try:
        if date !='':
            result = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        else:
            result = date
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
    if not web_page.wait_appear(gen_selector(Xpath.SearchButton), timeout=30):
        raise Exception(
            f"进入价格折扣页面失败，未找到搜索按钮： {Xpath.SearchButton}"
        )


def input_parameter_valid(web_page:WebBrowser,region_name:str,event_name:str,country_name:list,status_name:list,start_date:str,end_date:str,custom_type:list):
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (region_name in Option.region_list), f"大洲地区名称错误：{region_name}" # 如果大洲名称在大洲列表中，正常执行；否则触发异常
    assert (event_name in Option.event_list), f"事件名称错误：{event_name}"
    assert all(item in Option.country_list for item in country_name), f"国家/地区名称错误：{country_name}"
    assert all(item in Option.status_list for item in status_name), f"状态名称错误：{status_name}"
    assert all(item in Option.custom_list for item in custom_type), f"消费群体类型名称错误：{custom_type}"


def set_filter_parameters(web_page:WebBrowser,region_name:str,event_name:str,country_name:list,status_name:list,start_date:str,end_date:str,custom_type:list):
    # 设置筛选配置
    # 设置大洲地区名称（单选）
    for option in web_page.find_all_by_xpath(Xpath.RegionButtons):
        if option.get_attribute("label") == region_name:
            option.click()
            break

    # 设置事件名称（单选）
    for option in web_page.find_all_by_xpath(Xpath.EventButtons):
        if option.get_attribute("label") == event_name:
            option.click()
            break

    # 设置国家/地区名称（多选）
    try:
        web_page.find_by_xpath(Xpath.CountySelect,timeout=2).click()
        # 如果是全选项并被选中，要取消全选
        country_all = web_page.find(get_shadowroot_element(web_page,"screenshot_price_discount_国家地区全选选项"))
        if country_all.get_attribute('aria-selected')=="true":
            country_all.click()
        country_name_list = web_page.find_all(get_shadowroot_element(web_page,"screenshot_price_discount_国家地区选项"))
        country_all.dblclick()
        for option in country_name_list:
            if option.get_text() in country_name:
                option.click()
        web_page.find(get_shadowroot_element(web_page,"screenshot_price_discount_国家地区按钮组")).click(anchor=('bottomRight',-40,-30))
    except UIAError as e:
        pass

    # 设置状态名称（多选）
    web_page.find_by_xpath(Xpath.StatusSelect).click()
    status_name_list = web_page.find_all(get_shadowroot_element(web_page,"screenshot_price_discount_状态选项"))
    for option in status_name_list:
        # 如果是全选项并被选中，要取消全选
        if option.get_text().replace(" ", "") == '全选' and option.get_attribute('aria-selected')=="true":
            option.click()
            break
        # 如果是非全选项但被选中，也要取消勾选
        if option.get_text().replace(" ", "") != '全选' and option.get_attribute('aria-selected')=="true":
            option.click()
    for option in status_name_list:
        if option.get_text().replace(" ", "") in status_name:
            option.click()
    web_page.find(get_shadowroot_element(web_page,"screenshot_price_discount_状态应用按钮")).click()

    try:
        # 设置开始运行日期（输入框）
        web_page.find_by_xpath(Xpath.RunDateSelect,timeout=2).click()
        web_page.find(get_shadowroot_element(web_page,"screenshot_price_discount_开始运行日期输入框")).input(transform_date(start_date))
        web_page.find_by_xpath(Xpath.RunDateItem).click(anchor=('topRight',-30,30))

        # 设置结束运行日期（输入框）
        web_page.find(get_shadowroot_element(web_page,"screenshot_price_discount_结束运行日期输入框")).input(transform_date(end_date))
        web_page.find_by_xpath(Xpath.RunDateItem).click(anchor=('topRight',-30,30))
        web_page.find_by_xpath(Xpath.RunDateApply).click()
    except UIAError as e:
        pass

    # 设置消费群体类型（多选）
    web_page.find_by_xpath(Xpath.CustomerTypeSelect).click()
    custom_type_list = web_page.find_all(get_shadowroot_element(web_page,"screenshot_price_discount_消费群体类型选项"))
    for option in custom_type_list:
        # 如果是全选项并被选中，要取消全选
        if option.get_text().replace(" ", "") == '全选' and option.get_attribute('aria-selected')=="true":
            option.click()
            break
        # 如果是非全选项但被选中，也要取消勾选
        if option.get_text().replace(" ", "") != '全选' and option.get_attribute('aria-selected')=="true":
            option.click()
    for option in custom_type_list:
        if option.get_text().replace(" ", "") in custom_type:
            option.click()
    web_page.find(get_shadowroot_element(web_page,"screenshot_price_discount_消费群体类型应用按钮")).click()
    web_page.find_by_xpath(Xpath.CustomerTypeSelect).click(anchor=('topRight', 10, 0))


def screenshot_pages(web_page:WebBrowser, file_name:str, file_folder:str, domain:str):
    # 获取总行数
    total_items = web_page.find_by_xpath(Xpath.PageNavigation).get_attribute('total-items')
    # 获取每页总行数
    page_items = web_page.find_by_xpath(Xpath.PageNavigation).get_attribute('items-per-page')
    pages = math.ceil(int(total_items)/int(page_items))
    # print(pages)
    # 如果未找到任何结果，也截取空结果图
    if pages == 0:
        pages = 1
    result_list = []
    file_name_copy = file_name
    progress_product_link_list = [] # "进行中"状态的商品详情页链接列表
    for index in range(pages):
        file_name = file_name + '_第' + str(index+1) + '页.png'
        # 价格折扣查询结果区域截图
        screenshot_pic = web_page.find_by_xpath(Xpath.ScreenshotXpath)
        screenshot_pic.screenshot(str(file_folder), filename=file_name)
        # # 获取区域截图尺寸
        # image_width,image_height=process7(picture_path=str(file_folder)+'\\'+file_name)
        # # 图片裁剪
        # result_path = process2(picture_path=str(file_folder)+'\\'+file_name,left=0,top=0,width=image_width//2+100,height=image_height,save_name=str(file_folder)+'\\'+file_name)
        # result_list.append(result_path)
        #更新
        result_list.append(str(file_folder)+'\\'+file_name)
        # 获取每页中的"进行中"状态的商品详情页链接
        for item in web_page.find_all_by_xpath(Xpath.ProgressProductLink):
            progress_product_link_list.append(domain + item.get_attribute("href"))
        xbot.win32.mouse_move(point_x=1000, point_y=800, relative_to='window') # 移动鼠标到当前打开窗口的中心
        xbot.win32.mouse_wheel(wheel_direction='down', wheel_times=25) # 滚动表格滑动条至底部
        # 滚动鼠标后，再次获取每页后面中的"进行中"状态的商品详情页链接
        for item in web_page.find_all_by_xpath(Xpath.ProgressProductLink):
            last_item_link = domain + item.get_attribute("href")
            if last_item_link not in progress_product_link_list:
                progress_product_link_list.append(last_item_link)
        # 点击下一页
        web_page.find("screenshot_price_discount_下一页按钮").click()
        sleep(2)
        index += 1
        file_name = file_name_copy
    # 遍历"进行中"状态的商品详情页链接列表，下载对应的模板文件
    for item_link in progress_product_link_list:
        web_page.navigate(item_link)
        web_page.wait_load_completed()
        download_file_name = web_page.find_by_xpath(Xpath.DetailPromotionTitle).get_text().replace(' ', '') # 获取价格折扣商品详情页_促销标题
        web_page.find_by_xpath(Xpath.DetailDownloadBtn).click() # 点击价格折扣商品详情页_导出到模板链接按钮
        try:
            download_file_path = download_handler(web_page, file_folder, download_file_name) # 下载模板文件
        except:
            # 重试
            web_page.find_by_xpath(Xpath.DetailDownloadBtn).click() # 点击价格折扣商品详情页_导出到模板链接按钮
            download_file_path = download_handler(web_page, file_folder, download_file_name) # 下载模板文件
        result_list.append(download_file_path)
    return result_list


# 价格折扣报错截图
def screenshot_price_discount(web_page:WebBrowser,region_name:str,event_name:str,country_name:str,status_name:str,start_date:str,end_date:str,custom_type:str,file_folder:str,file_name:str):
    # 输入参数转换
    country_name = [item.strip() for item in country_name.split(',')]
    status_name = [item.strip() for item in status_name.split(',')]
    custom_type = [item.strip() for item in custom_type.split(',')]
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page,region_name,event_name,country_name,status_name,start_date,end_date,custom_type)

    # 进入价格折扣页面
    domain = get_domain(web_page)
    url = f"{domain}/discounts"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置筛选配置
    web_page.wait_load_completed(timeout=30) # 等待网页加载完成
    set_filter_parameters(web_page,region_name,event_name,country_name,status_name,start_date,end_date,custom_type)

    # 分页截图
    result_list = screenshot_pages(web_page, file_name, file_folder, domain)
    return result_list


def test_screenshot_price_discount():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="chrome")
    region_name = '欧洲' # 大洲地区名称
    event_name = '非动作' # 事件名称
    country_name = '' # 国家/地区名称
    status_name = '' # 状态名称
    start_date = '' # 开始运行日期
    end_date = '' # 结束运行日期
    custom_type = '' # 消费群体类型
    file_folder = r"C:\Users\\Administrator\Desktop\test" # 截图文件夹路径
    file_name = "test1" # 截图文件名
    
    result_path = screenshot_price_discount(web_page,region_name,event_name,country_name,status_name,start_date,end_date,custom_type,file_folder,file_name)
    print(result_path)
    exit()


def main(args):
    # 测试代码入口
    test_screenshot_price_discount()

    # 业务代码入口
    web_page = args.get('web_page')
    region_name = args.get('region_name') # 大洲地区名称
    event_name = args.get('event_name') # 事件名称
    country_name = args.get('country_name') # 国家/地区名称
    status_name = args.get('status_name') # 状态名称
    start_date = args.get('start_date') # 开始运行日期
    end_date = args.get('end_date') # 结束运行日期
    custom_type = args.get('custom_type') # 消费群体类型
    file_folder = args.get('file_folder') # 截图文件夹路径
    file_name = args.get('file_name') # 截图文件名
    
    result_path = screenshot_price_discount(web_page,region_name,event_name,country_name,status_name,start_date,end_date,custom_type,file_folder,file_name)
    args['result_path'] = result_path