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

def set_params(web_page, odds_number, start_time, end_time, status, discard_type, reason):

    Tools.check_web(web_page, 'wms/stock-mgt/return-receipt-mgt')
    if odds_number != '':
        web_page.find_by_xpath("//span[text()='退货单号']/ancestor::label/../..//following-sibling::div").input(odds_number)

    if start_time != '':
        web_page.find_by_xpath("//*[text()='创建日期']//ancestor::div[@data-testid='beast-core-grid-col-wrapper']/div/div[2]").click()
        date_iframe = web_page.find_by_xpath('//div[@data-testid="beast-core-portal-main"]')
        select_date(web_page, date_iframe, start_time, end_time)

    if status != '':
        web_page.find_by_xpath("//span[text()='弃货状态']/ancestor::label/../..//following-sibling::div").click()
        flow_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")
        Tools.down_select(web_page, status, flow_elems)

    if discard_type != '':
        web_page.find_by_xpath("//span[text()='退货类型']/ancestor::label/../..//following-sibling::div").click()
        flow_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")
        Tools.down_select(web_page, discard_type, flow_elems)

    if reason != '':
        web_page.find_by_xpath("//span[text()='退货原因']/ancestor::label/../..//following-sibling::div").click()
        flow_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")
        Tools.down_select(web_page, reason, flow_elems)

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
        trs = web_page.find_all_by_xpath("//tbody/tr")
        for index, tr in enumerate(trs):
            data_list = []
            tds = tr.find_all_by_xpath("./td")
            tds_data = [td.get_text() for td in tds[1:-1]]
            data_list.extend(tds_data)
            databook.append_row(data_list, begin_column_name = 'A')
        # web_page.find_by_xpath("//ul/li[last()]").click()
            

def run(web_page, odds_number, start_time, end_time, status, discard_type, reason):

    set_params(web_page, odds_number, start_time, end_time, status, discard_type, reason)
    get_data(web_page)


def main(args):
    
    web_page = args.get("web_page")

    odds_number = args.get("odds_number", '123')
    start_time = args.get("start_time", "2025-02-01")
    end_time = args.get("end_time", "2025-02-03")
    status = args.get("status", "待确认")
    discard_type = args.get("discard_type", "抽检退供")
    reason = args.get("reason", "其他")
    databook.clear()
    databook.set_row(1, ['退货单号', '剩余处理时长', '退货子仓', '退货子仓地址', '退货子仓联系人', '手机号', '弃货确认状态', '退货原因', '退货数量(件)', '创建时间'], begin_column_name = 'A')
    # web_page = web.get_active(mode='chrome')

    run(web_page, odds_number, start_time, end_time, status, discard_type, reason)

    
