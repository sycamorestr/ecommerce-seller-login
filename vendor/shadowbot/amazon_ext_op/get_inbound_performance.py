# 模板

import xbot
import re
from xbot import print, sleep
from xbot import print
from xbot.web import WebBrowser
from xbot.selector import Selector
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector ,create_frame
from datetime import datetime
from xbot import win32


# 所有元素Xpath路径
class Xpath:
    #第一层
    Iframe = '//iframe[contains(@src, "/fba/inboundperformancedashboard/defects")]'
    All_Category = '//div[@id="card-padding"]/div[@class = "card-width"]'
    #卡片
    Unresolved_Issue_Indicator = ".//small[@class='cardNumber' and contains(text(), '未解决的缺陷')]"
    Category_Name = './/div[contains(@class, "content-padding-top-defect-group")]'
    #具体数据
    Defect_Rows = '//*[@id="problem-table"]/kat-table/kat-table-body/kat-table-row'
    Defect_Type = './/kat-table-cell[1]'
    Shipment_ID = './/kat-table-cell[3]//div[@class="sub-cell"]'
    Defect_Quantity = './/div[div[@class="sub-cell" and ./span[normalize-space(.)="BOXES"]]]/div[@class="one-row"]'


# 构建所有需要用到的元素
class Element:
    all_category = create_frame(Xpath.Iframe,Xpath.All_Category , name ="类别")
    all_rows = create_frame(Xpath.Iframe,Xpath.Defect_Rows)
def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%Y/%m/%d")



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

def get_inbound_performance_defects(web_page: WebBrowser):
    """
    检查入库绩效页面，获取所有存在未解决问题类别的缺陷详情。
    """
    domain = get_domain(web_page)
    url = f"{domain}/fba/inboundperformancedashboard"
    to_page_if_needed(web_page, url)
    switch_language(web_page, 'zh_CN')
    sleep(2)
    all_defects_data = []
    print("开始检查入库绩效页面的主要缺陷...")

    # 步骤 1: 获取所有缺陷类别
    category_cards = web_page.find_all(Element.all_category, timeout=3)
    if not category_cards:
        print("未在页面上找到任何缺陷类别卡片。")
        return all_defects_data

    print(f"找到 {len(category_cards)} 个缺陷类别，正在逐一检查...")

    # 步骤 2: 遍历每一张卡片
    for card in category_cards:
        try:
            # 步骤 3: 检查卡片内是否存在“未解决的缺陷”的标志
            issue_indicator = card.find_by_xpath(Xpath.Unresolved_Issue_Indicator, timeout=1)

            # 如果找到了标志，就执行点击和数据提取
            category_name_element = card.find_by_xpath(Xpath.Category_Name)
            category_name = category_name_element.get_text().strip()

            # 步骤 4: 点击卡片，跳转到详情
            card.click()
            sleep(3)  # 等待页面滚动或加载详情内容

            # 步骤 5: 在详情区域查找所有缺陷记录行
            detail_rows = web_page.find_all(Element.all_rows, timeout=3)
            if not detail_rows:
                print(f"警告：在 '{category_name}' 的详情区域未找到任何缺陷记录。")
                continue

            print(f"在 '{category_name}' 详情中找到 {len(detail_rows)} 条记录，开始提取...")

            # 步骤 6: 遍历每一行缺陷记录，提取数据
            for row in detail_rows:
                # ... (这部分提取逻辑依赖于你确认详情页的 XPath) ...
                defect_type = row.find_by_xpath(Xpath.Defect_Type).get_text().strip()
                shipment_id = row.find_by_xpath(Xpath.Shipment_ID).get_text().strip()
                defect_quantity_text = row.find_by_xpath(Xpath.Defect_Quantity).get_text().strip()
                
                defect_data = {
                    "问题类别": category_name,
                    "缺陷类型": defect_type,
                    "货件编号": shipment_id,
                    "缺陷数量": int(defect_quantity_text)
                }
                all_defects_data.append(defect_data)

        except Exception as e:
            # 如果找不到“未解决的缺陷”标志，说明该卡片正常，安静地跳过
            print(f"找不到“未解决的缺陷”标志，说明该卡片正常{e}")
            pass
            
    if all_defects_data:
        print(f"所有缺陷信息提取完毕！总计获取到 {len(all_defects_data)} 条缺陷记录。")
    else:
        print("检查完成，未发现任何需要处理的未解决缺陷。")
    return all_defects_data


def test_run():
    if "xbot_extensions" in __file__:
        return

    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    get_inbound_performance_defects(web_page)
    # process_method(web_page)
    exit()


def main(args):
    test_run()
    web_page = args.get("web_page")
    result_dict = get_inbound_performance_defects(web_page)
    args["data"] = result_dict


