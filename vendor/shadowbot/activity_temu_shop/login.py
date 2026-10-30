# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import re

import xbot
from xbot import print, sleep, web
from . import package
from .package import variables as glv
from .utils import Tools
import xbot_visual

def login(web_page: xbot.web.WebBrowser, username, password, target_store, site, default_pwd):
    url = "https://seller.kuajingmaihuo.com/login"
    web_type = Tools.get_web_page_product_name(web_page)
    current_url = web_page.get_url()

    if not current_url.startswith(url):
        web_page.navigate(url, load_timeout=20)

    for _ in range(3):
        try:
            login_sel = web_page.find_all_by_xpath("//*[text()='手机号登录']", timeout=3)
            login_list = [_ for _ in login_sel if _.get_bounding(to96dpi=False)[2] != 0]
            if len(login_list) > 0:
                login_list[0].click()
            sleep(1)
            break
        except:
            pass

    if not default_pwd:
        web_page.find_by_xpath("//input[@placeholder='请输入手机号']").input(username)
        web_page.find_by_xpath("//input[@placeholder='请输入密码']").input(password,anchor=('middleLeft','0','0'))
    checkbox_elem = web_page.find_by_xpath(
        "//*[contains(text(),'我已阅读')]/..//preceding-sibling::div/input"
    )
    checkbox_elem.check()
    login_ele = web_page.find_all_by_xpath("//span[text()='登录']")
    log_list = [_ for _ in login_ele if _.get_bounding(to96dpi=False)[2] != 0]
    log_list[0].click(simulative=False)

    sleep(2)

    web_page = xbot.web.get_active(mode=web_page.product_name)

    if (
        len(
            web_page.find_all_by_xpath(
                '//div[text()="我已阅读并同意以上协议"]', timeout=1
            )
        )
        > 0
    ):
        web_page.find_by_xpath(
            '//div[text()="我已阅读并同意以上协议"]', timeout=1
        ).click()
        web_page.find_by_xpath('//span[text()="我已阅读并同意"]', timeout=1).click()

    if web_page.is_element_displayed("dr_elem"):
        Tools.handle_std_capture(web_page)
    
    if len(web_page.find_all_by_xpath('//span[text()="确认切换"]', timeout=2)) > 0:
        web_page.find_by_xpath('//span[text()="确认切换"]').click()

    if target_store != "" and target_store != None:
        target_store = re.sub(r'\s+','',target_store)
        web_page.find_by_xpath("//span[text()='切换']").click()
        store_list = "//div[contains(@class,'site-main_switchSection')]/div"
        Tools.switch_store(web_page, store_list, target_store)

    # else:
    # 授权并登录
    if (
        len(
            web_page.find_all_by_xpath(
                '//div[@data-testid="beast-core-checkbox-checkIcon"]/input'
            ,timeout=3
            )
        )
        > 0
    ):
        # web_page.find_by_xpath(
        #     '//div[@data-testid="beast-core-checkbox-checkIcon"]/div'
        # ).click()
        check_element = web_page.find_by_xpath('//div[@data-testid="beast-core-checkbox-checkIcon"]/input',timeout=5)
        check_element.check(mode="check")
        
    site = site.replace('除欧区、美国', '').strip()
    if site and site != "商家中心":
        site_list = web_page.find_all_by_xpath('//*[text()="Seller Central"]/following-sibling::div[contains(@class,"site-main_entryBox")]/div')
        for site_sel in site_list:
            if site in site_sel.get_text().replace('除欧区、美国', '').strip():
                site_sel.find_by_xpath('.//*[contains(@class,"site-main_enter") and contains(text(),"进入")]').click()
                # 获取浏览器类型
                web_product_name = web_page.product_name
                sleep(2)
                try:
                    xbot_visual.web.browser.wait_load_completed(browser=web_page, load_timeout="10", action_after_load_timeout="handleExcept", _block=("main", 8, "等待网页加载完成"))
                except Exception as e:
                    pass
                new_web_page = xbot_visual.web.get(web_type=web_product_name, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None)
                switch_span = new_web_page.find_all_by_xpath('//*[text()="确认切换"]')
                if len(switch_span) >= 1:
                    switch_span[0].click()
                break
    else:
        web_page.find_by_xpath('//*[text()="商家中心"]').click()

    # 授权验证
    if "authentication" in web_page.get_url():
        # 触发商家中心
        web_page.find_by_xpath('//div[contains(@class,"authentication_goto")]').click()
        web_page2 = xbot.web.get_active(mode='auto')
        web_page2.find_by_xpath('//span[text()="确认授权并前往"]').click()
    return 
    
    
def main(args):
    
    web_page = args.get("web_page")
    username = args.get("username")
    password = args.get("password")
    target_store = args.get("target_store")
    default_pwd = args.get('default_pwd')
    site = args.get('site')

    # web_page = web.get_active(mode='chrome')
    login(web_page, username, password, target_store, site, default_pwd)
