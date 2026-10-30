# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, databook
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from .utils import get_domain
from ._amazon_api import switch_language
from datetime import datetime
from .create_element import create_selector, create_selector_shadow
import re
from .utils import handler_feedback

# 表头字段（按照数据提取顺序）
HEADER_FIELDS = [
    "链接", "促销名称", "国家", "状态", "日期范围",
    "促销费用", "销售额", "商品已售出", "浏览量", "转化率", "费用/销售额"
]

STATUS_MAP = {
    '已取消':'CANCELED',
    '取消':'CANCELING',
    '已结束':'ENDED',
    '等待生效':'PROCESSING',
    '正在进行':'RUNNING',
    '存在问题':'SUPPRESSED',
    '即将开始':'UPCOMING',
    '失败':'FAILED'
}

AMAZON_MARKETPLACE_IDS = {
    # 美洲
    "美国": "ATVPDKIKX0DER",
    "加拿大": "A2EUQ1WTGCTBG2",
    "墨西哥": "A1AM78C64UM0Y8",
    "巴西": "A2Q3Y263D00KWC",

    # 亚太
    "新加坡": "A19VAU5U5O7RUS",
    "日本": "A1VC38T7YXB528",
    "澳大利亚": "A39IBJ37TRP1C6",
    "印度": "A21TJRUUN4KGV",

    # 欧洲
    "英国": "A1F83G8C2ARO7P",
    "德国": "A1PA6795UKMFR9",
    "法国": "A13V1IB3VIYZZH",
    "意大利": "APJ6JRA9NG5V4",
    "西班牙": "A1RKKUPIHCS9HS",
    "荷兰": "A1805IZSGTT6HS",
    "瑞典": "A2NODRKZP88ZB9",
    "波兰": "A1C3SOZRARQ6R3",
    "土耳其": "A33AVAJ2PDY3EV",

    # 中东
    "阿联酋": "A2VIGQ35RCS4UG",
}

class XPath:
    # 状态筛选相关
    status_dropdown = '//kat-dropdown[@data-testid="quick-filter-promotionStatus"]'
    status_checkbox = '//kat-dropdown[@data-testid="quick-filter-promotionStatus"]/xbotShadowRoot//kat-option[@value="{}"]'
    status_apply = '//kat-dropdown[@data-testid="quick-filter-promotionStatus"]/xbotShadowRoot//*[@id="pending-apply"]'
    clear_filters = '//kat-data-grid/xbotShadowRoot//kat-link[@part="clear-filters"]'
    
    # 国家筛选相关
    country_dropdown = '//kat-dropdown[@data-testid="quick-filter-store"]'
    country_all = '//kat-dropdown[@data-testid="quick-filter-store"]/xbotShadowRoor//*[@id="select-all"]'
    country_option = '//kat-dropdown[@data-testid="quick-filter-store"]/xbotShadowRoot//kat-option[@value="{}"]'
    country_apply = '//kat-dropdown[@data-testid="quick-filter-store"]/xbotShadowRoot//*[@id="pending-apply"]'
    
    # 日期筛选相关
    all_filter = '//kat-data-grid/xbotShadowRoot//*[@class="all-filter-button"]//kat-button'
    date_dropdown = '//*[contains(@class,"filter-toolpanel")]'
    start_dropdown = '(//*[contains(@class,"filter-toolpanel")]//*[@ref="eTitle"])[5]'
    end_dropdown = '(//*[contains(@class,"filter-toolpanel")]//*[@ref="eTitle"])[6]'

    start_status_frame = '(//*[@ref="eDisplayField"])[1]'
    time_input = '//*[@ref="eCondition1Body"]//input[@type="date"]'

    # 数据表格相关
    table_rows = '//*[@ref="centerContainer"]//*[@ref="eContainer"]/div'
    no_data = '//*[contains(@class,"no-rows")]'
    
    # 翻页相关
    next_page = '//div[@ref="btNext"]'


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
        
        # 遍历每个状态并勾选（处理中文逗号和空格）
        status_list = [item.strip() for item in campaign_status_filter.replace("，", ",").split(",") if item.strip()]
        for status in status_list:
            try:
                status_value = STATUS_MAP[status]
                checkbox_xpath = XPath.status_checkbox.format(status_value)
                checkbox_sel = create_selector_shadow(checkbox_xpath)
                web_page.find(checkbox_sel, timeout=2).click()
            except Exception as e:
                print(f"选择状态 '{status}' 失败: {e}")
        
        # 点击应用按钮
        apply_sel = create_selector_shadow(XPath.status_apply)
        web_page.find(apply_sel, timeout=2).click()
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
        
        # 遍历所有国家选项（处理中文逗号和空格）
        country_list = [item.strip() for item in country.replace("，", ",").split(",") if item.strip()]
        for country in country_list:
            country_option_xpath = XPath.country_option.format(AMAZON_MARKETPLACE_IDS[country])
            country_options_sel = create_selector_shadow(country_option_xpath)
            country_options = web_page.find(country_options_sel, timeout=2).click()
        
        # 点击应用按钮
        apply_sel = create_selector_shadow(XPath.country_apply)
        web_page.find(apply_sel, timeout=2).click()
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
        # 将数据进行分割
        start_time = date_range.split('_')[0].replace('-','')
        end_time = date_range.split('_')[1].replace('-','')

        sleep(1)
        # 点击所有筛选条件
        all_filter_sel = create_selector_shadow(XPath.all_filter)
        handler_feedback(web_page)
        web_page.find(all_filter_sel, timeout=2).click()

        # 点击开始日期，结束日期
        web_page.find_by_xpath(XPath.start_dropdown, timeout=2).click()
        sleep(0.5)
        web_page.find_by_xpath(XPath.end_dropdown, timeout=2).click()

        # 点击开始时间的状态
        web_page.find_by_xpath(XPath.start_status_frame, timeout=2).click()
        xbot.win32.send_keys('{DOWN}')
        xbot.win32.send_keys('{ENTER}')

        # 进行输入框输入
        start_time_input_sel = web_page.find_all_by_xpath(XPath.time_input, timeout=2)
        start_time_input_list = [_ for _ in start_time_input_sel if _.get_bounding(to96dpi=False)[2] != 0]
        start_time_input = start_time_input_list[0]
        end_time_input = start_time_input_list[1]
        
        start_time_input.input(f'00{start_time}')
        end_time_input.input(f'00{end_time}')
        sleep(3)

    except Exception as e:
        print(e)
        pass


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
            link_element = row_element.find_by_xpath('.//kat-link', timeout=1)
            link = link_element.get_attribute('href') or ""
            # 如果是相对路径，加上域名前缀
            if link and not link.startswith('http'):
                domain = get_domain(web_page)
                link = domain + link
        except:
            link = ""
        
        # 2. 促销名称 (获取文本)
        try:
            title_element = row_element.find_by_xpath('.//kat-link', timeout=1)
            title = title_element.get_text() or ""
        except:
            title = ""
        
        # 3. 国家 (获取文本)
        try:
            country_element = row_element.find_by_xpath('.//kat-flag[@country]/following-sibling::div', timeout=1)
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
            date_element = row_element.find_by_xpath('.//*[@class="date-range-container"]', timeout=1)
            date_range = date_element.get_text() or ""
        except:
            date_range = ""
        
        # 6. 促销费用 (获取文本)
        try:
            fee_element = row_element.find_by_xpath('.//*[contains(@class,"rate-card-fee-label")]', timeout=1)
            fee = fee_element.get_text() or ""
        except:
            fee = ""
        
        # 7. 销售额 (获取文本)
        try:
            sales_element = row_element.find_by_xpath('.//span[@class="resize-container"]//*[contains(@class,"promotion-performance")]/div[1]', timeout=1)
            sales = sales_element.get_text() or ""
        except:
            sales = ""
        
        # # 8. 商品已售出 (获取文本)
        # try:
        #     units_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][6]', timeout=1)
        #     units_sold = units_element.get_text() or ""
        # except:
        #     units_sold = ""
        
        # # 9. 浏览量 (获取文本)
        # try:
        #     views_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][7]/div[1]', timeout=1)
        #     views = views_element.get_text() or ""
        # except:
        #     views = ""
        
        # # 10. 转化率 (获取文本)
        # try:
        #     conversion_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][7]/div[2]', timeout=1)
        #     conversion_rate = conversion_element.get_text() or ""
        # except:
        #     conversion_rate = ""
        
        # # 11. 费用/销售额 (获取文本)
        # try:
        #     fee_sales_element = row_element.find_by_xpath('.//*[local-name()="kat-table-cell"][8]', timeout=1)
        #     fee_sales_ratio = fee_sales_element.get_text() or ""
        # except:
        #     fee_sales_ratio = ""
        
        # 按照指定顺序组装数据行
        row_data = [
            link,              # 1. 链接
            title,             # 2. 促销名称
            country,           # 3. 国家
            status,            # 4. 状态
            date_range,        # 5. 日期范围
            fee,               # 6. 促销费用
            sales,             # 7. 销售额
        ]
        # units_sold,        # 8. 商品已售出
        # views,             # 9. 浏览量
        # conversion_rate,   # 10. 转化率
        # fee_sales_ratio    # 11. 费用/销售额
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
            if 'disabled' in next_page_element.get_attribute('class'):
                break
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

    # 清空筛选条件
    clear_filter_sel = create_selector_shadow(XPath.clear_filters)
    web_page.find(clear_filter_sel).click()
    sleep(5)

    web_page.scroll_to()

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
    campaign_status_filter = "正在进行,已结束"  # 可选
    country = "日本"  # 可选
    date_range = "2025-12-01_2025-12-31"  # 可选
    result = get_deal_data(web_page, campaign_status_filter, country, date_range)
    print(f"获取到 {len(result) - 1} 行数据（不含表头）")
    for i, row in enumerate(result[:5]):  # 只打印前5行
        print(f"第{i}行: {row}")
    print('result:', result)
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
