# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .utils import select_click
from .activities_utils import download_handler
from xbot_extensions.web_action.select_date import select_date

def handle_options(web_page, check, scale, mode, start_time, end_time):
    check_type_list = web_page.find_all('sales_flow_check_type')
    keyword_list = ['按天', '按周', '按月']
    select_click(check, keyword_list, check_type_list)

    scale_type_list = web_page.find_all('sales_flow_scale_type')
    keyword_list = ['7天', '1个月', '3个月', '6个月', '1年', '2年']
    select_click(scale, keyword_list, scale_type_list)
    
    try:
        web_page.find("sales_flow_date_click", timeout=3).click()
    except:
        pass
    try:
        date_mode_list = web_page.find_all("sales_flow_date_type_list",timeout=3)
        keyword_list = ['昨天', '本周', '本月', '年初', '自定义']
        select_click(mode, keyword_list, date_mode_list)
    except:
        pass
    if mode == '自定义':
        web_page.find('sales_flow_starttime_frame').click()
        date_frame = web_page.find('sales_flow_date_body')
        select_date(web_page, date_frame, start_time, '')
        web_page.find('sales_flow_endtime_frame').click()
        date_frame = web_page.find('sales_flow_end_body')
        select_date(web_page, date_frame, end_time, '')
    
    # web_page.find('sales_flow_control_pannel').click()
    # control_pannel_list = web_page.find_all()



def run(web_page, check, scale, mode, start_time, end_time, file_folder, file_name):
    
    web_page.find('sales_flow_sale_flow').click()
    handle_options(web_page, check, scale, mode, start_time, end_time)
    web_page.find('sales_flow_download').click()
    file_path = download_handler(
        web_page,
        str(file_folder),
        file_name,
        wait_time=300,
        wait_timeout_appear=120,
    )
    return file_path

def main(args):
    web_page = args.get('web_page')
    check = args.get('check','')
    scale = args.get('scale')
    mode = args.get('mode')
    start_time = args.get('start_time')
    end_time = args.get('end_time')
    file_folder = args.get('file_folder')
    file_name = args.get('file_name')
    
    # web_page = web.get_active(mode='chrome')
    file_path = run(web_page, check, scale, mode, start_time, end_time, file_folder, file_name)
    args['file_path'] = file_path