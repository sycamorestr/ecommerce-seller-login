# 模板
import xbot
from xbot import print, sleep
from xbot.web import WebBrowser
from xbot.selector import Selector
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector

# --- 1. 定义所有需要用到的 XPath 路径 ---
class Xpath:
    # --- 定价状况页面 (主列表页) ---
    Load_More_Button = '//*[local-name()="kat-button"][contains(@class, "Pagination-module_secondary-button") and not(@disabled)]'
    Product_Cells = '//kat-table-cell[.//div[@id="consolidated-product-details"]]'
    Product_Link = './/kat-link'
    ASIN_Container = './/div[@id="consolidated-product-details-asin"]'
    SKU_Container = './/div[@id="consolidated-product-details-sku"]'
    # --- 商品详情页 ---
    Add_To_Cart_Button = '//input[@id="add-to-cart-button"]'
    Buy_Now_Button = '//input[@type="submit"][@name="submit.buy-now"]'
    Join_Prime = '//div[@id="primeSavingsUpsell-signup-link"]//input[@type="submit"]'

# --- 2. 构建所有需要用到的元素 ---
class Element:
    load_more_button = create_selector(Xpath.Load_More_Button, name='加载更多')
    add_to_cart_button = create_selector(Xpath.Add_To_Cart_Button, name='购物车按钮')
    buy_now_button = create_selector(Xpath.Buy_Now_Button, name='立即购买按钮')
    join_prime = create_selector(Xpath.Join_Prime,name = '加入会员')
def to_page_if_needed(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标页面，直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
    ):
        return
    # 如果不是，则导航到目标URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)

def get_product_data(web_page: WebBrowser) -> list:

    product_list = []

    try:
        product_cells = web_page.find_all_by_xpath(Xpath.Product_Cells, timeout=4)
        print(f"在当前页面找到 {len(product_cells)} 个产品，开始提取...")

        # 2. 遍历每一个单元格
        for cell in product_cells:
            try:
                # 提取 URL
                link_element = cell.find_by_xpath(Xpath.Product_Link)
                url = link_element.get_attribute('href')

                # 提取包含 ASIN
                asin_container_element = cell.find_by_xpath(Xpath.ASIN_Container)
                full_asin_text = asin_container_element.get_text().strip()
                asin = full_asin_text.split('：')[1].strip()

                # 提取包含 SKU
                sku_container_element = cell.find_by_xpath(Xpath.SKU_Container)
                full_sku_text = sku_container_element.get_text().strip()
                sku = full_sku_text.split('：')[1].strip()

                if url and asin and sku:
                    product_list.append({
                        'asin': asin,
                        'sku': sku,
                        'url': url
                    })
                    print(f"成功提取 -> ASIN: {asin}, SKU: {sku}, URL: {url}")

            except Exception as e:
                print(f"处理某个单元格时出错，跳过。错误: {e}")
                continue

    except Exception as e:
        print(f"未找到任何产品单元格，流程结束。错误: {e}")

    print(f"---获取{len(product_list)} 个产品的信息 ---")
    return product_list


# 检查商品按钮 (最终优化版)
def check_buy_box_on_products(web_page: WebBrowser, products_list: list) -> dict:
    """
    第二阶段：循环处理。
    打开一个新页面来执行所有检查，避免影响原后台页面。
    """
    final_results = {
        "asins_with_issues": [], # 用于存储按钮不完整的 ASIN
        "processing_errors": []   # 用于存储处理过程中出错的 ASIN
    }
    
    # --- 核心优化点：在新函数开头创建一个专用于检查的新页面 ---
    check_page = None  # 先初始化为空
    try:
        print("--- 阶段二：正在打开一个新页面用于商品检查 ---")
        # 创建一个空白的新页面，后续所有检查都在这个页面上进行
        check_page = xbot.web.create('about:blank', mode = web_page.product_name,load_timeout=20)
        
        for index, product in enumerate(products_list):
            print(f"正在处理第 {index + 1}/{len(products_list)} 个商品, ASIN: {product['asin']}")

            # 增加重试机制
            max_retries = 3
            navigation_success = False

            for attempt in range(1, max_retries + 1):
                try:
                    # 尝试导航
                    check_page.navigate(product['url'], load_timeout=30)
                    handler_container(check_page)
                    navigation_success = True
                    break 
                except Exception as nav_error:
                    if attempt < max_retries:
                        sleep(3) 
                    else:
                        print(f"  > 错误：处理 ASIN {product['asin']} 时重试三次仍出现错误，请人工处理: {nav_error}")

            # 如果 3 次都失败了，记录错误并跳过当前商品
            if not navigation_success:
                final_results["processing_errors"].append({
                    'asin': product['asin'],
                    'sku': product['sku']
                })
                continue

            try:
                # 1. 在【新页面 check_page】上导航到商品详情页
                # check_page.navigate(product['url'],load_timeout = 20)
                sleep(1)
                # 2. 在【新页面 check_page】上分别检查两个按钮是否可见
                # is_add_to_cart_visible = check_page.is_element_displayed(Element.add_to_cart_button)
                is_buy_now_visible = check_page.is_element_displayed(Element.buy_now_button)
                is_join_prime = check_page.is_element_displayed(Element.join_prime)

                # # 3. 判断两个按钮是否【同时】可见
                # if is_add_to_cart_visible and is_buy_now_visible:
                #     # 正常情况：两个都可见
                #     pass
                # else:
                #     # 异常情况：至少有一个不可见或不存在
                #     final_results["asins_with_issues"].append(product['asin'])
                # 新逻辑：首先判断是否为 Join Prime 如果是 Join Prime，则不进行丢购判断，默认 未丢购。
                # 如果没有 Join Prime，则判断是否存在 Buy NOW:·无 Buy Now:判定为 丢购。
                if is_join_prime:
                    #join prime 存在
                    pass
                else:
                    if not is_buy_now_visible:
                        final_results["asins_with_issues"].append({
                            'asin': product['asin'],
                            'sku': product['sku']
                        })
                            
            except Exception as e:
                print(f"  > 错误：处理 ASIN {product['asin']} 时发生页面导航或其他错误: {e}")
                final_results["processing_errors"].append({
                    'asin': product['asin'],
                    'sku': product['sku']
                })
                continue
    
    finally:
        # --- 核心优化点：无论流程是否出错，最后都确保关闭新打开的页面 ---
        if check_page:
            print("--- 检查完成，正在关闭检查页面 ---")
            check_page.close()
    print(f"--- 找到 {len(final_results['asins_with_issues'])} 个按钮不完整的商品 ---")
    print(f"--- 有 {len(final_results['processing_errors'])} 个商品在处理时出错 ---")
    return final_results


# --- 4. 整体业务流程 ---
def process_method(web_page: WebBrowser) -> list:
    # 步骤1: 准备目标URL并确保在目标页面
    domain = get_domain(web_page)
    url = f"{domain}/pricing/health" 
    to_page_if_needed(web_page, url)
    switch_language(web_page, 'zh_CN')
    sleep(3)

    #步骤 1 ： 点击更多 ，将所有元素加载完毕
    while True:
        try:
            #加载更多按钮
            load_more_button = web_page.find(Element.load_more_button, timeout=5)
            load_more_button.click()
            sleep(3) # 等待新数据加载
        except Exception:
            # 如果找不到可点击的按钮 (因为它被 disabled 或消失了)，循环结束
            print("未找到可点击的'加载更多'按钮，数据已全部加载。")
            break
    #  步骤2: 执行第一阶段，收集所有商品信息
    products_to_check = get_product_data(web_page)
    
    if not products_to_check:
        print("未能收集到任何商品信息，流程结束。")
        return {"asins_with_issues": [], "processing_errors": []}

    #步骤3: 执行第二阶段，检查商品
    result_dict = check_buy_box_on_products(web_page, products_to_check)
    
    return result_dict


# --- 5. 测试入口 ---
def test_run():
    if "xbot_extensions" in __file__:
        return

    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    final_asins = process_method(web_page)
    print(final_asins)
    # check_page = xbot.web.create('about:blank', mode = web_page.product_name,load_timeout=20)
    exit()

def main(args):
    test_run() 
    web_page = args.get("web_page")
    result_list = process_method(web_page)
    args["data"] = result_list