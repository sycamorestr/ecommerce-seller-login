# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import re
import math

import xbot
from xbot import print, sleep, web
from xbot.app import databook
from lxml import html, etree

from .import package
from .package import variables as glv
from .utils import Tools


def traffic_analysis_collection(web_page: any, date_time: str, need_rating=False):
    """进行流量分析的数据采集"""

    # 获取网站域名
    url = web_page.get_url()
    if 'main/flux-analysis-full' not in url:
        domain_url = Tools.get_domain_from_url(url)
        web_page.navigate(f'{domain_url}/main/flux-analysis-full')

    #创建返回的数据列表
    return_data = []

    # 消除弹窗
    Tools.handle_info(web_page)

    # 点击时间
    web_page.find_by_xpath(f'//div[text()="{date_time}"]').click()

    # 等待数据加载完毕
    Tools.wait_loading(web_page, appear_time=1)

    try:
        # 判断店铺是否有数据
        non_text = web_page.find_by_xpath('//div[contains(@class,"TB_emptyData")]', timeout=3).get_text()
        if non_text == '暂无数据':
            print('该店铺没有数据')
            return []
    except:
        pass

    # 点击条数 每页显示100条
    select_num_xpath = '//li[contains(@class,"PGT_sizeChanger")]//div[@data-testid="beast-core-select-header"]'
    # 点击所选数量
    num_xpath = f'//ul[contains(@class,"ST_dropdownPanel")]/li/span[text()="100"]'

    web_page.find_by_xpath(select_num_xpath).click()
    web_page.find_by_xpath(num_xpath).click()

    # 获取总共的商品数量
    goods_num_xpath = '//li[contains(@class,"PGT_totalText")]'
    goods_num_text = web_page.find_by_xpath(goods_num_xpath).get_text()
    # 通过正则去获取数字
    goods_num = re.search(r'(\d+)',goods_num_text).group(1)

    # 判断商品页数, 向上取整 例如 21条数据 则返回page为1  101条数据 则返回page为2  
    page = math.ceil(int(goods_num) / 100)

    # 当page > 1 时 进行换页操作
    # 进行循环获取数据
    for p in range(page):

        # 等待数据加载完毕
        Tools.wait_loading(web_page, appear_time=1)

        # 2. 整张表 outerHTML 只抓 1 次
        table_xpath = '//table[.//tr[@data-testid="beast-core-table-body-tr"]]'
        table_list_sel = web_page.find_all_by_xpath(table_xpath)
        table_elem = [_ for _ in table_list_sel if _.get_bounding(to96dpi=False)[2] != 0][0]
        table_html = table_elem.get_attribute('outerHTML')
        doc  = html.fromstring(table_html)
        rows = doc.xpath('.//tr[@data-testid="beast-core-table-body-tr"]')

        # 3. 本地 lxml 一次性解析
        for tr in rows:
            tds = tr.xpath('./td[position()>1 and position()<last()]')
            if not tds:
                continue
            td_text = ''.join(tds[0].itertext()).strip()
            introduction = re.search(r'vertical;}(.*?)\s*类目', td_text, re.S).group(1)
            category     = re.search(r'类目：\s*(.*?)\s*SPU ID',  td_text, re.S).group(1)
            spu_id       = re.search(r'SPU ID：\s*(\d+)',       td_text, re.S).group(1)

            body = []
            for td in tds[1:]:
                if need_rating is True:
                    text = ' '.join(td.itertext()).strip()
                    svg  = td.xpath('.//div[contains(@class,"compare-show")]/svg/@data-testid')
                    if svg:
                        if 'up' in svg[0]:
                            text += ' up'
                        elif 'down' in svg[0]:
                            text += ' down'
                else:
                    text = ' '.join(td.itertext()).strip().split('较')[0]
                body.append(text)

            # 将第一列的数据与其他数进行拼接 
            body.insert(0, introduction)
            body.insert(1, category)
            body.insert(2, spu_id)
            # body.insert(3, tag_group)

            return_data.append(body)
            # 将数据添加到数据表格中
            xbot.app.databook.append_row(body)

        # 4. 翻页（非最后一页）
        if page > 1 and p != page - 1:
            web_page.find_by_xpath('//li[@data-testid="beast-core-pagination-next"]').click()

    print(return_data)
    return return_data

def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return

    web_page = web.get_active(mode="superbrowser")
    date_type = '昨日'
    traffic_analysis_collection(web_page, date_type)
    exit()

def main(args):
    test()
    
    # 设置表头
    title = [
        '商品简介',
        '商品类目',
        'SPU ID',
        '流量情况-曝光量',
        '流量情况-点击量',
        '流量情况-访客量',
        '流量情况-浏览量',
        '流量情况-加购人数',
        '流量情况-收藏人数',
        '支付情况-支付件数',
        '支付情况-支付订单数',
        '支付情况-买家数',
        '转化情况-转化率',
        '转化情况-点击率',
        '转化情况-点击后支付率',
        '探索数据-曝光量',
        '搜索数据-点击量',
        '搜索数据-支付订单数',
        '搜索数据-支付件数',
        '推荐数据-曝光量',
        '推荐数据-点击量',
        '推荐数据-支付订单数',
        '推荐数据-支付件数',
        '增长潜力'
    ]

    web_page = args.get('web_page')
    date_time = args.get('date_time', '昨日')
    need_rating = args.get('need_rating')

    # 将表头插入到表格中
    row_count = databook.get_row_count()
    if row_count == 0:
        databook.set_row(1, title, begin_column_name="A")
    
    data = traffic_analysis_collection(web_page, date_time)
    args["data"] = [title] + data
