# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块 

import xbot
from xbot import print, sleep
from . import package
from .package import variables as glv

import re 

from enum import Enum

from xbot_visual.web.browser import wait_load_completed

from . import utils
from .utils import find_any_one_by_xpath, print
from .utils_beta import find_by_xpath

class XPaths:
    login_btn = '''//input[@id="signInSubmit"]'''  # 店铺登录按钮
    auth_btn = '''//input[@id="auth-signin-button"]'''  # 二次验证提交验证码按钮
    auth_input = '''//input[@id="auth-mfa-otpcode"]'''  # 二次验证验证码输入框
    
    # auth_select = '''//*[@id="auth-select-device-form"]'''                                                                            # 二次验证选择，出现这个元素表示用户没有配置二次验证，直接抛出异常
    continue_btn = '''(//*[@aria-labelledby="continue-announce"])[1]'''
    auth_select = '''//*[@id="guide-component"]'''  # 二次验证选择，出现这个元素表示用户没有配置二次验证，直接抛出异常
    select_user = '''(//div[@action="/ap/switchaccount"]//*[@class="a-row"])[1]'''  # 选择用户页面，第一个用户，需要选择后才会出现登录按钮
    # home = '''//*[@id="sc-logo-asset"]'''                                                                                               # 主页元素
    home = '''//*[@id="partner-switcher"] | //*[@id="dropdown-account-switcher-container"]'''  # 主页元素
    campaign_home = '''//header[@role="presentation" or @id="topBar"]'''  # 广告页的主页元素
    kat_tabs = '''//kat-tabs'''  # 导航标签元素
    reports = '''//kat-tab[@tab-id="REPORTS_REPOSITORY"]'''  # 报告库标签页

    partner_switcher = '''//*[@id="partner-switcher"]'''  # 打开站点列表按钮
    partner_switcher_new = '''//*[contains(@class, 'partner-switcher')]'''  # 打开站点列表按钮

    current_site = '''//*[@id="partner-switcher" and @data-marketplace_selection="{}"]'''  # 当前站点
    site_switcher_list = '''(//*[@id="partner-switcher"]//div[@class="scrollable-content"])[1]//ul[@class="merchant-level"]/li/a'''  # 站点列表


    site_switcher_first = '''(//*[@id="partner-switcher" or contains(@class, 'partner-switcher')]//div[@class="scrollable-content"]//ul[@class="merchant-level"]/li[1]/a)[1]'''  # 第一个站点
    site_switcher_first_new = '''//*[@id="partner-switcher" or contains(@class, 'partner-switcher')]//div[contains(@class,'list-item-label')]''' #新页面的第一个站点
    site_switcher_first_two = '''//div[@class='dropdown-account-switcher-list']//div[@class='dropdown-account-switcher-list-item'][1]'''
    site_switcher_first_three = '''//div[@class='dropdown-account-switcher-list']//div[@class='dropdown-account-switcher-list-item'][2]'''

    send_code_radio = '''(//input[contains(@value, "TOTP")])[1]'''  # 发送验证码单选框
    auth_send_code = '''//*[@id="auth-send-code"]'''  # 确认发送验证码

    LogIn = '(//strong[.="Log in"])[1]'

    captcha_iframe = '''//*[@id="aa-challenge-whole-page-iframe"]'''  # 验证码 iframe

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
    new_seetings = '//div[@id="ngstrim-settings-dropdown"]'    # 新版页面设置按钮
    new_language = '//div[@id="ngstrim-locale-picker"]'        # 新版页面展开语言框
    language_first = '''(//div[@data-test-tag="nav-locale-button"]//a[@class="locale-list-item"])[1]'''  # 可切换语言列表的第一个元素
    # target_language = '''//div[@data-test-tag="nav-locale-button"]//a[@data-test-tag="locale-list-item-{}"]'''                          # 当前要切换的语言元素
    target_language = '''//div[@data-test-tag="nav-locale-button"]//a[contains(@data-test-tag, "locale-list-item-{}")]'''  # 当前要切换的语言元素
    new_target_language = '//div[contains(@class,"ngstrim-dropdown-submenu")]//a[contains(@data-value,"mons_sel_locale={}")]'   #  新版语言元素

    ## 广告页切换语言
    setting_ad = '''//button[@data-takt-id="header_aac-user-name-dropdown"]'''  # 广告页设置
    language_ad = '''//button[@name="aac-select-language"]'''  # 当前语言元素(广告页)
    language_first_ad = '''(//*[@id="LanguageSwitcher"]//button[@role="option"])[1]'''  # 可切换语言列表的第一个元素(广告页)
    target_language_ad = '''//*[@id="LanguageSwitcher"]//button[@value="{}"]'''  # 当前要切换的语言元素(广告页)
    language_switch_btn = '''//button[@data-takt-id="header_aac-language-switch-btn"]'''  # 更改语言按钮


class AmazonHandler:
    def __init__(self, home_url=None):
        self.home_url = home_url
        self.site_id_map = {
            "墨西哥": "A1AM78C64UM0Y8",
            "MX": "A1AM78C64UM0Y8",
            "Mexico":"A1AM78C64UM0Y8",
            "澳大利亚": "A39IBJ37TRP1C6",
            "AU": "A39IBJ37TRP1C6",
            "Australia": "A39IBJ37TRP1C6",
            "比利时": "AMEN7PMS3EDWL",
            "Belgium": "AMEN7PMS3EDWL",
            "BE": "AMEN7PMS3EDWL",
            "日本": "A1VC38T7YXB528",
            "JP": "A1VC38T7YXB528",
            "Japan": "A1VC38T7YXB528",
            "瑞典": "A2NODRKZP88ZB9",
            "SE": "A2NODRKZP88ZB9",
            "Sweden": "A2NODRKZP88ZB9",
            "加拿大": "A2EUQ1WTGCTBG2",
            "CA": "A2EUQ1WTGCTBG2",
            "Canada": "A2EUQ1WTGCTBG2",
            "英国": "A1F83G8C2ARO7P",
            "UK": "A1F83G8C2ARO7P",
            "United Kingdom":"A1F83G8C2ARO7P",
            "GB": "A1F83G8C2ARO7P",
            "美国": "ATVPDKIKX0DER",
            "US": "ATVPDKIKX0DER",
            "America":"ATVPDKIKX0DER",
            "United States": "ATVPDKIKX0DER",
            "意大利": "APJ6JRA9NG5V4",
            "IT": "APJ6JRA9NG5V4",
            "Italy": "APJ6JRA9NG5V4",
            "法国": "A13V1IB3VIYZZH",
            "FR": "A13V1IB3VIYZZH",
            "France": "A13V1IB3VIYZZH",
            "西班牙": "A1RKKUPIHCS9HS",
            "ES": "A1RKKUPIHCS9HS",
            "Spain": "A1RKKUPIHCS9HS",
            "波兰": "A1C3SOZRARQ6R3",
            "PL": "A1C3SOZRARQ6R3",
            "Poland": "A1C3SOZRARQ6R3",
            "荷兰": "A1805IZSGTT6HS",
            "NL": "A1805IZSGTT6HS",
            "Netherlands":"A1805IZSGTT6HS",
            "德国": "A1PA6795UKMFR9",
            "DE": "A1PA6795UKMFR9",
            "Germany": "A1PA6795UKMFR9",
            "阿拉伯联合酋长国": "A2VIGQ35RCS4UG",
            "AE": "A2VIGQ35RCS4UG",
            "土耳其": "A33AVAJ2PDY3EV",
            "TR": "A33AVAJ2PDY3EV",
            "Turkey": "A33AVAJ2PDY3EV",
            "巴西": "A2Q3Y263D00KWC",
            "BR": "A2Q3Y263D00KWC",
            "Brazil":"A2Q3Y263D00KWC",
            "沙特阿拉伯": "A17E79C6D8DWNP",
            "SA": "A17E79C6D8DWNP",
            "新加坡共和国": "A19VAU5U5O7RUS",
            "SG": "A19VAU5U5O7RUS",
            "Singapore":"A19VAU5U5O7RUS",
            "印度": "A21TJRUUN4KGV",
            "IN": "A21TJRUUN4KGV",
            "India":"A21TJRUUN4KGV",
            "爱尔兰":"A28R8C7NBKEWEA",
            "Ireland":"A28R8C7NBKEWEA",
            "IL":"A28R8C7NBKEWEA"
        }

    def to_home_page(self, web_page):

        # 判断是否在首页
        url = web_page.get_url()
        if re.search("https?://sellercentral.+?amazon.+?(?=/)", url):
            return
        try:
            domain = utils.get_domain(web_page)
        except:
            domain = self.home_url
            if domain is None:
                raise
        web_page.navigate(domain, load_timeout=100)


    def login(self, web_page, pre_msg="亚马逊商家后台登录失败", ):
        """亚马逊登录操作，只点击登录和二次验证码验证提交按钮"""
        retry_time = 0
        last_name = None  # 上一次元素名
        error_msg = None
        if 'signin' not in web_page.get_url():
            return
        while retry_time < 10:
            retry_time += 1
            name, auth_ele = None, None
            try:
                error_msg = None
                try:
                    web_page.wait_load_completed(timeout=50)
                except:
                    pass
                xpath_map = {
                    "login_btn": XPaths.login_btn,
                    "auth_input": XPaths.auth_input,
                    "home": XPaths.home,
                    "campaign_home": XPaths.campaign_home,
                    "auth_select": XPaths.auth_select,
                    "select_user": XPaths.select_user,
                    "send_code_radio": XPaths.send_code_radio,
                    "log_in": XPaths.LogIn,
                    "continue_btn": XPaths.continue_btn,
                    "partner_switcher": XPaths.partner_switcher,
                    "new_home":XPaths.partner_switcher_new,
                    "captcha_iframe":XPaths.captcha_iframe
                }
                name, auth_ele = find_any_one_by_xpath(web_page, xpath_map, timeout=10)
            except Exception as login_error:
                print("login find all xpath error:", login_error)
                error_msg = login_error
                if "未找到元素" not in str(login_error) or retry_time == 2:
                    break

                # 未找到以上任意元素，判断网页是否加载完成
                if not web_page.is_load_completed():
                    # 未加载完成，继续等待，不消化重试次数
                    retry_time -= 1
                    continue

                web_page.reload(load_timeout=0)
                retry_time += 2
                sleep(1)
                continue

            if last_name == name:
                raise Exception(f"{pre_msg}，可检查项：1.密码是否填充；2.二次验证是否通过；3.其他")

            last_name = name

            if name == "home" or name == "campaign_home" or name == "new_home":
                # 首页元素，登录成功，循环中的唯一正常退出口
                return

            if name == "captcha_iframe":
                raise Exception("出现了数英验证码")

            if name == "continue_btn":
                auth_ele.click(delay_after=2)
                # 减少重试次数，下次循环中进行登录操作
                # retry_time -= 1
                continue                

            if name == "send_code_radio":
                # 出现发送验证码选项，选择发送验证码
                auth_ele.check()

                # 点击确认选项
                find_by_xpath(web_page, XPaths.auth_send_code).click()

                # 减少重试次数，下次循环中进行提交验证码操作
                # retry_time -= 1
                continue

            if name == "auth_select":
                # 出现二次验证选择，表示用户没有配置二次验证码的自动填充

                raise Exception(f"{pre_msg}，二次验证验证码没有自动填充，请先进行配置.")

            if name == "select_user":
                # 选择用户页面，点击第一个用户
                auth_ele.click(delay_after=2)

                # 减少重试次数，下次循环中进行登录操作
                # retry_time -= 1
                continue

            if name == "login_btn" or name == "log_in":
                # 点击登录按钮
                auth_ele.click(delay_after=2, simulative=False)

                # 登录按钮，点击登录后可能会出现二次验证，需要减少一次重试次数，下次循环判断二次验证
                # retry_time -= 1
                continue

            if name == "auth_input":
                # 二次验证的验证码输入框，检查一下有没有自动填充
                sleep(5)
                auth_code = auth_ele.get_value()
                if auth_code is None or auth_code == "":
                    raise Exception(f"{pre_msg}，二次验证验证码没有自动填充，请先进行配置")

                # 有自动填充，获取提交验证码按钮
                auth_ele = find_by_xpath(web_page, XPaths.auth_btn)
                auth_ele.click(delay_after=2)

                # 需要减少一次重试次数，下次循环判断是否登录成功
                # retry_time -= 1
                continue

            if name == "switch_accounts_button":
                # 出现 全局切换站点页面
                find_by_xpath(web_page, XPaths.picker_name).click()
                find_by_xpath(web_page, XPaths.switch_accounts_button).click()
                sleep(3)
                # 需要减少一次重试次数，下次循环判断是否登录成功
                # retry_time -= 1
                continue
        # 多次循环仍然登录失败，抛出异常
        raise Exception(f"{pre_msg}, 多次尝试登录失败, {error_msg}")

    def switch_site(self, web_page, site_name):
        """切换站点，可能会涉及登录以及二次验证"""
        # 获取站点id
        _site_name = re.sub("站$", "", site_name).upper()
        site_id = self.site_id_map.get(site_name, None)
        # assert site_id is not None, f"暂不支持该站点，{site_name}"

        browser_version = 'old'
        for retry_time in range(3):
            try:
                self.to_home_page(web_page)
                switcher_ele = find_by_xpath(web_page, XPaths.partner_switcher, timeout=3)
                # 记录首页地址
                self.home_url = utils.get_domain(web_page)
                if switcher_ele.get_attribute("data-marketplace_selection") == site_id:
                    # 不需要切换，当前站点就是要切换的站点
                    break
                switcher_ele.hover()
                switcher_ele.click() #点开页面
                
                '''
                后期需调整
                点开页面后有三个情况：
                1.完全的老页面
                2.点开第一个列表后的老页面
                3.新页面
                4.点展示之后不用点击第一个
                '''
            except:
                #打开新页面的站点列表
                find_by_xpath(web_page, XPaths.partner_switcher_new, timeout=3).hover()
                find_by_xpath(web_page, XPaths.partner_switcher_new, timeout=3).click()

            #针对点开即有选项的账号界面
            try:
                xpath = f"//*[contains(@class, 'partner-switcher')]//div[@title='{site_name}')]"
                find_by_xpath(web_page, xpath,timeout=3).click(simulative=False)
            except:
                try:
                    eles = web_page.find_all_by_xpath(XPaths.site_switcher_list,timeout=3)
                    tag = False
                    for ele in eles:
                        id_ = ele.get_attribute("id")
                        if id_ == site_id:
                            tag = True
                            ele.hover()
                            ele.click(simulative=True)
                            break
                    if tag ==True:
                        break
                except:
                    pass

            try:
                #点击弹开老页面选择项
                find_by_xpath(web_page, XPaths.site_switcher_first, timeout=3).click()
            except:
                try:
                    find_by_xpath(web_page, XPaths.site_switcher_first_new, timeout=2).click()
                except:
                    find_by_xpath(web_page, XPaths.site_switcher_first_two, timeout=1).click()
                    find_by_xpath(web_page, XPaths.site_switcher_first_three,timeout=1).click()
                finally:
                    browser_version = 'new'


            if browser_version =='old':
                eles = web_page.find_all_by_xpath(XPaths.site_switcher_list,timeout=3)
                tag = False
                for ele in eles:
                    id_ = ele.get_attribute("id")
                    if id_ == site_id:
                        tag = True
                        ele.click(simulative=False)
                        break

                if not tag:
                    raise Exception(f"当前店铺没有找到此站点 - {site_name}")
                self.login(web_page, pre_msg="亚马逊商家后台切换站点失败")

                try:
                    ele = find_by_xpath(web_page, XPaths.current_site.format(site_id), timeout=5)
                    break
                except:
                    raise Exception("切换站点失败")

            elif browser_version == 'new':
                try:
                    xpath = f"//*[contains(@class, 'partner-switcher')]//div[contains(text(),'{site_name}')]"
                    find_by_xpath(web_page, xpath).click(simulative=False)
                    break
                except:
                    raise Exception("切换站点失败")

        # except Exception as e:
        #     print("switch_site_err:", e)
        #     if "当前店铺没有找到此站点" in str(e) or "亚马逊商家后台切换站点失败" in str(e):
        #         raise
        #     if retry_time == 2:
        #         raise

        #     try:
        #         web_page.reload(load_timeout=50)
        #     except Exception as e:
        #         pass

    def switch_site_ad(self, web_page, site_name):
        for retry_time in range(3):
            try:
                if find_by_xpath(web_page, "/html").get_attribute("lang") != "zh":
                    self.switch_language_on_ad_page(web_page, "zh_CN")
                current_site_ele = find_by_xpath(web_page, XPaths.current_site_ad)
                if current_site_ele.get_text() == "国家/地区：{}".format(site_name):
                    # 不需要切换，当前站点就是要切换的站点
                    break

                current_site_ele.click()
                find_by_xpath(web_page, XPaths.site_switcher_first_ad, timeout=100)
                eles = web_page.find_all_by_xpath(XPaths.site_switcher_list_ad)
                tag = False
                for ele in eles:
                    if ele.get_text() == site_name:
                        tag = True
                        ele.click(simulative=False)
                        find_by_xpath(web_page, XPaths.change_country_btn).click(simulative=False)
                        break

                if not tag:
                    raise Exception(f"当前店铺没有找到此站点 - {site_name}")
                self.login(web_page, pre_msg="亚马逊广告页切换站点失败")

                web_page.wait_load_completed(100)
                break
            except Exception as e:
                print("switch_site_err:", e)
                if "当前店铺没有找到此站点" in str(e) or "亚马逊广告页切换站点失败" in str(e):
                    raise
                if retry_time == 2:
                    raise

                try:
                    web_page.reload(load_timeout=100)
                except Exception as e:
                    pass

    def switch_language(self, web_page, language):

        try:
            find_by_xpath(web_page, XPaths.language, timeout=5)
        except Exception as e:
            raise Exception("请先进入亚马逊后台")

        if find_by_xpath(web_page, "/html").get_attribute("lang").replace("-", "_") == language:
            return
        # 旧版语言操作

        if  find_by_xpath(web_page, XPaths.language, timeout=5):
            find_by_xpath(web_page, XPaths.language, timeout=5).click(simulative=True)
            try:
                find_by_xpath(web_page, XPaths.language_first, timeout=6)
            except:
                pass
            
            # 旧版点击切换语言
            # en_US
            try:
                find_by_xpath(web_page, XPaths.target_language.format(language), timeout=5).click(simulative=False)
                print(f'{language} 语言切换成功')
                return
            except Exception as e:
                # 没有目标元素
                xbot.print("当前店铺没有目标语言 - {}".format(language))
                return

        else:
            find_by_xpath(web_page, XPaths.new_seetings, timeout=5)
            find_by_xpath(web_page, XPaths.new_seetings, timeout=5).click()
            find_by_xpath(web_page, XPaths.new_language, timeout=5).click()

        # 新版点击切换语言
        # en
        try:
            find_by_xpath(web_page, XPaths.new_target_language.format(language), timeout=5).click(simulative=False)
        except Exception as e:
            return
        # 选择语言后等待网页加载完毕-判断是否浸入登录页面
        web_page.wait_load_completed()
        self.login(web_page, pre_msg="亚马逊商家后台切换语言失败")

    def switch_language_on_ad_page(self, web_page, language):
        setting_ad_ele = None
        try:
            setting_ad_ele = find_by_xpath(web_page, XPaths.setting_ad, timeout=5)
        except Exception as e:
            raise Exception("请先进入亚马逊广告页")
        is_open = setting_ad_ele.get_attribute("aria-expanded")
        print(is_open)
        if is_open == "true":
            setting_ad_ele.click(simulative=False)

        setting_ad_ele.click(simulative=False)
        language_ele = find_by_xpath(web_page, XPaths.language_ad)
        language_ele.click(simulative=False)
        find_by_xpath(web_page, XPaths.language_first_ad)
        try:
            find_by_xpath(web_page, XPaths.target_language_ad.format(language), timeout=1).click(simulative=False)
            language_switch_btn = find_by_xpath(web_page, XPaths.language_switch_btn.format(language), timeout=1)
            disabled = language_switch_btn.get_attribute("disabled")
            if disabled is False or disabled == "False":
                language_switch_btn.click(simulative=False)
            else:
                setting_ad_ele.click(simulative=False)
        except Exception as e:
            print(e)
            # 没有目标元素
            xbot.print("当前店铺没有目标语言 - {}".format(language))
            return

        try:
            web_page.wait_load_completed(timeout=20)
        except:
            pass

        pass


amazon = AmazonHandler()