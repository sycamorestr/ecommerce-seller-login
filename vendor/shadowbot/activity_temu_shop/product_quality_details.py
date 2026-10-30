# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import re

import xbot
from xbot import print, sleep
from xbot.app import databook

from .import package
from .package import variables as glv
from .utils import Tools


def product_quality_details(web_page):
    """商品品质分数据获取"""
    
    # 判断网页是否在目标页面
    Tools.check_target_web(web_page, 'main/quality/dashboard')

    return_data = []

    # 等待数据加载完毕
    Tools.wait_loading(web_page)

    # 消除信息框
    Tools.handle_info(web_page)

    # 获取品质分数量信息
    quality_grand_Eles = web_page.find_all_by_xpath('//div[contains(@class,"tab-item_count")]')
    for quality_grand_ele in quality_grand_Eles:

        # 获取品质分
        quality_grand = quality_grand_ele.get_text()
        quality_grand = re.search(r'(\d+)', quality_grand, re.S).group(1)

        # 若品质分不为0则获取数据
        if quality_grand != '0':
            quality_grand_ele.click()

            # 等待数据加载完毕
            Tools.gen_selector(web_page)

            # 获取当前的显示页码
            current_num_xpath = '//ul[@data-testid="beast-core-pagination"]//input[@placeholder]'
            current_num = web_page.find_by_xpath(current_num_xpath).get_attribute('value')

            if '40' not in current_num:

                # 切换页码为40
                page_frame_xpath = '//ul[@data-testid="beast-core-pagination"]//input[@placeholder]'
                web_page.find_by_xpath(page_frame_xpath).click()

                # 点击40
                page_num_xpath = '//ul[@role="listbox"]//span[text()="40"]'
                web_page.find_by_xpath(page_num_xpath).click()

                # 等待数据加载完毕
                Tools.wait_loading(web_page)

            while True:

                # 进行数据抓取
                # 获取所有的tr
                trs = web_page.find_all_by_xpath('//tbody/tr')
                trs_display = [_ for _ in trs if _.get_bounding(to96dpi=False)[2] != 0]
                
                # 循环每行，获取每列信息
                for tr in trs_display:

                    row_data = []
                    # 获取所有td
                    tds = tr.find_all_by_xpath('./td')
                
                    # 获取商品信息
                    shop_info = tds[0].find_by_xpath('./div').get_text()

                    # 分割商品简介
                    shop_introduction = re.search(r'\s*(.*?)\s*类目', shop_info, re.S).group(1)

                    # 获取商品类目
                    shop_category = re.search(r'类目：\s*(.*?)\s*SPU', shop_info, re.S).group(1)

                    # 获取SPU ID
                    SPU_ID = re.search('SPU：\s*(\d+)', shop_info, re.S).group(1)

                    # 获取剩下的信息
                    row_data = [td.get_text() for td in tds[1:]]

                    # 将商品信息添加到row_data中
                    row_data.insert(0, shop_introduction)
                    row_data.insert(1, shop_category)
                    row_data.insert(2, SPU_ID)

                    # 将row_data中的数据添加到return_data中
                    return_data.append(row_data)
                    # 将数据添加到数据表格中
                    xbot.app.databook.append_row(row_data)
                
                # 进行换页操作
                next_page_xpath = '//li[@data-testid="beast-core-pagination-next"]'
                next_page_sel = Tools.gen_selector(next_page_xpath)
                if web_page.wait_appear(next_page_sel, timeout=1):
                    next_page_class = web_page.find_by_xpath(next_page_xpath).get_attribute('class')
                    if 'disabled' not in next_page_class:
                        web_page.find_by_xpath(next_page_xpath).click()
                        quality_grand_ele.click()
                        continue
                    else:
                        break
                break

    print(return_data)
    return return_data
                
            
def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return 
    web_page = xbot.web.get_active(mode='superbrowser')

    product_quality_details(web_page)
    exit()


def main(args):
    # 测试模块
    test()

    title = [
        "商品简介",
        "类目",
        "SPU_ID",
        "品质分",
        "主要品质问题-售后问题",
        "主要品质问题-负向评价类型",
        "建议优化方案",
        "售后情况-品质售后率",
        "售后情况-品质售后次数",
        "售后情况-尺码售后率",
        "售后情况-尺码售后次数",
        "用户评价情况-评价数",
        "用户评价情况-评价均分",
        "用户评价情况-合身情况",
        "用户评价情况-负向评价关键词"
    ]
    # 功能模块
    web_page = args.get('web_page')

    # 将表头插入到表格中
    row_count = databook.get_row_count()
    if row_count == 0:
        databook.set_row(1, title, begin_column_name="A")

    data = product_quality_details(web_page)
    args['data'] = data