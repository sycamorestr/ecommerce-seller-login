# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

# 结算一览页面获取金额：标准订单、发票支付订单、延迟交易、所有账户汇总

import xbot
from xbot import print, sleep
from xbot.web import WebBrowser
from .import package
from .package import variables as glv
from .utils import get_domain, handler_container
from .create_element import create_selector_shadow


PAYMENTS_DASHBOARD_PATH = "/payments/dashboard/index.html/ref=xx_payments_dnav_xx"

# 结算一览 dashboard 金额元素 XPath
class Xpath:
    standard_orders = '//div[contains(@class, "dashboard-section-content") and .//span[contains(@class, "all-balances-span")]]/kat-card[2]/div[contains(@class, "linkable-multi-row-card-rows-container")]/div[1]//div[contains(@class, "underline-link")]'
    invoice_payment_orders = '//div[contains(@class, "dashboard-section-content") and .//span[contains(@class, "all-balances-span")]]/kat-card[2]/div[contains(@class, "linkable-multi-row-card-rows-container")]/div[2]//div[contains(@class, "underline-link")]'
    delayed_transactions = '//div[contains(@class, "dashboard-section-content") and .//span[contains(@class, "all-balances-span")]]/kat-card[2]/div[contains(@class, "linkable-multi-row-card-rows-container")]/div[3]//kat-link'
    all_account_summary = '(//div[contains(@class, "currency-total-amount")])[1]'


def to_payments_dashboard_if_needed(web_page: WebBrowser, url: str):
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(url + "/"):
        return
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)


def get_payment_amount(web_page: WebBrowser) -> dict:
    """在结算一览页面获取标准订单、发票支付订单、延迟交易、所有账户汇总的金额。"""
    domain = get_domain(web_page)
    url = f"{domain}{PAYMENTS_DASHBOARD_PATH}"
    to_payments_dashboard_if_needed(web_page, url)
    web_page.wait_load_completed(timeout=30)
    sleep(2)

    result = {}
    for key, xpath in [
        ("标准订单", Xpath.standard_orders),
        ("发票支付订单", Xpath.invoice_payment_orders),
        ("延迟交易", Xpath.delayed_transactions),
        ("所有账户", Xpath.all_account_summary),
    ]:
        try:
            if key == "延迟交易":
                try:
                    el = web_page.find_by_xpath(xpath, timeout=10)
                    result[key] = (el.get_attribute("label") or "").strip()
                except:
                    trans_xpath = '//*[@class="linkable-multi-row-card-rows-container"]//*[@id="link-target"]'
                    trans_sel = web_page.find_all_by_xpath(trans_xpath)
                    trans_sel = [_ for _ in trans_sel if _.get_bounding(to96dpi=False)[2] != 0][0]
                    result[key] = (trans_sel.get_attribute('label') or '').strip()
            else:
                el = web_page.find_by_xpath(xpath, timeout=10)
                result[key] = (el.get_text() or "").strip()
        except Exception as e:
            print(f"获取【{key}】失败: {e}")
            result[key] = ""

    return result


def test_run():
    if "xbot_extensions" in __file__:
        return

    print("--- 结算一览金额测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    data = get_payment_amount(web_page)
    print(data)
    exit()


def main(args):
    test_run()

    web_page = args.get("web_page")
    data = get_payment_amount(web_page)
    args["data"] = data
