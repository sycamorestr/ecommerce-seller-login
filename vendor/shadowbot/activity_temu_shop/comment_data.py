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

def handle_dropdown(target_text, elem_list):
    """处理横像复选框"""
    for elem in elem_list:
        check_box_elem = elem.find_by_xpath("./..")
        if elem.get_text() == target_text and check_box_elem.get_attribute('data-checked') == 'false':
            elem.click()
            break

def get_data(web_page, start_time, end_time, level):
    Tools.check_target_web(web_page, 'main/evaluate/evaluate-list')

    """选择日期"""
    if start_time:
        web_page.find_by_xpath("//*[text()='自定义']").click()
        date_frame = web_page.find_by_xpath("//section[contains(@class,'contentPicker')]")
        select_date(web_page, date_frame, start_time, end_time)

    """选择星级"""
    elem_list = web_page.find_all_by_xpath("//*[text()='评价星级']//following-sibling::div//div[contains(text(),'星')]")
    if level != '全部' and level != "":
        if isinstance(level, str):
            handle_dropdown(level, elem_list)
        elif isinstance(level, list):
            for text in level:
                handle_dropdown(text, elem_list)

    """设置页面展示的数据量"""
    try:
        web_page.find_by_xpath("//*[text()='暂无数据']", timeout=3)
        print("该条件下暂无数据")
        return
    except:
        web_page.find_by_xpath("//*[text()='每页']//following-sibling::div[@data-testid='beast-core-select']").click()
        elems = web_page.find_all_by_xpath("//*[text()='200']")
        for elem in elems:
            if elem.is_displayed():
                elem.click()
                break
        store_name = web_page.find_by_xpath("//div[contains(@class,'account-info_accountInfo')]/div[2]/div/div[1]/span").get_text()
        trs = web_page.find_all_by_xpath("//tbody/tr")
        for index, tr in enumerate(trs):
            data_list = []
            tds = tr.find_all_by_xpath("./td")
            title = tds[0].find_by_xpath(".//a").get_text()
            score = tds[1].get_text()
            comment = tds[2].find_by_xpath("./div/div/div[2]").get_text()
            comment_date = tds[2].find_by_xpath(".//span[contains(text(),'评价时间')]/..").get_text().split("：")[1]
            data_list.append(store_name)
            data_list.append(title)
            data_list.append(score)
            data_list.append(comment)
            data_list.append(comment_date)
            databook.append_row(data_list, begin_column_name = 'A')
    

def main(args):
    
    web_page = args.get("web_page")
    start_time = args.get("start_time", "2025-02-10")
    end_time = args.get("end_time", "2025-02-20")
    level = args.get("level", '')
    # web_page = web.get_active(mode='chrome')
    row_count = databook.get_row_count()
    if row_count == 0:
        databook.set_row(1, ['店铺名称', '商品信息', '评价星级', '评价信息', '评价时间'], begin_column_name = 'A')
    get_data(web_page, start_time, end_time, level)
