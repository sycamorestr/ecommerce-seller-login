# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement
import json
from xbot import excel, web
from .activities_utils import scroll_and_load


class Xpath:
    # 与此商品相关的产品轮播卡片
    RelateProductCard = '(//*[@id="sp_detail"]//ol)//li'
    # 与此商品相关的产品轮播总页数
    RelateProductPages = '//*[@id="sp_detail_heading"]//span[contains(@class, "page-max")]'
    # 与此商品相关的产品轮播下一页按钮
    RelateProductNextBtn = '//*[@id="sp_detail"]//a[contains(@class, "nextpage")]'
    # 与此商品相关的产品URL
    RelateProductUrl = '(//*[@id="sp_detail"]//ol)//li//*[@role="heading"]/a'
    # 与此商品相关的产品数据详情
    RelateProductDeail = '(//*[@id="sp_detail"]//ol)//li/div[contains(@id, "sp_detail")]'
    # 与此商品相关的产品星级
    RelateProductStar = '(//*[@id="sp_detail"]//ol)//li//div[3]/a'


def get_competitor_info(file_path: str, timeout: int=300):
    work_book = excel.open(file_name=file_path, kind='auto_check')
    work_sheet = work_book.get_active_sheet()
    total_rows = work_sheet.get_row_count()
    # 遍历输入文件中每行
    for row in range(2, total_rows+1):
        row_content_list = work_sheet.get_row(row_num=row, using_text=True) # 获取输入文件中行内容
        raw_product_asin = row_content_list[0] # 获取原商品的asin
        raw_product_url = row_content_list[1] # 获取原商品的url
        work_asin_sheet = work_book.create_sheet(name=raw_product_asin, create_way='last') # 根据原商品的asin创建sheet页，用来存放该原商品的竞品信息
        work_asin_sheet.append_row(values=['原始ASIN', '竞品URL', '竞品ASIN', '竞品图片', '竞品星级'])

        # 打开原商品所在的网页url
        web_page = web.get_active(mode='auto')
        if raw_product_url != '':
            web_page.navigate(url=raw_product_url, load_timeout=60)
        else:
            web_page.navigate(url='https://www.amazon.com/dp/' + raw_product_asin, load_timeout=60)
        scroll_and_load(web_page) # 滚动屏幕触发页面加载
        
        try:
            total_card_pages = int(web_page.find_by_xpath(Xpath.RelateProductPages).get_text()) # 获取与此商品相关的产品轮播总页数
        except:
            work_sheet.set_cell(row_num=row, col_name='C', value='未找到竞品广告信息')
            continue
        for _ in range(total_card_pages): # 遍历并获取每页的轮播卡片产品信息
            # 获取亚马逊商品的广告竞品信息
            for _ in range(timeout):
                # 获取与此商品相关的产品URL
                product_url_list = ["https://www.amazon.com/" + item.get_attribute('href') for item in web_page.find_all_by_xpath(Xpath.RelateProductUrl)]
                # 获取与此商品相关的产品数据详情
                product_detail_list = [json.loads(item.get_attribute('data-adfeedbackdetails')) for item in web_page.find_all_by_xpath(Xpath.RelateProductDeail)]
                # 获取与此商品相关的产品asin
                product_asin_list = [item.get("asin") for item in product_detail_list]
                # 获取与此商品相关的产品图片
                product_picture_list = [item.get("adCreativeImage").get("highResolutionImages")[0].get("url") for item in product_detail_list]
                # 获取与此商品相关的产品星级
                product_star_list = [item.get_attribute('aria-label') for item in web_page.find_all_by_xpath(Xpath.RelateProductStar)]
                # 如果轮播卡片页面数据有未加载出来，等待轮播卡片页面数据加载
                if '' not in product_url_list and '' not in product_detail_list and '' not in product_star_list:
                    break
                else:
                    sleep(6)
            
            # 获取与此商品相关的产品轮播卡片个数
            card_num = len(web_page.find_all_by_xpath(Xpath.RelateProductCard))
            for card_index in range(card_num): # 遍历轮播卡片，将产品信息写入对应的ASIN页sheet
                # 将产品信息写入对应的ASIN页sheet
                work_asin_sheet.append_row(values=[raw_product_asin, product_url_list[card_index], product_asin_list[card_index], product_picture_list[card_index], product_star_list[card_index]])

            web_page.find_by_xpath(Xpath.RelateProductNextBtn).click() # 点击与此商品相关的产品轮播下一页按钮
        work_sheet.set_cell(row_num=row, col_name='C', value='已采集竞品广告信息')
    work_book.save()
    work_book.close()


def test_get_competitor_info():
    if "xbot_extensions" in __file__:
        return
    
    # web_page = xbot.web.get_active(mode="edge")
    file_path = r"C:\Users\10577\Desktop\test\test13.xlsx" # 输入文件路径

    get_competitor_info(file_path)
    exit()


def main(args):
    # 测试代码入口
    test_get_competitor_info()
