# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import select_click,get_domain, handler_container
from xbot_extensions.web_action.select_date import select_date
from .activities_utils import download_handler


def configure(web_page, account_type, translation_type, translation_status, start_time, end_time, file_fold, file_name, wait_time):
    disabled = 'false'
    #账户类型选择
    disabled_xpath = '//kat-dropdown[@value="PAYABLE"]'
    disabled_sel = web_page.find_all_by_xpath(disabled_xpath, timeout=3)
    if len(disabled_sel) > 0:
        disabled = disabled_sel[0].get_attribute('disabled')
    if disabled == 'true':
        if account_type != "标准订单":
            raise Exception('账户类型错误')
    else:
        web_page.find("translation_view_account").click()
        translation_view_account_list = web_page.find_all("translation_view_account_list",timeout = 3)
        keyword_list = ['所有账户类型', '标准订单', '发票支付订单']
        if len(translation_view_account_list) > 0:
            select_click(account_type, keyword_list, translation_view_account_list)

    #交易类型选择
    web_page.find("translation_type").click()
    translation_type_list = web_page.find_all("translation_type_list",timeout = 3)
    keyword_list = ['所有交易类型', '临时付款', '订单付款', '退款', 
                    '信用卡拒付退款', '清算', '清仓盘点', '亚马逊商城交易保障退款',
                     '服务费用', '亚马逊 Easy Ship 费用', '通过亚马逊购买的配送服务', 
                     '付款至亚马逊', 'Receivables Adjustments', '自动贷款还款', '传递费用', 
                     '其他', '结转金额', '上一 结算周期中的未转账金额', '未转账金额', '库存赔偿', 'Amazon Shipping']
    if len(translation_type_list) > 0:
        select_click(translation_type, keyword_list, translation_type_list)

    #交易状态选择选择
    if len(web_page.find_all('translation_status', timeout=3)) > 0:
        web_page.find("translation_status").click()
        translation_status_list = web_page.find_all("translation_status_list",timeout = 3)
        keyword_list = ['所有交易状态', '已发放的交易', '延期交易']
        if len(translation_status_list) > 0:
            select_click(translation_status, keyword_list, translation_status_list)

    #日期选择
    web_page.find("translation_view_starttime").click()
    time_body = web_page.find("translation_view_date_body")
    select_date(web_page, time_body, start_time, '')
    web_page.find("translation_view_endtime").click()
    time_body = web_page.find("translation_view_date_body")
    select_date(web_page, time_body, end_time, '')

    #点击请求报告
    web_page.find("translation_type_updata").click()
    
    #验证是否可下载
    for retry in range(100):
        try:
            web_page.find("translation_tyoe_download_mark",timeout=2)
            break
        except:
            web_page.find("translation_tyoe_download_mark").click()
            continue
    web_page.find("translation_tyoe_download_mark").click()  
    
    file_path = download_handler(web_page, file_fold, file_name, wait_time)

def to_page_if_needed(web_page, url: str):
    # 如果当前页面已经是目标页面，直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
    ):
        return
    # 如果不是，则导航到目标URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)

def run(web_page, account_type, translation_type, translation_status, start_time, end_time, file_fold, file_name,wait_time):
    domain = get_domain(web_page)
    url = f"{domain}/payments/event/view"
    to_page_if_needed(web_page,url)
    configure(web_page, account_type, translation_type, translation_status, start_time, end_time, file_fold, file_name,wait_time)
    return file_fold + '\\' + file_name


def main(args):
    web_page = args.get("web_page")
    account_type = args.get("account_type",'所有账户类型')
    translation_type = args.get('translation_type','所有交易类型')
    translation_status = args.get('translation_status','所有交易状态')
    start_time = args.get('start_time','2025-10-10')
    end_time = args.get("end_time",'2025-10-20')
    file_fold = args.get("file_fold", r"C:\Users\58204\Desktop")
    file_name = args.get("file_name", r"test.csv")
    wait_time = args.get('wait_time') or ''
    file_path = run(web_page, account_type, translation_type, translation_status, start_time, end_time, file_fold, file_name, wait_time)
    args["file_path"] = file_path
