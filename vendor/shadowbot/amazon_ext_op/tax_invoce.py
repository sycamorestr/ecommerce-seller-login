# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
from datetime import datetime
from dateutil.relativedelta import relativedelta
import xbot
from xbot import print, sleep
from .create_element import create_selector_shadow
from xbot.selector import Selector
from .import package
from .package import variables as glv
from urllib.parse import urlparse
from .download_utils import download_handler
from .utils import handler_container


class Xpath:
    # 事件日期xpath
    date_frame = '//div[@id="daily-time-picker-style"]/kat-dropdown/xbotShadowRoot//div[@class="selection-text"]'  
    # 下拉框选项xpath
    option_xpath = '//div[@id="daily-time-picker-style"]/kat-dropdown/xbotShadowRoot//kat-option[@value="{}"]'

    # 开始时间打开框xpath
    start_frame_xpath = '//kat-date-range-picker[@id="daily-time-picker-kat-date-range-picker"]/xbotShadowRoot/kat-date-picker[1]'
    # 结束时间打开框xpath
    end_frame_xpath = '//kat-date-range-picker[@id="daily-time-picker-kat-date-range-picker"]/xbotShadowRoot/kat-date-picker[2]'
    # 开始时间框左箭头
    satrt_left_xpath = '//kat-date-range-picker[@id="daily-time-picker-kat-date-range-picker"]/xbotShadowRoot/kat-date-picker[1]/xbotShadowRoot//kat-calendar[contains(@part,"date-picker-calendar")]/xbotShadowRoot//button[@class="cal-lft"]'
    start_right_xpath = '//kat-date-range-picker[@id="daily-time-picker-kat-date-range-picker"]/xbotShadowRoot/kat-date-picker[1]/xbotShadowRoot//kat-calendar[contains(@part,"date-picker-calendar")]/xbotShadowRoot//button[@class="cal-rgt"]'
    #结束时间左边箭头
    end_left_xpath= '//kat-date-range-picker[@id="daily-time-picker-kat-date-range-picker"]/xbotShadowRoot/kat-date-picker[2]/xbotShadowRoot//kat-calendar[contains(@part,"date-picker-calendar")]/xbotShadowRoot//button[@class="cal-lft"]'
    # 结束时间有箭头
    end_right_xpath = '//kat-date-range-picker[@id="daily-time-picker-kat-date-range-picker"]/xbotShadowRoot/kat-date-picker[2]/xbotShadowRoot//kat-calendar[contains(@part,"date-picker-calendar")]/xbotShadowRoot//button[@class="cal-rgt"]'

    # 开始时间框的年月xpath
    start_year_month_xpath = '//kat-date-range-picker[@id="daily-time-picker-kat-date-range-picker"]/xbotShadowRoot/kat-date-picker[1]/xbotShadowRoot//kat-calendar[contains(@part,"date-picker-calendar")]/xbotShadowRoot//span[@part="calendar-month-name"]'
    # 结束时间框的年月xpath 
    end_year_month_xpath = '//kat-date-range-picker[@id="daily-time-picker-kat-date-range-picker"]/xbotShadowRoot/kat-date-picker[2]/xbotShadowRoot//kat-calendar[contains(@part,"date-picker-calendar")]/xbotShadowRoot//span[@part="calendar-month-name"]'
    # 开始时间的日期元素
    start_days_xpath = '//kat-date-range-picker[@id="daily-time-picker-kat-date-range-picker"]/xbotShadowRoot/kat-date-picker[1]/xbotShadowRoot//kat-calendar[contains(@part,"date-picker-calendar")]/xbotShadowRoot//button[@data-day="{}"]'
    # 结束时间的日期元素
    end_days_xpath = '//kat-date-range-picker[@id="daily-time-picker-kat-date-range-picker"]/xbotShadowRoot/kat-date-picker[2]/xbotShadowRoot//kat-calendar[contains(@part,"date-picker-calendar")]/xbotShadowRoot//button[@data-day="{}"]'

    # CSV文件类型
    csv_xpath = '//*[@value="CSV"]'
    # txt文件类型
    txt_path = '//*[@value="TSV"]'
    # 下载按钮
    download_button = '//kat-table-body//kat-table-row[1]/kat-table-cell[last()]/kat-button'
    none_data_xpath = '//kat-table-body//kat-table-row[1]/kat-table-cell[last()]'
def get_domain_from_url(url):
    # 获取域名
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc  # 例如：www.example.com
    except Exception as e:
        return None   


def gen_selector(xpath):
    xpaths = xpath.split(">>")
    data = {
        "id": "xbot-xpath",
        "name": "动态元素",
        "type": "simple",
        "xpath": {"enable": "true", "segments": xpaths},
    }
    selector = Selector(data)
    return selector

def get_event_value(time_select):
    """将输入的事件日期转换为网页所需的值"""

    if time_select in ['今天', '今日', '到目前为止']:
        return 0
    elif time_select in ['昨天', '昨日', '前一天']:
        return 1
    elif ('3' in time_select and '0' not in time_select) or ('三' in time_select and '十' not in time_select):
        return 3
    elif '7' in time_select or '七' in time_select:
        return 7
    elif '14' in time_select or '十四' in time_select:
        return 14
    elif '30' in time_select or '三十' in time_select:
        return 30
    else:
        return -1


def trans_month(month):
    """将中文和英文月份转换为正常的数字"""

    month_en_to_num = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }

    month_zh_to_num = {
        "一月": 1,
        "二月": 2,
        "三月": 3,
        "四月": 4,
        "五月": 5,
        "六月": 6,
        "七月": 7,
        "八月": 8,
        "九月": 9,
        "十月": 10,
        "十一月": 11,
        "十二月": 12
    }

    if str(month).isalpha() and str(month).isascii():
        return month_en_to_num[month]
    else:
        return month_zh_to_num[month]


def select_date(web_page, target_time, select_type='start'):
    """进行日期选择""" 

    # 将目标时间进行拆分
    target_year, target_month, target_day = target_time.split('-')

    # 进行开始时间的选择
    if select_type == 'start':

        # 进行月份选择
        # 获取网页的开始时间
        start_web_year_month_ele = create_selector_shadow(Xpath.start_year_month_xpath)
        start_web_month, start_web_year = web_page.find(start_web_year_month_ele).get_text().strip().split(' ')
        print(start_web_month)
        # 将网页的月份进行转换
        start_web_month = trans_month(start_web_month)
        # 进行计算网页年月与目标年月之间的差值
        diff = (int(target_year) - int(start_web_year))* 12 + (int(target_month) - start_web_month) * 1
        # 如果差值大于0则说明目标年月大于网页年月登，点击右箭头
        if diff > 0:
            start_right_ele = create_selector_shadow(Xpath.start_right_xpath)
            # 差值数就是点击的次数
            for _ in range(diff):
                web_page.find(start_right_ele).click()
                sleep(0.5)
        # 否则点击左箭头
        else:
            start_left_ele = create_selector_shadow(Xpath.satrt_left_xpath)
            for _ in range(abs(diff)):  # 注 此时diff是负数，需要取绝对值
                web_page.find(start_left_ele).click()
                sleep(0.5)

        # 选择具体日
        start_days_ele = create_selector_shadow(Xpath.start_days_xpath.format(int(target_day)))
        web_page.find(start_days_ele).click()

    else:

        # 选择月份
        # 类型是end,则进行结束时间的选择
        # 获取网页的开始时间
        end_web_year_month_ele = create_selector_shadow(Xpath.end_year_month_xpath)
        end_web_month, end_web_year = web_page.find(end_web_year_month_ele).get_text().strip().split(' ')
        # 将网页的月份进行转换
        end_web_month = trans_month(end_web_month)
        # 进行计算网页年月与目标年月之间的差值
        diff = (int(target_year) - int(end_web_year))* 12 + (int(target_month) - end_web_month) * 1
        print(diff)
        # 如果差值大于0则说明目标年月大于网页年月登，点击右箭头
        if diff > 0:
            end_right_ele = create_selector_shadow(Xpath.end_right_xpath)
            # 差值数就是点击的次数
            for _ in range(diff):
                web_page.find(end_right_ele).click()
                # sleep(0.5)
        # 否则点击左箭头
        else:
            end_left_ele = create_selector_shadow(Xpath.end_left_xpath)
            for _ in range(abs(diff)):  # 注 此时diff是负数，需要取绝对值
                web_page.find(end_left_ele).click()
                # sleep(0.5)

        # 选择具体日期
        end_days_ele = create_selector_shadow(Xpath.end_days_xpath.format(int(target_day)))
        web_page.find(end_days_ele).click()

def tax_invoice(web_page, time_select, time_range, file_folder, file_name):
    """销量-税务发票下载"""

    # 跳转税务发票页面
    if "reportcentral/AFNShipmentInvoicingReport/1" not in web_page.get_url():
        # 获取域名
        domain_url = get_domain_from_url(web_page.get_url())
        # 进行拼接url
        url = domain_url + '/reportcentral/AFNShipmentInvoicingReport/1'

        # 进行跳转
        for _ in range(3):
            web_page.navigate(url)
            handler_container(web_page)
            break
        else:
            raise Exception('页面跳转失败')

    #点击事件日期，进行下拉框选择日期
    date_frame_sel = create_selector_shadow(Xpath.date_frame)
    web_page.find(date_frame_sel, timeout=5).hover()
    sleep(5)
    web_page.find(date_frame_sel, timeout=5).click()
    # 进行下拉框选择
    time_select = get_event_value(time_select)
    option_sel = create_selector_shadow(Xpath.option_xpath.format(time_select))
    web_page.find(option_sel, timeout=5).click()

    if time_select == -1:
        # 如果日期选择值为-1 则说明需要自定义事件选择
        # 对事件范围进行分割
        start_time = time_range.split('~')[0]
        end_time = time_range.split('~')[1]

        # 点击展开开始时间框
        start_frame_ele = create_selector_shadow(Xpath.start_frame_xpath)
        web_page.find(start_frame_ele).click()
        select_date(web_page, start_time)

        # 点击展开结束时间框 
        end_frame_ele = create_selector_shadow(Xpath.end_frame_xpath)
        web_page.find(end_frame_ele).click()
        select_date(web_page, end_time, select_type='end')
    
    # 进行报表类型下载
    if 'csv' in file_name:
        csv_sel = create_selector_shadow(Xpath.csv_xpath)
        web_page.find(csv_sel).click()
    elif 'txt' in file_name:
        txt_sel = create_selector_shadow(Xpath.txt_path)
        web_page.find(txt_sel).click()
    sleep(5)
    
    for _ in range(100):

        # 判断是否无数据可用
        none_data_sel = web_page.find_all_by_xpath(Xpath.none_data_xpath, timeout=5)
        if len(none_data_sel) >0 and none_data_sel[0].get_text() == '无可用数据':
            xbot.logging.error('本次导出的数据无法下载，无数据可用')
            return None
        # 点击下载
        download_sel = web_page.find_all_by_xpath(Xpath.download_button, timeout=5)
        if len(download_sel) > 0 and download_sel[0].get_attribute('label') == '下载':
            # download_sel[0].click()
            file_path = download_handler(web_page, download_sel[0], file_folder, file_name)
            return file_path
        web_page.reload()
        sleep(10)
def test():
    if 'xbot_extensions' in __file__:
        return
    web_page = xbot.web.get_active(mode='superbrowser')
    time_select = '确切日期'
    time_range = '2025-12-01~2025-12-28'
    file_folder = r'C:\Users\Administrator\Desktop'
    file_name = '测试.csv'
    tax_invoice(web_page, time_select, time_range, file_folder, file_name)

    exit()
    
def main(args):
    # 进行测试
    test()

    web_page = args.get('web_page')
    time_select = args.get('time_select') or '今天'
    time_range = args.get('time_range') or ''
    file_folder = args.get('file_folder')
    file_name = args.get('file_name')

    file_path = tax_invoice(web_page, time_select, time_range, file_folder, file_name)
    args['file_path'] = file_path