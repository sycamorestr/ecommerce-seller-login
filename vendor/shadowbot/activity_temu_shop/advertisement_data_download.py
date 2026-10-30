# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
import re
import xbot
import xbot_visual
from xbot import print, sleep
from xbot_extensions.web_action.select_date import select_date

from .import package
from .package import variables as glv 
from .utils import Tools
from .advertisement_switch_area import switch_area
from .download_utils import download_handler

def advertisement_data_download(
    web_page: any,          
    report_type: str,
    data_type: str,
    date_range: str,
    time_select: str,
    file_folder: str,
    file_name: str,
    area: str
    ) -> str:                 
    """
    数据报表-广告数据下载

    :param web_page:      网页对象/URL
    :param report_type:   数据报表类型
    :param data_type:     数据类型
    :param date_range:    日期范围
    :param time_select:   自定义时间
    :params file_folder:  文件夹路径
    :params file_name:    文件名称
    :params area          半托店铺，切换区域
    """
    
    # 获取浏览器名称
    browser_mode = Tools.get_web_page_product_name(web_page)

    # 判断页面是否在目标页面
    Tools.check_target_web(web_page, 'data-report.html')

    # 等待数据加载完毕
    Tools.wait_loading(web_page, appear_time=1)

    # 判断是否可以进行切换区域    
    if area:
        area_frame_xpath = '//span[contains(text(),"当前区域")]'
        area_frame_sel = Tools.gen_selector(area_frame_xpath)
        if web_page.wait_appear(area_frame_sel, timeout=1):
            switch_area(web_page, area)
            sleep(1)
            web_page.wait_load_completed()

    # 进行数据报表类型选择
    report_type_xpath = f'//div[@data-testid="beast-core-tab"]//div[text()="{report_type}"]'
    web_page.find_by_xpath(report_type_xpath).click()

    try:
        # 进行数据类型点击
        data_type_xpath = f'//div[contains(@data-testid,"beast-core-tab")]//div[text()="{data_type}"]'
        web_page.find_by_xpath(data_type_xpath, timeout=1).click(simulative=False)
    except:
        pass

    # 将时间对比取消勾选
    time_compare_xpath ='//label[.="时间对比" and contains(@class,"active")]'
    if len(web_page.find_all_by_xpath(time_compare_xpath, timeout=2)) > 0:
        web_page.find_by_xpath(time_compare_xpath).click()

    # 等待数据加载完毕
    Tools.wait_loading(web_page, appear_time=1)

    # 选择日期
    date_range_xpath = f'//span[.="{date_range}"]'
    web_page.find_by_xpath(date_range_xpath).click()

    # 若日期为自定义，则进行时间选择
    if date_range == '自定义':

        if time_select:

            # 分割开始时间和结束时间
            start_time = time_select.split('~')[0]
            end_time = time_select.split('~')[1]

            # 获取时间框元素
            date_frame_xpath = '(//div[.="自定义时间"]/../..)[1]'
            date_frame_sel = web_page.find_by_xpath(date_frame_xpath)

            # 点击按时间段
            web_page.find_by_xpath('//span[text()="按时间段"]').click()
            
            #使用智能日期选择进行时间选择
            select_date(web_page, date_frame_sel, start_time, end_time)

    # 等待数据加载完毕
    Tools.wait_loading(web_page, appear_time=1)
    
    # 获取数据信息
    page_num = web_page.find_all_by_xpath('//li[contains(text(),"共有 ")]', timeout=5)
    if len(page_num) == 0:
        print('未找到下载按钮')
        return
    page_num = [_ for _ in page_num if _.get_bounding(to96dpi=False)[2] != 0]
    for page in page_num:
        page_text = re.search(r'\d+', page.get_text(), re.S).group().strip()
        if page_text == '0':
            print('店铺暂无数据')
            return 
    # 

    # 进行下载
    download_button_xpath_list = [
        '//span[text()="数据明细"]/..//span[text()="下载"]',
        '//div[text()="数据明细"]/../..//span[text()="下载"]'
        ]
    for idx, download_button_xpath in enumerate(download_button_xpath_list):
        try:
            download = web_page.find_all_by_xpath(download_button_xpath, timeout=1)
            download = [_ for _ in download if _.get_bounding(to96dpi=False)[2]!=0]
            download[0].click()
            break
        except:
            if idx == 1:
                print('请查看当前店铺页面是否有下载按钮')
                return 

    file_path = download_handler(
        web_page=web_page,
        file_folder=file_folder,
        file_name=file_name,
    )
    
    return file_path


def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return
    web_page = xbot.web.get_active(mode='ziniaobrowser')
    report_type = '商品数据报表'
    data_type = '全域出价'
    date_range = '今日'
    time_select = '2025-11-12~2025-11-22'
    file_folder = os.path.join(os.path.expanduser('~'),'Desktop')
    file_name = '广告数据.xlsx'
    area = '全球（除美国,欧区）'
    advertisement_data_download(web_page, report_type, data_type, date_range, time_select, file_folder, file_name, area)
    exit()

def main(args):

    # 测试功能
     test()

     # 功能
     web_page = args.get('web_page')
     report_type = args.get('report_type')
     data_type = args.get('data_type')
     date_range = args.get('date_range')
     time_select = args.get('time_select')
     file_folder = args.get('file_folder')
     file_name = args.get('file_name')
     area = args.get('area', None)

     file_path = advertisement_data_download(web_page, report_type, data_type, date_range, time_select, file_folder, file_name, area)
     args['file_path'] = file_path


