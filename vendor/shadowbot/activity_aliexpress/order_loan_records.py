# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import os
from xbot import print, sleep
from . import package
from .package import variables as glv
from xbot import web
from xbot import win32
from xbot.selector import Selector
from .utils import check_enterprise


def handle_order_loan_records(web_page: xbot.web.WebBrowser, order_type: str, start_date: str, end_date: str, account_type: str, save_directory: str, file_name: str) -> tuple:
    """资金结算报表下载功能
    :param web_page: xbot.web.WebBrowser, 网页浏览器对象
    :param order_type: str, 订单类型选择（如：非俄罗斯订单、俄罗斯订单）
    :param start_date: str, 开始日期（格式：YYYY-MM-DD）
    :param end_date: str, 结束日期（格式：YYYY-MM-DD）
    :param account_type: str, 账户类型选择（如：CNY账户、USD账户）
    :param save_directory: str, 文件保存目录路径
    :param file_name: str, 保存的文件名称
    :return: tuple, (文件路径, 放款记录字典)
    """
    assert os.path.splitext(file_name)[-1].lower() in ['.xlsx'], f"{file_name} 文件名不合法, 请以 .xlsx 为后缀"
    # 页面导航
    url = 'https://csp.aliexpress.com/m_apps/fund-center/popFundCenter?channelId=210070#/home/orderRecord/loan'
    current_url = web_page.get_url()
    
    if current_url != url:
        web_page.navigate(url)
        sleep(3)  # 等待页面加载

    enter_xpath = '//div[@id="rc-tabs-1-tab-loan"]//span[contains(@class, "ait-tabs-tab-inner-text")]'
    web_page.find_by_xpath(enter_xpath).click()

    # 输入开始日期
    start_date_input_xpath = '//*[@id="incomeTime"]'
    web_page.find_by_xpath(start_date_input_xpath).input(start_date, simulative=True)
    win32.send_keys(keys='{enter}', send_key_delay=50, delay_after=1)
    sleep(0.5)

    # 输入结束日期
    end_date_input_xpath = '//form//div[3]/input'
    web_page.find_by_xpath(end_date_input_xpath).input(end_date, simulative=True)
    win32.send_keys(keys='{enter}', send_key_delay=50, delay_after=1)
    sleep(0.5)

    # 订单类型选择
    order_dropdown_xpath = '//form//div[contains(@class, "ait-pro-filed-search-select")]//span[@title="全部订单范围"][contains(@class, "ait-select-selection-item")]'
    web_page.find_by_xpath(order_dropdown_xpath).click()
    sleep(0.5)
    
    order_options_xpath = '//div[@class="rc-virtual-list-holder-inner"]/div'
    order_elements = web_page.find_all_by_xpath(order_options_xpath)

    for element in order_elements:
        if element.get_text() == order_type:
            element.click()
            break
    sleep(1)

    # 选择账户类型
    account_dropdown_xpath = '//form//span[@title="USD账户"][contains(@class, "ait-select-selection-item")]'
    web_page.find_by_xpath(account_dropdown_xpath).click()
    sleep(0.5)
    
    account_options_xpath = '//div[@class="rc-virtual-list-holder-inner"]/div'
    account_elements = web_page.find_all_by_xpath(account_options_xpath)

    for element in account_elements:
        if element.get_text() == account_type:
            element.click()
            break
    sleep(1)

    # 执行数据查询
    query_button_xpath = '//form//button[normalize-space(.)="查 询"]'
    web_page.find_by_xpath(query_button_xpath).click()
    sleep(2)  # 等待查询结果加载
    
    # 获取订单放款记录金额并构建字典
    account_xpath = '//div[contains(@class, "ait-col-4")]'
    account_elements = web_page.find_all_by_xpath(account_xpath)
    
    loan_records_dict = {}
    
    for element in account_elements:
        element_text = element.get_text()
        # 按换行符分割文本，每两项组成一个键值对
        lines = [line.strip() for line in element_text.split('\n') if line.strip()]
        
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                key = lines[i]
                value = lines[i + 1]
                loan_records_dict[key] = value

    
    # 点击导出明细
    export_button_xpath = '//button[normalize-space(.)="导出明细"]'
    web_page.find_by_xpath(export_button_xpath).click()
    sleep(2)  # 等待导出处理

    # 等待导出历史页面出现
    history_xpath = '//span[@class="aep-tooltip-label"]/div'
    selector_data = {'id': 'iframe-xpath', 'name': 'iframe-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': [history_xpath]}}
    selector = Selector(selector_data)

    file_path = None
    
    # 判断导出历史页面是否加载完成
    if web_page.wait_appear(selector, timeout=20):
        download_button_xpath = '//table//tr[2]/td//a/span[normalize-space(.)="下载"]'
        web_page.find_by_xpath(download_button_xpath).click()
        
        # 处理文件保存对话框
        file_path = web.handle_save_dialog(save_directory, 'ok', mode=web_page.product_name, file_name=file_name, wait_appear_timeout=20)
    else:
        print("导出历史页面加载超时")
    
    return file_path, loan_records_dict


def test_handle_order_loan_records():
    """测试资金结算报表导出功能"""
    if "xbot_extensions" in __file__: 
        return
    
    url = "https://csp.aliexpress.com/m_apps/fund-center/popFundCenter?channelId=210070#/home/orderRecord/loan"
    web_page = web.create(url, mode='chrome')

    start_date = '2025-04-01'
    end_date = '2025-04-30'
    order_type = '非俄罗斯订单'
    account_type = 'CNY账户'
    save_directory = r'C:\Users\25414\Desktop\培训内容'
    file_name = '资金结算报表.xlsx'
    
    # 调用主函数
    file_path, loan_records_data = handle_order_loan_records(web_page, order_type, start_date, end_date, account_type, save_directory, file_name)
    print(f"测试完成，文件保存到: {file_path}")
    print(f"放款记录数据: {loan_records_data}")
    
    web_page.close()
    exit()


def main(args):
    """主函数入口"""
    # 测试功能
    test_handle_order_loan_records()

    check_enterprise()

    # 获取输入参数
    web_page = args.get('web_page')
    start_date = args.get('start_date')
    end_date = args.get('end_date')
    order_type = args.get('order_type')
    account_type = args.get('account_type')
    save_directory = args.get('save_directory')
    file_name = args.get('file_name')
    
    # 调用主功能函数
    file_path, loan_records_data = handle_order_loan_records(web_page, order_type, start_date, end_date, account_type, save_directory, file_name)
    
    # 设置返回值
    args['file_path'] = file_path
    args['loan_records_data'] = loan_records_data