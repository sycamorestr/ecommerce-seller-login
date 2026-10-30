# 模板

import xbot
import re
from xbot import print, sleep
from xbot import print
from xbot.web import WebBrowser
from xbot.selector import Selector
from .utils import get_domain
from .utils import handler_container
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector,create_frame
from datetime import datetime


# 所有元素Xpath路径
class Xpath:
    # 行数据
    table_row = '//tr[contains(@class, "mt-row")]'
    
    # ASIN (
    row_asin = './/*[@data-column="asin-field"]//span[contains(@class, "mt-text-content")]'
    
    # SKU 
    row_sku = './/*[@data-column="msku-field"]//a'


def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%m/%d/%Y")


def to_page_if_needed(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标页面，直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
    ):
        return
    # 如果不是，则导航到目标URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)


# 数据获取
def product_data(web_page: WebBrowser):
    data_list = []
    try:
        # 1. 先获取所有行元素
        rows = web_page.find_all_by_xpath(Xpath.table_row, timeout=3)
        
        if not rows:
            print("当前页面未找到任何数据行。")
            return data_list
        
        # 2. 遍历每一行，分别提取该行内的 ASIN 和 SKU
        for row in rows:
            try:
                # 在当前 row 元素下查找 ASIN
                asin_ele = row.find_by_xpath(Xpath.row_asin)
                asin_txt = asin_ele.get_text().strip() if asin_ele else ""
                
                # 在当前 row 元素下查找 SKU
                sku_ele = row.find_by_xpath(Xpath.row_sku)
                sku_txt = sku_ele.get_text().strip() if sku_ele else ""
                
                # 只有当ASIN或SKU至少有一个存在时才添加
                if asin_txt or sku_txt:
                    # 将数据存为字典，方便后续调用
                    data_list.append({
                        "ASIN": asin_txt,
                        "SKU": sku_txt
                    })
            except Exception as row_error:
                print(f"解析单行数据时出错: {row_error}")
                continue
                
    except Exception as e:
        print(f"获取表格数据时发生意外错误:{e}")

    # 返回列表，列表项现在是字典：[{'ASIN': '...', 'SKU': '...'}, ...]
    return data_list

# 整个业务操作流程
def process_method(web_page: WebBrowser):
    # 步骤1: 准备目标URL并调用函数，确保页面在政策合规页
    domain = get_domain(web_page)
    account_health_url = f"{domain}/inventoryplanning/stranded-inventory"
    to_page_if_needed(web_page, account_health_url)
    switch_language(web_page, 'zh_CN')
    sleep(3)
    data_list = product_data(web_page)
    return data_list


def test_run():
    if "xbot_extensions" in __file__:
        return

    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    data1 = process_method(web_page)
    print(data1)
    exit()


def main(args):
    test_run()
    web_page = args.get("web_page")
    result_list = process_method(web_page)
    args["data"] = result_list