# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from xbot.selector import Selector
from .import package
from .package import variables as glv
from .utils import Tools

def gen_selector(xpath):
    xpaths = xpath.split(">>")
    data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': xpaths}}
    selector = Selector(data)
    return selector

def get_reconciliation(web_page, start_time, end_time, capital_flow,
                financial_type, fund_mix, fund_max, confirm_download, file_folder, file_name):
    Tools.check_web(web_page, 'labor/bill')
    Tools.select_date(web_page, start_time, end_time)
    web_page.find_by_xpath("//span[text()='确认']").click()

    if capital_flow:
        web_page.find_by_xpath("//*[text()='资金流向']//ancestor::div[@data-testid='beast-core-grid-col-wrapper'][2]/div[1]/div[2]").click()
        capital_flow_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")
        Tools.click_dropdown(web_page, capital_flow, capital_flow_elems)

    if financial_type:
        web_page.find_by_xpath("//*[text()='账务类型']//ancestor::div[@data-testid='beast-core-grid-col-wrapper'][2]/div[1]/div[2]").click()
        financial_type_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")
        Tools.click_dropdown(web_page, financial_type, financial_type_elems)

    fund_input_list = web_page.find_all_by_xpath("//input[@placeholder='请输入']")
    if fund_mix != '':
        fund_input_list[0].input(fund_mix)
    if fund_max != '':
        fund_input_list[1].input(fund_max)

    web_page.find_by_xpath("//span[text()='查询']").click()
    
    # 等待加载
    load_sel = Tools.gen_selector('//div[contains(@class,"TB_loading")]')
    web_page.wait_disappear(load_sel)

    web_page.find_by_xpath("//span[text()='导出']").click()

    # web_page.find_by_xpath('//*[text()="导出列表"]').click()

    web_page.find_by_xpath('//*[text()="确认"]').click()

    # 判断是否重复导出
    flag_xpath = '//div[1][normalize-space(.)="当前筛选条件的导出任务已创建, 请勿重复创建"]'
    flag = web_page.wait_appear(gen_selector(flag_xpath), timeout=2)
    if flag:
        web_page.wait_disappear(gen_selector(flag_xpath), timeout=4)
        export_history_xpath = '//span[text()="导出历史"]'
        web_page.find_by_xpath(export_history_xpath, timeout=2).click()
    
    if confirm_download:
        sleep(2)
        for retry in range(100):
            target_report = web_page.find_by_xpath("//div[contains(@class,'exportHistoryList')]/div[1]//button//span[1]")
            if '生成中' in target_report.get_text():
                sleep(2)
                web_page.find_by_xpath("//span[text()='刷新']").click()
                continue
            else:
                target_report.click()
                web.handle_save_dialog(file_folder=file_folder, file_name=file_name, mode=web_page.product_name)
                break
        return file_folder + '\\' + file_name

def main(args):
    
    web_page = args.get("web_page",'')
    start_time = args.get("start_time", '2024-12-12')
    end_time = args.get("end_time", '2024-12-12')
    capital_flow = args.get("capital_flow", '流出')
    financial_type = args.get("financial_type", ['提现','结算'])
    fund_mix = args.get("fund_mix", '10')
    fund_max = args.get("fund_max", '100')
    confirm_download = args.get('confirm_download', True)
    file_folder = args.get("file_folder", r'C:\Users\11758\Desktop\test')
    file_name = args.get("file_name", r'text.xlsx')


    # web_page = web.get_active(mode='chrome')
    file_path = get_reconciliation(web_page, start_time, end_time, capital_flow,
                financial_type, fund_mix, fund_max, confirm_download, file_folder, file_name)
    args['file_path'] = file_path
