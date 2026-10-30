# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from xbot.app import databook
from .import package
from .package import variables as glv
from .utils import Tools
import re
from xbot_extensions.web_action.select_date import select_date

from xbot.selector import Selector



def set_params(web_page, SKU, package_num, start_time, end_time, stock):

    Tools.check_web(web_page, 'wms/stock-mgt/return-package-detail')
    if SKU != '':
        web_page.find_by_xpath("//span[text()='SKU']/ancestor::label/../..//following-sibling::div").input(SKU)
    if package_num != '':
        web_page.find_by_xpath("//span[text()='退货包裹号']/ancestor::label/../..//following-sibling::div").input(package_num)
    if stock != '':
        web_page.find_by_xpath("//span[text()='备货单号']/ancestor::label/../..//following-sibling::div").input(stock)

    if start_time != '':
        web_page.find_by_xpath("//*[text()='出库时间']//ancestor::div[@data-testid='beast-core-grid-col-wrapper']/div/div[2]").click()
        date_iframe = web_page.find_by_xpath('//div[@data-testid="beast-core-rangePicker-dropdown-contentRoot"]')
        select_date(web_page, date_iframe, start_time, end_time)
        web_page.find_by_xpath('//span[text()="确认"]').click()

    web_page.find_by_xpath("//*[text()='查询']").click()


def get_data(web_page:xbot.web.WebBrowser):
    data = []

    # 1. 如果找到暂无数据元素, 返回空列表
    no_data_ele = web_page.find_all_by_xpath("//*[text()='暂无数据']", timeout=2)
    if len(no_data_ele) > 0:
        return data

    # 2, 将网页表格中的数据批量抓取
    # 设置数据的 title
    data.append(['店铺', 'SPU', 'SKU', '商品信息', '备货单号', '退货原因', '退货包裹号', 'SKU件数', '出库时间'])
    # 设置分页数量为200
    web_page.find_by_xpath("//*[text()='每页']//following-sibling::div[@data-testid='beast-core-select']").click()
    web_page.find_by_xpath("//ul/li/span[text()='200']").click()

    # 获取店铺的名称
    store_name = web_page.find_by_xpath("//div[contains(@class,'account-info_accountInfo')]/div[2]/div/div[1]/span").get_text()

    next_page_xpath ='//li[@data-testid="beast-core-pagination-next"]' 
    while 1:
        
        table_ele = web_page.find_all_by_xpath("//tbody/tr")
        for row in table_ele:
            row_data = [td.get_text() for td in row.find_all_by_xpath("./td")] # 第一列是个复选框
            # 将第一列换成店铺名称
            row_data[0] = store_name
            data.append(row_data[:-1])

        # 翻页场景进行处理
        next_page_ele = web_page.find_all_by_xpath(next_page_xpath, timeout=2)
        if len(next_page_ele) > 0 and "disabled" not in next_page_ele[0].get_attribute("class"):
            web_page.find_by_xpath(next_page_xpath).click()
        else:
            break

    return data
            



def main(args):
    
    web_page = args.get("web_page")
    SKU = args.get("SKU", '')
    start_time = args.get("start_time", "2025-03-10")
    end_time = args.get("end_time", "2025-03-20")
    package_num = args.get("package_num", '')
    stock = args.get("stock", '')

    set_params(web_page, SKU, package_num, start_time, end_time, stock)
    data = get_data(web_page)
    args["data"] = data

    
