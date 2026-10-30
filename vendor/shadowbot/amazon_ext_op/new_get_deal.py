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
from .utils import get_domain
from ._amazon_api import switch_language
from datetime import datetime
from .create_element import create_selector
import re

# 表头字段（按照数据提取顺序）
HEADER_FIELDS = [
    "链接", "促销名称", "国家", "状态", "日期范围",
    "促销费用", "销售额", "商品已售出", "浏览量", "转化率", "费用/销售额"
]

class XPath:
    # 状态筛选相关
    status_dropdown = '//span[contains(text(), "状态")]'
    status_none = '//*[@label="未定"]/../..//*[text()="无"]'
    status_checkbox = '//kat-checkbox[@label="{}"]'
    status_apply = '//*[@label="未定"]/../../kat-button[@label="应用"]'
    
    # 国家筛选相关
    country_dropdown = '//*[contains(text(), "Amazon Stores")]'
    country_all = '//*[@label="所有"]'
    country_option = '//*[@class="smui-dropdown-list-option"]'
    country_apply = '//*[contains(text(), "Amazon Stores")]/../..//*[@label="应用"]'
    
    # 日期筛选相关
    date_dropdown = '//*[@id="search-and-filters"]//*[contains(text(), "日期")]'
    start_date_picker_host = '//kat-date-picker[@name="afterStartDate"]'
    start_date_picker_input = create_selector(
        '//kat-date-picker[@name="afterStartDate"]/xbotShadowRoot//*[local-name()="kat-input"][@type="text"]',
        name='开始日期输入框'
    )
    end_date_picker_host = '//kat-date-picker[@name="beforeStartDate"]'
    end_date_picker_input = create_selector(
        '//kat-date-picker[@name="beforeStartDate"]/xbotShadowRoot//*[local-name()="kat-input"][@type="text"]',
        name='结束日期输入框'
    )
    date_apply = create_selector('//ul[contains(@class, "d-block")]/*[local-name()="kat-button"][@label="应用"]/xbotShadowRoot/button[normalize-space(.)="应用"]',name ="日期应用")
    
    # 数据表格相关
    table_rows = '//*[@id="manage-table-container"]//*[local-name()="kat-table-body"]/*[local-name()="kat-table-row"]'
    no_data = '//div[contains(@class, "color-smui-dark-grey")]'
    
    # 翻页相关
    next_page = '//div[contains(@class, "pagination-bar")]/*[local-name()="kat-pagination"]/xbotShadowRoot//span[@part="pagination-nav-right" and not(contains(@class, "end"))]'


def transform_date(date_str: str) -> str:
    """
    转换日期格式：yyyy-mm-dd -> mm/dd/yyyy
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%m/%d/%Y")
    except Exception as e:
        raise Exception(f"日期格式错误：{date_str}，错误信息：{e}")


def parse_date_range(date_range: str) -> tuple:
    """
    解析日期范围：YYYY-MM-DD_YYYY-MM-DD -> (yyyy-mm-dd, yyyy-mm-dd)
    例如：2025-12-01_2025-12-31 -> (2025-12-01, 2025-12-31)
    """
    try:
        # 使用下划线分割，应该得到2部分：开始日期和结束日期
        parts = date_range.split("_")
        if len(parts) != 2:
            raise ValueError("日期格式错误，应为：YYYY-MM-DD_YYYY-MM-DD")
        # 第一部分是开始日期，第二部分是结束日期
        start_date = parts[0]
        end_date = parts[1]
        return start_date, end_date
    except Exception as e:
        raise Exception(f"日期范围格式错误：{date_range}，错误信息：{e}")


def to_deal_page(web_page: WebBrowser) -> bool:
    """
    导航到Deal页面
    返回：True表示成功，False表示无权限
    """
    url = '/merchandising-new'
    domain = get_domain(web_page)
    web_page.navigate(domain + url, load_timeout=100)
    sleep(3)
    
    # 检查是否有权限
    if web_page.get_url().endswith("/merchandising-new/landing"):
        return False
    return True


def set_status_filter(web_page: WebBrowser, campaign_status_filter: str = None):
    """
    设置状态筛选
    """
    if not campaign_status_filter:
        return
    
    try:
        # 点击状态筛选下拉框
        web_page.find_by_xpath(XPath.status_dropdown, timeout=5).click()
        sleep(0.5)
        
        # 点击"无"选项清除所有状态
        web_page.find_by_xpath(XPath.status_none, timeout=2).click()
        sleep(0.5)
        
        # 遍历每个状态并勾选（处理中文逗号和空格）
        status_list = [item.strip() for item in campaign_status_filter.replace("，", ",").split(",") if item.strip()]
        for status in status_list:
            try:
                checkbox_xpath = XPath.status_checkbox.format(status)
                web_page.find_by_xpath(checkbox_xpath, timeout=2).click()
            except Exception as e:
                print(f"选择状态 '{status}' 失败: {e}")
        
        # 点击应用按钮
        web_page.find_by_xpath(XPath.status_apply, timeout=2).click()
        sleep(2)
    except Exception as e:
        print(f"设置状态筛选失败: {e}")


def set_country_filter(web_page: WebBrowser, country: str = None):
    """
    设置国家筛选
    """
    if not country:
        return
    
    try:
        # 点击国家下拉框
        web_page.find_by_xpath(XPath.country_dropdown, timeout=5).click()
        sleep(0.5)
        
        # 点击"所有"按钮取消全选
        web_page.find_by_xpath(XPath.country_all, timeout=2).click()
        sleep(0.5)
        
        # 遍历所有国家选项（处理中文逗号和空格）
        country_list = [item.strip() for item in country.replace("，", ",").split(",") if item.strip()]
        country_options = web_page.find_all_by_xpath(XPath.country_option, timeout=2)
        
        for option in country_options:
            option_text = option.get_text()
            if option_text in country_list:
                option.click()
                sleep(0.3)
        
        # 点击应用按钮
        web_page.find_by_xpath(XPath.country_apply, timeout=2).click()
        sleep(2)
    except Exception as e:
        print(f"设置国家筛选失败: {e}")


def set_date_filter(web_page: WebBrowser, date_range: str = None):
    """
    设置日期范围筛选
    日期格式：YYYY-MM-DD_YYYY-MM-DD -> mm/dd/yyyy
    """
    if not date_range:
        return
    
    try:
        # 解析日期范围（去除前后空格）
        start_date_str, end_date_str = parse_date_range(date_range.strip())
        start_date_formatted = transform_date(start_date_str)
        end_date_formatted = transform_date(end_date_str)
        
        # 点击日期筛选下拉框
        web_page.find_by_xpath(XPath.date_dropdown, timeout=5).click()
        sleep(0.5)
        
        # 点击开始日期选择器
        web_page.find_by_xpath(XPath.start_date_picker_host, timeout=2).click()
        sleep(0.3)
        # 输入开始日期，并在末尾加上ESC快捷键关闭日期选择器
        web_page.find(XPath.start_date_picker_input).input(
            start_date_formatted + "{Esc}",
            contains_hotkey=True
        )
        sleep(0.5)
        
        # 点击结束日期选择器
        web_page.find_by_xpath(XPath.end_date_picker_host, timeout=2).click()
        sleep(0.3)
        # 输入结束日期，并在末尾加上ESC快捷键关闭日期选择器
        web_page.find(XPath.end_date_picker_input).input(
            end_date_formatted + "{Esc}",
            contains_hotkey=True
        )
        sleep(0.5)
        
        # 点击应用按钮
        web_page.find(XPath.date_apply, timeout=2).click()
        sleep(2)
    except Exception as e:
        raise Exception(f"设置日期筛选失败: {e}")


def check_no_data(web_page: WebBrowser) -> bool:
    """
    检查页面是否无数据
    """
    try:
        web_page.find_by_xpath(XPath.no_data, timeout=2)
        return True
    except:
        return False


def extract_row_data(row_element: WebElement, web_page: WebBrowser) -> list:
    """
    从表格行元素中提取数据，按照指定顺序直接获取原始文本
    顺序：链接、促销名称、国家、状态、日期范围、促销费用、销售额、商品已售出、浏览量、转化率、费用/销售额
    """
    try:
        # 1. 链接 (获取 href 属性，如果是相对路径则加上域名前缀)
        try:
            link_element = row_element.find_by_xpath('.//div[contains(@class, "hero-description")]/parent::a', timeout=1)
            link = link_element.get_attribute('href') or ""
            # 如果是相对路径，加上域名前缀
            if link and not link.startswith('http'):
                domain = get_domain(web_page)
                link = domain + link
        except:
            link = ""
        
        # 2. 促销名称 (获取文本)
        try:
            title_element = row_element.find_by_xpath('.//*[contains(@class, "hero-description")]', timeout=1)
            title = title_element.get_text() or ""
        except:
            title = ""
        
        # 3. 国家 (获取文本)
        try:
            country_element = row_element.find_by_xpath('.//*[local-name()="kat-flag"]/following-sibling::span', timeout=1)
            country = country_element.get_text() or ""
        except:
            country = ""
        
        # 4. 状态 (获取第一个 kat-badge 的 label 属性或文本)
        try:
            status_element = row_element.find_by_xpath('.//*[local-name()="kat-badge"][1]', timeout=1)
            status = status_element.get_attribute('label') or status_element.get_text() or ""
        except:
            status = ""
        
        # 5. 日期范围 (获取文本)
        try:
            date_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][3]//span[contains(@class, "d-inline-block")]', timeout=1)
            date_range = date_element.get_text() or ""
        except:
            date_range = ""
        
        # 6. 促销费用 (获取文本)
        try:
            fee_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][4]//*[contains(@class, "label")]', timeout=1)
            fee = fee_element.get_text() or ""
        except:
            fee = ""
        
        # 7. 销售额 (获取文本)
        try:
            sales_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][5]', timeout=1)
            sales = sales_element.get_text() or ""
        except:
            sales = ""
        
        # 8. 商品已售出 (获取文本)
        try:
            units_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][6]', timeout=1)
            units_sold = units_element.get_text() or ""
        except:
            units_sold = ""
        
        # 9. 浏览量 (获取文本)
        try:
            views_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][7]/div[1]', timeout=1)
            views = views_element.get_text() or ""
        except:
            views = ""
        
        # 10. 转化率 (获取文本)
        try:
            conversion_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][7]/div[2]', timeout=1)
            conversion_rate = conversion_element.get_text() or ""
        except:
            conversion_rate = ""
        
        # 11. 费用/销售额 (获取文本)
        try:
            fee_sales_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][8]', timeout=1)
            fee_sales_ratio = fee_sales_element.get_text() or ""
        except:
            fee_sales_ratio = ""
        
        # 按照指定顺序组装数据行
        row_data = [
            link,              # 1. 链接
            title,             # 2. 促销名称
            country,           # 3. 国家
            status,            # 4. 状态
            date_range,        # 5. 日期范围
            fee,               # 6. 促销费用
            sales,             # 7. 销售额
            units_sold,        # 8. 商品已售出
            views,             # 9. 浏览量
            conversion_rate,   # 10. 转化率
            fee_sales_ratio    # 11. 费用/销售额
        ]
        print(row_data)
        return row_data
    except Exception as e:
        print(f"提取行数据失败: {e}")
        return None


def get_all_data(web_page: WebBrowser, campaign_status_filter: str = None) -> list:
    """
    获取所有页面的数据
    """
    all_data = []
    
    while True:
        # 检查是否无数据
        if check_no_data(web_page):
            print("页面无数据")
            break
        
        # 获取当前页面的所有行
        try:
            row_elements = web_page.find_all_by_xpath(XPath.table_rows, timeout=5)
            print(f"找到 {len(row_elements)} 行数据")
        except Exception as e:
            print(f"获取表格行失败: {e}")
            break
        
        # 遍历每一行提取数据
        for row_element in row_elements:
            row_data = extract_row_data(row_element, web_page)
            if row_data:
                # 直接添加数据，状态筛选已在set_status_filter中完成
                all_data.append(row_data)
        
        # 尝试翻页
        try:
            next_page_element = web_page.find_by_xpath(XPath.next_page, timeout=2)
            next_page_element.click()
            sleep(2)
        except:
            # 没有下一页，说明已经是最后一页
            break
    # print(all_data)
    return all_data


def get_deal_data(web_page: WebBrowser, campaign_status_filter: str = None, country: str = None, date_range: str = None) -> list:
    """
    获取Deal数据的主函数
    
    参数:
        web_page: 浏览器对象
        campaign_status_filter: 促销状态筛选，多个状态用逗号分隔
        country: 国家筛选，多个国家用逗号分隔
        date_range: 日期范围筛选，格式：YYYY-MM-DD_YYYY-MM-DD
    
    返回:
        List[List]: 第一行为表头，后续行为数据
    """
    # 导航到Deal页面
    if not to_deal_page(web_page):
        # 无权限，返回空列表
        print("无权限，返回空列表")
        return []
    
    # 切换语言
    switch_language(web_page, 'zh_CN')
    web_page.wait_load_completed(timeout=30)

    
    # 设置筛选条件
    set_status_filter(web_page, campaign_status_filter)
    set_country_filter(web_page, country)
    if date_range:
        set_date_filter(web_page, date_range)
    
    # 等待数据加载
    sleep(3)
    
    # 获取所有数据
    all_data = get_all_data(web_page, campaign_status_filter)
    
    # 组装结果：表头 + 数据行
    result = [HEADER_FIELDS] + all_data
    print(result)
    return result


def test_get_deal_data():
    """
    测试函数
    """
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    campaign_status_filter = "正在进行,已结束,未定"  # 可选
    country = "美国,加拿大"  # 可选
    date_range = "2025-12-01_2025-12-31"  # 可选
    result = get_deal_data(web_page, campaign_status_filter, country, date_range)
    print(f"获取到 {len(result) - 1} 行数据（不含表头）")
    for i, row in enumerate(result[:5]):  # 只打印前5行
        print(f"第{i}行: {row}")
    exit()


def main(args):
    """
    主函数入口
    """
    # 测试代码入口
    test_get_deal_data()
    
    # 业务代码入口
    web_page = args.get('web_page')
    campaign_status_filter = args.get('campaignStatusFilter')  # 促销状态筛选
    country = args.get('country')  # 国家筛选
    date_range = args.get('date_range')  # 日期范围筛选
    
    result = get_deal_data(web_page, campaign_status_filter, country, date_range)
    args['result'] = result
