# 模板
import random
from datetime import time
import xbot
import re
from xbot import print, sleep
from xbot.web import WebBrowser
from xbot.selector import Selector
from lxml import html
from .utils import get_domain
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector
from datetime import datetime


# 所有元素Xpath路径
class Xpath:
    CustomQuote = '//*[@id="CUSTOM_QUOTE"]'
    MarketplaceQuote = '//*[@id="MARKETPLACE_QUOTE"]'
    ShopList = '//table/tbody/tr'
    NoData = '//*[contains(@class,"emptyTableString")]'
    PageSelect = '//*[contains(@class,"paginationSize")]'
    NextPage = '//ul[@class="a-pagination"]/li[contains(@class,"a-last")]'
    NewGoodsDown = '//kat-dropdown[@class="cqeFilterDropdown"]'
    NewGoods = '//*[@value="REQUEST_NEW"]'
    Unavail  = '//*[contains(@id,"marketplaceunavail")]'
    SiteName = '//*[contains(@class,"dropdown-account-switcher")]//span[contains(@class,"account-switcher-header-label-regional")]'
    SecondarySiteDwon = '//kat-dropdown[contains(@id,"merchant-marketplace")]'
    SecondarySite = '//kat-option[@value="{}"]'
# 构建二级站点映射
class mapping:
    map_dic ={
        '英国':'A2HQDPEY5U351R_A1F83G8C2ARO7P',
        '德国':'A2HQDPEY5U351R_A1PA6795UKMFR9',
        '法国':'A2HQDPEY5U351R_A13V1IB3VIYZZH',
        '意大利':'A2HQDPEY5U351R_APJ6JRA9NG5V4',
        '西班牙':'A2HQDPEY5U351R_A1RKKUPIHCS9HS',
        '美国':'A2XKE81PYMCHT4_ATVPDKIKX0DER',
    }

# 构建所有需要用到的元素
class Element:
    no_data = create_selector(Xpath.NoData ,name = '无数据')
    new_goods = create_selector(Xpath.NewGoodsDown,Xpath.NewGoods, name='新品')
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

    # if not web_page.wait_appear(Element.basket_product, timeout=5):
    #     raise Exception(
    #         f"进入管理报价页面失败"
    #     )


def get_first_asin(web_page, cust2):
    """
    获取当前表格第一页数据中的第一条“请求的 ASIN”。

    用途：
    点击下一页后，页面可能因为网络波动没有立刻刷新。
    此时如果马上解析表格，拿到的仍然是上一页数据。
    所以用当前页第一条 ASIN 作为页面是否刷新的参考值。
    """
    table_html = web_page.find_by_xpath('//table').get_attribute('outerHTML')
    doc = html.fromstring(table_html)
    rows = doc.xpath('.//tbody/tr')

    if not rows:
        return ''

    row = rows[0]
    quote_ASIN_sel = row.xpath(f'./td[{cust2}]//span[contains(text(),"请求的 ASIN")]/..')

    if quote_ASIN_sel:
        quote_text = ''.join(quote_ASIN_sel[0].itertext()).strip()
        if ':' in quote_text:
            return quote_text.split(':', 1)[1].strip()

    return ''


#数据获取
def quotes_Data(web_page: WebBrowser, quote_type='自定义报价请求'):
    
    # 判断市场是否可用
    unavailable_market = web_page.find_all_by_xpath(Xpath.Unavail, timeout=3)
    if len(unavailable_market) > 0:
        xbot.logging.warning("当前店铺的站点管理价格市场不可用")
        return []
    
    # 获取当前站点的中文名称
    site_name = web_page.find_by_xpath(Xpath.SiteName).get_text()
    try:
        site_value = mapping.map_dic[site_name]
    except:
        xbot.logging.warning(f'当前指令中未包含 {site_name} 站点的二级站点值，如有需要，请联系官方人员进行添加')

    if site_value:
        # 进行判断当前页面的二级站点是否与一级站点一致
        Secondary_site_value = web_page.find_by_xpath(Xpath.SecondarySiteDwon).get_attribute('value')
        if Secondary_site_value != site_value:
            try:
                # 值不相同说明站点不一致，进行切换
                web_page.find_by_xpath(Xpath.SecondarySiteDwon).click()
                # 进行切换操作
                web_page.find_by_xpath(Xpath.SecondarySite.format(site_value)).click()
            except:
                expanded = web_page.find_by_xpath(Xpath.SecondarySiteDwon).get_all_attributes()
                if 'expanded' in expanded.get_keys():
                    web_page.find_by_xpath(Xpath.SecondarySiteDwon).click()

    # 进行点击对应的tab获取数据操作
    if quote_type == '自定义报价请求':
        web_page.find_by_xpath(Xpath.CustomQuote).click()
        cust1 = 1
        cust2 = 1
        sleep(3)
    else:
        web_page.find_by_xpath(Xpath.MarketplaceQuote).click()
        cust1 = 2
        cust2 = 2
        sleep(3)
    cust2= cust2 + 2

    #新增 无数据直接返回空字典
    has_data = web_page.wait_appear(Element.no_data,timeout = 3)
    if has_data:
        return []
    
    # 进行页面切换--切换50条数据每页
    try:
        web_page.find_by_xpath(Xpath.PageSelect, timeout=10).click()
        for _ in range(3):
            xbot.win32.send_keys('{DOWN}')
        xbot.win32.send_keys('{ENTER}')
        sleep(3)
    except:
        pass

    if quote_type == '自定义报价请求':
        # 进行过滤报价状态
        web_page.find_by_xpath(Xpath.NewGoodsDown).click()
        web_page.find(Element.new_goods).click()
        sleep(3)

    last_first_asin = None
    quotes_summary = []

    while True:
        # 记录当前页第一条 ASIN。
        # 后面点击“下一页”后，会用它判断页面是否真的刷新成功。
        old_first_asin = get_first_asin(web_page, cust2)

        # 一次性获取整张表 HTML，再用 lxml 解析。
        # 这样比逐个 Selenium / Web 元素读取快，也能减少页面动态变化带来的干扰。
        table_html = web_page.find_by_xpath('//table').get_attribute('outerHTML')
        doc = html.fromstring(table_html)
        rows = doc.xpath('.//tbody/tr')

        for idx, row in enumerate(rows):
            # 报价截止时间：取指定 td 下所有 span 文本并拼接
            td_over_time = row.xpath(f'./td[{cust1}]//span')
            over_time = ' '.join(
                [''.join(span.itertext()).strip() for span in td_over_time]
            ).strip()

            # ASIN 信息都在 cust2 对应列中：
            # “请求的 ASIN”和“推荐的 ASIN”分别取各自文本所在的父节点，避免只拿到标题文本。
            quote_ASIN_sel = row.xpath(f'./td[{cust2}]//span[contains(text(),"请求的 ASIN")]/..')
            recommend_ASIN_sel = row.xpath(f'./td[{cust2}]//span[contains(text(),"推荐的 ASIN")]/..')

            quote_ASIN = ''
            recommend_ASIN = ''

            # 解析“请求的 ASIN”
            if quote_ASIN_sel:
                quote_text = ''.join(quote_ASIN_sel[0].itertext()).strip()
                if ':' in quote_text:
                    quote_ASIN = quote_text.split(':', 1)[1].strip()

            # 解析“推荐的 ASIN”
            if recommend_ASIN_sel:
                recommend_text = ''.join(recommend_ASIN_sel[0].itertext()).strip()
                if ':' in recommend_text:
                    recommend_ASIN = recommend_text.split(':', 1)[1].strip()

            # 保存到返回结果中
            quotes_summary.append({
                '报价截止日期': over_time,
                '请求的 ASIN': quote_ASIN,
                '推荐的 ASIN': recommend_ASIN
            })

            # 同步写入影刀数据表
            xbot.app.databook.append_row([over_time, quote_ASIN, recommend_ASIN])

        # 当前页处理完后，判断是否还有下一页
        next_page = web_page.find_by_xpath(Xpath.NextPage)

        if 'disabled' in next_page.get_attribute('class'):
            return quotes_summary

        next_page.click()

        # 点击下一页后不要立刻进入下一轮解析。
        # 因为页面可能还没刷新完成，甚至 loading 消失了但 DOM 仍然是旧数据。
        # 所以这里等待“第一页 ASIN 发生变化”，确认已经进入下一页。
        start_time = time.time()
        while True:
            sleep(1)

            new_first_asin = get_first_asin(web_page, cust2)

            # 第一条 ASIN 变了，说明页面数据已刷新，可以继续采集下一页。
            if new_first_asin and new_first_asin != old_first_asin:
                break

            # 超过 15 秒还没变化，认为翻页失败或页面卡住。
            # 这里直接返回已采集数据，避免程序无限循环。
            if time.time() - start_time > 15:
                print('点击下一页后页面长时间未刷新，停止采集，返回已采集数据')
                return quotes_summary


# 整个业务操作流程
def process_method(web_page: WebBrowser, quote_type):

    domain = get_domain(web_page)
    url = f"{domain}/business/manage-quotes"
    to_page_if_needed(web_page, url)
    switch_language(web_page, 'zh_CN')
    sleep(2)
    dataDict = quotes_Data(web_page, quote_type)
    return dataDict


def test_run():
    if "xbot_extensions" in __file__:
        return

    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="superbrowser")
    xbot.app.databook.set_row(1, ['时间', '请求的 ASIN', '推荐的 ASIN'])
    print(process_method(web_page, '自定义报价请求'))
    exit()


def main(args):
    test_run()
    web_page = args.get("web_page")
    quote_type = args.get('quote_type')
    xbot.app.databook.set_row(1, ['时间', '请求的 ASIN', '推荐的 ASIN'])
    result_dict = process_method(web_page, quote_type)
    args["data"] = result_dict


