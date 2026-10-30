# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from . import package
from .package import variables as glv
from xbot import web
from .utils import check_enterprise


def get_financial_summary(web_page: xbot.web.WebBrowser) -> dict:
    """获取资金汇总信息并返回结构化数据
    :param web_page: xbot.web.WebBrowser, 待操作的网页对象
    :return: dict, 包含资金信息的字典
    """
    url = 'https://csp.aliexpress.com/m_apps/fund-center/popFundCenter?channelId=210070#/home/settleRecord'
    current_url = web_page.get_url()
    
    if current_url != url:
        web_page.navigate(url)
        sleep(4)  # 等待页面加载
    
    result = {
        '账户总额': {},
        '冻结金额': {},
        '待结算金额': {},
        '待平台付款金额': {},
        '本月放款金额': {},
        '欠费金额': {}
    }

    # 获取账户总额和冻结金额
    sleep(2)
    account_xpath = '//div[contains(@class, "account")]//div[contains(@class, "aep-card-content")]/div/div/div/div[contains(@class, "ait-col")]'
    account_groups = web_page.find_all_by_xpath(account_xpath)
    
    for item in account_groups:
        item_text = item.get_text()
        lines = [line.strip() for line in item_text.split('\n') if line.strip()]
        
        if len(lines) >= 3:  # 标题 + CNY + USD
            title = lines[0]
            if title in ['账户总额', '冻结金额']:
                for i in range(1, len(lines)):
                    parts = lines[i].split()
                    if len(parts) >= 2:
                        currency = parts[0]
                        amount = ' '.join(parts[1:])
                        result[title][currency] = amount

    # 获取结算概览信息的数据
    settlement_xpath = '//div[contains(@class, "ait-col")][contains(@class, "ait-col-5")]'
    settlement_groups = web_page.find_all_by_xpath(settlement_xpath)
    
    for item in settlement_groups:
        item_text = item.get_text()
        lines = [line.strip() for line in item_text.split('\n') if line.strip()]
        
        if len(lines) >= 7:  # 标题 + 6个数据行
            title = lines[0]
            if title in ['待结算金额', '待平台付款金额', '本月放款金额', '欠费金额']:
                regions = ['全球', '非俄罗斯', '俄罗斯']
                
                # CNY 数据（前3行）
                cny_values = lines[1:4]
                result[title]['CNY'] = dict(zip(regions, cny_values))
                
                # USD 数据（后3行）
                usd_values = lines[4:7]
                result[title]['USD'] = dict(zip(regions, usd_values))
    
    return result,web_page


def test_financial_summary():
    """测试资金汇总信息获取功能"""
    if "xbot_extensions" in __file__:
        return
    
    url = 'https://csp.aliexpress.com/m_apps/fund-center/popFundCenter?channelId=210070#/home/settleRecord'
    web_page = web.create(url, mode='chrome')
    account_information = get_financial_summary(web_page)
    print(account_information)
    web_page.close()
    exit()


def main(args):
    # 测试功能
    test_financial_summary()

    check_enterprise()

    # 获取参数
    web_page = args.get('web_page')
    
    # 调用主函数获取资金信息
    account_information,web_page = get_financial_summary(web_page)
    
    # 设置返回值
    args['account_information'] = account_information
    args['web_page'] = web_page
   