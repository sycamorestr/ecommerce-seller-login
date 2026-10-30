#模板

import xbot
import re
from xbot import print, sleep
from xbot.web import WebBrowser
from xbot.selector import Selector
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector
from datetime import datetime
from ._amazon_api import login, switch_site

# 所有元素Xpath路径
class Xpath:
    StarteDate= '//*[local-name()="kat-date-picker"][@name="startDatePicker"]/xbotShadowRoot//*[local-name()="kat-input"][@type="text"]/xbotShadowRoot//input[@type="text"]'
    EndDate = '//*[local-name()="kat-date-picker"][@name="endDatePicker"]/xbotShadowRoot//*[local-name()="kat-input"][@type="text"]/xbotShadowRoot//input[@type="text"]'
    DateLast = '//*[local-name()="kat-input"][@type="text"]'
    SubbmitButton = '//*[local-name()="kat-button"][@data-testid="date-range-picker-apply"]'
    DataTd = '//div[@data-testid="ahd-product-policies-table-open"]//div[@data-testid="ahd-desktop-product-policy"]'
    #更新
    AccountScore = '//*[@id="ahd-numeric-ahr-section"]//h3[2]'
    NoData ='//div[@data-testid="ahd-product-policies-table-open"]//span[@slot="header"]'
    NextPageButton = '//kat-pagination[@id="ahd-pp-pagination-katal-control"]/xbotShadowRoot//span[@part="pagination-nav-right"][not(contains(@class, "end"))]'
    FilterImpact = '//kat-button[@data-testid="ahd-pp-filter-button"]'
    NoImpact = '(//div[contains(@class,"ahd-filter")])[3]//kat-checkbox'
    DisplayResult = '//*[contains(@data-testid,"filter-apply")]'
    UnsolvedButton = '//section[@class="ahd-product-policy__section"]//kat-tab[@data-testid="kat-tab-open-status"]'
# 构建所有需要用到的元素
class Element:
    start_date = create_selector(Xpath.StarteDate,Xpath.DateLast,name = '开始日期')
    end_date = create_selector(Xpath.EndDate,Xpath.DateLast,name = '结束日期')
    submit_button = create_selector(Xpath.SubbmitButton,Xpath.DateLast,name = '申请日期')
    no_data = create_selector(Xpath.NoData ,name = '无数据')
    next_page_button = create_selector(Xpath.NextPageButton, name='下一页按钮')
    unsolved_button = create_selector(Xpath.UnsolvedButton, name='未解决按钮')
def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%m/%d/%Y")

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

    # if not web_page.wait_appear(gen_selector(Xpath.ConditionRating), timeout=30):
    #     raise Exception(
    #         f"进入账户状况页面失败，未找到关键元素： {Xpath.ConditionRating}"
    #     )

#数据获取
def product_health_data(web_page: WebBrowser, xpath: str):
    data_list = []
    asin_pattern = re.compile(r"ASIN[：: ]\s*([A-Z0-9]{10})")
    count_failures = 0
    max_failures = 3
    cached_reason = "未知原因"  # 用于缓存最近一次出现的有效违规原因

    # 先尝试获取账户状况评分
    score_text = ""
    try:
        score_element = web_page.find_by_xpath(Xpath.AccountScore, timeout=10)
        score_text = score_element.get_text()
    except Exception as e:
        print(f"⚠️ 获取账户状况评分失败: {e}")
        score_text = ""

    has_data = web_page.wait_appear(Element.no_data, timeout=3)
    if has_data:
        final_report = {
            '账户状况评分': score_text,
            '未解决详情': data_list
        }
        return final_report
    
    # 翻页循环：持续抓取数据直到没有下一页
    page_count = 0
    while True:
        page_count += 1
        print(f"正在抓取第 {page_count} 页数据...")
        
        # 等待当前页数据加载
        sleep(1)
        xpath = '//div[@id="ahd-product-policies-table"]/div[not (@id)]'
        rows = web_page.find_all_by_xpath(xpath)

        if rows:
            for row in rows:
                try:
                    # 提取 Reason (原因)
                    reason = ""
                    try:
                        reason_element = row.find_by_xpath('(.//div[contains(@data-testid, "ahd-ppc-row-reason")])[1]', timeout=2)
                        reason = reason_element.get_text().strip().split('\n')[0]
                    except:
                        pass
                    
                    # 提取 ASIN
                    asin = ""
                    impacted_text = ""
                    try:
                        impacted_element = row.find_by_xpath('.//div[contains(@data-testid, "ahd-ppc-row-impacted")]', timeout=2)
                        impacted_text = impacted_element.get_text()
                        match = asin_pattern.search(impacted_text)
                        if match:
                            asin = match.group(1)
                    except:
                        pass
                    
                    # 提取 Date (日期)
                    date = ""
                    try:
                        date_element = row.find_by_xpath('.//div[contains(@data-testid, "ahd-ppc-row-date")]', timeout=2)
                        date = date_element.get_text().strip()
                    except:
                        pass
                    
                    # 提取 存在销售风险
                    sales_risk = ""
                    try:
                        sales_element = row.find_by_xpath('.//div[contains(@data-testid,"row-at-risk")]', timeout=2)
                        sales_risk = sales_element.get_text()
                    except Exception as e:
                        print(e)

                    # 更新缓存：如果当前行能提取到有效的 Reason 文本（非空），则更新 cached_reason
                    if reason:
                        cached_reason = reason
                    
                    # 数据保存：只有当提取到 ASIN 时，才保存数据到列表
                    # 保存时，原因字段必须使用当前的 cached_reason（这样子行就能自动继承父行的原因）
                    # if asin:
                    data_list.append({
                        "原因": cached_reason,
                        "日期": date,
                        "ASIN": asin,
                        "存在风险": sales_risk
                    })
                    
                    count_failures = 0
                except Exception as e:
                    count_failures += 1
                    if count_failures >= max_failures:
                        print(f"\n--- 数据加载失败 {e} ---")
                        break
                    continue
        
        # 检查是否有下一页（只能使用构建的元素）
        has_next_page = False
        try:
            next_page_button = web_page.find(Element.next_page_button, timeout=3)
            if next_page_button and next_page_button.is_displayed():
                print(f"第 {page_count} 页数据抓取完成，共 {len(data_list)} 条记录，找到下一页按钮，准备点击...")
                sleep(0.5)
                next_page_button.click()
                sleep(2)
                web_page.wait_load_completed(timeout=30)
                has_next_page = True
        except Exception as e:
            # 没有找到下一页按钮，说明已经是最后一页
            print(f"未找到下一页按钮（可能已是最后一页）: {e}")
        
        if not has_next_page:
            # 没有找到下一页按钮，说明已经是最后一页
            print(f"所有页面数据抓取完成，共 {page_count} 页，总计 {len(data_list)} 条记录")
            break

    # 始终返回字典格式
    final_report = {
        '账户状况评分': score_text,
        '未解决详情': data_list
    }
    return final_report

#整个业务操作流程
def execute_account_health_popup_check(web_page: WebBrowser, start_input=None, end_input=None, site_name=None, is_filter='否') -> bool:

    # if not isinstance(web_page, WebBrowser):
    #     raise ValueError("传入的'web_page'必须是一个浏览器对象")

    # 步骤1: 准备目标URL并调用函数，确保页面在政策合规页
    domain = get_domain(web_page)
    account_health_url = f"{domain}/performance/account/health/product-policies"
    to_account_health_page_if_needed(web_page, account_health_url)
    # switch_language(web_page, 'zh_CN')

    # 进行登录校验
    login(web_page)
    # 进行站点校验
    if site_name:
        if '/account-switcher/default/merchantMarketplace' in web_page.get_url():
            switch_site(web_page, site_name)
    
    sleep(3)

    # 步骤2: 日期选择（仅当提供了日期参数时执行）
    if start_input and end_input:
        # 先等开始日期元素出现，再额外等待 3 秒确保亚马逊前端渲染完成，避免误触全选等操作
        web_page.wait_appear(Element.start_date, timeout=20)
        sleep(3)
        expected_start = convert_date_format(start_input)
        expected_end = convert_date_format(end_input)
        for attempt in range(3):
            web_page.find(Element.unsolved_button, timeout=10).click()
            web_page.find(Element.start_date, timeout=10).input(expected_start)
            web_page.find(Element.end_date, timeout=10).input(expected_end)
            sleep(0.5)
            actual_start = (web_page.find(Element.start_date, timeout=5).get_attribute("value") or "").strip()
            actual_end = (web_page.find(Element.end_date, timeout=5).get_attribute("value") or "").strip()
            if actual_start == expected_start and actual_end == expected_end:
                break
            if attempt < 2:
                sleep(1)
        else:
            print("警告：日期填写校验未通过，已重试3次")
        
        if is_filter == '是':
            # 进行筛选无影响以外的数据
            for attempt in range(3):
                tmp_list = []
                is_end = False
                web_page.find_by_xpath(Xpath.FilterImpact).click()
                None_impact_sel = web_page.find_all_by_xpath(Xpath.NoImpact)
                if len(None_impact_sel) > 0:
                    for tmp in range(len(None_impact_sel)):
                        None_impact_sel = web_page.find_all_by_xpath(Xpath.NoImpact)
                        for None_impact in None_impact_sel:
                            None_text = None_impact.get_attribute('id')
                            if 'None' in None_text:
                                is_end = True
                                break
                            elif 'NONE' not in None_text and None_text not in tmp_list:
                                if None_impact.get_attribute('checked') != "true":
                                    None_impact.click()
                                tmp_list.append(None_text)
                                break
                        if is_end is True:
                            break
                    # 点击显示结果
                    web_page.find_by_xpath(Xpath.DisplayResult).click()
                    sleep(3)
                    break
            else:
                print("警告：按影响筛选复选框未筛选，已重试3次")

        # 点击提交
        web_page.find(Element.submit_button).hover()
        web_page.find(Element.submit_button, timeout=15).click()
        sleep(5)
        web_page.wait_load_completed(timeout=200)
    else:
        print("未提供日期参数，使用页面默认日期进行数据抓取")
        # 等待页面加载完成
        web_page.wait_load_completed(timeout=200)

    web_page = xbot.web.get_active(mode=web_page.product_name)

    dataDict = product_health_data(web_page, Xpath.DataTd)
    
    return dataDict

def test_run():
    if "xbot_extensions" in __file__:
        return

    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    # print(web_page)
    # print(web_page.product_name)
    # 测试1: 使用日期参数
    start_input = ''
    end_input = ''
    site_name = ''
    data1 = execute_account_health_popup_check(web_page, start_input, end_input, site_name, '否')
    print(data1)
    # web_page.find('test_input').input(convert_date_format(start_input),input_check=True,check_value = convert_date_format(start_input))
    # 测试2: 不使用日期参数（使用默认日期）
    # data2 = execute_account_health_popup_check(web_page, None, None)
    # print(data2)
    
    exit()
 

def main(args):
    test_run()
    web_page = args.get("web_page")
    start_input = args.get("start_input")  # 可选参数，可以为 None
    end_input = args.get("end_input")  # 可选参数，可以为 None
    is_filter = args.get('is_filter')
    site_name = args.get('site_name') or ''
    result_dict = execute_account_health_popup_check(web_page, start_input, end_input, site_name, is_filter)
    args["data"] = result_dict


