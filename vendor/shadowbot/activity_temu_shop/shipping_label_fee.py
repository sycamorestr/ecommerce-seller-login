# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
from datetime import datetime, timedelta, time
import xbot
import xbot_visual
from xbot import print, sleep
from xbot_extensions.web_action import select_date
from .import package
from .package import variables as glv
from .utils import Tools
from xbot._core.retry import Retry
from .download_utils import download_handler 

def shipping_label_fee(web_page, start_time, end_time, file_folder, file_name, over_time: int = 300):
    """发货面单费导出"""

    # 获取浏览器名称
    web_type = Tools.get_web_page_product_name(web_page)

    # 进行重试两次
    for i in range(2):
        try:

            # 判断是否在目标页面
            url = web_page.get_url()
            if '/labor/stml-logistics' not in url:
                # 获取网站域名
                domain_url = Tools.get_domain_from_url(url)
                # 进行跳转
                web_page.navigate(f'{domain_url}/labor/stml-logistics')

            # 点击已出账
            web_page.find_by_xpath('//div[text()="已出账"]').click()

            # 去除信息框
            Tools.handle_info(web_page)

            if start_time and end_time:

                # 点击展开时间框
                time_xpath = '//input[@placeholder="开始时间~结束时间"]'
                web_page.find_by_xpath(time_xpath).click()

                # 智能日期选择时间
                time_frame_xpath = '//div[contains(@class,"RPR_outerPickerWrapper")]'
                time_frame_list_sel = web_page.find_all_by_xpath(time_frame_xpath)
                time_frame_display = [_ for _ in time_frame_list_sel if _.get_bounding(to96dpi=False)[2] != 0][0]

                select_date.select_date(web_page, time_frame_display, start_time, end_time)

                # 点击确认
                confirm_click_xpath = '//span[text()="确认"]'
                confirm_click_list_sel = web_page.find_all_by_xpath(confirm_click_xpath)
                confirm_display = [_ for _ in confirm_click_list_sel if _.get_bounding(to96dpi=False)[2] !=0 ][0]
                confirm_display.click()

            # 点击查询
            web_page.find_by_xpath('//button/span[text()="查询"]').click()

            # 等待数据加载完毕
            Tools.wait_loading(web_page)

            # 如果没有数据则退出
            empty_data_xpath = '//div[contains(@class,"TB_emptyData")]/div[text()="暂无数据"]'
            empty_data_sel = Tools.gen_selector(empty_data_xpath)
            if web_page.wait_appear(empty_data_sel, timeout=2):
                print('暂无数据')
                return None

            # 点击导出
            web_page.find_by_xpath('//span[text()="导出"]').click()

            for _ in Retry(timeout=over_time, ignore_exception=True):
                # 找到导出历史的第一个div进行下载
                download_mission_xpath = '//div[contains(@class,"export-history_exportHistoryList")]/div[1]//button'
                mission_state = web_page.find_by_xpath(download_mission_xpath).get_text()
                if mission_state == '下载数据报表':
                    web_page.find_by_xpath(download_mission_xpath).click()
                    break
                # 点击刷新
                web_page.find_by_xpath('//a/span[text()="刷新"]').click()

            # 进行下载配置
            file_path = download_handler(
                web_page,
                file_folder,
                file_name
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
    
    web_page = xbot.web.get_active('ziniaobrowser')
    start_time = '2025-08-12'
    end_time = '2025-09-11'
    file_folder = os.path.join(os.path.expanduser('~'), 'Desktop')
    file_folder = r'C:\Users\Administrator\Desktop\测试'
    file_name = '发货面单费'
    file_path = shipping_label_fee(web_page, start_time, end_time, file_folder, file_name)

    exit()


def main(args):
    # 测试模块
    test()

    # 桌面路径
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')

    # 功能模块
    web_page = args.get('web_page')
    start_time = args.get('start_time', ' ')
    end_time = args.get('end_time', ' ')
    file_folder = args.get('file_folder', desktop)
    file_name = args.get('file_name')
    over_time = args.get('over_time') or 300
    if isinstance(over_time, str):
        over_time = int(over_time)

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

    file_path = shipping_label_fee(web_page, start_time, end_time, file_folder, file_name)
    args['file_path'] = file_path