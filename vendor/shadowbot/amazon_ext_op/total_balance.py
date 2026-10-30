# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv

def run(web_page):
    # site_name_xpath = "//button[@class='partner-dropdown-button']//span"
    site_name_xpath = "//div[@class='dropdown-account-switcher-header']"
    # site_name = web_page.find_by_xpath(site_name_xpath, timeout=3).get_text().split("|")[1]
    site_name = web_page.find_by_xpath(site_name_xpath, timeout=3).get_text().split("\n")[0]
    # total_balance_xpath = "//div[@id='KpiCardList']//div[@data-priority='3']"
    total_balance_xpath = "//*[@id='KPI_CARD_PAYMENTS']"
    # total_balance_xpath = "//div[@id='KpiCardList']//div[@data-priority='7']"
    web_page.find_by_xpath(total_balance_xpath,timeout=4).click()
    countries_name = web_page.find_all('countries_name')
    countries_balance = web_page.find_all('countries_balance')
    info_dict = {}
    info_dict['current_site'] = site_name
    for i in range(len(countries_name)):
        info_dict[countries_name[i].get_text()] = countries_balance[i].get_text()
    return info_dict


def main(args):
    web_page = args.get('web_page')
    # web_page = xbot.web.get_active(mode="superbrowser")
    info_dict = run(web_page)
    # print(info_dict)
    args['info'] = info_dict
    