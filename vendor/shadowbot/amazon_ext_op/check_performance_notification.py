# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数

import xbot  # type: ignore
import re  # type: ignore
import threading

from xbot import print, sleep  # type: ignore
from xbot.selector import Selector  # type: ignore
from xbot.web import WebBrowser, WebElement  # type: ignore

from .package import variables as glv  # type: ignore
from .utils import get_domain, handler_container
from datetime import datetime
from ._amazon_api import switch_site, switch_language, login


class Xpath:
    # 导航菜单
    NavigateMenu = '//*[@data-test-tag="nav-button-container"]'
    # 绩效菜单
    PerformanceMenu = '//*[@data-menu-id="performance"]'
    # 绩效选项
    PerformanceItem = '(//*[@class="flyout-menu"])[10]//span'
    # 开始日期图标
    StartDateIcon = '//kat-date-picker[1]//kat-icon[@role="button"]'
    # 结束日期图标
    EndDateIcon = '//kat-date-picker[2]//kat-icon[@role="button"]'
    # 开始日期输入框
    StartDateInput= "(//kat-date-range-picker//kat-input)[1]"
    # 结束日期输入框
    EndDateInput= "(//kat-date-range-picker//kat-input)[2]"
    # 开始日期选择器
    StartDatePicker = "(//*[@id='app-root']//div[@class='calendar'])[1]"
    # 结束日期选择器
    EndDatePicker = "(//*[@id='app-root']//div[@class='calendar'])[2]"
    # 提交按钮
    SubmitButton = "(//*[@id='app-root']//kat-button/button[@class='primary'])[1]"
    # 业绩通知表格
    NoticesTable = "//*[@id='app-root']//kat-table"
    # 下一页按钮
    NextButton = "(//*[@id='app-root']//*[@class='row']//button)[last()]"

def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%m/%d/%Y")

def gen_selector(xpath):
    xpaths = xpath.split(">>")
    data = {
        "id": "xbot-xpath",
        "name": "动态元素",
        "type": "simple",
        "xpath": {"enable": "true", "segments": xpaths},
    }
    selector = Selector(data)
    return selector

def goto_performance_notices(web_page:WebBrowser):
    # 通过菜单进入绩效通知
    # 点击导航菜单
    web_page.find_by_xpath(Xpath.NavigateMenu).click()
    # 悬浮绩效菜单
    web_page.find_by_xpath(Xpath.PerformanceMenu).hover()
    # 点击绩效通知选项
    for option in web_page.find_all_by_xpath(Xpath.PerformanceItem):
        if option.get_text() == '绩效通知':
            option.click()
            break

def to_reports_page_if_need(web_page: WebBrowser, url: str, site_name: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return

    # 可能重定向后并不能打开页面, 需要多次调整网页
    for _ in range(5):
        web_page.navigate(url, load_timeout=300)
        handler_container(web_page)

        # 进行登录校验
        login(web_page)
        # 进行站点校验
        if site_name:
            if '/account-switcher/default/merchantMarketplace' in web_page.get_url():
                switch_site(web_page, site_name)

        # 使用构建 selector 的方式来等待元素
        if  web_page.wait_appear(gen_selector(Xpath.SubmitButton), timeout=5):
            return
    
    raise Exception(f"进入业绩通知页面失败，未找到提交按钮： {Xpath.SubmitButton}")

def check_performance_notices(web_page:WebBrowser, start_date:str, end_date:str, site_name: str):
    # 检查绩效通知
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"

    # 0.切换语言
    # switch_language(web_page, 'zh_CN')

    # 进入业绩通知页面
    domain = get_domain(web_page)
    url = f"{domain}/performance/notifications"
    to_reports_page_if_need(web_page, url, site_name)


    web_page = xbot.web.get_active(mode=web_page.product_name, silent_running=True)

    # 选择开始日期范围
    web_page.find_by_xpath(Xpath.StartDateIcon).click()
    web_page.find_by_xpath(Xpath.StartDateInput).input(convert_date_format(start_date))

    # 选择结束日期范围
    web_page.find_by_xpath(Xpath.EndDateIcon).click()
    web_page.find_by_xpath(Xpath.EndDateInput).input(convert_date_format(end_date))

    # 校验日期
    web_page.find_by_xpath(Xpath.StartDateIcon).click()
    if web_page.find_by_xpath(Xpath.StartDateInput).get_attribute('value') != convert_date_format(start_date):
        web_page.find_by_xpath(Xpath.StartDateInput).input(convert_date_format(start_date))
    web_page.find_by_xpath(Xpath.EndDateIcon).click()
    if web_page.find_by_xpath(Xpath.EndDateInput).get_attribute('value') != convert_date_format(end_date):
        web_page.find_by_xpath(Xpath.EndDateInput).input(convert_date_format(end_date))
    
    web_page = xbot.web.get_active(mode=web_page.product_name, silent_running=False)

    # 点击提交按钮
    web_page.find_by_xpath(Xpath.SubmitButton).click()

    web_page.wait_load_completed(timeout = 200)
    sleep(5)
    notice_data_all = ""
    # 如果下一页按钮存在，则先获取当前页业绩通知表格数据，再点击下一页按钮，直到下一页按钮不存在（最后一页）
    # 可见返回True，不可见返回False
    while web_page.is_element_displayed(web_page.find_by_xpath(Xpath.NextButton)) and web_page.find_by_xpath(Xpath.NextButton).get_text()=='下一页':
        # 获取业绩通知表格数据
        notice_data_all = notice_data_all+web_page.find_by_xpath(Xpath.NoticesTable).get_text()+"\n"
        # 点击下一页按钮
        web_page.find_by_xpath(Xpath.NextButton).click()

    # 获取最后一页业绩通知表格数据
    notice_data_all = notice_data_all + web_page.find_by_xpath(Xpath.NoticesTable).get_text() + "\n"

    # 处理数据文本转为字典
    # 处理文本
    lines = notice_data_all.strip().split('\n')
    result = []
    for line in lines:
        line = line.strip()
        if line == "主题\t日期\t操作":
            continue
        parts = line.split('\t')

    #新增判断第三列数据
        if len(parts) >=2:
            notice = parts[0].strip()
            date = parts[1].strip()

            if len(parts)>=3:
                action = parts[2].strip()
            else:
                action = ""
  
            result.append({"通知内容":notice,"日期":date,"操作":action})
    # # 输出结果
    # print(result)
    return result
    
def test_check_performance_notices():
    if "xbot_extensions" in __file__:
        return

    web_page = xbot.web.get_active(mode="ziniaobrowser")
    start_date = "2024-08-11"
    end_date = "2025-10-11"
    site_name = ''
    result = check_performance_notices(
        web_page, start_date, end_date,site_name
    )
    print(result)
    exit()

def main(args):

    # 测试代码入口
    test_check_performance_notices()

    # 业务代码入口
    web_page = args.get("web_page")
    start_date = args.get("start_date")
    end_date = args.get("end_date")
    site_name = args.get('site_name')
    result = check_performance_notices(
        web_page, start_date, end_date, site_name
    )
    args["data"] = result
