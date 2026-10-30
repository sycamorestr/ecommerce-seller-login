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
from .create_element import create_selector, create_frame
from datetime import datetime
from xbot._core.retry import Retry


class Xpath:
    # ==================== 旧版页面 ====================
    Old_Product_Rows = '//div[@data-sku and not(./div[contains(@class, "variationBox")])]'
    Old_Image = './/div[contains(@class, "ProductDetails-module__container")]/img'
    Old_Inventory_Seller_Input = './/div[contains(@class, "Inventory-module__quantityInputBox")]//kat-input'
    Old_Inventory_FBA_Span = './/div[contains(@class, "JanusSplitBox-module__row") and .//kat-label]//span[contains(@class, "Inventory-module__popoverLink")]'
    Old_ASIN = ".//span[normalize-space(.)='ASIN']/parent::div/following-sibling::div/span"
    Old_Inventory_FBA_Div = './/*[local-name()="kat-label"][@emphasis="有货（亚马逊物流）"]/ancestor::div[contains(@class, "JanusSplitBox-module__panel")][1]/following-sibling::div[contains(@class, "JanusSplitBox-module__panel")]/div/span'
    Old_Product_status = '//*[local-name()="kat-dropdown"][@class="FilterPanel-module__statusDropdown--0Aa7Y"]/xbotShadowRoot//div[@class="select-header"]'
    Old_SortReason = '//*[local-name()="kat-dropdown"][contains(@class, "SortingWidget-module__sortingWidget--NUg3i")]'
    Old_HightoLow = '//*[local-name()="kat-dropdown"][contains(@class, "SortingWidget-module__sortingWidget--NUg3i")]/xbotShadowRoot//*[local-name()="kat-option"][normalize-space(.)="可售： 从高到低"]'
    Old_Next_Page_Clickable = '//*[local-name()="kat-pagination"]/xbotShadowRoot//span[@part="pagination-nav-right" and not(contains(@class, "end"))]'
    Old_Row_Status = './/div[contains(@class, "Status-module__container")]//*[local-name()="kat-label"]'
    Old_Data_Num = '//div[text()="所有商品"]/div'

    # ==================== 新版页面 ====================
    New_Product_Rows = '//table[contains(@class,"awsui-context-compact-table")]//tr[.//div[contains(@class,"awsui_body-cell-content")]]'
    New_Image = './td//img[@class="product-image"]'
    New_Inventory_Seller_Input = './/div[contains(@class, "Inventory-module__quantityInputBox")]//kat-input'
    New_Inventory_FBA_Span = './td//div[@data-testid="inventory-on-hand"]//div[normalize-space(.)="现货（亚马逊物流）"][contains(@class, "root")]/../../following-sibling::div/div/div'
    New_ASIN = './td//div[3][contains(@class, "awsui_horizontal_")]/div[1][contains(@class,"awsui_child")]/div[contains(@class,"awsui_text-content_")]'
    New_Inventory_FBA_Div = './/*[local-name()="kat-label"][@emphasis="有货（亚马逊物流）"]/ancestor::div[contains(@class, "JanusSplitBox-module__panel")][1]/following-sibling::div[contains(@class, "JanusSplitBox-module__panel")]/div/span'
    New_Product_status_Btn = '//button[normalize-space(.)="状态"]'
    New_SortReason = '(//button[@title="库存 列选项"]/span[contains(@class,"awsui_icon-left")])[1]'
    New_SortField = '//input[@value="QUANTITY_AVAILABLE"]'
    New_HightoLow = '//table//tr//div[contains(@class, "root")]/button[contains(.,"从低到高")]'
    New_Next_Page_Clickable = '//ul/li/button[not(@aria-disabled)]/span[contains(@class, "name-angle-right")]'
    New_Row_Status = './td//div/div[contains(@class, "status-blue")]/div[contains(@class, "root")]/span'


class Element:
    old_next_page = create_selector(Xpath.Old_Next_Page_Clickable, name='旧版下一页')
    old_product_rows = create_frame(Xpath.Old_Product_Rows, name='旧版数据')
    old_product_status = create_selector(Xpath.Old_Product_status, name='旧版商品状态')
    old_hightolow = create_selector(Xpath.Old_HightoLow, name='旧版库存高到低')

    new_next_page = create_selector(Xpath.New_Next_Page_Clickable, name='新版下一页')
    new_product_rows = create_frame(Xpath.New_Product_Rows, name='新版数据')
    new_product_status_btn = create_selector(Xpath.New_Product_status_Btn, name='新版状态按钮')
    new_sort_reason = create_selector(Xpath.New_SortReason, name='新版排序依据')
    new_sort_field = create_selector(Xpath.New_SortField, name='新版排序字段')
    new_hightolow = create_selector(Xpath.New_HightoLow, name='新版库存高到低')


class Option:
    ReportTypeList = {"全部": "[1]",
                      "在售": "[2]",
                      "在搜索结果中禁止显示": "[3]",
                      "改进商品信息质量": "[4]",
                      "不可售": "[5]",
                      "详情页面已删除": "[6]",
                      "缺货": "[7]",
                      "缺少报价": "[8]",
                      "需要批准": "[9]",
                      "已停售": "[10]",
                      "完善商品信息": "[11]",
                      "非在售": "[12]",
                      "配送问题": "[13]"}
    EventDateMap = {}


def convert_date_format(date_input):
    return datetime.strptime(date_input, "%Y-%m-%d").strftime("%Y/%m/%d")


def gen_selector(xpath: str) -> Selector:
    xpaths = xpath.split(">>")
    data = {
        "id": "xbot-xpath",
        "name": "动态元素",
        "type": "simple",
        "xpath": {"enable": "true", "segments": xpaths},
        'version': '2',
        'framework': 'chromium'
    }
    return Selector(data)


def to_page_if_needed(web_page: WebBrowser, url: str):
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
    ):
        return
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)


# ==================== 旧版页面数据获取 ====================
def asins_Data_old(web_page: WebBrowser, status_xpath: str):
    """
    旧版页面完整流程。
    “所有商品”计数元素做兜底：找不到时不抛异常，视为有数据继续。
    """
    # 兜底判断数据是否为空（找不到计数元素就跳过，不中断）
    try:
        for _ in Retry(timeout=10, ignore_exception=True):
            data_num = web_page.find_by_xpath(Xpath.Old_Data_Num, timeout=2).get_text()
            if data_num == "":
                continue
            else:
                if int(data_num) == 0:
                    print("当前店铺没有数据")
                    return []
                elif int(data_num) > 0:
                    break
    except Exception as e:
        print(f"旧版页面未找到“所有商品”计数，跳过空数据判断。原因：{e}")

    problematic_asins = []

    # 排序依据
    web_page.find_by_xpath(Xpath.Old_SortReason, timeout=2).click()
    web_page.find(Element.old_hightolow, timeout=2).click()

    # 设置分页大小
    trigger_page_size_btn_xpath = '//kat-dropdown[@id="page-size-dropdown-id"]'
    web_page.find_by_xpath(trigger_page_size_btn_xpath).click()
    sleep(1)

    page_size_btn_xpath = '//*[local-name()="kat-dropdown"][@id="page-size-dropdown-id"]/xbotShadowRoot//*[local-name()="kat-option"][2]/xbotShadowRoot/div[@class="content-wrapper"]'
    web_page.find(gen_selector(page_size_btn_xpath)).click()
    sleep(1)

    while True:
        try:
            web_page.wait_appear(Element.old_product_rows, timeout=20)
            product_rows = web_page.find_all_by_xpath(Xpath.Old_Product_Rows, timeout=3)

            if not product_rows:
                print("当前页面未找到任何商品行。")
                break

            for row in product_rows:
                try:
                    product_element = row.find_by_xpath(Xpath.Old_Row_Status, timeout=1).get_attribute('emphasis')

                    if product_element in ("捆绑商品", "商品信息已删除"):
                        continue

                    inventory_count = 0
                    try:
                        seller_input = row.find_by_xpath(Xpath.Old_Inventory_Seller_Input, timeout=0.5)
                        inventory_value_str = seller_input.get_attribute('value')
                        cleaned_str = inventory_value_str.strip().replace(",", "")
                        inventory_count = int(cleaned_str) if cleaned_str.isdigit() else 0
                    except Exception:
                        try:
                            fba_span = row.find_by_xpath(Xpath.Old_Inventory_FBA_Span, timeout=0.5)
                            inventory_value_str = fba_span.get_text()
                            cleaned_str = inventory_value_str.strip().replace(",", "")
                            inventory_count = int(cleaned_str) if cleaned_str.isdigit() else 0
                        except Exception:
                            try:
                                fba_div = row.find_by_xpath(Xpath.Old_Inventory_FBA_Div, timeout=0.5)
                                inventory_value_str = fba_div.get_text()
                                cleaned_str = inventory_value_str.strip().replace(",", "")
                                inventory_count = int(cleaned_str) if cleaned_str.isdigit() else 0
                            except Exception:
                                return problematic_asins

                    if inventory_count == 0:
                        return problematic_asins

                    image_element = row.find_by_xpath(Xpath.Old_Image)
                    image_src = image_element.get_attribute('src')
                    is_image_missing = image_src.endswith('.gif')
                    if not is_image_missing:
                        continue

                    is_inventory_positive = inventory_count > 0

                    if is_image_missing and is_inventory_positive:
                        asin_element = row.find_by_xpath(Xpath.Old_ASIN)
                        asin = asin_element.get_text().strip()
                        print(f"✔️ 发现问题商品 -> ASIN: {asin} (图片丢失, 库存: {inventory_count})")
                        problematic_asins.append(asin)

                except Exception as e:
                    print(f"处理某一行时出错，跳过。错误: {e}")
                    continue

        except Exception as e:
            print(f"获取商品行列表时发生错误，可能本页无数据: {e}")
            break

        # 翻页
        try:
            if web_page.wait_appear(Element.old_next_page, timeout=2):
                web_page.find(Element.old_next_page).click()
                web_page.wait_load_completed(timeout=20)
                sleep(1)
            else:
                print("已到达最后一页。")
                break
        except Exception as e:
            print(f"查找'下一页'按钮时出错或未找到:{e}")
            break

    return problematic_asins


# ==================== 新版页面数据获取 ====================
def asins_Data_new(web_page: WebBrowser, status_xpath: str):
    for _ in Retry(timeout=10, ignore_exception=True):
        none_xpath = '//table//tr/td//p[normalize-space(.)="我们无法找到匹配项。"]'
        if len(web_page.find_all_by_xpath(none_xpath)) > 0:
            print("当前店铺没有数据")
            return []

    problematic_asins = []

    web_page.wait_load_completed(20)
    web_page.wait_appear(Element.new_product_rows, timeout=20)

    if status_xpath:
        try:
            web_page.find(Element.new_product_status_btn, timeout=3).click()
            web_page.find_by_xpath(status_xpath, timeout=3).click()
        except Exception as e:
            print(f"新版页面筛选商品状态失败:{status_xpath}，出错原因：{e}")
            return []

    web_page.find_by_xpath(Xpath.New_SortReason, timeout=2).click()
    web_page.find_by_xpath(Xpath.New_SortField).click()
    if len(web_page.find_all_by_xpath(Xpath.New_HightoLow)) > 0:
        web_page.find_all_by_xpath(Xpath.New_HightoLow)[0].click()
        sleep(3)
    web_page.wait_appear(Element.new_product_rows, timeout=20)

    while True:
        try:
            web_page.wait_appear(Element.new_product_rows, timeout=20)
            product_rows = web_page.find_all_by_xpath(Xpath.New_Product_Rows, timeout=3)

            if not product_rows:
                print("当前页面未找到任何商品行。")
                break

            for row in product_rows:
                try:
                    product_element = row.find_by_xpath(Xpath.New_Row_Status, timeout=1).get_attribute('emphasis')

                    if product_element in ("捆绑商品", "商品信息已删除"):
                        continue

                    inventory_count = 0
                    try:
                        seller_input = row.find_by_xpath(Xpath.New_Inventory_Seller_Input, timeout=0.5)
                        inventory_value_str = seller_input.get_attribute('value')
                        cleaned_str = inventory_value_str.strip().replace(",", "")
                        inventory_count = int(cleaned_str) if cleaned_str.isdigit() else 0
                    except Exception:
                        try:
                            fba_span = row.find_by_xpath(Xpath.New_Inventory_FBA_Span, timeout=0.5)
                            inventory_value_str = fba_span.get_text()
                            cleaned_str = inventory_value_str.strip().replace(",", "")
                            inventory_count = int(cleaned_str) if cleaned_str.isdigit() else 0
                        except Exception:
                            try:
                                fba_div = row.find_by_xpath(Xpath.New_Inventory_FBA_Div, timeout=0.5)
                                inventory_value_str = fba_div.get_text()
                                cleaned_str = inventory_value_str.strip().replace(",", "")
                                inventory_count = int(cleaned_str) if cleaned_str.isdigit() else 0
                            except Exception:
                                return problematic_asins

                    if inventory_count == 0:
                        return problematic_asins

                    image_element = row.find_by_xpath(Xpath.New_Image)
                    image_src = image_element.get_attribute('src')
                    is_image_missing = image_src.endswith('.gif')
                    if not is_image_missing:
                        continue

                    is_inventory_positive = inventory_count > 0

                    if is_image_missing and is_inventory_positive:
                        asin_element = row.find_by_xpath(Xpath.New_ASIN)
                        asin = asin_element.get_text().strip()
                        print(f"✔️ 发现问题商品 -> ASIN: {asin} (图片丢失, 库存: {inventory_count})")
                        problematic_asins.append(asin)

                except Exception as e:
                    print(f"处理某一行时出错，跳过。错误: {e}")
                    continue

        except Exception as e:
            print(f"获取商品行列表时发生错误，可能本页无数据: {e}")
            break

        try:
            if web_page.wait_appear(Element.new_next_page, timeout=2):
                web_page.find(Element.new_next_page).click()
                web_page.wait_load_completed(timeout=20)
                web_page.wait_appear(Element.new_product_rows, timeout=20)
                sleep(2)
            else:
                print("已到达最后一页。")
                break
        except Exception as e:
            print(f"查找'下一页'按钮时出错或未找到:{e}")
            break

    return problematic_asins


# ==================== 统一入口：先旧版，失败走新版 ====================
def asins_Data(web_page: WebBrowser, status_xpath_old: str, status_xpath_new: str):
    """
    严格判断旧版结构：
    - 旧版商品行存在，且旧版“所有商品”计数元素存在，才认定为旧版；
    - 否则直接走新版逻辑。
    """
    try:
        web_page.wait_load_completed(20)
        web_page.wait_appear(Element.old_product_rows, timeout=20)
        # 额外确认旧版特征元素存在（“所有商品”计数）
        web_page.find_by_xpath(Xpath.Old_Data_Num, timeout=2)
        # 仅当需要筛选状态时才点击
        if status_xpath_old:
            web_page.find(Element.old_product_status, timeout=3).click()
            web_page.find_by_xpath(status_xpath_old, timeout=3).click()
    except Exception as e:
        print(f"旧版页面结构确认失败，切换到新版逻辑。原因：{e}")
        return asins_Data_new(web_page, status_xpath_new)

    return asins_Data_old(web_page, status_xpath_old)


# 整个业务操作流程
def process_method(web_page: WebBrowser, status_row: str):
    domain = get_domain(web_page)
    url = f"{domain}/myinventory/inventory"
    to_page_if_needed(web_page, url)
    switch_language(web_page, 'zh_CN')
    sleep(2)

    if status_row == "全部":
        status_xpath_old = ""
        status_xpath_new = ""
    else:
        status_xpath_old = f'//*[local-name()="kat-option"][starts-with(normalize-space(.), "{status_row}")]'
        status_xpath_new = f'(//span[contains(@class, "awsui_label")]/span[starts-with(normalize-space(.), "{status_row}")])[1]'

    dataList = asins_Data(web_page, status_xpath_old, status_xpath_new)
    return dataList


def test_run():
    if "xbot_extensions" in __file__:
        return

    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    status_row = '在售'

    data = process_method(web_page, status_row)
    # print(data)

    exit()


def main(args):
    test_run()
    web_page = args.get("web_page")
    status_row = args.get("商品状态")
    result_dict = process_method(web_page, status_row)
    args["data"] = result_dict