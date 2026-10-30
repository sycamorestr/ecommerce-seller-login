"""
beta 逐步替换旧的实现

"""
from tkinter import N
import xbot
import xbot_visual
from xbot import print, sleep, win32
from . import package
from .package import variables as glv

from xbot.web import WebBrowser, WebElement
from xbot._core.retry import Retry
from xbot.errors import UIAError
from xbot import logging
import uiautomation as auto

TITLE = "没有可用的通行密钥"

import re
from enum import Enum
from typing import Optional
# from ._amazon_core import amazon
from .utils_beta import wait_by_xpath, find_by_xpath

class XPaths:
    # -- 登录 --    
    login_btn = '''//input[@id="signInSubmit"]'''  # 店铺登录按钮
    auth_btn = '''//input[@id="auth-signin-button"]'''  # 二次验证提交验证码按钮
    auth_input = '''//input[@id="auth-mfa-otpcode"]'''  # 二次验证验证码输入框
                                                                             # 二次验证选择，出现这个元素表示用户没有配置二次验证，直接抛出异常
    passkey_dialog = '''//div[@id="a-popover-root"]/following-sibling::div[contains(@style,"center")]''' # 已托管PassKey弹窗
    continue_btn = '''(//*[@aria-labelledby="continue-announce"] | //*[@id="continue" and not (contains(text(),"密钥"))])[1]'''
    auth_select = '''//*[@id="guide-component"]'''  # 二次验证选择，出现这个元素表示用户没有配置二次验证，直接抛出异常
    select_user = '''(//div[@action="/ap/switchaccount"]//*[@class="a-row"])[1]'''  # 选择用户页面，第一个用户，需要选择后才会出现登录按钮
    select_user_1 = '(//div[@data-test-id="customerName"])[1]'

    # disposable_pwd = '//div[contains(@class,"auth-TOTP")]'    # 没有出现短信验证则去点击一次性密码
    # send_dis_pwd = '//*[@id="auth-send-code"]'          # 发送一次性密码

    home = '''//*[@id="partner-switcher"] | //*[@id="dropdown-account-switcher-container"] '''  # 主页元素
    campaign_home = '''//header[@role="presentation" or @id="topBar"]'''  # 广告页的主页元素

    send_code_radio = '''(//input[contains(@value, "TOTP")])[1]'''  # 发送验证码单选框
    auth_send_code = '''//*[@id="auth-send-code"]'''  # 确认发送验证码
    LogIn = '(//strong[.="Log in"])[1]'    
    
    
    # -- 验证码 --
    captcha_iframe = '''//*[@id="aa-challenge-whole-page-iframe"]'''  # 验证码 iframe
    captcha_input = '''//*[@id="aa_captcha_input"]'''  # 验证码输入框
    captcha_image = '''//*[@id="aa_amazon_image_captcha"]'''  # 验证码图片
    captcha_continue_btn = '//*[@id="aa_captcha_submit_button-announce"]'
    
    # -- 站点切换 --
    partner_switcher = '''(//*[@id="partner-switcher"]|//*[contains(@class, 'partner-switcher')])[1]'''  # 打开站点列表按钮
    # account_switcher_link = '//*[@href="/account-switcher/default/merchantMarketplace"]' # 如果账户异常，partner_switcher 子元素就会有这个XPath, 要获取这个链接跳转页面来切换站点
    account_switcher_link = '//*[contains(@href, "/account-switcher")]' # 如果账户异常，partner_switcher 子元素就会有这个XPath, 要获取这个链接跳转页面来切换站点
    
    new_partner_switcher = '//div[@id="dropdown-account-switcher-container"]//span[contains(@class,"switcher-header-label-regional-child")]'  # 新版灰度切换账号按钮
    list_point  = '//div[contains(@class,"switcher-list-pointer-area")]//a'        # 新版灰度进入选择账户页面
    new_target_account = ''   # 新版灰度页面账户元素
    confimr_button = '//kat-button[@data-test="confirm-selection"]'   # 选择账户按钮

    site_switcher_list = '''
    (//*[@id="partner-switcher"]//div[@class="scrollable-content"])[1]//ul[@class="merchant-level"]/li | //*[@class="dropdown-account-switcher-list-item-label"]
    |
    //div[@class="full-page-account-switcher-account"]/div//span[@class="full-page-account-switcher-account-label"]
    '''  # 站点列表
    account_switcher_list_dropdown = '''//*[@class="dropdown-account-switcher-list-item"]/*[name()="svg"]''' # 账号展开站点列表按钮
    new_full_page_expander = '''//div[@class="full-page-account-switcher-accounts-wrapper" and .//span[@*="current-account"]]//kat-icon[contains(@class,"full-page-account-switcher-account-expander-icon")]'''  # 新版灰度页面 展开站点列表图标
    error_page = '//*[@id="mons-error-page-template"]' # 无效链接页面
    
    
    link_site_switcher_list = '//button[@class="full-page-account-switcher-account-details" and .//span[@*="current-account"]]/following-sibling::div//button | //*[@class="full-page-account-switcher-account-details full-page-account-switcher-account-selected"]'  # 链接页面 站点列表
    link_account_switcher_list_dropdown = '//button[@class="full-page-account-switcher-account-details"]/*[1][name()="svg"]' # 链接页面 账号展开站点列表按钮
    link_account_switcher_button = '//*[@class="full-page-account-switcher-footer"]/button' # 链接页面 需要额外点击一次切换按钮

def get_site_id(params):
    """映射站点"""
    site_id_map = {
        "墨西哥": "Mexico",
        "澳大利亚": "Australia",
        "比利时": "Belgium",
        "日本": "Japan",
        "瑞典": "Sweden",
        "加拿大": "Canada",
        "英国": "United Kingdom",
        "美国": "United States",
        "意大利": "Italy",
        "法国": "France",
        "西班牙": "Spain",
        "波兰": "Poland",
        "荷兰": "Netherlands",
        "德国": "Germany",
        "阿拉伯联合酋长国": "United Arab Emirates",
        "土耳其": "Turkey",
        "巴西": "Brazil",
        "沙特阿拉伯": "Saudi Arabia",
        "新加坡共和国": "Singapore",
        "印度": "India",
        "爱尔兰": "Ireland"
    }
    return site_id_map[params]


def get_site_name_variants(site_name):
    """返回站点名的中英文变体集合，用于兼容中英文页面匹配"""
    site_id_map = {
        "墨西哥": "Mexico",
        "澳大利亚": "Australia",
        "比利时": "Belgium",
        "日本": "Japan",
        "瑞典": "Sweden",
        "加拿大": "Canada",
        "英国": "United Kingdom",
        "美国": "United States",
        "意大利": "Italy",
        "法国": "France",
        "西班牙": "Spain",
        "波兰": "Poland",
        "荷兰": "Netherlands",
        "德国": "Germany",
        "阿拉伯联合酋长国": "United Arab Emirates",
        "土耳其": "Turkey",
        "巴西": "Brazil",
        "沙特阿拉伯": "Saudi Arabia",
        "新加坡共和国": "Singapore",
        "印度": "India",
        "爱尔兰": "Ireland"
    }
    # 简体 -> 繁体 映射
    cn_to_tw = {
        "墨西哥": "墨西哥",
        "澳大利亚": "澳大利亞",
        "比利时": "比利時",
        "日本": "日本",
        "瑞典": "瑞典",
        "加拿大": "加拿大",
        "英国": "英國",
        "美国": "美國",
        "意大利": "意大利",
        "法国": "法國",
        "西班牙": "西班牙",
        "波兰": "波蘭",
        "荷兰": "荷蘭",
        "德国": "德國",
        "阿拉伯联合酋长国": "阿拉伯聯合大公國",
        "土耳其": "土耳其",
        "巴西": "巴西",
        "沙特阿拉伯": "沙烏地阿拉伯",
        "新加坡共和国": "新加坡共和國",
        "印度": "印度",
        "爱尔兰": "愛爾蘭"
    }
    # 构建反向映射：英文 → 中文
    en_to_cn = {v: k for k, v in site_id_map.items()}

    variants = {site_name}
    # 如果输入是简体中文
    if site_name in site_id_map:
        variants.add(site_id_map[site_name])          # 英文
        variants.add(cn_to_tw.get(site_name, site_name))  # 繁体
    # 如果输入是英文
    if site_name in en_to_cn:
        cn_name = en_to_cn[site_name]
        variants.add(cn_name)                          # 简体
        variants.add(cn_to_tw.get(cn_name, cn_name))   # 繁体
    # 如果输入是繁体中文
    tw_to_cn = {v: k for k, v in cn_to_tw.items()}
    if site_name in tw_to_cn:
        cn_name = tw_to_cn[site_name]
        variants.add(cn_name)                          # 简体
        variants.add(site_id_map.get(cn_name, cn_name))  # 英文

    # 德国额外兼容 Deutschland（亚马逊页面可能显示 Germany 或 Deutschland）
    if site_name in ("德国", "德國", "Germany", "Deutschland"):
        variants.update({"德国", "德國", "Germany", "Deutschland"})

    return variants


def _clean_site_text(text: str) -> str:
    """清洗站点文本，去除当前标记、空白等"""
    if not text:
        return ""
    # 兼容 简体/繁体/英文 的 "当前" 标记
    for mark in [" (当前)", " (current)", " (目前)", "（目前）", "（当前）"]:
        text = text.replace(mark, "")
    return text.strip()


def match_site_text(element_text, site_name):
    """检查元素文本是否匹配目标站点名（兼容简中/繁中/英文）"""
    variants = get_site_name_variants(site_name)
    clean_text = _clean_site_text(element_text)
    return clean_text in variants


def site_name_in_text(element_text, site_name):
    """检查元素文本中是否包含目标站点名（子串匹配，兼容简中/繁中/英文）"""
    if not element_text:
        return False
    variants = get_site_name_variants(site_name)
    clean_text = _clean_site_text(element_text)
    for variant in variants:
        if variant in clean_text:
            return True
    return False


def close_passkey_dialog():
    dialog = auto.WindowControl(
        searchDepth=5,
        ClassName="RootView",
        Name=TITLE,
    )

    if not dialog.Exists(maxSearchSeconds=5):
        return

    close_button = dialog.ButtonControl(
        searchDepth=8,
        Name="关闭",
    )

    if not close_button.Exists(maxSearchSeconds=2):
        return

    close_button.Click()

    # 检查原弹窗是否消失
    auto.Sleep(0.5)
    if dialog.Exists(maxSearchSeconds=1):
        raise RuntimeError("点击后弹窗仍存在")



def login(web_page: WebBrowser):
    """
    亚马逊商家后台登录
    """
    
    not_condition_count = 0
    last_error = None
    if 'signin' not in web_page.get_url() and 'mfa' not in web_page.get_url():
        return
    for _, set_last_error in Retry(times=20):
        try:
            web_page.wait_load_completed()
            if wait_by_xpath(web_page, XPaths.home, timeout=0):
                return
            if wait_by_xpath(web_page, XPaths.campaign_home, timeout=0):
                return
            if wait_by_xpath(web_page, XPaths.partner_switcher, timeout=0):
                return
            if wait_by_xpath(web_page, XPaths.auth_select, timeout=0):
                raise Exception("二次验证验证码没有自动填充，请先进行配置")
            if wait_by_xpath(web_page, XPaths.captcha_iframe, timeout=0):
                raise Exception("出现了数英验证码")

            # 前处理，判断Passkey登录按钮是否已经出现，如果已出现，不执行enter，防止焦点错误，导致触发正常登录
            exists1 = xbot_visual.win32.element.wait(window="0", element=package.selector("使用该Passkey登录"), state="appear", iswait=True, timeout=0)
            exists2 = xbot_visual.win32.element.wait(window="0", element=package.selector("使用该Passkey登录1"), state="appear", iswait=True, timeout=0)
            if not exists1 and not exists2:
                xbot.win32.send_keys('{ENTER}')

            try:
                xbot_visual.win32.element.click(window="0", element=package.selector("使用该Passkey登录"), clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_mouse=True, simulate=True, timeout=0)
            except Exception as e:
                pass
            
            try:
                xbot_visual.win32.element.click(window="0", element=package.selector("使用该Passkey登录1"), clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_mouse=True, simulate=True, timeout=0)
            except Exception as e:
                pass

            continue_btn = wait_by_xpath(web_page, XPaths.continue_btn, timeout=0)
            if continue_btn:
                current_url = web_page.get_url()
                continue_btn.click()
                sleep(1)
                xbot.win32.send_keys('{ENTER}')
                check_continue_btn = wait_by_xpath(web_page, XPaths.continue_btn, timeout=0)
                if check_continue_btn:
                    pass
                else:
                    continue
            
            send_code_radio = wait_by_xpath(web_page, XPaths.send_code_radio, timeout=0)
            if send_code_radio:
                send_code_radio.check()
                find_by_xpath(web_page, XPaths.auth_send_code).click()
                continue
            
            select_user = wait_by_xpath(web_page, XPaths.select_user, timeout=0)
            if select_user:
                select_user.click()
                continue

            select_user = wait_by_xpath(web_page, XPaths.select_user_1, timeout=0)
            if select_user:
                select_user.click()
                continue

            
            login_btn = wait_by_xpath(web_page, XPaths.login_btn, timeout=0)
            if login_btn:
                login_btn.click(simulative=False)

                close_passkey_dialog()
                continue
            
            log_in = wait_by_xpath(web_page, XPaths.LogIn, timeout=0)
            if log_in:
                log_in.click()
                close_passkey_dialog()
                continue
            
            auth_input = wait_by_xpath(web_page, XPaths.auth_input, timeout=0)
            if auth_input:
                auth_code = None
                for _ in Retry(timeout=10, ignore_exception=True):
                    auth_code = auth_input.get_value()
                    if auth_code:
                        break
                if not auth_code:
                    raise Exception("二次验证验证码没有自动填充，请先进行配置")
                
                find_by_xpath(web_page, XPaths.auth_btn).click(simulative=False)

                if wait_by_xpath(web_page, XPaths.auth_btn, timeout=2):
                    web_page = xbot.web.get_active(mode=web_page.product_name, silent_running=False)
                    if find_by_xpath(web_page, XPaths.auth_btn):
                        find_by_xpath(web_page, XPaths.auth_btn).click(simulative=True)

                continue
            if not web_page.is_load_completed():
                continue
            not_condition_count += 1
            if not_condition_count > 30:
                raise Exception("登录超时")
        except UIAError as e:
            set_last_error(e)


def _is_login_page(web_page: WebBrowser) -> bool:
    """判断当前是否处于亚马逊登录/二次验证页面"""
    try:
        url = web_page.get_url() or ""
    except Exception:
        return False
    return ("signin" in url) or ("mfa" in url) or ("ap/signin" in url)


def switch_site(web_page: WebBrowser, site_name: str):
    """
    亚马逊切换站点
    @param: web_page, 网页对象
    @param: site_name, 亚马逊站点名称
    """
    regex = re.compile(r"https?://sellercentral.+?amazon")
    domain = web_page.execute_javascript("() => origin")

    if not regex.match(domain):
        raise Exception(f"请先进入亚马逊商家后台, 当前网址：{domain}")

    # 切换站点前，若已掉线到登录页，先自动登录
    if _is_login_page(web_page):
        print("切换站点前检测到登录页，先执行自动登录")
        login(web_page)
        web_page.wait_load_completed()

    # 打开站点列表，点击目标站点
    for _, set_last_error in Retry(times=4):
        try:
            if not regex.search(domain):
                web_page.navigate(domain)
            isLinkPage = False
            curr_url = web_page.get_url()

            if "account-switcher" in curr_url and "account-switcher/default/merchantMarketplace" not in curr_url:
                href = "/account-switcher/default/merchantMarketplace"
                url = f"{domain}{href}"
                web_page.navigate(url, load_timeout=30)

            if "account-switcher/default/merchantMarketplace" not in web_page.get_url():
                # 切换过程中掉线，先登录
                if _is_login_page(web_page):
                    print("切换站点过程中检测到登录页，先执行自动登录")
                    login(web_page)
                    web_page.wait_load_completed()

                try:
                    switcher_ele = find_by_xpath(web_page, XPaths.partner_switcher)
                except Exception as e:
                    xbot.logging.info(e)
                    # 再次兜底：如果这时是登录页，先登录再重新查找
                    if _is_login_page(web_page):
                        print("未找到 partner_switcher 且当前为登录页，先执行自动登录")
                        login(web_page)
                        web_page.wait_load_completed()
                    switcher_ele = find_by_xpath(web_page, XPaths.partner_switcher)
                
                if switcher_ele:
                    if switcher_ele.get_text() and site_name_in_text(switcher_ele.get_text(), site_name):
                        # 当前站点就是目标站点
                        return
                    switcher_ele.hover()
                elif not switcher_ele:
                    # 新版页面，切换前再兜底一次登录页判断
                    if _is_login_page(web_page):
                        print("新版切换流程检测到登录页，先执行自动登录")
                        login(web_page)
                        web_page.wait_load_completed()

                    # 进行新版页面的站点选择
                    switcher_ele = find_by_xpath(web_page, XPaths.new_partner_switcher, timeout=3)
                    if switcher_ele.get_text() and site_name_in_text(switcher_ele.get_text(), site_name):
                        return  # 当前站点与目标站点一致
                    switcher_ele.hover()
                    switcher_ele.click()
                    sleep(2)
                    # 点击进入选择账户
                    try:
                        web_page.find_by_xpath(XPaths.list_point).click()
                    except:
                        href = "/account-switcher/default/merchantMarketplace"
                        url = f"{domain}{href}"
                        web_page.navigate(url, load_timeout=30)
                    
                    if _is_login_page(web_page):
                        print("新版切换流程检测到登录页，先执行自动登录")
                        login(web_page)
                        web_page.wait_load_completed()
                        
                    # switcher_list_dropdown_xpath = XPaths.account_switcher_list_dropdown + " | " + XPaths.new_full_page_expander
                    switcher_list_dropdown_xpath = XPaths.new_full_page_expander
                    for acc in web_page.find_all_by_xpath(switcher_list_dropdown_xpath):
                        # 通过 expanded 来判断站点列表是否展开
                        if "expanded" not in acc.get_attribute('class'):
                            acc.click(simulative=False, delay_after=0)
                    sleep(2)
                    # 进行站点选择（兼容中英文），跳过含"注册/registr"的未注册站点，等待已注册站点加载
                    variants = get_site_name_variants(site_name)
                    target_elem = None
                    for _ in Retry(timeout=30, ignore_exception=True):
                        for name in variants:
                            try:
                                all_elems = web_page.find_all_by_xpath(XPaths.new_target_account.format(name), timeout=3)
                                for elem in all_elems:
                                    text = elem.get_text()
                                    if "注册" in text or "registr" in text.lower():
                                        continue
                                    target_elem = elem
                                    break
                                if target_elem:
                                    break
                            except Exception:
                                continue
                        if target_elem:
                            break
                    if target_elem:
                        target_elem.click()
                    else:
                        country_list = get_all_country()
                        raise Exception(f"未找到目标站点：{site_name},当前站点：{country_list}")
                    # 轮询点击确认按钮，直到退出选择账户页面
                    for _ in Retry(timeout=15, ignore_exception=True):
                        try:
                            web_page.find_by_xpath(XPaths.confimr_button, timeout=2).click()
                        except Exception:
                            pass
                        web_page.wait_load_completed()
                        if len(web_page.find_all_by_xpath(XPaths.confimr_button, timeout=1)) == 0:
                            break
                    else:
                        if len(web_page.find_all_by_xpath(XPaths.confimr_button, timeout=1)) > 0:
                            raise Exception("点击确认选择账户按钮失败，未能退出选择账户页面")
                    break   # 退出循环

                # 如果存在 switcher_link， 就只能通过跳转链接切换站点
                switcher_link: Optional[WebElement] = None
                try:
                    switcher_link = find_by_xpath(switcher_ele, XPaths.account_switcher_link, timeout=3)
                    isLinkPage = True
                except UIAError:
                    pass
            
                switcher_list_dropdown_xpath = XPaths.account_switcher_list_dropdown + " | " + XPaths.new_full_page_expander
                switcher_list_xpath = XPaths.site_switcher_list
            
                if switcher_link:
                    # href = switcher_link.get_attribute('href')
                    # 通过 get_attribute('href') 获取链接会有不一样的情况，这是亚马逊页面的bug, 直接写死 href 就好了
                    href = "/account-switcher/default/merchantMarketplace"
                    url = f"{domain}{href}"
                    web_page.navigate(url, load_timeout=30)
                    switcher_list_dropdown_xpath = XPaths.link_account_switcher_list_dropdown + " | " + XPaths.new_full_page_expander
                    switcher_list_xpath = XPaths.link_site_switcher_list
                else:
                    switcher_ele.click()
            else:
                isLinkPage = True
                switcher_list_dropdown_xpath = XPaths.link_account_switcher_list_dropdown + " | " + XPaths.new_full_page_expander
                switcher_list_xpath = XPaths.link_site_switcher_list                
            
            for acc in web_page.find_all_by_xpath(switcher_list_dropdown_xpath):
                # 通过 expanded 来判断站点列表是否展开
                if "expanded" not in acc.get_attribute('class'):
                    acc.click(simulative=False, delay_after=0)

            find_target_site = False
            # 这里重试是为了等待所有账户站点列表展开，如果有多个账户，单独通过 find_all_by_xpath 无法保证在全部展开后才返回
            # 并且没有太好的方式来判断站点列表是否全部展开，所以只能通过重试来等待
            for _ in Retry(timeout=30, ignore_exception=True):
                for _ in range(3):
                    site_elems = web_page.find_all_by_xpath(switcher_list_xpath, timeout=10)
                    if len(site_elems) == 0:
                        continue
                    break
                else:
                    raise Exception(f"未找到站点列表：{switcher_list_xpath}")
                        
                # 兼容中英文站点名称匹配（跳过含"注册"或"registr"的站点）
                target_site_elem = next(
                    filter(
                        lambda e: site_name_in_text(e.get_text(), site_name)
                        and not ("注册" in e.get_text() or "registr" in e.get_text().lower()),
                        site_elems
                    ), None
                )
                if not target_site_elem:
                    continue
                
                target_site_elem.click(simulative=False)
                find_target_site = True
                # 点击切换登录
                # web_page.find_by_xpath('//*[@class="full-page-account-switcher-button"]').click()

                if len(web_page.find_all_by_xpath('//*[@class="full-page-account-switcher-button"]', timeout=3)) > 0:
                    web_page.find_by_xpath('//*[@class="full-page-account-switcher-button"]', timeout=3).click()

                if len(web_page.find_all_by_xpath('//*[@aria-labelledby="auth-signin-button-announce"]', timeout=3)) > 0:
                    web_page.find_by_xpath('//*[@aria-labelledby="auth-signin-button-announce"]', timeout=3).click()

                if len(web_page.find_all_by_xpath('//*[@aria-labelledby="continue-announce"]', timeout=3)) > 0:
                    web_page.find_by_xpath('//*[@aria-labelledby="continue-announce"]', timeout=3).click()
          
                break
            
            if not find_target_site:
                country_list = get_all_country()
                raise Exception(f"未找到目标站点：{site_name},当前站点：{country_list}")
            
            # if isLinkPage:
            #     find_by_xpath(web_page, XPaths.link_account_switcher_button).click(simulative=False)
            break  
        except UIAError as e:
            print(e)
            set_last_error(e)
    
    # 暂时用旧的，需要的时候再替换
    # amazon.login(web_page)
    #新的
    login(web_page)
    # 轮询校验当前站点是否为目标站点
    for _ in Retry(timeout=10, ignore_exception=True):
        web_page.wait_load_completed()
        try:
            switcher_ele = find_by_xpath(web_page, XPaths.partner_switcher, timeout=2)
            if switcher_ele.get_text() and site_name_in_text(switcher_ele.get_text(), site_name):
                break
        except Exception:
            pass
        try:
            switcher_ele = find_by_xpath(web_page, XPaths.new_partner_switcher, timeout=2)
            if switcher_ele.get_text() and site_name_in_text(switcher_ele.get_text(), site_name):
                break
        except Exception:
            pass
    else:
        raise Exception(f"切换站点失败，当前站点不是目标站点：{site_name}")

def get_all_country():
    web_page = xbot.web.get_active('ziniaobrowser')
    all_country = web_page.find_all_by_xpath('//div[@class="full-page-account-switcher-account"]/div//span[@class="full-page-account-switcher-account-label"]',timeout=3)
    all_country_name_list = []
    for i, country in enumerate(all_country):
        country_name = country.get_text()
        all_country_name_list.append(country_name)

    return all_country_name_list

def main(args):
    web_page = xbot.web.get_active('ziniaobrowser')
    login(web_page)