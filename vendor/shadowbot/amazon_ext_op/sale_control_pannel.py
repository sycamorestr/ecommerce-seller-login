# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web, win32
from .import package
from .package import variables as glv
from .utils import select_click, handler_container
from xbot_extensions.web_action.select_date import select_date

def handle_date(web_page, mode, start_time, end_time):
    web_page.find("sale_control_pannel_date_frame").click()
    date_mode_list = web_page.find_all("sale_control_pannel_date_select")
    keyword_list = ['当天', '昨天','本周', '本月', '本年', '自定义']
    select_click(mode, keyword_list, date_mode_list)
    if mode == '自定义':
        web_page.find('sale_control_pannel_starttime').click()
        date_frame = web_page.find('sale_control_pannel_date_body')
        select_date(web_page, date_frame, start_time, '')
        web_page.find('sale_control_pannel_endtime').click()
        date_frame = web_page.find('sale_control_pannel_date_body')
        select_date(web_page, date_frame, end_time, '')

def handle_sale_detail(web_page, sale_detail):
    web_page.find('sale_control_pannel_sale_detail').click()
    sale_detail_list = web_page.find_all('sale_control_pannel_sale_detail_list')
    keyword_list = ['商城汇总', '企业买家', '非企业买家']
    select_click(sale_detail, keyword_list, sale_detail_list)

def handle_channel(web_page, channel):
    web_page.find('sale_control_pannel_channel').click()
    sale_channel_list = web_page.find_all('sale_control_pannel_channel_list')
    keyword_list = ['全部', '亚马逊', '卖家']
    select_click(channel, keyword_list, sale_channel_list)

def run(web_page, mode, start_time, end_time, sale_detail, channel, file_folder, file_name):
    web_page.navigate("https://sellercentral.amazon.com/business-reports/ref=xx_sitemetric_dnav_xx#/dashboard")
    handler_container(web_page)
    handle_date(web_page, mode, start_time, end_time)
    handle_sale_detail(web_page, sale_detail)
    handle_channel(web_page, channel)
    web_page.find('sale_control_pannel_apply').click()
    web_page.find('sale_control_pannel_download').click()
    web.handle_save_dialog(file_folder = file_folder, mode=web_page.product_name, file_name=file_name, wait_complete=False)
    try:
        win = win32.get(class_name='Chrome_WidgetWin_1',timeout=5)
        win.find('send_post_confirm').click()
    except:
        pass
    return file_folder + '\\' + file_name

def main(args):
    web_page = args.get('web_page')
    mode = args.get('mode','自定义')
    start_time = args.get('start_time','2024-11-30')
    end_time = args.get('end_time','2024-12-2')
    sale_detail = args.get('sale_detail','企业买家')
    channel = args.get('channel','卖家')
    file_folder = args.get('file_folder','')
    file_name = args.get('file_name','')

    # web_page = web.get_active(mode='superbrowser')
    file_path = run(web_page, mode, start_time, end_time, sale_detail, channel, file_folder, file_name)
    args['file_path'] = file_path
