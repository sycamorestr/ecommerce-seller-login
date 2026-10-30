# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .switch_old_ul import switch_old_ui

def run(web_page):
    switch_old_ui(web_page)
    sleep(3)
    # site_name_xpath = "//button[@class='partner-dropdown-button']//span"
    site_name_xpath = "//div[@class='dropdown-account-switcher-header']"
    # site_name = web_page.find_by_xpath(site_name_xpath, timeout=3).get_text().split("|")[1]
    site_name = web_page.find_by_xpath(site_name_xpath, timeout=3).get_text().split("\n")[0]
    # total_balance_xpath = "//div[@id='KpiCardList']//div[@data-priority='3']"
    total_balance_xpath = "//*[@id='KPI_CARD_MESSAGES_V2']"
    web_page.find_by_xpath(total_balance_xpath,timeout=4).click()
    countries_name = web_page.find_all('countries_name')
    need_reply = web_page.find('need_reply').get_text()
    unresolved = web_page.find('unresolved').get_text()
    need_reply_value_list = web_page.find_all('need_reply_value')
    unresolved_value_list = web_page.find_all('unresolved_value')

    info_dict = {}
    data_dict = {}
    info_dict['current_site'] = site_name
    for i in range(len(countries_name)):
        value_dict = {}
        value_dict[need_reply] = need_reply_value_list[i].get_text()
        value_dict[unresolved] = unresolved_value_list[i].get_text()
        data_dict[countries_name[i].get_text()] = value_dict
    info_dict["current_site"] = site_name
    info_dict["data"] = data_dict
    return info_dict


def main(args):
    web_page = args.get('web_page')
    # web_page = xbot.web.get_active(mode="superbrowser")
    info_dict = run(web_page)
    # print(info_dict)
    args['info'] = info_dict
    