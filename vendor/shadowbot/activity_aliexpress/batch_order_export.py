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
from xbot import excel
from xbot import web
from xbot import win32
from .utils import check_enterprise,gen_selector


def select_order_status(web_page: xbot.web.WebBrowser, order_status: str):
    """
    选择订单状态
    
    :param web_page: xbot.web.WebBrowser,  网页对象
    :param order_status: str, 订单状态文本
    """
    # 点击订单状态下拉框
    order_status_xpath = '//span[contains(@class, "order-export-status-select")]//span[contains(@class, "next-select-values")]'
    web_page.find_by_xpath(order_status_xpath).click()
    
    # 获取所有订单状态选项
    all_order_status_xpath = '(//div[contains(@class, "next-overlay-inner")])//span'
    order_status_options = web_page.find_all_by_xpath(all_order_status_xpath)
    
    # 选择对应的订单状态
    for option in order_status_options:
        option_text = option.get_text()
        if option_text == order_status:
            option.click()
            break  # 找到后跳出循环


def select_business_model(web_page: xbot.web.WebBrowser, business_model: str):
    """
    选择业务模式
    
    :param web_page: xbot.web.WebBrowser,  网页对象
    :param business_model: str, 业务模式文本
    """
    # 点击业务模式下拉框
    business_model_xpath = '//span[contains(@class, "order-export-mode-select")]//span[contains(@class, "next-select-values")]'
    web_page.find_by_xpath(business_model_xpath).click()
    
    # 获取所有业务模式选项
    business_model_all_xpath = '(//div[contains(@class, "next-overlay-inner")])//span'
    business_model_options = web_page.find_all_by_xpath(business_model_all_xpath)

    for option in business_model_options:
        option_text = option.get_text()
        if option_text == business_model:
            option.click()
            break 


def select_date_range(web_page: xbot.web.WebBrowser, date_filter_type: str, start_date: str, end_date: str,reason_download:str, save_directory: str, order_status: str, file_name: str) -> str:
    """
    选择日期范围,下载对应订单
    :param web_page: xbot.web.WebBrowser, 网页对象
    :param date_filter_type: str, 日期筛选类型
    :param start_date: str, 开始日期
    :param end_date: str, 结束日期
    :param save_directory: str, 文件保存目录
    :param order_status: str,  订单状态
    :param file_name: str, 文件名称
    :return: 文件保存路径
    """
    # 点击筛选日期下拉框
    date_filter_xpath = '//div[@class="order-export-filter-time"]/span'
    web_page.find_by_xpath(date_filter_xpath).click()
    
    # 获取所有日期筛选选项
    date_filter_all_xpath = '//div[contains(@class, "opened")]//ul[@role="listbox"]/li'
    date_filter_options = web_page.find_all_by_xpath(date_filter_all_xpath)
    
    for option in date_filter_options:
        option_text = option.get_text()
        if option_text == date_filter_type:
            option.click()
            break  # 找到后跳出循环
    
    # 输入开始日期
    formatted_start_date = start_date + ' 00:00:00'
    start_date_xpath = '//div[@class="ait-picker ait-picker-range"]/div[1]/input'
    web_page.find_by_xpath(start_date_xpath).input(formatted_start_date)
    win32.send_keys(keys='{enter}', send_key_delay=50, delay_after=1)

    # 输入结束日期
    formatted_end_date = end_date + ' 23:59:59'
    end_date_xpath = '//div[contains(@class,"ait-picker ait-picker-range")]/div[3]/input'
    sleep(1)
    web_page.find_by_xpath(end_date_xpath).input(formatted_end_date)
    win32.send_keys(keys='{enter}', send_key_delay=50, delay_after=1)

    # 选择导出原因
    casue_xpath = '//span[contains(@class, "order-export-reason-select")]/span[contains(@class, "next-input")][contains(@class, "next-medium")]'
    web_page.find_by_xpath(casue_xpath).click()
    elenmets_xpath = '//div[contains(@class, "opened")]//ul/li[contains(@class, "next-menu-item")]'
    elements_sel = web_page.find_all_by_xpath(elenmets_xpath)
    for item in elements_sel:
        item_text = item.get_text()
        if item_text == reason_download:
            item.click()
            break
    
    sleep(1)
    # 点击确认按钮
    confirm_button_xpath = '//section[@class="order-export-filters"]/button'
    web_page.find_by_xpath(confirm_button_xpath).click()
    sleep(4)

    # 正确的日期格式：页面显示的是 "2025-04-01 00:00:00 - 2025-04-30 23:59:59"
    page_date_format = f"{start_date} 00:00:00 - {end_date} 23:59:59"
    # print(order_status)
    # print(page_date_format)
    
    order_status_xpath = "//table//thead//th[.//div/text()='导出订单状态']/preceding-sibling::th"
    order_status_index = len(web_page.find_all_by_xpath(order_status_xpath)) + 1

    order_range_xpath = "//table//thead//th[.//div/text()='导出订单时间范围']/preceding-sibling::th"
    order_range_index = len(web_page.find_all_by_xpath(order_range_xpath)) + 1

    operate_xpath = "//table//thead//th[.//div/text()='操作']/preceding-sibling::th"
    operate_index = len(web_page.find_all_by_xpath(operate_xpath)) + 1

    file_path = None

    for _ in range(10):
        # 确认下载的订单
        export_button_all_xpath = '//div[contains(@class,"next-table next-table-medium")]/table/tbody/tr'
        tr_elements = web_page.find_all_by_xpath(export_button_all_xpath)
        sleep(2)
        flag = True
        for item in tr_elements:
            # 获取页面中的订单状态
            order_tr_element = item.find_by_xpath(f'./td[{order_status_index}]')
            order_tr_element_text = order_tr_element.get_text()

            # 获取页面中的时间范围
            date_tr_element = item.find_by_xpath(f'./td[{order_range_index}]')
            date_tr_element_text = date_tr_element.get_text()
            
            # 使用正确的日期格式进行比较
            if order_tr_element_text == order_status and date_tr_element_text == page_date_format:
                try:
                    export_button = item.find_by_xpath(f'./td[{operate_index}]//a', timeout=3)
                    flag = True
                except:
                    flag = False
                    break
                export_button.click()
                sleep(3)
                # 处理保存对话框
                file_path = web.handle_save_dialog(save_directory, mode=web_page.product_name, dialog_result='ok', wait_appear_timeout=20, file_name=file_name)
                break
            else:
                print("日期不匹配或订单状态不匹配")
        if flag:
            break
    
    return file_path


def export_orders(web_page: xbot.web.WebBrowser, order_status: str, business_model: str, date_filter_type: str, 
                 start_date: str, end_date: str, reason_download:str, save_directory: str, file_name: str) -> str:
    """
    导出订单数据
    :param web_page: 网页对象
    :param order_status: 订单状态
    :param business_model: 业务模式
    :param date_filter_type: 日期筛选类型
    :param start_date: 开始日期
    :param end_date: 结束日期
    :param save_directory: 文件保存目录
    :param file_name: 文件名称
    :return: 保存的文件路径
    """
    assert os.path.splitext(file_name)[-1].lower() in ['.xlsx'], f"{file_name} 文件名不合法, 请以 .xlsx 为后缀"
    url = 'https://csp.aliexpress.com/m_apps/order-manage/orderExport?channelId=210070'
    current_url = web_page.get_url()
    
    if current_url != url:
        web_page.navigate(url)
        sleep(3)  # 等待页面加载
        
    web_page = xbot.web.get_active(mode=web_page.product_name)
    # 选择订单状态
    select_order_status(web_page, order_status)
    
    # 选择业务模式
    select_business_model(web_page, business_model)
    
    # 选择日期范围并下载
    file_path = select_date_range(web_page, date_filter_type, start_date, end_date,reason_download, save_directory, order_status, file_name)
    
    
    return file_path


def test_order_export():
    """
    测试订单导出功能
    """
    if "xbot_extensions" in __file__:
        return
        
    # 文件保存目录
    save_directory = r'C:\Users\25414\Desktop\操作题一川' 
    
    url = "https://csp.aliexpress.com/m_apps/newhome/pop?channelId=210070"
    web_page = web.create(url,mode='chrome')
    
    order_status = '等待买家付款'
    business_model = '半托管订单'
    date_filter_type = '付款时间'
    start_date = '2025-04-01'
    end_date = '2025-04-30'
    file_name = 'my.xlsx'
    reason_download = '发货'
    
    # 调用导出订单函数
    file_path = export_orders(
        web_page, 
        order_status, 
        business_model, 
        date_filter_type, 
        start_date, 
        end_date, 
        reason_download,
        save_directory,
        file_name
    )
    print(f"测试完成，文件保存到: {file_path}")

    web_page.close()
    exit()


def main(args: dict):
    # 运行测试
    test_order_export()

    check_enterprise()

    # 获取输入参数
    order_status = args.get('order_status_path')
    business_model = args.get('business_model_path')
    date_filter_type = args.get('filter_date')
    start_date = args.get('start_date')
    end_date = args.get('end_date')
    web_page = args.get('web_page')
    save_directory = args.get('save_directory')
    file_name = args.get('file_name')
    reason_download = args.get('reason_download')
    
    # 调用导出函数
    file_path = export_orders(
        web_page, 
        order_status, 
        business_model, 
        date_filter_type, 
        start_date, 
        end_date, 
        reason_download, 
        save_directory,
        file_name
    )
    
    # 将文件路径添加到返回参数中
    args['file_path'] = file_path


