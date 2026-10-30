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
from .activities_utils import gen_selector,download_handler
from ._amazon_api import switch_language


class Xpath:
    # 下载报告按钮
    DownloadButton = "//*[@class='download-tab']/kat-button"
    # 下载弹窗
    DownloadAlert = "//*[@id='app-main']/kat-alert"


def input_parameter_valid(web_page:WebBrowser):
    # 输入参数校验
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"


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
    if not web_page.wait_appear(gen_selector(Xpath.DownloadButton), timeout=30):
        raise Exception(
            f"进入亚马逊自有包装发货页面失败，未找到下载报告按钮： {Xpath.DownloadButton}"
        )


def download_shipping_report(web_page:WebBrowser,file_folder:str,file_name:str):
    # 输入参数转换
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page)

    # 进入批量管理您的采购页面
    domain = get_domain(web_page)
    url = f"{domain}/sipp-enrollment"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 下载报告
    file_path = ''
    web_page.find_by_xpath(Xpath.DownloadButton).click()
    # 等待下载已完成弹窗出现
    if web_page.wait_appear(web_page.find_by_xpath(Xpath.DownloadAlert,timeout=120),timeout=120):
        if "完成" in web_page.find_by_xpath(Xpath.DownloadAlert).get_text():
            file_path = download_handler(web_page, file_folder, file_name)
    return file_path


def test_download_shipping_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="chrome")
    file_folder = r"C:\Users\10577\Desktop\test" # 保存文件夹路径
    file_name = "test3" # 保存文件名

    file_path = download_shipping_report(web_page,file_folder,file_name)
    print(file_path)
    exit()


def main(args):
    # 测试代码入口
    test_download_shipping_report()

    # 业务代码入口
    web_page = args.get("web_page")
    file_folder = args.get("file_folder") # 保存文件夹路径
    file_name = args.get("file_name") # 保存文件名

    file_path = download_shipping_report(web_page,file_folder,file_name)
    args["file_path"] = file_path
