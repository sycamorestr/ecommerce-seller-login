# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,win32, web
from .import package
from .package import variables as glv



from ._amazon_api import login
from . import process34 as upload_post

class XPaths:
    login_btn = '''//input[@id="signInSubmit"]'''  # 店铺登录按钮
    # //*[@id="auth-signin-button"]
    auth_btn = '''//input[@id="auth-signin-button"]'''  # 二次验证提交验证码按钮
    auth_input = '''//input[@id="auth-mfa-otpcode"]'''  # 二次验证验证码输入框
    # auth_select = '''//*[@id="auth-select-device-form"]'''       # 二次验证选择，出现这个元素表示用户没有配置二次验证，直接抛出异常
    continue_btn = '''(//*[@aria-labelledby="continue-announce"])[1]'''
    auth_select = '''//*[@id="guide-component"]'''  # 二次验证选择，出现这个元素表示用户没有配置二次验证，直接抛出异常
    select_user = '''(//div[@action="/ap/switchaccount"]//*[@class="a-row"])[1]'''  # 选择用户页面，第一个用户，需要选择后才会出现登录按钮
    # home = '''//*[@id="sc-logo-asset"]'''                                                                                               # 主页元素
    home = '''//*[@id="partner-switcher"]'''  # 主页元素
    campaign_home = '''//header[@role="presentation" or @id="topBar"]'''  # 广告页的主页元素
    kat_tabs = '''//kat-tabs'''  # 导航标签元素
    reports = '''//kat-tab[@tab-id="REPORTS_REPOSITORY"]'''  # 报告库标签页
    partner_switcher = '''//*[@id="partner-switcher"]'''  # 打开站点列表按钮
    current_site = '''//*[@id="partner-switcher" and @data-marketplace_selection="{}"]'''  # 当前站点
    site_switcher_list = '''(//*[@id="partner-switcher"]//div[@class="scrollable-content"])[1]//ul[@class="merchant-level"]/li/a'''  # 站点列表
    site_switcher_first = '''(//*[@id="partner-switcher"]//div[@class="scrollable-content"]//ul[@class="merchant-level"]/li[1]/a)[1]'''  # 第一个站点
    send_code_radio = '''//input[contains(@value, "TOTP")]'''  # 发送验证码单选框
    auth_send_code = '''//*[@id="auth-send-code"]'''  # 确认发送验证码

    LogIn = '(//strong[.="Log in"])[1]'

    ## 全局切换站点页面
    switch_accounts_button = '//*[@class="picker-footer-buttons"]//*[@class="picker-switch-accounts-button"]'
    picker_name = '(//*[@class="picker-view-column"][last()]//*[@class="picker-name"])[1]'

    ## 广告页切换站点
    current_site_ad = '//button[contains(text(), "国家/地区：")]'
    site_switcher_list_ad = '//*[contains(@for, "aac-chrome-select-list-")]'
    site_switcher_first_ad = '(//*[contains(@for, "aac-chrome-select-list-")])[1]'
    change_country_btn = '//*[@id="aac-chrome-change-country-button"]'

    ## 切换语言
    language = '''//div[@data-test-tag="nav-locale-button"]'''  # 当前语言元素
    language_first = '''(//div[@data-test-tag="nav-locale-button"]//a[@class="locale-list-item"])[1]'''  # 可切换语言列表的第一个元素
    # target_language = '''//div[@data-test-tag="nav-locale-button"]//a[@data-test-tag="locale-list-item-{}"]'''                          # 当前要切换的语言元素
    target_language = '''//div[@data-test-tag="nav-locale-button"]//a[contains(@data-test-tag, "locale-list-item-{}")]'''  # 当前要切换的语言元素

    ## 广告页切换语言
    setting_ad = '''//button[@data-takt-id="aac-user-name-dropdown"]'''  # 广告页设置
    language_ad = '''//button[@name="aac-select-language"]'''  # 当前语言元素(广告页)
    language_first_ad = '''(//*[@id="LanguageSwitcher"]//button[@role="option"])[1]'''  # 可切换语言列表的第一个元素(广告页)
    target_language_ad = '''//*[@id="LanguageSwitcher"]//button[@value="{}"]'''  # 当前要切换的语言元素(广告页)
    language_switch_btn = '''//button[@data-takt-id="aac-language-switch-btn"]'''  # 更改语言按钮


def test_upload_post():
    post_url = "https://advertising.amazon.com/brand-content-manager/profiles/d09ce62e-5bb0-4524-b9cf-6eb9c0afed78"
    file_path = r"C:\Users\Administrator\Desktop\G1.jpg"
    title = "TwoTwo"
    asin_list = ["B08FHS3537", "B0BGMJDBFT"]
    start_time = "2024-02-29 07:00"
    end_time = None
    web_page = xbot.web.get_active(mode="chrome")
    upload_post(web_page, post_url, file_path, title, asin_list, start_time, end_time)

def test_xpath():
    xpath_map = {
        "login_btn": XPaths.login_btn,
        "auth_input": XPaths.auth_input,
        "home": XPaths.home,
        "campaign_home": XPaths.campaign_home,
        "auth_select": XPaths.auth_select,
        "select_user": XPaths.select_user,
        "send_code_radio": XPaths.send_code_radio,
        "log_in": XPaths.LogIn,
        "continue_btn": XPaths.continue_btn
    }    
    print(" | ".join(xpath_map.values()))

def main(args):
    # test_xpath()
    web_page = web.get_active(mode='superbrowser')
    web_page.find_by_xpath('//*[@id="publisher:create-post:caption-input"]').click()
