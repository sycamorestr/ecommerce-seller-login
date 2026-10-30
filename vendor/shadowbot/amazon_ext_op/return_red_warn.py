# 模板

import xbot
import re
from xbot import print, sleep
from xbot.web import WebBrowser
from xbot.selector import Selector
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector
from datetime import datetime
from xbot import win32


# 旧版元素Xpath路径
class OldXpath:
    Time_Filter = '//div[contains(@class, "popover-inline-filter-container")]/div/div//input[@class="inline-filter-chip"]'
    Time_Day ='//*[local-name()="kat-radiobutton"][@name="lastUpdatedInline"][@value="1"]/input'
    Status_Filters = '//div[contains(@class, "popover-inline-filter-container")]/div/*[local-name()="kat-popover"]//input[@class="inline-filter-chip"]'
    Cancel_Status = '//div[@class ="shipment-status-filter-inline"]//*[local-name()="kat-link"][@class="select-link" and normalize-space(.)="取消全选"]'
    Already_Order = '//div/*[local-name()="kat-checkbox"][@value="SHIPPED"]'
    In_Convey ='//div/*[local-name()="kat-checkbox"][@value="IN_TRANSIT"]'
    Appy_Button = '//div/div[contains(@class, "filter-bar-container")]/kat-popover-hide'
    Next_Page = '//a[contains(text(), "下一页") and not(ancestor::div[@id="hide"])]'
    Data_Element = '//*[@id="content-row"]'
    # 旧版行内
    Error_Flag = './/div[starts-with(@class, "error-")]'
    Shipment_ID = './/div[@id="shipment_id_text"]'

# 新版元素Xpath路径 (AWS UI)
class NewXpath:
    Time_Filter = '//button[contains(., "上次更新时间")]'
    Time_Day = '//div[@role="option" and .//span[@title="最近 7 天"]]'
    Status_Filters = '//button[contains(., "状态")]'
    Cancel_Status = '//div[@role="option" and .//span[text()="取消全选"]]'
    Already_Order = '//div[@role="option" and .//span[@title="已发货"]]'
    In_Convey = '//div[@role="option" and .//span[@title="在途"]]'
    Appy_Button = '//button[contains(., "应用")]'
    Next_Page = '//button[contains(@aria-label, "Next page") or contains(@aria-label, "下一页")]'
    Data_Element = '//tr[contains(@class, "awsui_table-row")]'
    # 新版行内
    Error_Flag = './/span[contains(@class, "status-error")]'
    Shipment_ID = './/div[@data-column-id="shipmentId"]//span[@data-atom-id="secondary"]'

def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%Y/%m/%d")

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

def to_page_if_needed(web_page: WebBrowser, url: str):
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
    ):
        return
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)

# 数据获取
def shipping_Data(web_page: WebBrowser, is_new_ui: bool):
    all_unuseual_data = []
    xpath_config = NewXpath if is_new_ui else OldXpath
    
    try:
        data_lists = web_page.find_all_by_xpath(xpath_config.Data_Element, timeout=3)
        if not data_lists:
            print("没有数据")
            return all_unuseual_data
    except Exception:
        pass
    
    while True:
        rows = web_page.find_all_by_xpath(xpath_config.Data_Element, timeout=5)
        if not rows:
            break

        for row in rows:
            try:
                # 存在异常标志，才记录
                if row.find_by_xpath(xpath_config.Error_Flag, timeout=0):
                    id_element = row.find_by_xpath(xpath_config.Shipment_ID)
                    full_id_text = id_element.get_text().strip()
                    shipment_id = full_id_text.split(',')[0].strip() if not is_new_ui else full_id_text
                    if shipment_id:
                        all_unuseual_data.append(shipment_id)
            except Exception:
                pass

        # 处理翻页
        try:
            next_page_sel = gen_selector(xpath_config.Next_Page)
            if web_page.wait_appear(next_page_sel, timeout=3):
                btn = web_page.find(next_page_sel)
                if btn.is_enabled():
                    btn.click()
                    sleep(2)
                else:
                    print("下一页按钮不可点击。")
                    break
            else:
                print("已到达最后一页。")
                break
        except Exception:
            print("查找'下一页'按钮时出错或未找到，已到达最后一页。")
            break
            
    return all_unuseual_data

# 整个业务操作流程
def process_method(web_page: WebBrowser):
    domain = get_domain(web_page)
    url = f"{domain}/gp/ssof/shipping-queue.html"
    to_page_if_needed(web_page, url)
    switch_language(web_page, 'zh_CN')
    sleep(2)
    
    # UI 版本自动识别
    # 如果能找到新版的状态筛选器按钮，则判定为新版
    is_new_ui = web_page.wait_appear(gen_selector(NewXpath.Status_Filters), timeout=3)
    print(f"识别到页面版本：{'新版(AWS UI)' if is_new_ui else '旧版'}")
    
    xpath_config = NewXpath if is_new_ui else OldXpath

    # 执行筛选逻辑
    try:
        # 1. 点击时间筛选
        web_page.find_by_xpath(xpath_config.Time_Filter).click()
        sleep(1)
        # 2. 选择天数
        time_day_sel = gen_selector(xpath_config.Time_Day)
        if web_page.wait_appear(time_day_sel, timeout=5):
            web_page.find(time_day_sel).click()
        else:
            # 新版如果已经选了，点击空白处关闭
            win32.mouse_click(0, 0)
        sleep(1)

        # 3. 点击状态筛选
        web_page.find_by_xpath(xpath_config.Status_Filters).click()
        sleep(1)
        # 4. 取消全选 (如果存在)
        cancel_sel = gen_selector(xpath_config.Cancel_Status)
        if web_page.wait_appear(cancel_sel, timeout=3):
            web_page.find(cancel_sel).click()
            sleep(0.5)
        
        # 5. 勾选状态
        web_page.find_by_xpath(xpath_config.Already_Order).click()
        sleep(0.5)
        web_page.find_by_xpath(xpath_config.In_Convey).click()
        sleep(0.5)
        
        # 6. 应用筛选
        if is_new_ui:
            # 新版再次点击触发器即可收起
            web_page.find_by_xpath(xpath_config.Status_Filters).click()
        else:
            # 旧版需要显式点击应用按钮
            apply_sel = gen_selector(xpath_config.Appy_Button)
            if web_page.wait_appear(apply_sel, timeout=2):
                web_page.find(apply_sel).click()
        
        sleep(2)
    except Exception as e:
        print(f"筛选操作中出现异常: {e}")

    dataList = shipping_Data(web_page, is_new_ui)
    return dataList

def test_run():
    if "xbot_extensions" in __file__:
        return

    web_page = xbot.web.get_active(mode="ziniaobrowser")
    result_dict = process_method(web_page)
    print(f"最终结果: {result_dict}")
    print(f"总数: {len(result_dict)}")
    exit()

def main(args):
    test_run()
    web_page = args.get("web_page")
    result_dict = process_method(web_page)
    args["shipping_list"] = result_dict
    args["count_shipping"] = len(result_dict)
