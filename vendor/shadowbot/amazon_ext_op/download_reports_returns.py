# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,win32
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from pathlib import Path
from .utils import get_domain
from .utils import handler_container
from ._amazon_api import switch_site, switch_language
from datetime import datetime
from .activities_utils import download_handler
from .create_element import create_selector,create_selector_shadow


class Xpath:
    # 下载链接导航
    DownloadLinkNav = '//span[normalize-space(.)="退货报告" or normalize-space(.)="Return Reports"]'
    # 请求下载.xml文件按钮
    RequestXmlBtn = '//div[1]/span//a[normalize-space(.)="Download" or normalize-space(.)="下载"]'
    # 请求.tsv下载按钮
    RequestTsvBtn = '//div[2]/div/div/div/div[contains(@class, "a-span-last")]/span//a[normalize-space(.)="Download" or normalize-space(.)="下载"] '
    #刷新
    ReFrash = '//button[normalize-space(.)="Refresh" or normalize-space(.)="刷新"]'
    # 报告状态项
    ReportStatus = '//div[contains(@class, "reportRequestRecord")][1]//div[contains(@class, "a-span-last")]//div[contains(@class, "a-row")]/div[last()]'

    # 所有退货/prime退货
    ReturnClass = '//div[@class="a-row"]/span//span[contains(@class, "a-button-text")]'
    ReturnAll ='//ul/li/a[@id="reportTypesDropDown_0"]'
    ReturnPrime = '//ul/li/a[@id="reportTypesDropDown_1"]'
    # 事件日期
    ReportDate = '//span[@data-action="adhoc-report-date-range-dropdown-change"]//span[contains(@class, "a-button-text")]'
    # 确切日期
    ExactDate = '//ul/li/a[@id="adhocReportDateRangeDropDown_3"]'

    StartDate = '//input[@id="adhocReportFromDateInput"]'
    EndDate = '//input[@id="adhocReportToDateInput"]'
    # 请求按钮
    DownloadButton = '//button[@type="button"][@id="buttonRequestAdhocReport-announce"]'

def input_parameter_valid(web_page: WebBrowser, file_type: str):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (file_type in ['xml', 'tsv']), f"不支持下载文件类型：{file_type}"


def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%m/%d/%Y")

def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)


def set_filter_params(web_page: WebBrowser, return_type: str,start_date,end_date):
    # 设置报告参数
    web_page.find_by_xpath(Xpath.DownloadLinkNav).click()

    web_page.find_by_xpath(Xpath.ReturnClass).click()
    if return_type == '所有退货':
        web_page.find_by_xpath(Xpath.ReturnAll).click
    else:
        web_page.find_by_xpath(Xpath.ReturnPrime).click()

    web_page.find_by_xpath(Xpath.ReportDate).click()
    web_page.find_by_xpath(Xpath.ExactDate).click()
    web_page.find_by_xpath(Xpath.StartDate).input(convert_date_format(start_date))
    web_page.find_by_xpath(Xpath.EndDate).input(convert_date_format(end_date))
    web_page.find_by_xpath(Xpath.DownloadButton).click()
    sleep(3)



def wait_download_report(web_page: WebBrowser, file_folder: str, file_name: str, download_xpath: str):

    # 等待并下载报告
    # 等待报告状态变化

    # 开始轮询（建议适当增加次数，防止大文件生成慢）
    for retry in range(60): 
        try:
            # 获取状态单元格的文本 ---
            try:
                cell_element = web_page.find_by_xpath(Xpath.ReportStatus, timeout=2)
                cell_text = cell_element.get_text()
            except:
                cell_text = "" 

            if "无记录" in cell_text:
                return "无记录"

            try:
                # 尝试点击，如果元素不存在会触发异常，跳到 except
                web_page.find_by_xpath(download_xpath, timeout=1).click()
                
                # 如果点击成功，跳出循环
                print("找到下载按钮，点击成功！")
                break 
            except:
                # 没找到下载按钮，说明还在生成中（包含“进行中”或“空”的情况）
                pass

            #  刷新重试 
            web_page.find_by_xpath(Xpath.ReFrash).click()
            sleep(5)

        except Exception as e:
            print(f"发生未知错误: {e}，尝试刷新重试")
            web_page.find_by_xpath(Xpath.ReFrash).click()
            sleep(5)

    else:
        # 如果循环结束还没 break，说明超时
        raise TimeoutError("报表生成超时，未找到下载按钮或无记录状态")

    file_path = download_handler(web_page, file_folder, file_name)
    return file_path


def return_processing_report(web_page: WebBrowser,file_folder: str, file_name: str, return_type: str,start_date,end_date,file_type):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page,file_type)

    # 进入亚马逊配送货件
    domain = get_domain(web_page)
    url = f"{domain}/returns/report/ref=xx_scnvrr_dnav_xx"
    to_reports_page_if_need(web_page, url)
    
    # 切换语言
    switch_language(web_page, 'zh_CN')
    web_page.wait_load_completed(timeout=30)
    # 设置报告参数
    set_filter_params(web_page,return_type,start_date,end_date)
    # 点击下载文件类型按钮
    if file_type == 'xml':
        download_xpath = Xpath.RequestXmlBtn
    elif file_type == 'tsv':
        download_xpath = Xpath.RequestTsvBtn

    # 等待并下载报告
    file_path = wait_download_report(web_page, file_folder, file_name,download_xpath)
    return file_path
    


def test_return_processing_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="superbrowser")
    file_folder = r"C:\Users\58204\Desktop"  # 下载文件夹路径
    file_name = "111"  # 下载文件名
    file_type = 'tsv' # 下载文件类型
    start_date = '2025-11-01'
    end_date ='2025-11-02'
    return_type = "所有退货"
    file_path = return_processing_report(web_page,file_folder, file_name, return_type,start_date,end_date,file_type)
    print(file_path)

    exit()


def main(args):
    # 测试代码入口
    test_return_processing_report()

    # 业务代码入口
    web_page = args.get('web_page')
    file_folder = args.get('下载文件路径')  # 下载文件夹路径
    file_name = args.get('下载文件名')  # 下载文件名
    file_type = args.get('下载文件类型') # 下载文件类型
    start_date = args.get('开始日期')
    end_date = args.get('结束日期')    
    return_type = args.get('退货类型') # 退货类型


    file_path = return_processing_report(web_page,file_folder, file_name, return_type,start_date,end_date,file_type)
    args['file_path'] = file_path
