import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement
from xbot._core.retry import Retry
from xbot import logging
from xbot.errors import UIAError, UIAErrorCode
from xbot import strings
import re
from typing import Optional, Union

def get_domain(web_page: WebBrowser) -> str:
    return web_page.execute_javascript("() => origin")

def is_amazon_domain(domain: str) -> bool:
    regex = re.compile(r"https?://sellercentral\.amazon")
    return regex.match(domain) is not None

def wait_by_xpath(web_page: WebBrowser, xpath: str, timeout: int = 10) -> Optional[WebElement]:
    try:
        return find_by_xpath(web_page, xpath, timeout=timeout)
    except UIAError:
        return None
    
def find_by_xpath(self: Union[WebBrowser, WebElement], xpath_selector: str, *, timeout: int = 10) -> WebElement:
    """
    原来函数找不到元素不会抛出XPath, 这里封装一层抛出去
    """
    try:
        return self.find_by_xpath(xpath_selector, timeout=timeout)
    except UIAError as e:
        pass
        # if e.code == UIAErrorCode.NoSuchElement:
        #     raise UIAError(f"{strings.Mobile_Error_Not_Found_Element} - {xpath_selector}", UIAErrorCode.NoSuchElement)
        # raise
        

def to_page(web_page: WebBrowser, url: str, suss_ele_xpath: str):
    domain = get_domain(web_page)
    if not re.match(r"^https?://", url):
        url = "{}{}".format(domain, url)
    for retry_times , set_last_error in Retry(times=2):
        for inner_retry_times, _ in Retry(timeout=20, ignore_exception=True):
            try:
                # 找到目标元素，进入页面成功，退出函数
                elem = web_page.find_all_by_xpath(suss_ele_xpath, timeout=0)
                if len(elem) > 0:
                    return

                if inner_retry_times == 0:
                    web_page.navigate(url, load_timeout=0)

                # 页面加载完成，退出循环，进入下一次重试
                if web_page.is_load_completed():
                    # 需要二次判断，防止刚好加载完成
                    elem = web_page.find_all_by_xpath(suss_ele_xpath, timeout=0)
                    if len(elem) > 0:
                        return                    
                    break
                # 页面没有加载完成，继续等待
            except Exception as e:
                logging.warning(e)
                set_last_error(e)
            


def main(args):
    web_page = xbot.web.get_active(mode="superbrowser")
    to_page(web_page, "/payments/dashboard/index.html/ref=xx_payments_foot_xx", '''//a[contains(@data-menu-id, "payments-account")]''')
    pass
