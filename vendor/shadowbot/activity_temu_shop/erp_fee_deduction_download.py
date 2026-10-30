# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
from datetime import datetime

import xbot
import xbot_visual
from xbot import print, sleep
from xbot_extensions.web_action.select_date import select_date
from .import package
from .package import variables as glv
from .utils import Tools
from .download_utils import download_handler


def transform_month(month):
    """进行月份转换"""
    transform = {
        '01':'一月',
        '02':'二月',
        '03':'三月',
        '04':'四月',
        '05':'五月',
        '06':'六月',
        '07':'七月',
        '08':'八月',
        '09':'九月',
        '10':'十月',
        '11':'十一月',
        '12':'十二月'
    }
    return transform[month]

def period_select(web_page, start_time):
    """选择月份周期"""

    left_button_xpath = '//*[local-name()="svg"][@data-testid="beast-core-icon-left"]'
    right_button_xpath = '//*[local-name()="svg"][@data-testid="beast-core-icon-right"]'

    # 点击展开扣费费用周期
    month_frame_xpath = '//input[@placeholder="选择月份"]'
    web_page.find_by_xpath(month_frame_xpath).click()

    # 获取参数中的年和月
    target_year, target_month = start_time.split('-')[0], start_time.split('-')[1]
    target_month = transform_month(target_month)        # 对参数中的月份转换，转换为网页中的月份

    # 获取网页中的年
    year_xpath = '//input[contains(@value,"年")]'
    year = web_page.find_by_xpath(year_xpath).get_attribute('value')
    year = year.split('年')[0]
    
    # 进行判断, 并点击左/右按钮进行年份选择
    click_times = int(target_year) - int(year)
    if click_times < 0:
        for _ in range(abs(click_times)):
            web_page.find_by_xpath(left_button_xpath).click()
            sleep(0.5)
    elif click_times > 0:
        for _ in range(click_times):
            web_page.find_by_xpath(right_button_xpath).click()
            sleep(0.5)
    
    # 选择月份
    month_xpath = f'//span[text()="{target_month}"]'
    web_page.find_by_xpath(month_xpath).click()


def erp_fee_download(web_page, fee_type, start_time, end_time, file_folder, file_name):
    """erp扣费下载"""

    # 获取浏览器名称
    web_type = Tools.get_web_page_product_name(web_page)

    # 判断是否在目标页面
    Tools.check_target_web(web_page, 'labor/epr-fee')

    # 判断是否在卖家中心元素
    Tools.check_saler_center(web_page)

    for _ in range(2):
        try:
            # 进行选择费用类型
            fee_type_xpath = f'//div[text()="{fee_type}"]'
            web_page.find_by_xpath(fee_type_xpath).click()
            break
        except:
            continue

    # 进行弹窗消除
    Tools.handle_info(web_page,wait_appear=1)

    # 点击已扣费
    charged_xpath = '//div[text()="已扣费"]'
    web_page.find_by_xpath(charged_xpath).click()

    if fee_type == '物流包装环保费':
        # 如果类型是物流包装环保费，则需要选择周期
        period_select(web_page, start_time)

    if fee_type != "授权代理费":
        # 点击展开时间框
        time_frame_xpath = '//input[@placeholder="请选择" and @value!=""]'
        web_page.find_by_xpath(time_frame_xpath).click()

        # 进行时间选择
        time_select_frame_xpath = '//div[@data-testid="beast-core-portal-main"]'
        time_select_frame_sel   = web_page.find_all_by_xpath(time_select_frame_xpath, timeout=3)
        time_select_frame_display = [_ for _ in time_select_frame_sel if _.get_bounding(to96dpi=False)[2] != 0][0]
        select_date(web_page, time_select_frame_display, start_time, end_time)

        # 判断是否有确认按钮出现
        confirm_xpath = '//span[text()="确认"]'
        confirm_sel   = web_page.find_all_by_xpath(confirm_xpath, timeout=3)
        confirm_display = [_ for _ in confirm_sel if _.get_bounding(to96dpi=False)[2] != 0]
        if len(confirm_display) > 0:
            confirm_display[0].click()  # 点击确认

        # 点击查询
        query_xpath = '//span[text()="查询"]'
        web_page.find_by_xpath(query_xpath).click()

    # 点击导出
    export_xpath = '//span[text()="导出"]'
    web_page.find_by_xpath(export_xpath).click()

    for _ in range(100):

        # 等待下载数据报表按钮出现
        download_data_xpath = '(//div[contains(@class,"export-history_right")])[1]/div[1]/button'
        download_data       = web_page.find_by_xpath(download_data_xpath).get_text()
        if "下载数据报表" in download_data:
            web_page.find_by_xpath(download_data_xpath).click()
            break   # 点击下载后结束循环
        
        web_page.find_by_xpath('//span[text()="刷新"]').click()
        sleep(5)    # 等待五秒，进行刷新
    
    # 进行下载数据
    file_path = download_handler(
        web_page=web_page,
        file_folder=file_folder,
        file_name=file_name,
    )
    # 下载后点击费用类型进行退出右侧下载框
    web_page.find_by_xpath(fee_type_xpath).click()

    return file_path

def test():
    """测试模块"""

    if "xbot_extensions" in __file__:
        return
    
    web_page    = xbot.web.get_active(mode="ziniaobrowser")
    fee_type    = '物流包装环保费'
    start_time  = '2025-02-12'
    end_time    = '2025-02-20'
    file_folder = r'C:\Users\thinkpad\Desktop\测试'
    file_name   = '费用下载'

    erp_fee_download(web_page, fee_type, start_time, end_time, file_folder, file_name)
    exit()

def main(args):
    test()

    web_page = args.get('web_page')
    fee_type = args.get('fee_type', '商品环保费')
    start_time = args.get('start_time')
    end_time   = args.get('end_time')
    file_folder= args.get('file_folder')
    file_name  = args.get('file_name')

    file_path = erp_fee_download(web_page, fee_type, start_time, end_time, file_folder, file_name)
    args['file_path'] = file_path