# 模板

import xbot
import re
from xbot import print, sleep
from xbot.web import WebBrowser
from xbot.selector import Selector
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector,create_frame
from datetime import datetime


class Xpath:
    # --- 产品行相关 ---
    Product_Rows = '//div[@data-sku and not(./div[contains(@class, "variationBox")])]'
    # 产品链接：在titleContainer中的a标签
    Product_Link = './/div[contains(@class, "ProductDetails-module__titleContainer")]//a'
    
    # --- 翻页相关 ---
    Next_Page_Clickable = '//*[local-name()="kat-pagination"]/xbotShadowRoot//span[@part="pagination-nav-right" and not(contains(@class, "end"))]'

    # --- 搜索相关 ---
    Search_text = '//*[local-name()="kat-input-group"]/div/*[local-name()="kat-input"][@type="text"]'
    Search_button = '//div[contains(@class, "searchButton")]'
    
    # --- 商品详情页相关 ---
    # 购物车按钮
    Add_To_Cart_Button = '//input[@id="add-to-cart-button"]'
    # 立即购买按钮
    Buy_Now_Button = '//input[@type="submit"][@name="submit.buy-now"]'
    # 商品标题
    Product_Title = '//span[@id="productTitle"]'
    # 最大购买数量输入框或下拉菜单
    Max_Quantity_Input = '//input[@id="quantity"]'
    Max_Quantity_Select = '//select[@id="quantity"]'
    # 价格相关
    Price_Container = '//span[contains(@class, "a-price")]'
    # 列表价格（List Price）
    List_Price = '//span[contains(@class, "a-price") and contains(@data-a-color, "base")]'
    # 价格列表
    Price_List = '//span[contains(@class, "basisPrice")]//span[contains(@class, "a-price")]/span[@aria-hidden="true"]'
    # Regular Price按钮（用于从Prime Price切换到Regular Price）
    Regular_Price_Button = '//div[contains(@class, "accordion-header")][.//span[contains(text(), "Regular Price")]]//i[contains(@class, "a-accordion-radio")]'

class Element:
    next_page = create_selector(Xpath.Next_Page_Clickable, name='下一页')
    product_rows = create_frame(Xpath.Product_Rows, name='数据')
    search_text = create_selector(Xpath.Search_text, name='搜索框')
    search_button = create_selector(Xpath.Search_button, name='搜索按钮')
    # 商品详情页元素
    add_to_cart_button = create_selector(Xpath.Add_To_Cart_Button, name='购物车按钮')
    buy_now_button = create_selector(Xpath.Buy_Now_Button, name='立即购买按钮')



# 3. 页面进入与校验

def to_page_if_needed(web_page: WebBrowser, url: str):

    # 如果当前页面已经是目标页面，直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
    ):
        return
    # 如果不是，则导航到目标URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)


# 4. 数据抓取函数


def search_asin_and_get_links(web_page: WebBrowser, asin: str) -> list:
    product_list = []
    
    try:
        # 1. 输入ASIN
        print(f"正在搜索 ASIN: {asin}")
        search_input = web_page.find(Element.search_text, timeout=10)
        search_input.click()
        sleep(0.5)
        search_input.clipboard_input(asin)
        sleep(1)
        
        # 2. 点击搜索按钮
        search_button = web_page.find(Element.search_button, timeout=5)
        search_button.click()
        
        # 3. 等待页面加载完成
        web_page.wait_load_completed(timeout=20)
        sleep(4)  # 等待页面加载完成后，再等待3-5秒确保数据加载完成
        
        # 4. 获取第一条产品行（一个ASIN只对应一个链接，可能有多个SKU，只取第一条即可）
        try:
            product_rows = web_page.find_all_by_xpath(Xpath.Product_Rows, timeout=5)
            
            if not product_rows:
                print(f"搜索 ASIN {asin} 未找到任何产品行")
                return product_list
            
            # 只获取第一条结果
            first_row = product_rows[0]
            try:
                # 提取产品链接
                link_element = first_row.find_by_xpath(Xpath.Product_Link, timeout=2)
                url = link_element.get_attribute('href')
                
                if url:
                    product_list.append({
                        'asin': asin,
                        'url': url
                    })
                    print(f"成功提取 -> ASIN: {asin}, URL: {url}")
                else:
                    print(f"警告：未找到产品链接")
                    
            except Exception as e:
                print(f"提取第一条产品链接时出错: {e}")
                
        except Exception as e:
            print(f"获取产品行列表时发生错误: {e}")
        
    except Exception as e:
        print(f"搜索 ASIN {asin} 时发生错误: {e}")
    
    return product_list


def get_all_product_links(web_page: WebBrowser, asin_list: list) -> list:
    #获取所有链接
    all_products = []
    
    for index, asin in enumerate(asin_list):
        print(f"=== 处理第 {index + 1}/{len(asin_list)} 个ASIN: {asin} ===")
        
        # 搜索并获取链接
        products = search_asin_and_get_links(web_page, asin)
        all_products.extend(products)
    
    print(f"=== 所有ASIN处理完成，共获取 {len(all_products)} 个产品链接 ===")
    return all_products



# 5. 商品页面操作函数

def process_product_pages(web_page: WebBrowser, products_list: list, max_quantity: int = 5) -> list:

    # 在新页面中打开所有产品链接并执行商品检查

    check_results = []
    
    # 创建新页面用于处理商品页面
    product_page = None
    try:
        print("\n--- 正在打开新页面用于商品页面检查 ---")
        product_page = xbot.web.create('about:blank', mode=web_page.product_name, load_timeout=20)
        
        for index, product in enumerate(products_list):
            print(f"\n正在检查第 {index + 1}/{len(products_list)} 个商品, ASIN: {product['asin']}")
            
            # 初始化当前商品的检查结果
            product_result = {
                "asin": product['asin'],
                "url": product['url'],
                "max_quantity_abnormal": False,  # 最大购买数量是否异常（不匹配为异常）
                "cart_abnormal": False,  # 购物车是否异常（不显示为异常）
                "list_price_abnormal": False,  # 列表价格是否异常（不显示为异常）
                "title_length_abnormal": False,  # 标题字符数是否异常（小于198个字符为异常）
                "check_status": "失败",
                "error": ""
            }
            
            # 重试机制
            max_retries = 3
            navigation_success = False
            
            for attempt in range(1, max_retries + 1):
                try:
                    print(f"正在处理{product['url']}")
                    product_page.navigate(product['url'], load_timeout=60)
                    handler_container(product_page)
                    navigation_success = True
                    break
                except Exception as nav_error:
                    if attempt < max_retries:
                        print(f"  导航失败，重试 {attempt}/{max_retries}...")
                        sleep(3)
                    else:
                        error_msg = f"导航失败: {str(nav_error)}"
                        print(f"  错误：{error_msg}")
                        product_result["error"] = error_msg
                        check_results.append(product_result)
                        navigation_success = False
            
            if not navigation_success:
                continue
            
            try:
                # 等待页面加载
                sleep(2)
                product_page = xbot.web.get_active(mode = 'auto')
                
                # ========== 0. 检查是否为Prime Price，如果是则点击Regular Price按钮 ==========
                try:
                    regular_price_button = product_page.find_by_xpath(Xpath.Regular_Price_Button, timeout=3)
                    if regular_price_button:
                        print(f"  检测到Prime Price，正在切换到Regular Price...")
                        regular_price_button.click()
                        sleep(2)  # 等待切换完成
                        product_page.wait_load_completed(timeout=10)
                        print(f"  ✓ 已切换到Regular Price")
                except Exception:
                    # 如果找不到Regular Price按钮，说明已经是Regular Price或没有Prime Price选项
                    pass
                
                # ========== 1. 检查最大购买数量是否匹配用户传入的值 ==========
                try:
                    actual_max_quantity = 0
                    # 先尝试从input输入框获取
                    try:
                        max_quantity_input = product_page.find_by_xpath(Xpath.Max_Quantity_Input, timeout=2)
                        max_quantity_value = max_quantity_input.get_attribute('max') or max_quantity_input.get_attribute('value')
                        if max_quantity_value:
                            actual_max_quantity = int(max_quantity_value)
                    except:
                        # 如果input找不到，尝试从select下拉菜单获取
                        try:
                            max_quantity_select = product_page.find_by_xpath(Xpath.Max_Quantity_Select, timeout=2)
                            options = max_quantity_select.find_all_by_xpath('.//option')
                            if options:
                                # 获取最后一个option的值（通常是最大值）
                                last_option = options[-1]
                                max_quantity_value = last_option.get_attribute('value')
                                if max_quantity_value:
                                    actual_max_quantity = int(max_quantity_value)
                        except:
                            pass
                    
                    if actual_max_quantity > 0:
                        # 不匹配为异常
                        product_result["max_quantity_abnormal"] = (actual_max_quantity != max_quantity)
                        print(f"  ✓ 最大购买数量：{actual_max_quantity} ({'异常(不匹配)' if product_result['max_quantity_abnormal'] else '正常(匹配)'}用户传入值: {max_quantity})")
                    else:
                        # 未找到也视为异常
                        product_result["max_quantity_abnormal"] = True
                        print(f"  ✗ 未找到最大购买数量（异常）")
                except Exception as e:
                    print(f"  ✗ 检查最大购买数量失败: {e}")
                    product_result["error"] += f"最大购买数量检查失败: {str(e)}; "
                
                # ========== 2. 检查购物车是否显示 ==========
                try:
                    cart_displayed = product_page.is_element_displayed(Element.add_to_cart_button)
                    # 不显示为异常
                    product_result["cart_abnormal"] = not cart_displayed
                    print(f"  ✓ 购物车：{'异常(未显示)' if product_result['cart_abnormal'] else '正常(显示)'}")
                except Exception as e:
                    # 检查失败也视为异常
                    product_result["cart_abnormal"] = True
                    print(f"  ✗ 检查购物车失败（异常）: {e}")
                    product_result["error"] += f"购物车检查失败: {str(e)}; "
                
                # ========== 3. 检查列表价格是否显示 ==========
                try:
                    price_elements = product_page.find_all_by_xpath(Xpath.Price_List, timeout=3)
                    list_price_displayed = len(price_elements) > 0
                    # 不显示为异常
                    product_result["list_price_abnormal"] = not list_price_displayed
                    if list_price_displayed:
                        price_texts = [elem.get_text().strip() for elem in price_elements if elem.get_text().strip()]
                        print(f"  ✓ 列表价格：正常(显示) ({price_texts[0] if price_texts else ''})")
                    else:
                        print(f"  ✗ 列表价格：异常(未显示)")
                except Exception as e:
                    # 检查失败也视为异常
                    product_result["list_price_abnormal"] = True
                    print(f"  ✗ 检查列表价格失败（异常）: {e}")
                    product_result["error"] += f"列表价格检查失败: {str(e)}; "
                
                # ========== 4. 检查标题字符数量是否异常（小于198个字符为异常） ==========
                try:
                    title_element = product_page.find_by_xpath(Xpath.Product_Title, timeout=3)
                    title = title_element.get_text().strip()
                    title_length = len(title)
                    # 小于198个字符为异常
                    product_result["title_length_abnormal"] = title_length < 198
                    print(f"  ✓ 商品标题：{title[:50]}... (长度: {title_length}, {'异常(小于198字符)' if product_result['title_length_abnormal'] else '正常(大于等于198字符)'})")
                except Exception as e:
                    # 提取失败也视为异常
                    product_result["title_length_abnormal"] = True
                    print(f"  ✗ 提取商品标题失败（异常）: {e}")
                    product_result["error"] += f"标题提取失败: {str(e)}; "
                
                # 标记为成功
                product_result["check_status"] = "成功"
                print(f"  ✓ ASIN {product['asin']} 检查完成")
                
            except Exception as e:
                error_msg = f"页面操作错误: {str(e)}"
                print(f"  ✗ 错误：{error_msg}")
                product_result["error"] = error_msg
                product_result["check_status"] = "失败"
            
            check_results.append(product_result)
                
    finally:
        # 确保关闭新打开的页面
        if product_page:
            print("\n--- 商品页面检查完成，正在关闭处理页面 ---")
            product_page.close()
    
    # 统计结果
    success_count = sum(1 for r in check_results if r["check_status"] == "成功")
    abnormal_count = sum(1 for r in check_results if any([
        r.get("max_quantity_abnormal", False),
        r.get("cart_abnormal", False),
        r.get("list_price_abnormal", False),
        r.get("title_length_abnormal", False)
    ]))
    
    print(f"\n=== 检查完成：总计 {len(check_results)} 个，成功 {success_count} 个，有异常 {abnormal_count} 个 ===")
    
    # 返回列表格式，方便后续流程处理成通知内容
    return check_results



# 6. 业务流程

def process_method(web_page: WebBrowser, asin_list: list, max_quantity: int = 5) -> list:
  
    #主业务流程：进入库存页面，搜索ASIN列表，获取所有产品链接，然后在商品页面执行检查


    # 步骤1: 进入库存管理页面
    domain = get_domain(web_page)
    url = f"{domain}/myinventory/inventory"
    to_page_if_needed(web_page, url)
    switch_language(web_page, 'zh_CN')
    sleep(2)
    
    # 步骤2: 等待页面加载完成
    web_page.wait_load_completed(timeout=20)
    
    # 步骤3: 遍历ASIN列表，搜索并获取所有产品链接
    if not asin_list:
        print("ASIN列表为空，流程结束")
        return []
    
    all_products = get_all_product_links(web_page, asin_list)
    
    if not all_products:
        print("未能获取任何产品链接，流程结束")
        return []
    
    # 步骤4: 在商品页面执行检查操作
    check_results = process_product_pages(web_page, all_products, max_quantity)
    
    return check_results



def test_run():
    """
    测试函数：用于本地调试
    """
    if "xbot_extensions" in __file__:
        return

    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="superbrowser")
    
    test_asin_list = ["B0FZV3B139", "B08XYZ1234","B0FY22QL54","B0FPMGVRDC"]  
    
    result_dict = process_method(web_page, test_asin_list)
    print(f"\n=== 测试结果 ===")
    print(result_dict)
    
    exit()


def main(args):

    test_run()
    
    web_page = args.get("web_page")
    asin_list = args.get("ASIN列表", [])
    max_quantity = args.get("最大购买数量", 5)  # 默认值为5
    
    if not asin_list:
        print("警告：未提供ASIN列表")
        args["data"] = []
        return
    
    result_list = process_method(web_page, asin_list, max_quantity)
    args["data"] = result_list


