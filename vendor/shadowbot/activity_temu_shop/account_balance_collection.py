# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
from datetime import datetime

import xbot
from xbot import print, sleep, web
from xbot.selector import Selector
from .import package
from .package import variables as glv


def gen_selector(xpath):
    # 判断xpath是否存在
    data = {
        "id": "ifream-xpath",
        "name": "ifream-xpath",
        "type": "simple",
        "xpath": {"enable": "true", "segments": [xpath]},
    }
    return Selector(data)


def account_balance_collection(web_page):
    """资金中心-账户余额数据采集"""

    # 判断是否在目标网页，进行跳转
    traget_url = 'https://seller.kuajingmaihuo.com/labor/account'

    # 轮询两次，进行跳转
    if web_page.get_url() != traget_url:
        for _ in range(2):
            try:
                web_page.navigate(traget_url)
                break
            except Exception as e:
                continue
        else:
            raise Exception('网页加载失败')

    for _ in range(3):
        # 等待数据列表出现
        data_list_xpath = '//div[contains(@class,"dashboard-wrapper_baseInfo")]'
        data_list_sel = gen_selector(data_list_xpath)
        try:
             if web_page.wait_appear(data_list_sel, timeout=20):
                break
        except:
            continue
    
    # 进行点击贷款账户，用于应用中适配智能屏蔽弹窗以及自动处理弹窗指令
    web_page.find_by_xpath('//span[text()="货款账户"]').click()

    # 创建数据字典
    data_dict = {}

    # 获取当前时间,年/月/日
    current_time = datetime.now().strftime('%Y/%m/%d')

    # 获取店铺名称
    shop_name_xpath = '(//span[@data-testid="beast-core-ellipsis"])[1]'
    shop_name = web_page.find_by_xpath(shop_name_xpath).get_text()
    data_dict['店铺名称'] = shop_name

    # 获取账户币种
    account_currency_xpath = '//span[contains(@class,"account_blockTipFontSize")]'
    account_currency = web_page.find_by_xpath(account_currency_xpath).get_text()

    # 进行切割文本
    account_currency_title = account_currency.split('：')[0]
    account_currency_info = account_currency.split('：')[1]
    data_dict[account_currency_title] = account_currency_info

    # 获取账户数据列表元素
    account_data_list_xpath = '//div[contains(@class,"dashboard-wrapper_baseInfo")]/div'
    account_data_list_ele = web_page.find_all_by_xpath(account_data_list_xpath, timeout=0)

    # 对列表中的元素进行循环
    for i,account_data_ele in enumerate(account_data_list_ele):

        # 获取金额名称
        money_title_xpath = './/div[contains(@class,"dashboard-item_titleWrapper")]/span[1]'
        money_title = account_data_ele.find_by_xpath(money_title_xpath).get_text()

        # 获取金额数值
        money_number_xpath = './/div[contains(@class,"number-tip_wrapper")]'
        money_number = account_data_ele.find_by_xpath(money_number_xpath).get_text().replace('\n','')

        # 添加数据到字典中
        data_dict[money_title] = money_number

        if i == 2:
            # 获取预留额度元素
            reserved_quota_title_xpath = './/div[contains(@class,"mall-depositLimit-amount")]/div/span'
            reversed_quota_number_xpath = './/div[contains(@class,"mall-depositLimit-amount")]/div/div'
            
            try:
                # 获取预留额度信息
                reserved_quota_title = account_data_ele.find_by_xpath(reserved_quota_title_xpath, timeout=0.5).get_text()
                reversed_quota_number = account_data_ele.find_by_xpath(reversed_quota_number_xpath, timeout=0.5).get_text()

                # 将数据添加到字典中
                data_dict[reserved_quota_title] = reversed_quota_number
            except:
                pass

    # 将时间添加入字典中
    data_dict['采集时间'] = current_time
    return data_dict


def test():
    """测试功能"""
    if "xbot_extensions" in __file__:
        return
    
    web_page = web.get_active(mode='chrome')
    data = account_balance_collection(web_page)
    print(data)
    exit()
    

def main(args):
    # 测试模块
    test()

    # 功能模块
    web_page = args.get('web_page')
    data = account_balance_collection(web_page)
    args['输出结果'] = data