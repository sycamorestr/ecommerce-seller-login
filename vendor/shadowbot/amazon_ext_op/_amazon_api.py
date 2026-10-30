from ._amazon_core import *
from . import _amazon_core_beta



def login(web_page):
    # amazon.login(web_page)
    _amazon_core_beta.login(web_page)


def switch_site(web_page, site_name):
    # amazon.switch_site(web_page, site_name)
    _amazon_core_beta.switch_site(web_page, site_name)


def switch_language(web_page, language):
    amazon.switch_language(web_page, language)


def switch_language_on_ad_page(web_page, language):
    amazon.switch_language_on_ad_page(web_page, language)



def main(args):
    web_page = xbot.web.get_active(mode="superbrowser")  
    # web_page.reload(load_timeout=0)
    # web_page = xbot.web.get_active(mode="firefox")  
    # web_page = xbot.web.get_active(mode="superbrowser")
    # web_page = xbot.web.get_active(mode="chrome") 

    # web_page.find_by_xpath('''//*[contains(@class, 'partner-switcher')]''').click()
    web_page.find_by_xpath("//*[contains(@class, 'partner-switcher')]", timeout=3).click()
    # web_page.find_by_xpath('''//*[@id="partner-switcher" or contains(@class, 'partner-switcher')]//div[contains(@class,'list-item-label')]''').click()
    # web_page.find_by_xpath(f'''//*[contains(@class, 'partner-switcher')]//div[contains(text(),'Spain')]''').click()
    a = web_page.find_by_xpath('''//*[contains(@class, 'partner-switcher')]''').get_html()
    web_page.find_by_xpath("//div[@class='dropdown-account-switcher-list']//div[@class='dropdown-account-switcher-list-item'][1]").click()
    print(a)
    # switch_site(web_page, "美国")   
    # amazon.switch_site_ad(web_page, "加拿大")
    # amazon.switch_site(web_page, "Brazil")
    pass
