# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from xbot.web import WebBrowser,WebElement
from pathlib import Path
from datetime import datetime
from .utils import get_domain
from .utils import handler_container
from .activities_utils import gen_selector, download_handler
from ._amazon_api import switch_language


class Xpath:
    # 国家名称下拉框
    CountryNameSelect = '//*[@data-test-id="DashboardHeaderContainer"]//kat-dropdown[@id="countryPicker"]'
    # 国家名称选项
    CountryNameOption = '//*[@data-test-id="DashboardHeaderContainer"]//kat-dropdown[@id="countryPicker"]//kat-option'
    # 报告范围下拉框
    ReportRangeSelect = '//*[@id="root"]//*[@id="reporting-range"]'
    # 选择周下拉框（报告范围为每周）
    SelectWeek = '//*[contains(@id, "week")]'
    # 选择年份下拉框（报告范围为每月，每季度）
    SelectYear = '//*[contains(@id, "year")]'
    # 选择月份下拉框（报告范围为每月）
    SelectMonth = '(//*[contains(@id, "month")])[2]'
    # 选择季度下拉框（报告范围为每季度）
    SelectQuarter = '(//*[contains(@id, "quarter")])[2]'
    # 点击量最高的商品输入框
    ProductInput = '//*[@data-test-id="TextFilter"]//kat-input'
    # 热门点击品牌输入框
    BrandInput = '//*[@id="brand-freeform"]'
    # 点击量最高的分类下拉框
    CategorySelect = '//*[@id="category-dropdown"]'
    # 搜索词输入框
    SearchTermInput = '//*[@id="search-term-freeform"]'
    # 应用按钮
    ApplyButton = '(//*[@data-test-id="RequiredFilterApplyButton"])[1]'
    # 细化结果按钮
    RefineResultBtn = '(//*[@data-test-id="RequiredFilterApplyButton"])[2]'
    # 生成下载项按钮
    GenerateButton = '//*[@id="GenerateDownloadButton"]'
    # 选择下载类型弹窗中生成下载项和打开下载管理器按钮
    ToastGenerateBtn = '//*[@id="downloadModalGenerateDownloadButton"]'
    # 下载管理器页面中下载操作标签
    ManagerDownloadSpan = '(//*[@role="rowgroup"]//*[@role="row"])[1]/div[last()]//span'
    # 下载管理器页面中进行中操作状态
    ManagerDownloadStatus = '(//*[@role="rowgroup"]//*[@role="row"])[1]/div[last()]//kat-badge'


class Option:
    # 选择月份选项
    MonthOptionMap = {'01':'1月', '02':'2月', '03':'3月', '04':'4月', '05':'5月', '06':'6月', '07':'7月', '08':'8月', '09':'9月', '10':'10月', '11':'11月', '12':'12月'}


def transform_date(date: str):
    """
    转换选择日期（每天）的格式
    """
    try:
        result = datetime.strptime(date, "%Y-%m-%d").strftime("%Y/%m/%d")
        return result
    except Exception as e:
        raise Exception(f"日期格式错误：{date}")


def input_parameter_valid(web_page: WebBrowser, select_date_day: str, select_year_month: str, select_year_quarter: str, report_range: str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (report_range in ['每日', '每周', '每月', '每季度']), f"报告范围 {report_range} 错误"
    if select_date_day != '':
        assert (datetime.strptime(select_date_day, '%Y/%m/%d') < datetime.today()), f"选择日期 {select_date_day} 需在今天的日期之前"
    if select_year_month != '':
        assert (1 <= int(select_year_month.split('-')[1]) <= 12), f"选择年月 {select_year_month} 月份错误"
    if select_year_quarter != '':
        assert (1 <= int(select_year_quarter.split('-')[1]) <= 4), f"选择年季度 {select_year_quarter} 季度错误"


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)
    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(Xpath.GenerateButton), timeout=30):
        raise Exception(
            f"进入亚马逊热门搜索词页面失败，未找到生成下载项按钮： {Xpath.GenerateButton}"
        )


def set_filter_params(web_page: WebBrowser, country_name: str, report_range: str, select_date_day: str, select_week: str, select_year_month: str, select_year_quarter: str, product_asin: str, brand_name: str, category_name: str, search_term_name: str, file_name: str, is_refined: bool):
    # 选择国家名称
    web_page.find("download_popular_terms_国家名称下拉框").click() # 点击国家名称下拉框
    country_name_option = web_page.find_all("download_popular_terms_国家名称选项")
    for option in country_name_option:
        if option.get_text() == country_name:
            option.click()
            break
    # 选择报告范围
    web_page.find("download_popular_terms_报告范围下拉框").click() # 点击报告范围下拉框
    for option in web_page.find_all("download_popular_terms_报告范围选项"):
        if option.get_text() == '每日' and report_range == '每日':
            option.click() # 点击每日报告范围选项
            # 选择日期（每日）
            web_page.find("download_popular_terms_选择日期输入框(报告范围为每日)").clipboard_input(text=select_date_day)
        elif option.get_text() == '每周' and report_range == '每周':
            option.click() # 点击每周报告范围选项
            if select_week != '':
                # 选择周（每周）
                year_name = select_week.split('-')[0]
                week_name = select_week.split('-')[1]
                web_page.find_by_xpath(Xpath.SelectWeek).click() # 点击选择周下拉框
                for option in web_page.find_all("download_popular_terms_选择周选项(报告范围为每周)"):
                    option_year_name = option.get_text().split(',')[1].replace(' ', '')
                    option_week_name = option.get_text().split('|')[0].replace(' ', '')
                    if option_year_name == year_name and option_week_name == week_name:
                        option.click()
                        break
            else:
                select_week_header = web_page.find("download_popular_terms_选择周下拉框内容头").get_attribute("title")
                select_year_week_header = select_week_header.split(',')[1].replace(' ', '') + "-" + select_week_header.split('|')[0].replace(' ', '')
        elif option.get_text() == '每月' and report_range == '每月':
            option.click() # 点击每月报告范围选项
            # 选择年月（每月）
            year_name = select_year_month.split('-')[0]
            month_name = Option.MonthOptionMap.get(select_year_month.split('-')[1])
            # 选择年份
            web_page.find_by_xpath(Xpath.SelectYear).click() # 点击选择年份下拉框
            for option in web_page.find_all("download_popular_terms_选择年份选项(报告范围为每月或每季度)"):
                if option.get_text() == year_name:
                    option.click()
                    break
            # 选择月份
            web_page.find_by_xpath(Xpath.SelectMonth).click() # 点击选择月份下拉框
            for option in web_page.find_all("download_popular_terms_选择月份选项(报告范围为每月)"):
                if option.get_text().replace(' ', '') == month_name:
                    option.click()
                    break
        elif option.get_text() == '每季度' and report_range == '每季度':
            option.click() # 点击每季度报告范围选项
            # 选择年季度（每季度）
            year_name = select_year_quarter.split('-')[0]
            quarter_name = select_year_quarter.split('-')[1]
            # 选择年份
            web_page.find_by_xpath(Xpath.SelectYear).click() # 点击选择年份下拉框
            for option in web_page.find_all("download_popular_terms_选择年份选项(报告范围为每月或每季度)"):
                if option.get_text() == year_name:
                    option.click()
                    break
            # 选择季度
            web_page.find_by_xpath(Xpath.SelectQuarter).click() # 点击选择季度下拉框
            for option in web_page.find_all("download_popular_terms_选择季度选项(报告范围为每季度)"):
                if option.get_text() == quarter_name:
                    option.click()
                    break
    web_page.find_by_xpath(Xpath.ApplyButton).click() # 点击应用按钮

    # 搜索点击量最高的商品
    web_page.find_by_xpath(Xpath.ProductInput).clipboard_input(text=product_asin)
    # 搜索热门点击品牌
    web_page.find_by_xpath(Xpath.BrandInput).clipboard_input(text=brand_name)
    # 选择点击量最高的分类
    web_page.find_by_xpath(Xpath.CategorySelect).click() # 点击点击量最高的分类下拉框
    for option in web_page.find_all("download_popular_terms_点击量最高的分类选项"):
        if option.get_text() == category_name:
            option.click()
            break
    # 搜索搜索词
    web_page.find_by_xpath(Xpath.SearchTermInput).clipboard_input(text=search_term_name)
    if is_refined:
        # web_page.find_by_xpath(Xpath.RefineResultBtn).click() # 点击细化结果按钮
        sleep(2)
        web_page.find("download_popular_terms_细化结果按钮").click() # 点击细化结果按钮

    if file_name == '':
        if select_week != '':
            file_name = country_name + '_' + select_date_day + select_week + select_year_month + select_year_quarter + '_' + product_asin + '_' + brand_name + '_' + category_name + '_' + search_term_name
        else:
            file_name = country_name + '_' + select_date_day + select_year_week_header + select_year_month + select_year_quarter + '_' + product_asin + '_' + brand_name + '_' + category_name + '_' + search_term_name
        file_name = file_name.replace(' ', '')
    return file_name


def download_popular_terms_report(web_page: WebBrowser, file_folder: str, file_name: str, time_out: int=300):
    # 点击生成下载项按钮
    sleep(5)
    web_page.find_by_xpath(Xpath.GenerateButton).click()
    # 点击选择下载类型弹窗中生成下载项按钮
    web_page.find_by_xpath(Xpath.ToastGenerateBtn).click()
    # 等待按钮变化
    for _ in range(10):
        if web_page.find_by_xpath(Xpath.ToastGenerateBtn).get_attribute('label') == '打开下载管理器':
            break
        else:
            sleep(2)
    # 点击选择下载类型弹窗中打开下载管理器按钮
    web_page.find_by_xpath(Xpath.ToastGenerateBtn).click()
    web_page = web.get_active(mode='auto', load_timeout=20)
    # 等待下载管理器页面中进行中操作状态元素出现
    for _ in range(5):
        try:
            web_page.find_by_xpath(Xpath.ManagerDownloadStatus, timeout=2)
            break
        except:
            sleep(2)
    # 等待下载管理器页面中下载操作标签元素出现
    download_flag = False # 下载操作标签元素标识
    for _ in range(time_out):
        try:
            web_page.find_by_xpath(Xpath.ManagerDownloadSpan, timeout=2).click() # 点击下载操作标签元素
            download_flag = True
            break
        except:
            sleep(2)
    if download_flag:
        file_path = download_handler(web_page, file_folder, file_name) # 下载报告
        return file_path
    else:
        raise Exception(f"等待报告完成超时：{time_out}")


def download_popular_terms(web_page: WebBrowser, country_name: str, report_range: str, select_date_day: str, select_week: str, select_year_month: str, select_year_quarter: str, product_asin: str, brand_name: str, category_name: str, search_term_name: str, file_folder: str, file_name: str, is_refined: bool):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)
    if select_date_day != '':
        select_date_day = transform_date(select_date_day) # 转换选择日期（每天）的格式

    # 输入参数校验
    input_parameter_valid(web_page, select_date_day, select_year_month, select_year_quarter, report_range)

    # 进入热门搜索词页面
    domain = get_domain(web_page)
    url = f"{domain}/brand-analytics/dashboard/top-search-terms"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置报告参数
    new_file_name = set_filter_params(web_page, country_name, report_range, select_date_day, select_week, select_year_month, select_year_quarter, product_asin, brand_name, category_name, search_term_name, file_name, is_refined)

    # 下载热门搜索词报告
    file_path = download_popular_terms_report(web_page, file_folder, new_file_name)
    return file_path


def test_download_popular_terms():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="chrome") # chrome
    country_name = '德国' # 国家名称
    report_range = '每周' # 报告范围，可选项：每日，每周，每月，每季度
    select_date_day = '' # 选择日期（每天），例如：2025-08-01
    select_week = '' # 选择周（每周），例如：2025-周1
    select_year_month = '' # 选择年月（每月），例如：2025-08
    select_year_quarter = '' # 选择年季度（每季度），例如：2025-1
    product_asin = 'B0DT6FY8MG' # 点击量最高的商品ASIN
    brand_name = 'VAHOIALD' # 热门点击品牌名称
    category_name = 'Camera' # 点击量最高的分类名称
    search_term_name = 'digital camera' # 搜索词名称
    file_folder = r"C:\Users\Administrator\Desktop\test" # 保存文件夹路径 Administrator
    file_name = "" # 保存文件名
    is_refined = False # 是否点击细化结果按钮

    file_path = download_popular_terms(web_page, country_name, report_range, select_date_day, select_week, select_year_month, select_year_quarter, product_asin, brand_name, category_name, search_term_name, file_folder, file_name, is_refined)
    print(file_path)
    exit()


def main(args):
    # 测试代码入口
    test_download_popular_terms()

    # 业务代码入口
    web_page = args.get("web_page")
    country_name = args.get("country_name") # 国家名称
    report_range = args.get("report_range") # 报告范围，可选项：每日，每周，每月，每季度
    select_date_day = args.get("select_date_day") # 选择日期（每天），例如：2025-08-01
    select_week = args.get("select_week") # 选择周（每周），例如：2025-周1
    select_year_month = args.get("select_year_month") # 选择年月（每月），例如：2025-08
    select_year_quarter = args.get("select_year_quarter") # 选择年季度（每季度），例如：2025-1
    product_asin = args.get("product_asin") # 点击量最高的商品ASIN
    brand_name = args.get("brand_name") # 热门点击品牌名称
    category_name = args.get("category_name") # 点击量最高的分类名称
    search_term_name = args.get("search_term_name") # 搜索词名称
    file_folder = args.get("file_folder") # 保存文件夹路径
    file_name = args.get("file_name") # 保存文件名
    is_refined = args.get("is_refined") # 是否点击细化结果按钮

    file_path = download_popular_terms(web_page, country_name, report_range, select_date_day, select_week, select_year_month, select_year_quarter, product_asin, brand_name, category_name, search_term_name, file_folder, file_name, is_refined)
    args["file_path"] = file_path
