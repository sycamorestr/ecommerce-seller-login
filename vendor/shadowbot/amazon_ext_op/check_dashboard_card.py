# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import re 
from xbot import print, sleep
from xbot import print  
from xbot.web import WebBrowser  
from xbot.selector import Selector 
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language


class Xpath:
    ConditionRating = '//*[contains(@class, "ahr-status-badge")]'
    # 亚马逊dashboard页的通知弹窗
    NotificationCard = '//kat-card'
    

def gen_selector(xpath: str) -> Selector:
    xpaths = xpath.split(">>")
    data = {
        "id": "xbot-xpath",
        "name": "动态元素",
        "type": "simple",
        "xpath": {"enable": "true", "segments": xpaths},
    }
    selector = Selector(data)
    return selector

def to_account_health_page_if_needed(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标页面，直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，则导航到目标URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)

    if not web_page.wait_appear(gen_selector(Xpath.ConditionRating), timeout=30):
        raise Exception(
            f"进入账户状况页面失败，未找到关键元素： {Xpath.ConditionRating}"
        )



def check_for_notification_card(web_page: WebBrowser) -> bool:
    """
    检查当前网页中是否存在亚马逊通知卡片 (<kat-card>)。
    """
    try:
        kat_card_elements = web_page.find_all_by_xpath(Xpath.NotificationCard)
        if len(kat_card_elements) > 0:
            print("检测到页面上存在 <kat-card> 通知卡片。")
            return True
        else:
            print("页面上未发现 <kat-card> 通知卡片。")
            return False
    except Exception as e:
        print(f"在检查 <kat-card> 元素时发生错误: {e}")
        return False


def execute_account_health_popup_check(web_page: WebBrowser) -> bool:

    if not isinstance(web_page, WebBrowser):
        raise ValueError("传入的'web_page'必须是一个浏览器对象")

    # 步骤1: 准备目标URL并调用函数，确保页面在账户状况页
    domain = get_domain(web_page)
    account_health_url = f"{domain}/performance/dashboard"
    to_account_health_page_if_needed(web_page, account_health_url)
    # 切换中文
    switch_language(web_page, 'zh_CN')
    sleep(3)

    # 步骤2: 在账户状况页上检查是否存在弹窗
    has_popup = check_for_notification_card(web_page)
    
    return has_popup


def test_run():
    if "xbot_extensions" in __file__:
        return
    
    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="superbrowser")
    result_bool = execute_account_health_popup_check(web_page)
    print(result_bool)
    exit()


def main(args):
    # test_run()
    web_page = args.get("web_page")
    result_bool = execute_account_health_popup_check(web_page)
    args["是否存在弹窗"] = result_bool

