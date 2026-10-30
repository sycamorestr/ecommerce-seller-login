# 模板

import xbot
import re
from xbot import print, sleep
from xbot import print
from xbot.web import WebBrowser
from xbot.selector import Selector
from .utils import get_domain
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector
from datetime import datetime


# 所有元素Xpath路径
class Xpath:
    Lobby_Filter = '//*[local-name()="kat-filter-bar"]/xbotShadowRoot//*[@id="filters" and self::kat-button]'
    Need_Attention = '//*[local-name()="kat-checkbox"][@data-testid="case-status-OpenedCasesNeedingAttention"]/xbotShadowRoot//*[local-name()="kat-label"][contains(@class, "checkbox-label")]'
    Clear_Button_Term = '//*[local-name()="kat-section-header"][@data-testid="case-log-filter-case-status-section-header"]/xbotShadowRoot//*[local-name()="kat-button"][@id="action"]/xbotShadowRoot/button[@type="button"]'
    Clear_Button_Date = '//*[local-name()="kat-section-header"][@header="创建日期"]/xbotShadowRoot//*[local-name()="kat-button"][@id="action"]/xbotShadowRoot/button[@type="button"]'
    Begin_Date = '//*[local-name()="kat-section-header"][@header="创建日期"]//*[local-name()="kat-date-picker"]/xbotShadowRoot//*[local-name()="kat-input"][@unique-id="katal-id-10"][@type="text"]/xbotShadowRoot//input[@type="text"]'
    End_Date = '//*[local-name()="kat-section-header"][@header="创建日期"]//*[local-name()="kat-date-picker"]/xbotShadowRoot//*[local-name()="kat-input"][@unique-id="katal-id-11"][@type="text"]/xbotShadowRoot//input[@type="text"]'
    Apply_Button = '//*[local-name()="kat-button"][@data-testid="hill-case-log-filter-apply-button"]'
    Summary_Xpath = '//div[@class="pagination-display-summary"]/span'
    All_Data = '//kat-data-table//tbody/tr'
    Un_Next_Page = "//*[local-name()='kat-pagination']/xbotShadowRoot//span[@class='nav item end' and @part='pagination-nav-right']"
    Next_Page = '//*[local-name()="kat-pagination"]/xbotShadowRoot//span[@class="nav item"][@part="pagination-nav-right"]'
    Close_Filter = '//*[local-name()="kat-panel"][@visible="true"]/xbotShadowRoot//button/*[local-name()="kat-icon"]'
    ManageIssue = '//*[@data-test-tag="hill-case-log-title"]'

# 构建所有需要用到的元素
class Element:
    lobby_filter = create_selector(Xpath.Lobby_Filter,name = '筛选')
    need_attention = create_selector(Xpath.Need_Attention, name = '需要注意')
    clear_button_term = create_selector(Xpath.Clear_Button_Term , name = '清除条件')
    clear_button_date = create_selector(Xpath.Clear_Button_Date , name = '清除日期')
    begin_date = create_selector(Xpath.Begin_Date , name = '开始日期')
    end_date = create_selector(Xpath.End_Date , name = '结束日期')
    apply_button = create_selector(Xpath.Apply_Button , name = '应用')
    summary_element = create_selector(Xpath.Summary_Xpath, name= '是否有数据')
    next_page = create_selector(Xpath.Next_Page, name ='下一页')
    close_filter = create_selector(Xpath.Close_Filter,"关闭筛选")


def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%Y/%m/%d")


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

    # if not web_page.wait_appear(gen_selector(Xpath.ConditionRating), timeout=30):
    #     raise Exception(
    #         f"进入账户状况页面失败，未找到关键元素： {Xpath.ConditionRating}"
    #     )


#数据获取
def lobby_Data(web_page: WebBrowser):
    
    # 1. 初始化一个列表
    all_lobby_data = []
    try:
        is_lobby_element = web_page.wait_appear(Element.summary_element,timeout = 5)
        if not is_lobby_element:
            print("没有问题单")
            return all_lobby_data # 返回一个空列表

        summary_text = is_lobby_element.get_text()
        match = re.search(r'共\s*(\d+)\s*个', summary_text)
        if match:
            # 非0
            count = int(match.group(1))
            return count
        else:
            print("没有问题单")
            return all_lobby_data

    except Exception:
        pass
    
    # 3. 如果程序能走到这里，说明页面上有信息，开始执行循环和翻页逻辑
    while True:
        rows = web_page.find_all_by_xpath(Xpath.All_Data, timeout = 5)
        if not rows:
            break
        count_failures = 0
        max_failures = 5

        for row in rows:
            try:
                case_id = row.find_by_xpath('.//td[contains(@class, "panel-caseId")]').get_text().strip()
                status = row.find_by_xpath('.//td/div[contains(@class, "hill-case-lobby-search-results-panel-status-container")]').get_text().strip()
                subject = row.find_by_xpath('.//td[contains(@class, "panel-shortDescription")]').get_text().strip()
                creation_date = row.find_by_xpath('.//td[contains(@class, "panel-creationDate")]').get_text().strip()
                all_lobby_data.append({"编号": case_id, "状态": status, "主题": subject,"创建日期":creation_date})
                #重置计数器
                count_failures = 0
            except Exception as e:
                count_failures += 1
                if count_failures >= max_failures:
                    print(f"\n--- 数据加载失败{e} ---")
                    break
                continue

        # 处理翻页
        try:
            if web_page.wait_appear(Element.next_page,timeout = 3):
                web_page.find(Element.next_page).click()
                sleep(4)
            else:
                print("未找到可点击的'下一页'按钮，已到达最后一页。")
                break
        except Exception as e:
            print(f"查找'下一页'按钮时出错或未找到，已到达最后一页。")
            break
            
    # 4. 所有页面处理完毕，打印最终结果
    if all_lobby_data:
        print(f"总计获取到 {len(all_lobby_data)} 条信息。")
        # print(all_message_data)
    else:
        # 如果经过循环后列表仍为空
        print("执行完成，无需要关注信息。")
    
    return all_lobby_data

# 整个业务操作流程
def process_method(web_page: WebBrowser,begin_date_input,end_date_input):
    # if not isinstance(web_page, WebBrowser):
    #     raise ValueError("传入的'web_page'必须是一个浏览器对象")

    domain = get_domain(web_page)
    url = f"{domain}/cu/case-lobby"
    to_page_if_needed(web_page, url)
    switch_language(web_page, 'zh_CN')
    sleep(3)
    web_page.find_by_xpath(Xpath.ManageIssue).click()
    web_page.find(Element.lobby_filter).click()
    web_page.find(Element.clear_button_term).click()
    web_page.find(Element.need_attention).click()
    web_page.find(Element.clear_button_date).click()
    
    #新 输入日期
    web_page.find(Element.begin_date).input(begin_date_input, simulative=True)
    print(begin_date_input)
    xbot.win32.send_keys('{esc}')
    sleep(2)
    web_page.find(Element.end_date).input(end_date_input, simulative=True)
    print(end_date_input)
    xbot.win32.send_keys('{esc}')
    # web_page.find(Element.begin_date).input(
    # begin_date_input + "{esc}", 
    #     contains_hotkey=True, 
    #     simulative=True,         # 显式开启模拟输入，这是让快捷键生效的关键
    #     # cdp_input=False          # 显式关闭CDP输入，确保不会走错模式
    # )
    # sleep(2)
    # web_page.find(Element.end_date).input(
    #     end_date_input + "{esc}", 
    #     contains_hotkey=True, 
    #     simulative=True,         # 显式开启模拟输入，这是让快捷键生效的关键
    #     # cdp_input=False          # 显式关闭CDP输入，确保不会走错模式
    # )

    
    web_page.find(Element.apply_button).click()
    # 目前情况，点击应用后无需点击取消筛选按钮
    try:
        web_page.find(Element.close_filter,timeout=3).click()
    except:
        pass
    dataList = lobby_Data(web_page)
    return dataList

def test_run():
    if "xbot_extensions" in __file__:
        return

    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")

    begin_date_input = '2026-08-14'
    end_date_input = '2026-08-21'
    data2 = process_method(web_page,convert_date_format(begin_date_input),convert_date_format(end_date_input))
    print(data2)
    exit()


def main(args):
    test_run()
    web_page = args.get("web_page")
    begin_date_input = args.get("begin_date_input")
    end_date_input = args.get("end_date_input")
    result_dict = process_method(web_page,convert_date_format(begin_date_input),convert_date_format(end_date_input))
    args["data"] = result_dict


