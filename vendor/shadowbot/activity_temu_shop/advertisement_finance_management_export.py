# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
import xbot
from xbot import print, sleep
from xbot_extensions.web_action.select_date import select_date
from .import package
from .package import variables as glv
from .utils import Tools
from .download_utils import download_handler


def advertisement_finance_management_export(web_page, bill_type, time_select, file_folder, file_name):
    """广告平台-财务管理-广告流水导出"""

    # 判断是否在目标页面
    Tools.check_target_web(web_page,'financial-management.html')

    # 进入广告流水页面
    web_page.find_by_xpath('//div[.="广告流水" and (@data-testid="beast-core-tab-itemLabel")]').click()

    # 选择日账单/月账单
    if bill_type == '月账单':
        web_page.find_by_xpath('//div[text()="月账单"]').click()
    
    # 如果是日账单并且有自定义时间则进行点击
    if bill_type == '日账单' and time_select:

        # 分割时间
        start_time = time_select.split('~')[0]
        end_time = time_select.split('~')[1]

        # 点击展开时间框
        web_page.find_by_xpath('//input[@placeholder="请选择时间"]').click()

        # 使用智能日期选择进行选择时间
        time_frame_sel = web_page.find_by_xpath('//div[@data-testid="beast-core-rangePicker-dropdown-contentRoot"]')
        select_date(web_page, time_frame_sel, start_time, end_time)

        # 点击确定
        web_page.find_by_xpath('//button/span[text()="确认"]').click()

        # 等待数据加载完毕
        Tools.wait_loading(web_page)
    
    # 判断是否有数据,没有数据则退出
    Tools.get_page_num(web_page, is_switch=False)

    # 点击下载
    web_page.find_by_xpath('//span[text()="下载"]').click()
    
    # 进行下载
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

    web_page = xbot.web.get_active(mode="chrome")
    bill_type = '日账单'
    time_select = '2025-10-18~2025-10-20'
    file_folder = os.path.join(os.path.expanduser('~'),'Desktop')
    file_name = '广告流水-月账单.xlsx'

    advertisement_finance_management_export(web_page, bill_type, time_select, file_folder, file_name)

    exit()


def main(args):
    # 测试功能
    test()

    desktop = os.path.join(os.path.expanduser('~'), 'desktop')
    # 功能模块
    web_page = args.get('web_page')
    bill_type = args.get('bill_type', '日账单')
    time_select = args.get('time_select', '')
    file_folder = args.get('file_folder',desktop)
    file_name = args.get('file_name')
    
    file_path = advertisement_finance_management_export(web_page, bill_type, time_select, file_folder, file_name)
    args['file_path'] = file_path