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
from .utils import handler_container
from xbot._core.retry import Retry
from ._amazon_api import login
from .utils import request_error


def reserved_inventory(web_page, folder_path, file_name, wait_timeout=300):
    """进行预留数量下载"""

    # 进行校验地址
    if "sellercentral.amazon" in web_page.get_url():
        if 'reportcentral/ReserveBreakdown/1' not in web_page.get_url():
            domain = urlparse(web_page.get_url()).netloc
            url = f"{domain}/reportcentral/ReserveBreakdown/1"
            web_page.navigate(url)
            login(web_page)
            handler_container(web_page)
    else:
        web_page.navigate("https://sellercentral.amazon.com/reportcentral/ReserveBreakdown/1")
        login(web_page)
        handler_container(web_page)

    sleep(3)
    for _ in range(3):
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
            web_page.reload(load_timeout=60)
            continue
        else:
            break
    else:
        xbot.logging.warning('文件下载，请稍后再试')
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
        
    # 判断是否下载成功
    request_status = request_error(web_page)
    if request_status is True:
        raise Exception('请求下载失败，请稍后重试')

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
    reserved_inventory(web_page, folder_path, file_name)

    exit()


def main(args):
    test()
    web_page = args.get('web_page')
    folder_path = args.get('folder_path')
    file_name = args.get('file_name')
    wait_timeout = args.get('wait_timeout')
    wait_timeout = int(wait_timeout)

    if '.csv' not in file_name and '.txt' not in file_name:
        file_name = file_name + '.csv'

    file_path = reserved_inventory(web_page, folder_path, file_name, wait_timeout)
    args['file_path'] = file_path
