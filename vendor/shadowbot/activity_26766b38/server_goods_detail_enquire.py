# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv

def select(web_page, xpath, keyword):
    lis = web_page.find_all_by_xpath(xpath)
    for li in lis:
        if li.get_text() == keyword and li.is_displayed():
            li.click()
            break

def set_options(web_page, ww_group, customer_ww, splite_flow, buier_ww, goods_id, enquiry_status, file_folder, file_name):
    if '/qos/service/frame' not in web_page.get_url():
        web_page.navigate('https://sycm.taobao.com/qos/service/frame/performance/detail/new#/detail')
    
    xpath = "//*[text()='商品明细']"
    web_page.find_by_xpath(xpath).click()
    
    if ww_group !='':
        xpath = "//span[text()='旺旺分组']//following-sibling::span"
        web_page.find_by_xpath(xpath).click()
        xpaths = "//ul[contains(@class,'ant-select-dropdown-menu')]/li"
        select(web_page, xpaths, ww_group)

    if customer_ww!='':
        xpath = "//span[text()='分组分流']//following-sibling::span"
        web_page.find_by_xpath(xpath).click()
        xpaths = "//ul[contains(@class,'ant-select-dropdown-menu')]/li"
        select(web_page, xpaths, customer_ww)

    if splite_flow!='':
        xpath = "//span[text()='客服旺旺']//following-sibling::span"
        web_page.find_by_xpath(xpath).click()
        xpaths = "//ul[contains(@class,'ant-select-dropdown-menu')]/li"
        select(web_page, xpaths, splite_flow)

    if buier_ww!='':
        test_xpath = "//span[text()='买家旺旺']//following-sibling::span//input"
        web_page.find_by_xpath(test_xpath).input(buier_ww)

    if goods_id!='':
        xpath = "//span[text()='商品ID或名称者']//following-sibling::span//input"
        web_page.find_by_xpath(xpath).input(goods_id)

    if enquiry_status!='': 
        xpath = "//span[text()='咨询状态']//following-sibling::span"
        web_page.find_by_xpath(xpath).click()
        xpaths = "//ul[contains(@class,'ant-select-dropdown-menu')]/li"
        select(web_page, xpaths, enquiry_status)

    web_page.find_by_xpath("//span[text()='下载']").click()
    web.handle_save_dialog(file_folder=file_folder, file_name=file_name, mode='chrome')
    
def main(args):
    web_page = args.get('web_page')
    ww_group = args.get('ww_group','全部')
    splite_flow = args.get('splite_flow','全部')
    customer_ww = args.get('customer_ww','全部')
    buier_ww = args.get('buier_ww','')
    goods_id = args.get('goods_id', '')
    enquiry_status = args.get('enquiry_status', '全部')
    file_folder = args.get('file_folder')
    file_name = args.get('file_name')

    # web_page = web.get_active(mode='chrome')

    set_options(web_page, ww_group, customer_ww, splite_flow, buier_ww, goods_id, enquiry_status, file_folder, file_name)
    args['save_path'] = file_folder + '//' + file_name