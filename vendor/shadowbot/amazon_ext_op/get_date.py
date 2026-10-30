import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from datetime import datetime, timedelta
from xbot.web import WebBrowser
import time


def select_date_generic(web_page: WebBrowser, target_date_str: str, xpath_config: dict) -> bool:
    """
    一个通用的、可配置的日期选择函数（工具方法）。
    """
    try:
        target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
        target_year, target_month, target_day = target_dt.year, target_dt.month, target_dt.day
        month_map = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        #初始化
        input_xpath = xpath_config['input']
        header_xpath = xpath_config['header']
        prev_button_xpath = xpath_config['prev_button']
        next_button_xpath = xpath_config['next_button']
        day_xpath_template = xpath_config['day_template']
        #点击
        web_page.find_by_xpath(input_xpath).click()
        time.sleep(1)

        for _ in range(36):
            if not web_page.find_by_xpath(header_xpath, timeout=5):
                print("错误：未能找到日历的月份标题。")
                return False
            header_text = web_page.find_by_xpath(header_xpath, timeout=5).get_text().strip()
            current_month_name, current_year_str = header_text.split()
            current_year = int(current_year_str)
            current_month = month_map[current_month_name]
            if current_year == target_year and current_month == target_month:
                break
            else:
                if target_dt < datetime(current_year, current_month, 1):
                    web_page.find_by_xpath(prev_button_xpath, timeout=4).click()
                else:
                    web_page.find_by_xpath(next_button_xpath, timeout=4).click()
            time.sleep(0.5)
        else:
            print("错误：在12次尝试内未能导航到目标月份。")
            return False

        day_xpath = day_xpath_template.format(target_day=target_day)
        
        if web_page.find_by_xpath(day_xpath):
            web_page.find_by_xpath(day_xpath).click()
            return True
        else:
            print(f"错误：在当前月份视图中找不到日期 '{target_day}' 或该日期不可选。")
            return False
            
    except Exception as e:
        print(f"选择日期时发生未知错误：{e}")
        return False

# (B) 业务流程层 - 使用最终版“可见性判断”XPath
def execute_date_selection_workflow(web_page: WebBrowser,start_date_str: str, end_date_str: str):
    #日期XPath
    generic_calendar_xpaths = {
        'header': '//h4[@class="a-cal-month-header" and not(ancestor::div[contains(@style,"display: none")])]',
        'prev_button': '//a/i[contains(@class, "a-icon-previous") and not(ancestor::div[contains(@style,"display: none")])]',
        'next_button': '//a/i[contains(@class, "a-icon-next") and not(ancestor::div[contains(@style,"display: none")])]',
        'day_template': "//td[contains(@class, 'a-cal-inbound') and not(ancestor::div[contains(@style, 'display: none')])]/a[text()='{target_day}']"
    }

    # --- 1. 执行开始日期选择 ---
    start_date_config = generic_calendar_xpaths.copy()
    start_date_config['input'] = '//*[@id="all-orders-report-start-date"]//input'
    
    success_start = select_date_generic(web_page, start_date_str, start_date_config)
    if not success_start:
        print("\n 起始日期选择失败，流程终止。")
        return
    
    time.sleep(1)

    # --- 2. 执行结束日期校验和选择 ---
    try:
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
        today = datetime.now().date()
        
        if end_dt.date() > today or start_dt > end_dt or (end_dt - start_dt).days > 31:
            print(f"校验失败：截止日期不满足要求（晚于今天、早于开始日期或间隔超一个月）。")
            return
        
        end_date_config = generic_calendar_xpaths.copy()
        end_date_config['input'] = '//div[@id="all-orders-report-end-date"]//input[contains(@class, "a-cal-input")]'

        success_end = select_date_generic(web_page, end_date_str, end_date_config)
        if not success_end:
            print("\n截止日期选择失败，流程终止。")
            return
    except Exception as e:
        print(f"处理截止日期时发生错误: {e}")
        return


def test():
    if "xbot_extensions" in __file__:
        return
    web_page = xbot.web.get_active(mode = 'ziniaobrowser')
    target_start_date_str = "2024-12-28" 
    target_end_date_str = "2025-01-15"
    # 调用业务流程方法，将日期作为参数传入
    execute_date_selection_workflow(web_page,target_start_date_str, target_end_date_str)
def main(args):
    test()
    web_page = args.get('web_page')
    start_date = args.get('start_date') # 开始日期
    end_date = args.get('end_date') # 结束日期
    # 调用业务流程方法，将日期作为参数传入
    execute_date_selection_workflow(web_page,start_date,end_date)
