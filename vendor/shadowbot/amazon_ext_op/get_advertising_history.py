# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from .utils import get_ad_domain
from ._amazon_api import switch_language_on_ad_page
from datetime import datetime

# XPath定义
class Xpath:
    # 日期范围按钮
    DateRangeButton = '//button[@data-e2e-id="dateRangePickerButton"]'
    # 所有可见月份标题
    CurrentMonthTitle = '//div[contains(@class, "CalendarMonth") and @data-visible="true"]//div[contains(@class, "CalendarMonth_caption")]'
    # 上一月箭头
    PrevMonthButton = '//button[.//i[@data-testid="storm-ui-icon-angle-left"]]'
    # 下一月箭头
    NextMonthButton = '//button[.//i[@data-testid="storm-ui-icon-angle-right"]]'
    # 保存按钮（启用状态）
    SaveButton = '//button[normalize-space()="保存"][not(@disabled)]'
    # 下一页按钮（可点击状态）
    NextPageButton = '//button[@data-e2e-id="nextButton"][not(@disabled)]'
    # 右侧滚动容器（JS Scroll Target）
    ScrollTarget = '(//div[contains(@class, "ReactVirtualized__Grid")][contains(@class, "bottomRightGridStyle")])[1]'

# 中文月份映射
MONTH_MAP = {
    '一月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
    '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}

def to_page_if_needed(web_page: WebBrowser, url: str):
    """如果当前页面不是目标页面，则导航到目标页面"""
    current_url = web_page.get_url()
    if not current_url.startswith(url):
        web_page.navigate(url, load_timeout=300)
        web_page.wait_load_completed(timeout=30)

def select_single_date(web_page: WebBrowser, target_date_str: str):
    """选择单个日期（支持多月份DOM）"""
    # 解析目标日期
    target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
    target_year = target_dt.year
    target_month = target_dt.month
    target_day = target_dt.day
    
    # 翻页逻辑
    max_iterations = 24  # 最多翻12个月（前后各12个月）
    iteration = 0
    
    while iteration < max_iterations:
        # 获取所有可见月份的标题文本
        try:
            month_title_elements = web_page.find_all_by_xpath(Xpath.CurrentMonthTitle, timeout=5)
            if not month_title_elements:
                raise Exception("未找到可见的月份标题")
        except Exception as e:
            print(f"获取月份标题失败: {e}")
            raise
        
        # 总是使用第一个（索引0）作为"左月份"
        left_month_element = month_title_elements[0]
        left_month_text = left_month_element.get_text().strip()
        
        # 解析左月份（例如 "十一月 2025"）
        parts = left_month_text.split()
        if len(parts) != 2:
            raise Exception(f"无法解析月份标题格式: {left_month_text}")
        
        left_month_name = parts[0]
        left_year = int(parts[1])
        left_month = MONTH_MAP.get(left_month_name)
        
        if left_month is None:
            raise Exception(f"无法识别的月份名称: {left_month_name}")
        
        # 计算右月份（左月份+1）
        right_year = left_year
        right_month = left_month + 1
        if right_month > 12:
            right_month = 1
            right_year += 1
        
        # 将目标年月和左右月份转换为可比较的数值
        target_value = target_year * 12 + target_month
        left_value = left_year * 12 + left_month
        right_value = right_year * 12 + right_month
        
        # 比较逻辑
        if target_value < left_value:
            # 目标 < 左月份，点击上一月
            try:
                prev_btn = web_page.find_by_xpath(Xpath.PrevMonthButton, timeout=5)
                prev_btn.click()
                sleep(0.5)
            except Exception as e:
                raise Exception(f"点击上一月按钮失败: {e}")
        elif target_value > right_value:
            # 目标 > 右月份，点击下一月
            try:
                next_btn = web_page.find_by_xpath(Xpath.NextMonthButton, timeout=5)
                next_btn.click()
                sleep(0.5)
            except Exception as e:
                raise Exception(f"点击下一月按钮失败: {e}")
        else:
            # 目标在左或右月份内，跳出循环
            break
        
        iteration += 1
    
    if iteration >= max_iterations:
        raise Exception(f"无法导航到目标月份 {target_year}-{target_month}，超过最大迭代次数")
    
    # 格式化日期为亚马逊要求的格式（去除前导零）
    formatted_date_str = f"{target_year}年{target_month}月{target_day}日"
    
    # 点击日期（检查是否可用）
    try:
        date_xpath = f'//td[contains(@class, "CalendarDay")][contains(@aria-label, "{formatted_date_str}")]'
        date_elements = web_page.find_all_by_xpath(date_xpath, timeout=5)
        
        if not date_elements:
            raise Exception(f"未找到日期元素: {formatted_date_str}")
        
        # 找到第一个没有 aria-disabled="true" 的元素
        date_element = None
        for elem in date_elements:
            aria_disabled = elem.get_attribute('aria-disabled')
            if aria_disabled != 'true':
                date_element = elem
                break
        
        if date_element is None:
            raise Exception(f"日期 {formatted_date_str} 不可用（已被禁用）")
        
        date_element.click()
        sleep(0.5)
        # print(f"成功选择日期: {target_date_str}")
    except Exception as e:
        raise Exception(f"点击日期失败: {e}，日期格式: {formatted_date_str}")

def select_amazon_date_range(web_page: WebBrowser, start_date_str: str, end_date_str: str):
    
    # 打开日历
    try:
        date_button = web_page.find_by_xpath(Xpath.DateRangeButton, timeout=10)
        date_button.click()
        sleep(1)
    except Exception as e:
        raise Exception(f"打开日历失败: {e}")
    
    # 选择开始日期
    select_single_date(web_page, start_date_str)
    
    # 选择结束日期
    select_single_date(web_page, end_date_str)
    
    # 等待并点击保存按钮（等待按钮启用）
    try:
        # 等待保存按钮启用（最多等待10秒）
        max_wait = 20  # 最多等待20次，每次0.5秒
        wait_count = 0
        save_button = None
        
        while wait_count < max_wait:
            try:
                save_button = web_page.find_by_xpath(Xpath.SaveButton, timeout=1)
                if save_button:
                    break
            except:
                pass
            sleep(0.5)
            wait_count += 1
        
        if save_button is None:
            raise Exception("保存按钮未启用或未找到")
        
        save_button.click()
        sleep(1)
    except Exception as e:
        raise Exception(f"点击保存按钮失败: {e}")

def setup_page_and_filter(web_page: WebBrowser, start_date: str, end_date: str):
    """设置页面和筛选条件"""
    # 1. 打开广告历史网页
    domain = get_ad_domain(web_page)
    url = f"{domain}/cm/history"
    to_page_if_needed(web_page, url)
    sleep(2)
    
    # 2. 切换语言为中文
    try:
        switch_language_on_ad_page(web_page, 'zh_CN')
        sleep(2)
    except Exception as e:
        print(f"切换语言失败: {e}")
        # 语言切换失败不影响后续操作，继续执行
    
    # 3. 选择日期范围（使用自定义函数）
    try:
        select_amazon_date_range(web_page, start_date, end_date)
        sleep(2)  # 等待数据加载
    except Exception as e:
        print(f"选择日期范围失败: {e}")
        raise

def extract_row_data(web_page: WebBrowser, row_index: int) -> dict:
    """从指定行索引提取数据"""
    row_data = {}
    
    try:
        # 第 0 列 (名称 - 左侧)
        name_element = web_page.find_by_xpath(
            f'//div[@data-e2e-index="cellIndex_{row_index}_0"]//*[@data-e2e-id="entityNameRenderer"]',
            timeout=1
        )
        row_data['名称'] = name_element.get_text().strip()
    except:
        row_data['名称'] = ""
    
    try:
        # 第 1 列 (类型 - 右侧)
        type_element = web_page.find_by_xpath(
            f'//div[@data-e2e-index="cellIndex_{row_index}_1"]//span[@data-e2e-id="simpleTextRenderer"]',
            timeout=1
        )
        row_data['类型'] = type_element.get_text().strip()
    except:
        row_data['类型'] = ""
    
    try:
        # 第 2 列 (修改前 - 右侧)
        from_element = web_page.find_by_xpath(
            f'//div[@data-e2e-index="cellIndex_{row_index}_2"]//span[@data-e2e-id="simpleTextRenderer"]',
            timeout=1
        )
        row_data['修改前'] = from_element.get_text().strip()
    except:
        row_data['修改前'] = ""
    
    try:
        # 第 3 列 (修改后 - 右侧)
        to_element = web_page.find_by_xpath(
            f'//div[@data-e2e-index="cellIndex_{row_index}_3"]//span[@data-e2e-id="simpleTextRenderer"]',
            timeout=1
        )
        row_data['修改后'] = to_element.get_text().strip()
    except:
        row_data['修改后'] = ""
    
    try:
        # 第 4 列 (日期 - 右侧)
        date_element = web_page.find_by_xpath(
            f'//div[@data-e2e-index="cellIndex_{row_index}_4"]//span[@data-e2e-id="simpleTextRenderer"]',
            timeout=1
        )
        row_data['日期'] = date_element.get_text().strip()
    except:
        row_data['日期'] = ""
    
    return row_data

def scroll_to_row(scroll_target: WebElement, row_index: int):
    """滚动到指定行"""
    # 每隔5行滚动一次
    if row_index % 5 == 0:
        # 使用scroll_to方法滚动到指定位置
        scroll_top = row_index * 50
        scroll_target.scroll_to(
            location='point',
            behavior='instant',
            top=scroll_top,
            left=0,
            search_up=False
        )
        sleep(0.5)  # 等待滚动完成

def scrape_table_data(web_page: WebBrowser) -> list:
    """抓取表格数据"""
    data = []
    
    # 定位右侧滚动容器
    try:
        scroll_target = web_page.find_by_xpath(Xpath.ScrollTarget, timeout=10)
    except Exception as e:
        print(f"未找到滚动容器: {e}")
        return data
    
    page_num = 1
    row_index = 0
    consecutive_empty_rows = 0  # 连续空行计数
    max_empty_rows = 4  # 最大连续空行数，超过则认为无数据
    
    while True:
        # print(f"正在处理第 {page_num} 页，行索引: {row_index}")
        
        # 滚动到当前行
        scroll_to_row(scroll_target, row_index)
        
        # 提取数据
        row_data = extract_row_data(web_page, row_index)
        
        # 检查是否为空行（所有字段都为空）
        if all(not value for value in row_data.values()):
            consecutive_empty_rows += 1
            if consecutive_empty_rows >= max_empty_rows:
                # 检查是否有下一页
                try:
                    next_btn = web_page.find_by_xpath(Xpath.NextPageButton, timeout=3)
                    if next_btn:
                        print(f"发现下一页按钮，点击翻页")
                        next_btn.click()
                        sleep(3)  # 等待下一页加载
                        page_num += 1
                        row_index = 0  # 重置行索引
                        consecutive_empty_rows = 0  # 重置空行计数
                        continue
                    else:
                        print("未找到下一页按钮，所有数据抓取完成")
                        break
                except:
                    print("未找到下一页按钮，所有数据抓取完成")
                    break
        else:
            # 有数据，添加到列表
            data.append(row_data)
            consecutive_empty_rows = 0  # 重置空行计数
        
        row_index += 1
        
        # 防止无限循环（设置最大行数限制）
        if row_index > 350:
            print("达到最大行数限制，停止抓取")
            break
    
    return data

def get_advertising_history(
    web_page: WebBrowser,
    start_date: str,
    end_date: str
) -> dict:

    # 参数校验
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    
    # 1. 设置页面和筛选条件
    setup_page_and_filter(web_page, start_date, end_date)
    
    # 等待数据加载
    sleep(3)
    
    # 2. 抓取表格数据
    data = scrape_table_data(web_page)
    
    return {
        'data': data
    }

def test_get_advertising_history():
    """测试函数"""
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    start_date = '2025-12-01'
    end_date = '2025-12-04'
    
    result = get_advertising_history(
        web_page=web_page,
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"处理完成:{result}")
    print(f"数据条数: {len(result['data'])}")
    

    
    exit()

def main(args):
    """主函数入口"""
    # 测试代码入口
    test_get_advertising_history()
    
    # 业务代码入口
    web_page = args.get('web_page')
    start_date = args.get('开始日期')
    end_date = args.get('结束日期')
    
    result = get_advertising_history(
        web_page=web_page,
        start_date=start_date,
        end_date=end_date
    )
    
    # 将结果保存到args中
    args['data'] = result['data']
