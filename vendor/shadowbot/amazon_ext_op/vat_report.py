# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from urllib.parse import urlparse
from .create_element import create_selector_shadow, create_selector
from .activities_utils import download_handler
from xbot._core.retry import Retry
from .utils import handler_container


def trans_value(params):
    """将传入的时间转换为网页需要的value"""
    year, month = params.split('-')
    month = int(month) - 1
    value = f'{month}#{year}'
    
    return value


def compensation_amount(web_page, range_date, start_time, end_time, folder_path, file_name, wait_timeout=300):
    """进行增值税报告下载"""

    # 进行校验地址
    if "sellercentral.amazon" in web_page.get_url():
        if 'reportcentral/VAT_TRANSACTION/1' not in web_page.get_url():
            domain = urlparse(web_page.get_url()).netloc
            url = f"{domain}/reportcentral/VAT_TRANSACTION/1"
            web_page.navigate(url)
            handler_container(web_page)
    else:
        web_page.navigate("https://sellercentral.amazon.com/reportcentral/VAT_TRANSACTION/1")
        handler_container(web_page)

    sleep(3)
    
    # 进行事件日期下拉框选择
    event_dropdown_xpath = '//kat-dropdown[contains(@class,"vat-reports-month-select-dropdown")]/xbotShadowRoot//div[@class="select-header"]'     # 下拉框定位元素
    drop_down = create_selector(event_dropdown_xpath,name='下拉框元素')
    web_page.find(drop_down).click()


    specific_time_xpath = '//kat-dropdown[contains(@class,"vat-reports-month-select-dropdown")]/xbotShadowRoot//kat-option[@value="{}"]'
    # 如果是确切日期，则value的为-1
    if range_date == '确切日期':
        value = -1
    else:
        # 否则将传入的具体时间进行格式化
        value = trans_value(range_date)
    
    # 进行勾选事件日期
    specific_xpath = specific_time_xpath.format(value)
    specific_time = create_selector_shadow(specific_xpath, name='事件日期')
    web_page.find(specific_time).click()

    # 如果时间范围是确切日期，则进行自定义事件输入
    if range_date == '确切日期':
        if start_time == '' or end_time == '':
            raise ValueError('开始时间或结束时间为空，请重新填写')
        start_input_xpath = '//*[local-name()="kat-date-range-picker"]/xbotShadowRoot/*[local-name()="kat-date-picker"][@class="start"]/xbotShadowRoot//*[local-name()="kat-input"]'
        end_input_xpath = '//*[local-name()="kat-date-range-picker"]/xbotShadowRoot/*[local-name()="kat-date-picker"][@class="end"]/xbotShadowRoot//*[local-name()="kat-input"]'

        start_input = create_selector_shadow(start_input_xpath, name='开始时间')
        end_input = create_selector_shadow(end_input_xpath, name='结束时间')

        placeholder = web_page.find(start_input).get_attribute("placeholder") or ""
        if "MM/DD/YYYY" in placeholder:
            parts = start_time.split("-")
            start_time = f"{parts[1]}/{parts[2]}/{parts[0]}"
            parts = end_time.split("-")
            end_time = f"{parts[1]}/{parts[2]}/{parts[0]}"
        else:
            start_time = start_time.replace("-", "/")
            end_time = end_time.replace("-", "/")
        web_page.find(start_input).clipboard_input(start_time)
        web_page.find(end_input).clipboard_input(end_time)

    web_page.find('亚马逊配送报告').click()
    # 根据文件名称进行确认下载的文件类型
    if 'csv' in file_name:
        csv_button = '//kat-button[@value="CSV"]'
        web_page.find_by_xpath(csv_button).click(simulative=False)
    else:
        txt_button = '//kat-button[@value="TSV"]'
        web_page.find_by_xpath(txt_button).click(simulative=False)
    
    # 判断是否有请求失败的情况
    error_req = '//p[@class="request-report-error"]'
    error = web_page.find_all_by_xpath(error_req, timeout=5)
    if len(error) > 0:
        xbot.logging.warning('请求失败，请稍后再试')
        return 

    # 进行下载操作
    for retry in Retry(timeout=wait_timeout):
        try:
            # 判断有无报表可以下载
            xpath = '(//kat-table-row)[2]/*[local-name()="kat-table-cell"][normalize-space(.)="无可用数据" or normalize-space(.)="No Data Available"]'
            if len(web_page.find_all_by_xpath(xpath)) >= 1:
                return "无可用数据"
            # 尝试找下载按钮
            dwonload_button_xpath = '(//kat-table-body//kat-table-row)[1]//kat-button[@label="下载" or @label="Download"]'
            web_page.find_by_xpath(dwonload_button_xpath, timeout=2).click()
            break
        except:
            # 点击下载刷新
            web_page.find_by_xpath('//a[@id="reportpage_download_tab"]').click()
            sleep(3)
    else:
        print(f'超过最大等待时间 {wait_timeout}s')
        return
        
    file_path = download_handler(web_page, folder_path, file_name,wait_time=wait_timeout)
    return file_path


def test():
    if 'xbot_extensions' in __file__:
        return
    web_page = xbot.web.get_active('ziniaobrowser')
    range_data = '确切日期'
    start_time = '2026-05-12'
    end_time = '2026-06-01'
    folder_path = r'D:'
    file_name = '测试.csv'
    compensation_amount(web_page, range_data, start_time, end_time, folder_path, file_name)

    exit()


def main(args):
    test()
    web_page = args.get('web_page')
    range_data = args.get('range_data')
    start_time = args.get('start_time') or ''
    end_time = args.get('end_time') or ''
    folder_path = args.get('folder_path')
    file_name = args.get('file_name')
    wait_timeout = args.get('wait_timeout')
    wait_timeout = int(wait_timeout)

    if '.csv' not in file_name and '.txt' not in file_name:
        file_name = file_name + '.csv'

    file_path = compensation_amount(web_page, range_data, start_time, end_time, folder_path, file_name, wait_timeout)
    args['file_path'] = file_path