# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from . import utils
from xbot_extensions import web_action
import os

def choose_select(web_page, select_name, select_value):
    ''' 选择下拉框
    :param web_page: 网页对象
    :param select_name: 下拉框名称
    :param select_value: 下拉框值
    '''
    try:
        if select_value:
            select_xpath = f'//label[@title="{select_name}"]/../following-sibling::div'
            web_page.find_by_xpath(select_xpath).click()
            xpaths = f'//div[@class="ant-select-dropdown ant-select-dropdown-placement-bottomLeft "]//div[@label="{select_value}"]'
            web_page.find_by_xpath(xpaths, timeout=5).click()
    except:
        raise Exception(f'{select_name}下拉框选择失败，请检查下拉框值: {select_value}')

def service_performance_quality_detail(web_page, quick_datetime, datetime, ww_type, customer_service, evaluation_result, file_path, file_name):
    '''服务-绩效明细-接待评价明细数据获取
    params: web_page, 网页对象
    params: datetime, 日期
    params: ww_type, 旺旺类型
    params: customer_service, 客服
    params: evaluation_result, 评价结果
    params: file_path, 文件路径
    params: file_name, 文件名
    return: output_path, 输出文件路径
    '''
    url = web_page.get_url()
    if "https://sycm.taobao.com/qos/service/frame/performance/detail/new#/detail" in url:
        web_page.reload()
    else:
        web_page.navigate('https://sycm.taobao.com/qos/service/frame/performance/detail/new#/detail')

    # 进入质量明细-接待评价明细
    tab_xpath = '//span[.="质量明细"]'
    web_page.find_by_xpath(tab_xpath).click()
    recepthion_xpath = "//*[text()='接待评价明细']"
    web_page.find_by_xpath(recepthion_xpath).click()

    # 选择日期
    if quick_datetime not in ['昨天', '近7天', '近30天', '自定义']:
        raise Exception('快捷日期选择错误，请检查快捷日期，当前只支持: 昨天, 近7天, 近30天, 自定义')
    select_datetime_xpath = '//div[@class="oui-date-picker-particle-button"]/button'
    select_datetime_ele_list = web_page.find_all_by_xpath(select_datetime_xpath)
    for date in select_datetime_ele_list:
        if date.get_text() == quick_datetime:
            date.click()
            break
    verify_datetime_text = ''
    verify_symbol = False
    # 自定义日期使用智能日期选择
    for i in range(3):
        if quick_datetime == '自定义':
            start_time, end_time = datetime.split('_')
            datetime_selector = utils.get_select('(//div[@class="oui-dt-calendar-content rangeRight"]//td)[1]', 'datetime_selector')
            web_action.select_date.main({"web_page": web_page, "date_elem": datetime_selector, "date_start": start_time, "date_end": end_time})
            confirm_xpath = '//div[@class="rangeValue"]//span[.="确 定"]'
            web_page.find_by_xpath(confirm_xpath).click()

            # 校验时间
            verify_datetime_xpath = '//div[@class="oui-date-picker-current-date"]'
            verify_datetime_list = web_page.find_by_xpath(verify_datetime_xpath).get_text().split(' ')
            verify_datetime_text = ''.join(verify_datetime_list[1:])
            if f'{start_time}~{end_time}' == verify_datetime_text:
                verify_symbol = True
                break
            else:
                sleep(2)
        else:
            verify_symbol = True
    if not verify_symbol:
        raise Exception('当前日期校验错误，请检查日期格式')

    # 选择旺旺类型
    choose_select(web_page, '旺旺类型', ww_type)
    # 选择客服旺旺
    choose_select(web_page, '客服旺旺', customer_service)
    # 选择评价结果
    choose_select(web_page, '评价结果', evaluation_result)

    no_result_ele = utils.get_select('//p[@class="ant-empty-description"]', '暂无数据')
    if web_page.is_element_displayed(no_result_ele):
        return 

    if not file_name:
        parts = ['绩效质量明细']
        if ww_type:
            parts.append(ww_type)
        if customer_service:
            parts.append(customer_service)
        if evaluation_result:
            parts.append(evaluation_result)
        file_name = '_'.join(parts) + '.xlsx'
    elif file_name.endswith('.xlsx'):
        file_name = file_name
    else:
        file_name = f'{file_name}.xlsx'

    # 点击下载
    download_xpath = '//a[.="下载历史"]//following-sibling::a'
    web_page.find_by_xpath(download_xpath).click()
    # 点击第一行的下载按钮
    first_row_download_xpath = '//div[@class="ant-table-body"]//tr[2]//a[.="下载"]'
    web_page.find_by_xpath(first_row_download_xpath).click()
    # 处理下载对话框
    web_page_mode = utils.get_active_by_web_page(web_page)
    xbot.web.handle_save_dialog(file_folder=file_path, dialog_result='ok', mode=web_page_mode, file_name=file_name, wait_complete=True)

    return f'{file_path}\\{file_name}'

def test_func():
    if "xbot_extensions" not in __name__:
        web_page = xbot.web.get_active('chrome')
        quick_datetime = '自定义'
        datetime = '2025-12-10_2025-12-15'
        ww_type = ''
        customer_service = ''
        evaluation_result = ''
        file_path = r'D:\env_text\服务-绩效明细'
        file_name = ''
        output_path = service_performance_quality_detail(web_page, quick_datetime, datetime, ww_type, customer_service, evaluation_result, file_path, file_name)
        print(output_path)
        exit()

def main(args):
    test_func()
    web_page = args.get('web_page')
    quick_datetime = args.get('quick_datetime')
    datetime = args.get('datetime')
    ww_type = args.get('ww_type', '')
    customer_service = args.get('customer_service', '')
    evaluation_result = args.get('evaluation_result', '')
    file_path = args.get('file_path')
    file_name = args.get('file_name')
    output_path = service_performance_quality_detail(web_page, quick_datetime, datetime, ww_type, customer_service, evaluation_result, file_path, file_name)
    args['output_path'] = output_path