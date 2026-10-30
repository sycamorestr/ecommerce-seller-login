# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
from datetime import datetime, timedelta

import xbot
from xbot import print, sleep
from xbot_extensions.web_action import select_date
from .import package
from .package import variables as glv
from .utils import Tools
from .download_utils import download_handler


def return_label_fee(web_page, select_way, start_time, end_time, file_folder, file_name):
    """退货面单费导出"""

    for i in range(2):
        try:
            # 判断页面是否在目标页面
            url = web_page.get_url()
            if 'labor/stml-reverse-logistics' not in url:
                # 获取网站域名
                domain_url = Tools.get_domain_from_url(url)
                # 跳转到目标页面
                web_page.navigate(f'{domain_url}/labor/stml-reverse-logistics')

            if select_way == '退至第三方仓库':
                web_page.find_by_xpath('//div[text()="退至第三方仓库"]').click()

            # 消除信息框
            Tools.handle_info(web_page,wait_appear=3)

            if start_time and end_time:
                

                # 点击账单支出/退款时间,展开时间框
                return_bill_xpath = '//input[@placeholder="开始时间~结束时间"]'
                web_page.find_by_xpath(return_bill_xpath).click()

                # 使用智能日期，进行选择
                time_frame_xpath = '//div[@data-testid="beast-core-portal"]/div'
                time_frame_list_sel = web_page.find_all_by_xpath(time_frame_xpath)
                time_frame_display = [_ for _ in time_frame_list_sel if _.get_bounding(to96dpi=False)[2] != 0][0]

                select_date.select_date(web_page, time_frame_display, start_time, end_time)

                # 点击确认
                confirm_click_xpath = '//span[text()="确认"]'
                confirm_click_list_sel = web_page.find_all_by_xpath(confirm_click_xpath)
                confirm_display = [_ for _ in confirm_click_list_sel if _.get_bounding(to96dpi=False)[2] !=0 ][0]
                confirm_display.click()

            # 点击查询
            query_xpath = '//button/span[text()="查询"]'
            web_page.find_by_xpath(query_xpath).click()

            # 等待数据加载完毕
            Tools.wait_loading(web_page)

            # 如果没有数据则退出
            empty_data_xpath = '//div[contains(@class,"TB_emptyData")]/div[text()="暂无数据"]'
            empty_data_sel = Tools.gen_selector(empty_data_xpath)
            if web_page.wait_appear(empty_data_sel, timeout=1):
                return None

            # 点击导出
            web_page.find_by_xpath('//span[text()="导出"]').click()
            current_day = datetime.now().strftime('%y-m-d')

            # 获取店铺名称
            shop_name_xpath = '//span[@data-testid="beast-core-ellipsis"]/span[contains(@class,"elli_outerWrapper")]'
            shop_name = web_page.find_by_xpath(shop_name_xpath).get_text()

            for _ in range(20):
                # 找到导出历史的第一个div进行下载
                download_mission_xpath = '//div[contains(@class,"export-history_exportHistoryList")]/div[1]//button'
                mission_state = web_page.find_by_xpath(download_mission_xpath).get_text()
                if mission_state == '下载数据报表':
                    web_page.find_by_xpath(download_mission_xpath).click()
                    break
                # 点击刷新
                web_page.find_by_xpath('//a/span[text()="刷新"]').click()
                sleep(3)

            # 进行下载配置
            file_path = download_handler(
                web_page=web_page,
                file_folder=file_folder,
                file_name=file_name
            )
            return file_path
        except Exception as e:
            if i == 1:
                raise e
            continue
    

def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return
    
    web_page = xbot.web.get_active(mode='chrome')
    select_way = ''
    start_time = '2025-08-12'
    end_time = '2025-09-11'
    file_folder = os.path.join(os.path.expanduser('~'), 'Desktop')
    file_name = '退至第三方.xlsx'

    return_label_fee(web_page, select_way, start_time, end_time, file_folder, file_name)

    exit()


def main(args):

    # 测试模块
    # test()

    # 获取桌面路径
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')

    # 功能模块
    web_page = args.get('web_page')
    select_Way = args.get('select_way','')
    start_time = args.get('start_time','')
    end_time = args.get('end_time','')
    file_folder = args.get('file_folder', desktop)
    file_name = args.get('file_name')
    
    # 进行时间校验：开始、结束时间均有时，跨度不得超过一个月（起止日相差不超过 31 天）
    if start_time and end_time:
        _fmts = ('%Y-%m-%d', '%Y/%m/%d', '%Y%m%d')
        s_date = e_date = None
        for _fmt in _fmts:
            try:
                s_date = datetime.strptime(str(start_time).strip(), _fmt).date()
                e_date = datetime.strptime(str(end_time).strip(), _fmt).date()
                break
            except ValueError:
                continue
        if s_date is None or e_date is None:
            raise ValueError('开始时间或结束时间格式无效，请使用 YYYY-MM-DD')
        if s_date > e_date:
            raise ValueError('开始时间不能晚于结束时间')
        if (e_date - s_date) > timedelta(days=31):
            raise ValueError('开始时间与结束时间的间隔不能超过一个月（31 天）')
    
    file_path = return_label_fee(web_page, select_Way, start_time, end_time ,file_folder, file_name)

    args['file_path'] = file_path