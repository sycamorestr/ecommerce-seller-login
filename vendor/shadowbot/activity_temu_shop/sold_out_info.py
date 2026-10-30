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
from xbot_extensions.web_action.select_date import select_date

def set_params(web_page, available_start_day, available_end_day):

    Tools.check_web(web_page, 'main/board/sku-sale-out')

    if available_start_day != '':
        web_page.find_by_xpath("//*[text()='库存可售天数']//following-sibling::div/div/div[1]//input").input(available_start_day)

    if available_end_day != '':
        web_page.find_by_xpath("//*[text()='库存可售天数']//following-sibling::div/div/div[2]//input").input(available_end_day)

    web_page.find_by_xpath("//*[text()='查询']").click()


def get_data(web_page):
    try:
        web_page.find_by_xpath("//div[contains(@class,'TB_body')]//*[text()='暂无数据']",timeout=2)
        return "当前条件下无数据"
    except:
        web_page.find_by_xpath("//*[text()='每页']//following-sibling::div[@data-testid='beast-core-select']").click()
        elems = web_page.find_all_by_xpath("//*[text()='100']")
        for elem in elems:
            if elem.is_displayed():
                elem.click()
                
        trs = web_page.find_all_by_xpath("//tbody/tr")
        for index, tr in enumerate(trs):
            data_list = []
            tds = tr.find_all_by_xpath("./td")
            title = tds[0].find_by_xpath("./div/div/div[2]").get_text()
            data_list.append(title)
            tds_data = [td.get_text() for td in tds[1:-1]]
            data_list.extend(tds_data)
            databook.append_row(data_list, begin_column_name = 'A')

            

def run(web_page, available_start_day, available_end_day):

    set_params(web_page, available_start_day, available_end_day)
    get_data(web_page)
            

def main(args):

    web_page = args.get("web_page")
    available_start_day = args.get("available_start_day", '')
    available_end_day = args.get("available_end_day", '')
    databook.clear()

    databook.set_row(1, ['商品信息', '商品SKC信息', '近7天SKU销量', '近7天SKC销量', '仓内可用库存', '仓内暂不可用库存',
         '已发货库存', '合计库存', '库存可售天数', '近7天销售损失（CNY）', '近7天销售损失占比', 
         '近7天sku已支付销量', '待发货备货单数量', '降低售罄引导'], begin_column_name = 'A')
    # web_page = web.get_active(mode='chrome')

    run(web_page, available_start_day, available_end_day)

    
