# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import os
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot import web
from xbot import win32
from xbot.selector import Selector
from .utils import check_enterprise


def export_financial_report(web_page: xbot.web.WebBrowser, start_date: str, end_date: str, expense_type: list, save_directory: str, file_name: str) -> str:
    """执行财务报告导出操作：输入日期范围、费用类型，执行查询并导出文件
    :param web_page: xbot.web.WebBrowser, 待操作的网页对象
    :param start_date: str, 开始日期，格式如：2024-01-01
    :param end_date: str, 结束日期，格式如：2024-12-31
    :param expense_type: list, 费用项类型列表，如：['广告费', '技术服务费']
    :param file_path: str, 文件保存路径
    :return: str, 保存的文件完整路径，如果失败返回None
    """
    assert os.path.splitext(file_name)[-1].lower() in ['.xlsx'], f"{file_name} 文件名不合法, 请以 .xlsx 为后缀"
    url = 'https://csp.aliexpress.com/m_apps/fund-center/popFundCenter?channelId=210070#/home/incomeAndExpenseRecord'
    current_url = web_page.get_url()
    
    if current_url != url:
        web_page.navigate(url)
        sleep(4)  # 等待页面加载
    # 输入开始日期
    start_date_xpath = '//*[@id="incomeTime"]'
    web_page.find_by_xpath(start_date_xpath).input(start_date)
    win32.send_keys(keys='{enter}', send_key_delay=50, delay_after=1)
    
    # 输入结束日期
    end_date_xpath = '//div[@class="ait-picker-input ait-picker-input-active"]/input'
    web_page.find_by_xpath(end_date_xpath).input(end_date)
    win32.send_keys(keys='{enter}', send_key_delay=50, delay_after=1)

    # 费用类型的选择
    for item in expense_type:
        # 先点击费用类型输入框激活
        change_xpath = '//*[@id="feeItemTypes"]'
        fee_input = web_page.find_by_xpath(change_xpath)
        fee_input.click()
        
        # 输入单个费用类型
        fee_input.input(item)
        
        # 按回车确认选择
        win32.send_keys(keys='{enter}', send_key_delay=50, delay_after=1)

    # 点击查询数据
    query_xpath = '//div[@class="ait-space ait-space-horizontal ait-space-align-center"]//button[@class="ait-btn ait-btn-secondary"]'
    web_page.find_by_xpath(query_xpath).click()
    sleep(3)
    
    # 点击导出明细
    export_xpath = '//button[@class="ait-btn ait-btn-secondary"]//span[text()="导出明细"]'
    web_page.find_by_xpath(export_xpath).click()
    
    # 判断是否出现可以点击的下载页面
    history_xpath = '//span[@class="aep-tooltip-label"]/div'
    data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': [history_xpath]}}
    selector = Selector(data)
    if web_page.wait_appear(selector, timeout=30):
        # 点击文件下载按钮
        download_xpath = '//table//tr[2]/td//a/span[normalize-space(.)="下载"]'
        web_page.find_by_xpath(download_xpath).click()
        # 处理文件保存对话框
        file_path = web.handle_save_dialog(save_directory, dialog_result='ok', mode=web_page.product_name, file_name=file_name, wait_appear_timeout=30)
    return file_path
        
def test_export_income_expense():
    """测试收支明细导出功能"""
    if "xbot_extensions" in __file__:
        return
        
    # 文件路径
    save_directory = r'C:\Users\25414\Desktop\操作题一川'
    expense_type = ['佣金', '运费退款', '赔付商家']
    url = "https://csp.aliexpress.com/m_apps/fund-center/popFundCenter?channelId=210070#/home/incomeAndExpenseRecord"
    web_page = web.create(url, mode='chrome')
    file_name = 'text.xlsx'
    start_date = '2025-04-01'
    end_date = '2025-04-30'
    file_path = export_financial_report(web_page, start_date, end_date, expense_type, save_directory, file_name)
    print(file_path)
    
    web_page.close()
    exit()


def main(args):
    # 测试
    test_export_income_expense()

    check_enterprise()

    # 获取输入参数
    start_date = args.get('start_date')
    end_date = args.get('end_date')
    expense_type = args.get('expense_type')
    save_directory = args.get('save_directory')
    web_page = args.get('web_page')
    file_name = args.get('file_name')

    # 调用主函数
    file_path = export_financial_report(web_page, start_date, end_date, expense_type, save_directory, file_name)

    #传出参数
    args['file_path'] = file_path
