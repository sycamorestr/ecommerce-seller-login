# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

# 此模块主要处理 超龄库存附加费报告 下载操作
# 网址：/reportcentral/LONGTERM_STORAGE_FEE_CHARGES/1

import xbot
import xbot_visual
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from pathlib import Path
from xbot_visual import datetime

from . import utils
from .utils import get_domain
from .utils import handler_container
from .activities_utils import download_handler
from .utils_beta import find_by_xpath
from . import _amazon_api


class Xpath:
    RequestCsvBtn = '//kat-button[@value="CSV"]'
    RequestTxtBtn = '//kat-button[@value="TSV"]'
    DownloadLinkNav = "//*[@id='root']//a[@id='reportpage_download_tab']"
    NoDataAvailable = '//kat-table-body/kat-table-row[1]/kat-table-cell[last()][not(*)]'
    DownloadBtn = '//kat-table-body/kat-table-row[1]/kat-table-cell[last()]/kat-button'


class Sel:
    sel = package.selector
    year = sel("月度仓储费-年")
    month = sel("月度仓储费-月")


def input_parameter_valid(web_page: WebBrowser, file_type: str):
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert file_type.upper() in ['CSV', 'TSV', 'TXT'], f"不支持下载文件类型：{file_type}"


def check_params(year_month, wait_time):
    """参数校验，返回合法的 year_month (YYYY-MM)"""
    try:
        wait_time = int(wait_time)
        if bool(year_month):
            year_month = datetime.to_string(datetime="{}-01".format(year_month), format="%Y-%m")
            datetime_instance, _ = datetime.add(datetime="", timeway="decrease", duration="1", unit="year", output_text=False)
            start_date = datetime.to_string(datetime=datetime_instance, format="%Y-%m")
            end_date = datetime.to_string(datetime="", format="%Y-%m")
            assert start_date <= year_month <= end_date, "只支持前1年当月到今年当月的日期区间"
        else:
            datetime_instance, _ = datetime.add(datetime="", timeway="decrease", duration="1", unit="month", output_text=False)
            year_month = datetime.to_string(datetime=datetime_instance, format="%Y-%m")
        return year_month
    except Exception as e:
        raise ValueError(str(e))


def to_report_page_if_need(web_page: WebBrowser, url: str):
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(url + "/"):
        return
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)


def set_download_params(web_page: WebBrowser, year_month: str):
    """选择年份和月份"""
    year, month = year_month.split("-")
    web_page.find(Sel.year).find_by_xpath(".//kat-option[@value='{}']".format(year)).click(simulative=False)
    web_page.find(Sel.month).find_by_xpath(".//kat-option[@value='{}']".format(int(month) - 1)).click(simulative=False)


def wait_request_completed(web_page: WebBrowser, file_type: str, wait_time: int = 300):
    """请求报告并等待生成完成"""
    if file_type.upper() == "CSV":
        find_by_xpath(web_page, Xpath.RequestCsvBtn).click(simulative=False)
    else:
        find_by_xpath(web_page, Xpath.RequestTxtBtn).click(simulative=False)

    # 判断是否请求失败
    request_report_error_xpath = '//*[@class="request-report-error"]'
    request_report_error = web_page.find_all_by_xpath(request_report_error_xpath, timeout=5)
    if len(request_report_error) > 0:
        xbot.logging.warning('当前报表请求失败，请查看是否达到每日下载次数上限 或 遇到网络波动')
        return "请求失败", None

    sleep(5)
    xpath_map = {
        "no_data_available": Xpath.NoDataAvailable,
        "download_btn": Xpath.DownloadBtn
    }
    name, ele = None, None
    for retry in range(50):
        try:
            name, ele = utils.find_any_one_by_xpath(web_page, xpath_map, timeout=2)
            if name is not None:
                break
        except Exception as e:
            try:
                web_page.find_by_xpath(Xpath.DownloadLinkNav).click()
                sleep(3)
            except:
                pass

    return name, ele


def return_aged_report(web_page: WebBrowser, file_folder: str, file_name: str,
                       file_type: str = 'CSV', year_month: str = None, wait_time: int = 300):
    """超龄库存附加费报告下载主流程"""
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    input_parameter_valid(web_page, file_type)
    year_month = check_params(year_month, wait_time)


    # 进入超龄库存附加费报告页面
    domain = get_domain(web_page)
    url = f"{domain}/reportcentral/LONGTERM_STORAGE_FEE_CHARGES/1"
    to_report_page_if_need(web_page, url)

    # 设置年月参数
    set_download_params(web_page, year_month)

    # 等待请求完成
    name, ele = wait_request_completed(web_page, file_type, wait_time)
    if name == "no_data_available":
        raise ValueError("没有可用数据")
    if name is None:
        raise Exception("长时间等待，文件状态加载中")
    if name == "请求失败":
        return "请求失败"

    # 点击下载按钮
    ele.click()

    # 下载文件
    file_path = download_handler(web_page, str(file_folder), file_name, wait_time=wait_time)
    return file_path


def test_return_aged_report():
    if "xbot_extensions" in __file__:
        return

    web_page = xbot.web.get_active(mode="superbrowser")
    file_folder = r"C:\Users\Administrator\Desktop\test"
    file_name = "aged_report_test.csv"
    file_type = 'CSV'
    year_month = "2026-02"
    file_path = return_aged_report(web_page,file_folder, file_name,
                                   file_type=file_type, year_month=year_month)
    print(file_path)
    exit()


def main(args):
    test_return_aged_report()

    web_page = args.get('web_page')
    file_folder = args.get('file_folder')
    file_name = args.get('file_name')
    file_type = args.get('file_type', 'CSV')
    year_month = args.get('year_month')
    wait_time = args.get('wait_time', 300)

    file_path = return_aged_report(web_page,file_folder, file_name,
                                   file_type=file_type, year_month=year_month,
                                   wait_time=wait_time)
    args['file_path'] = file_path
