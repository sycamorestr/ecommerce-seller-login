# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import re
import math
import xbot  # type: ignore
from xbot import print, sleep, web  # type: ignore
from xbot.app import databook  # type: ignore
from lxml import html  # type: ignore
from . import package  # type: ignore
from .package import variables as glv
from .utils import Tools
from xbot_extensions.web_action.select_date import select_date  # type: ignore
from xbot.selector import Selector

def gen_selector(xpath):
    xpaths = xpath.split(">>")
    data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': xpaths}}
    selector = Selector(data)
    return selector


def get_data(web_page: xbot.web.WebBrowser, page_key: str):

    # 跳转页面
    Tools.check_target_web(web_page, "stock/fully-mgt/sale-manage/main")

    if len(web_page.find_all_by_xpath("//*[text()='暂无数据']", timeout=5)) > 0:
        return []

    web_page.find_by_xpath(
        "//*[text()='每页']//following-sibling::div[@data-testid='beast-core-select']"
    ).click()

    # 设置每页的数量
    elems = web_page.find_all_by_xpath("//li//*[text()='40']")
    for elem in elems:
        if elem.is_displayed():
            elem.click()
            break

    flag_selector = gen_selector('//div[text()="加载中"]')
    if web_page.wait_appear(flag_selector, timeout=3):
        web_page.wait_disappear(flag_selector, timeout=5) 
    # 处理仅有一页的场景, 将页码赋值为 2
    max_page = web_page.find_by_xpath("//ul/li[contains(@class,'totalText')]").get_text()
    max_page_num = re.search(r'\d+', max_page)
    if max_page_num:
        max_page_num = max_page_num.group()

    if max_page_num == 0:
        print('该店铺销售管理没有数据')
        return 
    
    # 点击今日（用 JS 点击避免被页面数据遮挡）
    click_today_script = """
        function (element, input) {
            element.click();
        }
    """
    web_page.find_by_xpath('//thead/tr//span[text()="今日"]').execute_javascript(click_today_script)
    # 等待数据加载完毕
    Tools.wait_loading(web_page, appear_time=1)
    
    # 获取翻页数量
    page_num = math.ceil( int(max_page_num) / 40)

    # 获取当前店铺名称
    store_name = web_page.find_by_xpath(
        "//div[contains(@class,'account-info_accountInfo')]/div[2]/div/span/span"
    ).get_text()

    return_data = []  # 指令返回的数据

    def _td_text(td_el):
        """从 lxml 元素获取文本，等价于 get_text()"""
        return ''.join(td_el.itertext()).strip()

    for page in range(int(page_num)):
        # 等待数据加载后，获取表格 outerHTML，用 lxml 解析
        table_xpath = "//table[.//tbody/tr]"
        table_list_sel = web_page.find_all_by_xpath(table_xpath)
        table_elem = [_ for _ in table_list_sel if _.get_bounding(to96dpi=False)[2] != 0][0]
        table_html = table_elem.get_attribute('outerHTML')
        doc = html.fromstring(table_html)
        trs = doc.xpath('//tbody/tr')

        temp_row_data = []  # 用于处理合并单元格的情况
        for index, tr in enumerate(trs):
            row_data = []
            tds = tr.xpath('./td')  # 找当前页的所有 td

            # 跳过合计这一行
            if any("合计" in _td_text(td) for td in tds):
                continue

            if len(tds) > 26:
                title_el = tds[1].xpath('.//span[contains(@class,"main_productName")]')
                title = _td_text(title_el[0]) if title_el else ''
                skc_el = tds[1].xpath(".//div[contains(@class, 'main_productInfo')]//p[contains(., 'SKC：')]")
                skc = _td_text(skc_el[0]).replace('SKC：', '') if skc_el else ''
                spu_el = tds[1].xpath(".//div[contains(@class, 'main_productInfo')]//p[contains(., 'SPU：')]")
                spu = _td_text(spu_el[0]).replace('SPU：', '') if spu_el else ''
                join_time_el = tds[1].xpath(".//div[contains(@class, 'main_productInfo')]//p[contains(., '加入站点时长：')]")
                join_time = _td_text(join_time_el[0]).replace('\\n', '') if spu_el else ''

                # 获取 sku 与备货仓租
                sku_el = tds[2].xpath('.//*[contains(@class,"main_subLine") and contains(.,"SKU ID：")]')
                sku_text = _td_text(sku_el[0]) if sku_el else ''
                sku_id = re.search(r'\d+', sku_text).group() if re.search(r'\d+', sku_text) else ''

                # 获取货号
                item_num_el = tds[2].xpath('.//*[contains(@class,"main_subLine") and contains(.,"SKU货号：")]')
                item_num = _td_text(item_num_el[0]) if item_num_el else ''

                # 获取备货仓组
                stock_group_el = tds[2].xpath('.//*[contains(@class,"main_subLine")]/*[contains(.,"备货仓组")]/..')
                stock_group_text = _td_text(stock_group_el[0]) if stock_group_el else ''
                stock_group = stock_group_text.split('：')[1].strip() if '：' in stock_group_text else ''

                # 获取 SKC 图片链接（tds[1] 下 img 的 src 属性）
                img_srcs = tds[1].xpath('.//img/@src')
                skc_img_src = img_srcs[0] if img_srcs else ''

                tds_data = [_td_text(td) for td in tds[3:-2]]

                row_data.insert(0, store_name)
                row_data.append(title)
                row_data.append(item_num)
                row_data.append(sku_id)
                row_data.append(stock_group)
                row_data.extend(tds_data)
                row_data.append(skc)
                row_data.append(spu)
                row_data.append(skc_img_src)
                row_data.append(join_time)
                temp_row_data = row_data

            elif len(tds) == 26:
                row_prefix = temp_row_data[:2]  # 取当前行前2列数据

                # 获取 sku 与备货仓租
                sku_el = tds[0].xpath('.//*[contains(@class,"main_subLine") and contains(.,"SKU ID：")]')
                sku_text = _td_text(sku_el[0]) if sku_el else ''
                sku = re.search(r'\d+', sku_text).group() if re.search(r'\d+', sku_text) else ''

                # 获取货号
                item_num_el = tds[0].xpath('.//*[contains(@class,"main_subLine") and contains(.,"SKU货号：")]')
                item_num = _td_text(item_num_el[0]) if item_num_el else ''

                # 获取备货仓组
                stock_group_el = tds[0].xpath('.//*[contains(@class,"main_subLine")]/*[contains(.,"备货仓组")]/..')
                stock_group_text = _td_text(stock_group_el[0]) if stock_group_el else ''
                stock_group = stock_group_text.split('：')[1].strip() if '：' in stock_group_text else ''

                tds_data = [_td_text(td) for td in tds[1:-1]]
                # 末尾四列：SKC、SPU、SKC图片链接、 加入站点天数（与上一行同商品）
                row_data = row_prefix + tds_data + temp_row_data[-4:]
                row_data.insert(2, item_num)
                row_data.insert(3, sku)
                row_data.insert(4, stock_group)
                temp_row_data = row_data

            else:
                row_prefix = temp_row_data[:2]  # 取当前行前两列数据
                tds_data = [_td_text(td) for td in tds[:-1]]
                # 末尾四列：SKC、SPU、SKC图片链接、 加入站点天数（与上一行同商品）
                row_data = row_prefix + tds_data + temp_row_data[-4:]
                row_data.insert(5, temp_row_data[5])
                row_data.insert(6, temp_row_data[6])
                row_data.insert(7, temp_row_data[7])
                row_data.insert(9, temp_row_data[9])
                row_data.insert(10, temp_row_data[10])
                row_data.insert(11, temp_row_data[11])
                row_data.insert(15, temp_row_data[15])

            return_data.append(row_data)
            xbot.app.databook.append_row(row_data)

        # 获取前几页的判断
        if page_key != '':
            if int(page + 1) == int(page_key) or int(page_key) == 0:
                break

        # 如果不是最后一页，执行翻页操作
        if page < page_num - 1 and page_num > 1:  # 最后一页不需要翻页
            try:
                # 点击翻页
                next_page_xpath = "//ul/li[last()]"
                next_page_list = web_page.find_all_by_xpath(next_page_xpath)
                next_page_sel = [_ for _ in next_page_list if _.get_bounding(to96dpi=False)[2] != 0][0] 
                next_page_sel.click()
     
                # 等待翻页完成
                flag_selector = gen_selector('//div[text()="加载中"]')
                if web_page.wait_appear(flag_selector, timeout=3):
                    web_page.wait_disappear(flag_selector, timeout=5) 
            except Exception as e:
                print(f"翻页失败: {e}")
                break

    return return_data


def main(args):
    
    title = [
        "TEMU店铺名称",
        "商品信息",
        "SKU信息",
        'sku_id',
        "备货仓组",
        "申报价格(CNY)",
        "开款价格状态",
        "缺货数量",
        "近7日用户加购数量",
        "用户累计加购数量",
        "已订阅待提醒到货",
        "今日",
        "近7天",
        "近30天",
        "仓内可用库存",
        "仓内预占用库存",
        "仓内暂不可用库存",
        "已发货库存",
        "已创建备货单待发货库存",
        "待审核备货库存",
        "仓内实物库存",
        "建议目标库存天数",
        "建议目标库存",
        "建议生产/采购量",
        "备货逻辑",
        "建议备货量",
        "库存可售天数",
        "仓内库存可售天数",
        "可售天数",
        "SKC", 
        "SPU",
        "SKC图片链接",
        "加入站点时长"
    ]

    web_page = args.get("web_page")
    page_key = args.get('page_key') or ''
    # databook.clear()

    row_count = databook.get_row_count()
    if row_count == 0:
        databook.set_row(1, title, begin_column_name="A")

    data = get_data(web_page, page_key)
    
    print(data)
    args["data"] = [title] + data
