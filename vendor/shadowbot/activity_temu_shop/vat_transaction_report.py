# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
import re

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .utils import Tools
from .download_utils import download_handler


def transforfm_date(params):
    """進行月份转换"""
    date = {
        '01':'一',
        '02':'二',
        '03':'三',
        '04':'四',
        '05':'五',
        '06':'六',
        '07':'七',
        '08':'八',
        '09':'九',
        '10':'十',
        '11':'十一',
        '12':'十二'
    }
    return date[params]

def vat_transaction_report(web_page, data_range, data_type, time_zone, time_select, file_folder, file_name):
    """增值税交易数据下载"""

    # 判断是否在目标页面(目前只有欧区才有这个模块)
    url = 'https://agentseller-eu.temu.com/labor/tax-settle'
    if url not in web_page.get_url():
        web_page.navigate(url)
    
    # 進行賣家中心判斷
    Tools.check_saler_center(web_page)
    
    # 创建下载任务
    create_tsak_xpath = '//button[@data-testid="beast-core-button"]/span[text()="创建下载任务"]'
    web_page.find_by_xpath(create_tsak_xpath).click()
    
    # 选择数据范围
    data_range_frame = '//input[@placeholder="请选择数据范围"]'
    web_page.find_by_xpath(data_range_frame).click()
    web_page.find_by_xpath(f'//ul/li/span[contains(text(),"{data_range}")]').click()

    # 选择数据类型
    data_type_xpath = f'//label[text()="数据类型"]/../../following-sibling::div//*[text()="{data_type}"]'
    web_page.find_by_xpath(data_type_xpath).click()

    # 选择申报时区
    time_zone_xpath = '//input[@placeholder="请选择时区"]'
    web_page.find_by_xpath(time_zone_xpath).click()
    web_page.find_by_xpath(f'//ul/li/span[text()="{time_zone}"]').click()

    # 选择数据申报周期
    cycle_xpath = '//input[@placeholder="请选择"]'
    web_page.find_by_xpath(cycle_xpath).click()

    # f分割时间
    target_year = time_select.split('-')[0]
    target_month = time_select.split('-')[1]

    # 选择年份
    year_xpath = '//div[@data-testid="beast-core-portal-main"]//section/div/div'
    web_page.find_by_xpath(year_xpath).click()
    web_page.find_by_xpath(f'//ul/li/span[text()="{target_year}年"]').click()
    
    # 进行月份选择
    month_xpath = '//div[@data-testid="beast-core-portal-main"]//span[contains(@class,"MPR_month")]'
    month_list_sel = web_page.find_all_by_xpath(month_xpath)
    target_month = transforfm_date(target_month)
    for month_sel in month_list_sel:
        month = month_sel.get_text().split('月')[0]

        if target_month == month:
            month_sel.click()
            break

    # 创建下载任务
    web_page.find_by_xpath('//div[contains(@class,"MDL_bottom")]//span[text()="取消"]').click()

    # 查询下载表格，找到匹配的下载任务
    trs_xpath = '//tbody/tr'
    trs = web_page.find_all_by_xpath(trs_xpath)

    for tr in trs:

        # 获取所有的行
        tds = tr.find_all_by_xpath('./td')

        # 获取数据类型，申报数据时区以及申报数据周期
        web_data_type = tds[1].get_text()
        web_time_zone = tds[2].get_text()
        web_cycle     = tds[3].get_text()

        download = False

        # 如果数据类型、申报数据时区、申报数据周期都匹配的上则进行下载
        if web_data_type == data_type and web_cycle == time_select and web_time_zone in time_zone:
            for _ in range(5):
                try:
                    tds[7].find_by_xpath('.//span[text()="下载数据"]', timeout=1).click()
                    download = True
                    break
                except Exception as e:
                    print(e)
                    sleep(1)

        if download is True:
            break

    # 下载文件
    file_path = download_handler(
        web_page=web_page,
        file_folder=file_folder,
        file_name=file_name
    )

    return file_path


def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return

    web_page = xbot.web.get_active(mode='chrome')
    data_range = '欧区'
    data_type = '汇总'
    time_zone = 'UTC+1(东一区)'
    time_select = '2025-09'
    file_folder = os.path.join(os.path.expanduser('~'),'Desktop')
    file_name = '增值税下载.xlsx'
    vat_transaction_report(web_page, data_range, data_type, time_zone, time_select, file_folder, file_name)
    exit()

def main(args):
    # 测试模块
    # test()

    # 功能模块
    web_page = args.get('web_page')
    date_range = args.get('date_range')
    data_type = args.get('data_type')
    time_zone = args.get('time_zone')
    time_select = args.get('time_select')
    file_folder = args.get('file_folder')
    file_name = args.get('file_name')

    file_path = vat_transaction_report(web_page, date_range, data_type, time_zone, time_select, file_folder, file_name)
    args['file_path'] = file_path