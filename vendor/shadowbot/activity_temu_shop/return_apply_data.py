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

def set_params(web_page, odds_number, start_time, end_time, SKC, stock):

    Tools.check_web(web_page, 'wms/stock-mgt/return-apply')
    if odds_number != '':
        web_page.find_by_xpath("//span[text()='申请单号']/ancestor::label/../..//following-sibling::div").input(odds_number)
    if SKC != '':
        web_page.find_by_xpath("//span[text()='SKC ID']/ancestor::label/../..//following-sibling::div").input(SKC)
    if stock != '':
        web_page.find_by_xpath("//span[text()='备货单号']/ancestor::label/../..//following-sibling::div").input(stock)

    if start_time != '':
        web_page.find_by_xpath("//*[text()='创建时间']//ancestor::div[@data-testid='beast-core-grid-col-wrapper']/div/div[2]").click()
        date_iframe = web_page.find_by_xpath('//div[@data-testid="beast-core-portal-main"]')
        select_date(web_page, date_iframe, start_time, end_time)

    web_page.find_by_xpath("//*[text()='查询']").click()


def get_data(web_page):

    try:
        web_page.find_by_xpath("//*[text()='暂无数据']",timeout=2)
        return "当前条件下无数据"
    except:
        web_page.find_by_xpath("//*[text()='每页']//following-sibling::div[@data-testid='beast-core-select']").click()
        elems = web_page.find_all_by_xpath("//*[text()='200']")
        for elem in elems:
            if elem.is_displayed():
                elem.click()
        # max_page = web_page.find_by_xpath("//ul/li[last()-1]").get_text()
        # numbers = re.findall(r'\d+', max_page)[0]
        # for page in range(int(numbers)-1):
        store_name = web_page.find_by_xpath("//div[contains(@class,'account-info_accountInfo')]/div[2]/div/div[1]/span").get_text()
        trs = web_page.find_all_by_xpath("//tbody/tr")
        for index, tr in enumerate(trs):
            data_list = []
            tds = tr.find_all_by_xpath("./td")
            tds_data = [td.get_text() for td in tds[1:-1]]
            data_list.extend(tds_data)
            data_list.insert(0, store_name)
            databook.append_row(data_list, begin_column_name = 'A')
        # web_page.find_by_xpath("//ul/li[last()]").click()
            

def run(web_page, odds_number, start_time, end_time, SKC, stock):

    set_params(web_page, odds_number, start_time, end_time, SKC, stock)
    get_data(web_page)


def main(args):
    
    web_page = args.get("web_page")
    odds_number = args.get("odds_number", '')
    start_time = args.get("start_time", "")
    end_time = args.get("end_time", "")
    SKC = args.get("SKC", '')
    stock = args.get("stock", '')

    row_count = databook.get_row_count()
    if row_count == 0:
        databook.set_row(1, ['店铺名称', '申请单号', '申请类型', 'SKC ID', '备货单号', '创建时间', '申请原因', '申请状态', '申请人'], begin_column_name = 'A')
    
    web_page = web.get_active(mode='chrome')
    run(web_page, odds_number, start_time, end_time, SKC, stock)

    
