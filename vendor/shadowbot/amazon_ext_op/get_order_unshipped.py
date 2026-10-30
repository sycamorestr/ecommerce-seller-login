
import xbot
import re
from xbot import print, sleep
from xbot.web import WebBrowser
from xbot.selector import Selector
from .utils import get_domain
from .utils import handler_container
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector
from datetime import datetime
# from xbot_ai import *


# 所有元素Xpath路径
class Xpath:
    Unshipped = '//div[contains(@class,"myo-spa-quick-filter")]//a[contains(@href, "VergeOfLateShipment")]'
    HasOrder = '//div[@class="a-row"]//span[contains(@class, "icon-container")]'
    OrderId = "//tr//div[contains(@class,'cell-body')]//a[starts-with(@href, '/orders-v3/order/')]"
    NextPage = "//li[contains(@class, 'a-last') and not(contains(@class, 'a-disabled'))]"
    DisNextPage = "//li[contains(@class, 'a-disabled') and contains(@class, 'a-last')]"

# 构建所有需要用到的元素
class Element:
    next_page_button = create_selector(Xpath.NextPage,  name='下一页')
    unshipped = create_selector(Xpath.Unshipped, name = '濒临延迟发货')
    has_order = create_selector(Xpath.HasOrder,name ='无订单')



def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%m/%d/%Y")


def gen_selector(xpath: str) -> Selector:
    xpaths = xpath.split(">>")
    # print(xpaths)
    data = {
        "id": "xbot-xpath",
        "name": "动态元素",
        "type": "simple",
        "xpath": {"enable": "true", "segments": xpaths},
    }
    selector = Selector(data)
    return selector


def to_page_if_needed(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标页面，直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
    ):
        return
    # 如果不是，则导航到目标URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)

    # if not web_page.wait_appear(gen_selector(Xpath.ConditionRating), timeout=30):
    #     raise Exception(
    #         f"进入账户状况页面失败，未找到关键元素： {Xpath.ConditionRating}"
    #     )


#数据获取
def scrape_late_shipment_orders_v2(web_page: WebBrowser):
    
    # 1. 初始化一个列表，用于存储所有获取到的订单号
    all_order_ids = []
    # 2. 首先检查是否存在“无订单”的提示
    try:
        no_orders_element = web_page.find(Element.has_order,timeout = 5)
        
        if no_orders_element:
            print("检测到页面提示'无濒临发货订单'，程序结束。")
            return all_order_ids # 返回一个空列表
            
    except Exception:
        pass # 继续执行下面的代码
    
    # 3. 如果程序能走到这里，说明页面上有订单，开始执行循环和翻页逻辑
    while True:
        order_elements = web_page.find_all_by_xpath(Xpath.OrderId, timeout = 5)
        if not order_elements:
            break

        for element in order_elements:
            try:
                order_id = element.get_text()
                if order_id:
                    all_order_ids.append(order_id)
            except Exception as e:
                print(f"获取某个订单号时发生错误: {e}")

        # 处理翻页
        try:
            if web_page.wait_appear(Element.next_page_button,timeout = 5):
                print("找到'下一页'按钮，准备点击翻页...")
                web_page.find(Element.next_page_button).click()
                sleep(4)
            else:
                print("未找到可点击的'下一页'按钮，已到达最后一页。")
                break
        except Exception as e:
            print(f"查找'下一页'按钮时出错或未找到，已到达最后一页。")
            break
            
    # 4. 所有页面处理完毕，打印最终结果
    if all_order_ids:
        print(f"总计获取到 {len(all_order_ids)} 个订单。")
        print("订单号列表如下:")
        print(all_order_ids)
    else:
        # 如果经过循环后列表仍为空
        print("执行完成，未抓取到任何订单号。")
    
    return all_order_ids

# 整个业务操作流程
def process_method(web_page: WebBrowser):
    # if not isinstance(web_page, WebBrowser):
    #     raise ValueError("传入的'web_page'必须是一个浏览器对象")

    # 步骤1: 准备目标URL并调用函数，确保页面在政策合规页
    domain = get_domain(web_page)
    account_health_url = f"{domain}/orders-v3/mfn/unshipped?fulfillmentType=mfn&orderStatus=unshipped&UnShippedOrdersDefects=VergeOfLateShipment"
    to_page_if_needed(web_page, account_health_url)
    switch_language(web_page, 'zh_CN')
    sleep(3)
    dataList = scrape_late_shipment_orders_v2(web_page)
    return dataList

def test_run():
    if "xbot_extensions" in __file__:
        return
    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    data = process_method(web_page)
    exit()


def main(args):
    test_run()
    web_page = args.get("web_page")
    result_dict = process_method(web_page)
    args["dataList"] = result_dict


