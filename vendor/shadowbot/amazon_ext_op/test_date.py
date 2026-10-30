# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from datetime import datetime
from xbot.web import WebBrowser, WebElement
import time

# =================================================================================
# --- 用户自定义区域 ---
# 请在此处设置您想要选择的起始日期 (格式: "年-月-日")

# =================================================================================


def select_date_on_calendar(web_page: WebBrowser ,target_date_str: str, date_input_xpath: str):
    """
    一个通用的函数，用于在您指定的日历控件上选择一个确切的日期。

    :param target_date_str: 目标日期字符串，格式为 "YYYY-MM-DD"。
    :param date_input_xpath: 打开日历控件的输入框的XPath。
    """
    try:
        # --- 1. 数据准备 ---
        # 将输入的日期字符串转换为程序可以理解的日期对象
        target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
        target_year, target_month, target_day = target_dt.year, target_dt.month, target_dt.day

        # 创建一个月份名称到数字的映射，用于解析日历标题
        month_map = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
        }

        # --- 2. 打开日历 ---
        # 点击日期输入框，弹出日历选择界面
        print(f"步骤1: 点击日期输入框...")
        web_page.find_by_xpath('//*[@id="all-orders-report-start-date"]//input').click()
        time.sleep(1)  # 等待1秒，确保日历完全加载出来

        # --- 3. 切换到正确的月份 ---
        print(f"步骤2: 导航至目标月份 {target_year}-{target_month}...")
        # 设置一个最大循环次数（12次），防止因意外情况导致无限循环
        for _ in range(12):
            header_xpath = '//div[@id="a-popover-content-3"]//*[local-name()="h4"][@class="a-cal-month-header"]'
            if not web_page.find_by_xpath(header_xpath , timeout = 5):
                print("错误：未能找到日历的月份标题。")
                return

            # 获取日历当前显示的月份和年份，例如 "September 2025"
            header_text = web_page.find_by_xpath(header_xpath , timeout = 5).get_text()
            current_month_name, current_year_str = header_text.split()
            current_year = int(current_year_str)
            current_month = month_map[current_month_name]
            
            print(f"  - 当前显示: {current_month_name} {current_year_str}")

            # 检查当前显示的月份是否就是我们想要的月份
            if current_year == target_year and current_month == target_month:
                print(f"  - 已找到目标月份。")
                break  # 如果是，就跳出循环，准备选择日期

            # 如果不是，则判断是该点击“上一月”还是“下一月”
            current_view_dt = datetime(current_year, current_month, 1)
            target_view_dt = datetime(target_year, target_month, 1)

            if target_view_dt < current_view_dt:
                # 目标月份在当前显示月份之前，点击“上一月”按钮
                print(f"  - 目标月份较早, 点击 '上一月'。")
                prev_month_xpath = '//div[@id="a-popover-content-3"]//a/i[contains(@class, "a-icon-previous")]'
                web_page.find_by_xpath(prev_month_xpath , timeout = 4).click()
            else:
                # 目标月份在当前显示月份之后，点击“下一月”按钮
                print(f"  - 目标月份较晚, 点击 '下一月'。")
                next_month_xpath = '//a/i[contains(@class, "a-icon-next")]'
                if web_page.find_by_xpath(next_month_xpath):
                    web_page.find_by_xpath(next_month_xpath).click()
                else:
                    print(f"错误：无法导航到未来的月份 {target_year}-{target_month}，因为“下一月”按钮不存在。")
                    return
            
            time.sleep(0.5)  # 等待0.5秒，让月份切换动画完成
        else:
            # 如果循环12次后仍未找到正确的月份，则报错退出
            print("错误：在12次尝试内未能导航到目标月份。")
            return

        # --- 4. 点击具体的日期 ---
        print(f"步骤3: 点击日期 '{target_day}'...")
        # 构造目标日期的XPath，并执行点击操作
        day_xpath = f"//td[contains(@class, 'a-cal-inbound') and not(ancestor::div[contains(@style, 'display: none')])]/a[text()='{target_day}']"
        
        if web_page.find_by_xpath(day_xpath):
            web_page.find_by_xpath(day_xpath).click()
            print(f"✅ 成功选择日期: {target_date_str}")
        else:
            print(f"错误：在当前月份视图中找不到日期 '{target_day}' 或该日期不可选。")

    except Exception as e:
        print(f"发生未知错误：{e}")



def select_end_date(web_page: WebBrowser, start_date_str: str, end_date_str: str):

    print(f"\n--- 开始选择截止日期: {end_date_str} ---")

    # --- 1. 日期有效性预检查 ---
    print("--- 正在进行截止日期有效性预检查 ---")
    try:
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date_str, "%Y-m-%d")
        today = datetime.now().date()

        if end_dt.date() > today:
            print(f"❌ 校验失败：截止日期 {end_date_str} 不能晚于今天 ({today.strftime('%Y-%m-%d')})。")
            return False
        if start_dt > end_dt:
            print(f"❌ 校验失败：截止日期 {end_date_str} 不能早于起始日期 {start_date_str}。")
            return False
        if (end_dt - start_dt).days > 31:
            print(f"❌ 校验失败：截止日期和起始日期的间隔超过一个月。")
            return False
        
        print("✅ 日期有效性校验通过。")
    except ValueError:
        print("❌ 校验失败：日期格式错误，请确保格式为 'YYYY-MM-DD'。")
        return False

    # --- 2. 开始浏览器操作 ---
    try:
        target_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
        target_year, target_month, target_day = target_dt.year, target_dt.month, target_dt.day
        month_map = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
        }

        # --- 定义结束日期日历相关的XPath路径 ---
        # ‼️ 重要：请根据实际情况替换下面的XPath占位符
        end_date_input_xpath = '//div[@id="all-orders-report-end-date"]//input[contains(@class, "a-cal-input")]'
        end_date_header_xpath = '//h4[@class="a-cal-month-header"]'  # ‼️ 请替换为结束日期日历的月份标题XPath
        end_date_prev_button_xpath = '//a/i[contains(@class, "a-icon-previous")]' # ‼️ 请替换为结束日期日历的“上一月”按钮XPath
        end_date_next_button_xpath = '//a/i[contains(@class, "a-icon-next")]'     # ‼️ 请替换为结束日期日历的“下一月”按钮XPath
        
        # --- 打开日历 ---
        print("步骤1: 点击结束日期输入框...")
        web_page.find_by_xpath(end_date_input_xpath).click()
        time.sleep(1)

        # --- 切换月份 ---
        print(f"步骤2: 导航至目标月份 {target_year}-{target_month}...")
        for _ in range(12):
            if not web_page.find_by_xpath(end_date_header_xpath, timeout=5):
                print("错误：未能找到结束日期日历的月份标题。")
                return False
            
            header_text = web_page.find_by_xpath(end_date_header_xpath, timeout=5).get_text()
            current_month_name, current_year_str = header_text.split()
            current_year = int(current_year_str)
            current_month = month_map[current_month_name]

            if current_year == target_year and current_month == target_month:
                break

            if target_dt < datetime(current_year, current_month, 1):
                web_page.find_by_xpath(end_date_prev_button_xpath, timeout=4).click()
            else:
                web_page.find_by_xpath(end_date_next_button_xpath, timeout=4).click()
            time.sleep(0.5)
        else:
            print("错误：在12次尝试内未能导航到目标月份。")
            return False

        # --- 点击日期 ---
        print(f"步骤3: 点击日期 '{target_day}'...")
        # ‼️ 请根据结束日期日历的结构，确认这个XPath是否需要修改
        day_xpath = f"//td[contains(@class, 'a-cal-inbound') and not(ancestor::div[contains(@style, 'display: none')])]/a[text()='{target_day}']"
        
        if web_page.find_by_xpath(day_xpath):
            web_page.find_by_xpath(day_xpath).click()
            print(f"✅ 成功选择截止日期: {end_date_str}")
            return True
        else:
            print(f"错误：在当前月份视图中找不到日期 '{target_day}' 或该日期不可选。")
            return False

    except Exception as e:
        print(f"选择截止日期时发生未知错误：{e}")
        return False





# --- 脚本执行入口 ---
def test():
    if "xbot_extensions" in __file__:
        return
    start_date_input_xpath = '//*[@id="all-orders-report-start-date"]//input'
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    target_start_date_str = "2024-08-05"
# --- 执行选择起始日期的操作 ---
    print(f"--- 开始选择起始日期: {target_start_date_str} ---")
    select_date_on_calendar(web_page,target_start_date_str, start_date_input_xpath)
    print("\n--- 起始日期选择流程执行完毕 ---")
# 定义起始日期输入框的XPath
# 这个XPath是根据您提供的HTML代码编写的
def main(args):
    test()
    pass