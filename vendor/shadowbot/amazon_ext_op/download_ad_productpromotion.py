# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser,WebElement
from pathlib import Path
from .utils import get_ad_domain
from .activities_utils import gen_selector,download_handler
from ._amazon_api import switch_language_on_ad_page
from datetime import datetime
from xbot_extensions.web_action.select_date import select_date


class Xpath:
    # 创建电子表格按钮
    CreateTableBtn = "//*[text()='下载广告活动' or text()='Download campaigns']"
    # 日期范围按钮
    DateRangeBtn = "(//*[contains(@class, 'MuiGrid-container')]//button)[2]"
    start_frame = '//input[contains(@data-takt-id,"start_date")]'
    end_frame = '//input[contains(@data-takt-id,"end_date")]'
    # 日期范围选择器
    DateRangePicker = '//div[@role="application"]/div[2][contains(@class, "DayPicker")]'
    # 日期范围选择器保存按钮（支持中英文）
    DateSaveBtn = "//*[@id='portal']//button[normalize-space()='保存' or normalize-space()='Save' or normalize-space()='save']"
    # 投放和关键词筛选按钮
    FilterButton = "//*[contains(@data-takt-id,'exportModal_keyword_target_state')]"
    # 投放和关键词筛选选项
    FilterItems = '//*[@data-takt-value="Dropdown-open"]//*[@role="presentation"]//button[@value="{}"]'
    # 包含复选框
    ContainsCheck = "(//fieldset//child::div)[1]//label"
    # 包含复选框图标
    ContainsIcon = "(//fieldset//child::div)[1]//input"
    # 下载文件状态项
    FileStatusItem = '(//*[@role="rowgroup"]/div[contains(@class,"ag-row")]/div[1])[1]'
    # # 下载报告按钮项
    # ReportButtonItem = "(//*[contains(@class, 'MuiGrid-spacing')]//child::div)[1]//tr[1]/td[2]"
    # 下载报告按钮
    ReportButton = '(//*[@role="rowgroup"]/div[contains(@class,"ag-row")]/div//a[@download])[1]'
    # 开始年月
    StartYearMonth = '(//*[@id="portal"]//strong)[2]'
    # 开始天选项
    StartDayOption = '(//*[@id="portal"]//table)[2]//td'
    # 结束年月
    EndYearMonth = '(//*[@id="portal"]//strong)[3]'
    # 结束天选项
    EndDayOption = '(//*[@id="portal"]//table)[3]//td'
    # 上一月切换按钮
    LastMonthBtn = '(//*[@id="portal"]//div[@aria-label="Calendar"]//button)[1]'
    # 下一月切换按钮
    NextMonthBtn = '(//*[@id="portal"]//div[@aria-label="Calendar"]//button)[2]'
    # 点击下载按钮
    DownloadButton = '//*[contains(@data-takt-id,"exportModal_download_button")]'


class Option:
    # 包含项（中英文完整列表）
    ContainsOption = [
        # 中文选项
        '已终止的广告活动',
        '已暂停的广告活动',
        '展示量为零的广告活动项目', 
        '广告活动的广告位数据', 
        '品牌素材数据', 
        '商品推广数据', 
        '品牌推广数据', 
        '品牌推广多广告组数据', 
        '展示型推广数据', 
        '商品推广指南', 
        '商品推广搜索词数据', 
        '品牌推广搜索词数据', 
        '预算规则数据',
        # 英文选项
        'Terminated campaigns',
        'Paused campaigns',
        'Campaign items with zero impressions',
        'Placement data for campaigns',
        'Brand assets data',
        'Sponsored Products data',
        'Sponsored Brands data',
        'Sponsored Brands multi-ad group data',
        'Sponsored Display data',
        'Guidance for Sponsored Products',
        'Sponsored Products Search term data',
        'Sponsored Brands Search term data',
        'Budget Rules Data'
    ]
    
    # 中英文映射字典（用于参数校验和匹配）
    ContainsOptionMap = {
        # 中文 -> 英文
        '已终止的广告活动': 'Terminated campaigns',
        '展示量为零的广告活动': 'Campaign items with zero impressions',
        '适用于广告活动的广告位数据': 'Placement data for campaigns',
        '品牌资产数据': 'Brand assets data',
        '商品推广数据': 'Sponsored Products data',
        '品牌推广数据': 'Sponsored Brands data',
        '品牌推广多广告组数据': 'Sponsored Brands multi-ad group data',
        '展示型推广数据': 'Sponsored Display data',
        '商品推广指南 (not available in language)': 'Guidance for Sponsored Products',
        '商品推广搜索词数据': 'Sponsored Products Search term data',
        '品牌推广搜索词数据': 'Sponsored Brands Search term data',
        # 英文 -> 中文（反向映射）
        'Terminated campaigns': '已终止的广告活动',
        'Paused campaigns': 'Paused campaigns',  # 英文版特有
        'Campaign items with zero impressions': '展示量为零的广告活动',
        'Placement data for campaigns': '适用于广告活动的广告位数据',
        'Brand assets data': '品牌资产数据',
        'Sponsored Products data': '商品推广数据',
        'Sponsored Brands data': '品牌推广数据',
        'Sponsored Brands multi-ad group data': '品牌推广多广告组数据',
        'Sponsored Display data': '展示型推广数据',
        'Guidance for Sponsored Products': '商品推广指南 (not available in language)',
        'Sponsored Products Search term data': '商品推广搜索词数据',
        'Sponsored Brands Search term data': '品牌推广搜索词数据',
        'Budget Rules Data': 'Budget Rules Data'  # 英文版特有
    }
    
    # 过滤项（支持中英文）
    FilterOption = ['已启用和已暂停', '已启用', '已暂停', 'Enabled & Paused', 'Enabled', 'Paused']
    FilterMap = {
        # 中文 -> 英文
        '已启用和已暂停': 'ALL',
        '已启用': 'ENABLED',
        '已暂停': 'PAUSED',
        # 英文 -> 英文（保持原样）
        'Enabled & Paused': 'ALL',
        'Enabled': 'ENABLED',
        'Paused': 'PAUSED'
    }
    # 月份映射（支持中英文）
    MonthMap = {
        # 中文月份
        '一月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
        '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12,
        # 英文月份
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }


def transform_date(date: str):
    # 转换日期格式
    try:
        result = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        return result
    except Exception as e:
        raise Exception(f"日期格式错误：{date}")


def input_parameter_valid(web_page: WebBrowser, contains_items: list, filter_item: str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (filter_item in Option.FilterOption), f"过滤项错误：{filter_item}"
    assert all(item in Option.ContainsOption for item in contains_items), f"包含项错误：{contains_items}"


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(url + "/"):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(Xpath.CreateTableBtn), timeout=30):
        raise Exception(f"进入亚马逊搜索广告批量操作页面失败，未找到创建电子表格按钮： {Xpath.CreateTableBtn}")
    web_page.find_by_xpath(Xpath.CreateTableBtn).click()


def date_select(web_page: WebBrowser, start_date: str, end_date: str):
    # 获取输入开始年月日
    input_start_year = int(start_date.split('-')[0])
    input_start_month = int(start_date.split('-')[1])
    input_start_day = int(start_date.split('-')[2])
    # 获取输入结束年月日
    input_end_year = int(end_date.split('-')[0])
    input_end_month = int(end_date.split('-')[1])
    input_end_day = int(end_date.split('-')[2])
    
    # 获取当前开始年月（支持中英文）
    start_month_text = web_page.find_by_xpath(Xpath.StartYearMonth).get_text().strip()
    start_month_parts = start_month_text.split()
    if len(start_month_parts) >= 2:
        current_start_month_name = start_month_parts[0]
        current_start_year = int(start_month_parts[1])
        current_start_month = Option.MonthMap.get(current_start_month_name)
        if current_start_month is None:
            raise Exception(f"无法识别的月份名称: {current_start_month_name}")
    else:
        raise Exception(f"无法解析开始月份格式: {start_month_text}")
    
    # 计算输入和当前开始月份差
    start_month_diff = (current_start_year - input_start_year)*12 + (current_start_month - input_start_month)
    if start_month_diff > 0:
        while(start_month_diff > 0):
            web_page.find_by_xpath(Xpath.LastMonthBtn).click()
            start_month_diff -= 1
            sleep(0.3)
    elif start_month_diff < 0:
        while(start_month_diff < 0):
            web_page.find_by_xpath(Xpath.NextMonthBtn).click()
            start_month_diff += 1
            sleep(0.3)
    
    # 选择开始天选项
    for option in web_page.find_all_by_xpath(Xpath.StartDayOption):
        if option.get_text() != '' and int(option.get_text()) == input_start_day:
            option.click()
            break
    
    # 获取当前结束年月（支持中英文）
    end_month_text = web_page.find_by_xpath(Xpath.EndYearMonth).get_text().strip()
    end_month_parts = end_month_text.split()
    if len(end_month_parts) >= 2:
        current_end_month_name = end_month_parts[0]
        current_end_year = int(end_month_parts[1])
        current_end_month = Option.MonthMap.get(current_end_month_name)
        if current_end_month is None:
            raise Exception(f"无法识别的月份名称: {current_end_month_name}")
    else:
        raise Exception(f"无法解析结束月份格式: {end_month_text}")
    
    # 计算输入和当前结束月份差
    end_month_diff = (input_end_year - current_end_year)*12 + (input_end_month - current_end_month)
    if end_month_diff > 0:
        while(end_month_diff > 0):
            web_page.find_by_xpath(Xpath.NextMonthBtn).click()
            end_month_diff -= 1
            sleep(0.3)
    elif end_month_diff < 0:
        while(end_month_diff < 0):
            web_page.find_by_xpath(Xpath.LastMonthBtn).click()
            end_month_diff += 1
            sleep(0.3)
    
    # 获取结束天选项
    for option in web_page.find_all_by_xpath(Xpath.EndDayOption):
        if option.get_text() != '' and int(option.get_text()) == input_end_day:
            option.click()
            break


def set_filter_params(web_page: WebBrowser, start_date: str, end_date: str, filter_item: str, contains_items: list, time_type: str):
    # 选择报告周期
    # web_page.find_by_xpath(Xpath.DateRangeBtn).click()
    # web_page.find_by_xpath(Xpath.DateSaveBtn).hover()
    # date_select(web_page, start_date, end_date)
    # date_picker = web_page.find("download_product_promotion_日期选择器")
    # select_date(web_page, date_picker, start_date, end_date)
    for  _ in range(2):
        if time_type == '年月日':
            # 获取开始时间的年
            start_year = start_date.split('-',1)[0]
            web_page.find_by_xpath(Xpath.start_frame).input(start_date)
            # 获取结束时间的年
            end_year = end_date.split('-',1)[0]
            # 如果开始时间与结束时间一致，则结束时间不需要输入年
            if start_year == end_year:
                end_date = end_date.split('-',1)[1]
            web_page.find_by_xpath(Xpath.end_frame).input(end_date)
        elif time_type == "月日年":
            # 获取开始时间的年
            start_year = start_date.split('-',1)[0]
            start_date = start_date.split('-',1)[1] + '-' + start_year
            web_page.find_by_xpath(Xpath.start_frame).input(start_date)
            # 获取结束时间的年
            end_year = end_date.split('-',1)[0]
            # 如果开始时间与结束时间一致，则结束时间不需要输入年
            if start_year == end_year:
                end_date = end_date.split('-',1)[1]
            else:
                end_date = end_date.split('-',1)[1] + '-' + end_year
            web_page.find_by_xpath(Xpath.end_frame).input(end_date)
        
        start_value = web_page.find_by_xpath(Xpath.start_frame).get_attribute('value')
        end_value = web_page.find_by_xpath(Xpath.end_frame).get_attribute('value')
        if start_value and end_value:
            start_value = start_value.split('-',1)[0]
            end_value = end_value.split('-', 1)[0]
            if start_value not in ['2025', '2026', '2027'] or end_value not in  ['2025', '2026', '2027']:
                continue
            break
        else:
            continue            
    else:
        raise Exception('时间选择错误')

    # 选择过滤项
    web_page.find_by_xpath(Xpath.FilterButton).click()
    web_page.find_by_xpath(Xpath.FilterItems.format(Option.FilterMap[filter_item])).click()

    # 选择包含项
    for option in web_page.find_all_by_xpath(Xpath.ContainsIcon):
        if option.is_checked():
            option.click(simulative=False) # 初始化取消选中
    
    # 构建匹配集合：包含用户输入的选项及其对应的中英文版本
    matched_items = set()
    for item in contains_items:
        matched_items.add(item)  # 添加原始选项
        # 如果存在映射，添加对应的中英文版本
        if item in Option.ContainsOptionMap:
            mapped_item = Option.ContainsOptionMap[item]
            matched_items.add(mapped_item)
    
    # 遍历所有包含项复选框，匹配并选中
    for option in web_page.find_all_by_xpath(Xpath.ContainsCheck):
        # 获取选项文本
        option_text = option.get_text().strip()
        
        # 清理文本：去除中文的"新增"标签和英文可能的额外标签
        # 处理中文的"新增"标签（可能在文本末尾）
        option_text = option_text.replace('\n新增', '').replace('新增', '').strip()
        # 处理可能的换行符和多余空格
        option_text = ' '.join(option_text.split())
        
        # 检查是否匹配（支持中英文）
        # 优先精确匹配
        if option_text in matched_items:
            option.click(anchor=('middleLeft', 0, 0))
            continue
        
        # 如果精确匹配失败，尝试部分匹配（处理可能的额外文本，如"New"标签）
        # 但只匹配主要文本部分，避免误匹配
        for item in matched_items:
            # 检查选项文本是否包含目标项，或目标项是否包含选项文本的主要部分
            if item in option_text:
                option.click(anchor=('middleLeft', 0, 0))
                break
            # 反向检查：如果目标项较长，检查选项文本是否是目标项的一部分
            elif len(item) > len(option_text) and option_text in item:
                option.click(anchor=('middleLeft', 0, 0))
                break


def wait_download_report(web_page: WebBrowser, file_folder: str, file_name: str, timeout: int=300):
    # 等待并下载报告
    download_flag = False # 下载按钮标识
    # 等待报告状态变化
    for retry in range(5):
        if "Success" in web_page.find_by_xpath(Xpath.FileStatusItem).get_text():
            break
        sleep(2)
    # 等待报告生成
    for retry in range(timeout):
        try:
            # 尝试找下载按钮
            web_page.find_by_xpath(Xpath.ReportButton, timeout=2).click()
            download_flag = True # 找到下载按钮
            break
        except:
            sleep(6)
    # 下载报告
    if download_flag:
        file_path = download_handler(web_page, file_folder, file_name)
    else:
        raise Exception(f"等待报告完成超时：{timeout}")
    return file_path


def download_product_promotion(web_page: WebBrowser, start_date: str, end_date: str, filter_item: str, contains_items: list, file_folder: str, file_name: str, time_type: str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)
    start_date = transform_date(start_date)
    end_date = transform_date(end_date)

    # 输入参数校验
    input_parameter_valid(web_page, contains_items, filter_item)

    # 进入批量管理您的采购页面
    domain = get_ad_domain(web_page)
    url = f"{domain}/bulksheet/HomePage"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    # switch_language_on_ad_page(web_page, 'zh_CN')

    # 设置报告参数
    set_filter_params(web_page, start_date, end_date, filter_item, contains_items, time_type)

    # 下载报告
    web_page.find_by_xpath(Xpath.DownloadButton).click()
    web_page.find_by_xpath(Xpath.FileStatusItem).hover()
    file_path = wait_download_report(web_page, file_folder, file_name)
    return file_path


def test_download_product_promotion():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    start_date = '2026-05-04' # 开始日期
    end_date = '2026-05-05' # 结束日期
    filter_item = '已启用和已暂停' # 过滤项
    contains_items = ['品牌素材数据','品牌推广数据'] # 包含项
    file_folder = r"D:" # 保存文件夹路径
    file_name = "test9" # 保存文件名
    time_type = '年月日'

    file_path = download_product_promotion(web_page, start_date, end_date, filter_item, contains_items, file_folder, file_name, time_type)
    print(file_path)
    exit()


def main(args):
    # 测试代码入口
    test_download_product_promotion()

    # 业务代码入口
    web_page = args.get("web_page")
    start_date = args.get("start_date") # 开始日期
    end_date = args.get("end_date") # 结束日期
    filter_item = args.get("filter_item") # 过滤项
    contains_items = args.get("contains_items") # 包含项
    file_folder = args.get("file_folder") # 保存文件夹路径
    file_name = args.get("file_name") # 保存文件名
    time_type = args.get('time_type', '') # 时间选择
    if time_type == '':
        time_type = '年月日' 

    file_path = download_product_promotion(web_page, start_date, end_date, filter_item, contains_items, file_folder, file_name, time_type)
    args["file_path"] = file_path
