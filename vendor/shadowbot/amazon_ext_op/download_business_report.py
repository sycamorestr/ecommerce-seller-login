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
from .utils import get_domain
from .utils import handler_container
from .activities_utils import gen_selector, download_handler
from ._amazon_api import switch_language
from datetime import datetime


class Xpath:
    # 日期下拉框
    DateRangeSelect = '(//*[@id="root"]//kat-dropdown)[1]'
    # 控制面板视图下拉框
    ControlViewSelect= '(//*[@id="root"]//kat-dropdown)[2]'
    # 应用按钮
    ApplyButton = '//*[@id="root"]//kat-button[@label="应用"]'
    # 下载按钮
    DownloadButton = '//*[@id="root"]//kat-button[contains(@label, "下载")]'


class Option:
    # 日期选项列表
    DateRangeList = ['昨天', '本周至今', '本月至今', '年初至今', '定制']
    # 控制面板视图选项列表
    ControlViewList = ['默认', '所有列', 'B2B', '']


def transform_date(date: str):
    # 转换日期格式
    try:
        # 去除日期前后的空格
        date = date.strip() if date else date
        result = datetime.strptime(date, "%Y-%m-%d").strftime("%Y/%m/%d")
        return result
    except Exception as e:
        raise Exception(f"日期格式错误：{date}")


def input_parameter_valid(web_page: WebBrowser, date_range: str, control_view: str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (date_range in Option.DateRangeList), f"日期有误：{date_range}"
    assert (control_view in Option.ControlViewList), f"控制面板视图有误：{control_view}"


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
    if not web_page.wait_appear(gen_selector(Xpath.ApplyButton), timeout=30):
        raise Exception(
            f"进入亚马逊详情页面销售和流量（按子商品）业务报告页面失败，未找到应用按钮： {Xpath.ApplyButton}"
        )


def set_filter_params(web_page: WebBrowser, date_range: str, start_date: str, end_date: str, control_view: str):
    # 选择日期
    web_page.find_by_xpath(Xpath.DateRangeSelect).click() # 点击日期下拉框
    for option in web_page.find_all("download_business_report_日期下拉框选项"):
        if option.get_text() == date_range:
            if date_range == '定制':
                option.click()
                web_page.find("download_business_report_开始日期输入框").clipboard_input(text=transform_date(start_date))
                web_page.find("download_business_report_开始日期输入框").click(anchor=('topLeft', -50, 0))
                sleep(5)
                web_page.find("download_business_report_结束日期输入框").clipboard_input(text=transform_date(end_date))
                web_page.find("download_business_report_结束日期输入框").click(anchor=('bottomRight', 10, 0))
                sleep(5)
                break
            else:
                option.click()
                sleep(5)
                break
    # 选择控制面板视图
    web_page.find_by_xpath(Xpath.ControlViewSelect).click() # 点击控制面板视图下拉框
    for option in web_page.find_all("download_business_report_控制面板视图下拉框选项"):
        if option.get_text() == control_view:
            option.click()
            break
    web_page.find_by_xpath(Xpath.ApplyButton).click() # 点击应用按钮
    sleep(5)


def download_business_report(web_page: WebBrowser, date_range: str, start_date: str, end_date: str, control_view: str, file_folder: str, file_name: str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)
    if file_name == '':
        if date_range == '定制':
            file_name = start_date + '_' + end_date + '_详情页面销售和流量（按子商品）业务报告'
        else:
            file_name = date_range + '_详情页面销售和流量（按子商品）业务报告'

    # 输入参数校验
    input_parameter_valid(web_page, date_range, control_view)

    # 进入批量管理您的采购页面
    domain = get_domain(web_page)
    url = f"{domain}/business-reports/ref=xx_sitemetric_favb_xx#/report?id=102:DetailSalesTrafficByChildItem"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置报告参数
    set_filter_params(web_page, date_range, start_date, end_date, control_view)

    # 下载报告
    web_page.find_by_xpath(Xpath.DownloadButton).click() # 点击下载按钮
    file_path = download_handler(web_page, file_folder, file_name)
    return file_path


def test_download_business_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="superbrowser")
    date_range = '定制' # 日期范围
    start_date = '2024-11-03' # 开始日期
    end_date = '2025-09-03' # 结束日期
    control_view = '' # 控制面板视图
    file_folder = r"C:\Users\10577\Desktop\test" # 保存文件夹路径
    file_name = "" # 保存文件名

    file_path = download_business_report(web_page, date_range, start_date, end_date, control_view, file_folder, file_name)
    print(file_path)
    exit()


def main(args):
    # 测试代码入口
    test_download_business_report()

    # 业务代码入口
    web_page = args.get("web_page")
    date_range = args.get("date_range") # 日期范围
    start_date = args.get("start_date") # 开始日期
    end_date = args.get("end_date") # 结束日期
    control_view = args.get("control_view") # 控制面板视图
    file_folder = args.get("file_folder") # 保存文件夹路径
    file_name = args.get("file_name") # 保存文件名

    file_path = download_business_report(web_page, date_range, start_date, end_date, control_view, file_folder, file_name)
    args["file_path"] = file_path
