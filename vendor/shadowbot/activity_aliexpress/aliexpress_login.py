# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from xbot import web
import re
import time
from .utils import gen_selector
from xbot.selector import Selector
from .package import variables as glv
import xbot_visual

def aliexpress_login(web_page:xbot.web.WebBrowser, switch_language:str, account_user:str, password:str, email_type:str, email_username:str, authorization_code:str, email_number:str):
    url = f'https://login.aliexpress.com/user/seller/login?bizSegment=CSP&_lang={switch_language}'
    current_url = web_page.get_url()
    if current_url != url:
        web_page.navigate(url)

    wait_xpath = '//form/button[normalize-space(.)="Sign In" or normalize-space(.)="登录"]'
    data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': [wait_xpath]}}
    selector = Selector(data)
    web_page.wait_appear(selector,timeout=20)

    # 登陆账号
    login_xpath = '//form//input[@id="loginName"]'
    web_page.find_by_xpath(login_xpath).input(account_user,simulative=True,input_check=True)

    # 随机点击一个不存在的元素去解决输入账号时出现的提示窗口
    web_page.find_by_xpath('//div[contains(@class,"title2_field_item ")]//b').click()

    # 登陆密码
    pass_xpath  = '//form//input[@type="password"]'
    web_page.find_by_xpath(pass_xpath).input(password,simulative=True,input_check=True,delay_after=2)
    # 点击登录
    web_page.find_by_xpath(wait_xpath).click(delay_after=5)

    # 判断是否登陆成功
    fail_xpath = '//form/section[normalize-space(.)="您的帐户名或密码不正确。"]'
    data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': [fail_xpath]}}
    selector = Selector(data)
    if web_page.wait_appear(selector,timeout=3):
        raise Exception("您的帐户名或密码不正确，程序终止，请重新输入账号和密码")

    # 处理邮箱
    data = {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//iframe', '//button[normalize-space(.)="验证"]']}}
    selector = Selector(data)
    if web_page.is_element_displayed(selector):

        # 设置最大尝试次数和重试间隔
        max_attempts = 3
        retry_delay = 5  # 秒

        for attempt in range(max_attempts):
            try:
                # 获取邮箱验证码
                mailmessage_list = xbot_visual.email.retrieve_email(mail_kind=email_type, address="", port="", use_ssl=True, username=email_username, authcode=xbot_visual.decrypt(authorization_code), only_unread=True, top=int(email_number), save_attachments=False, attachments_savefolder="", folder_name_specifc_mode="default", folder_name="INBOX", mark_as_read=True, keyword_in_from=None, keyword_in_to=None, keyword_in_subject=None, keyword_in_textBody=None, _block=("main", 1, "获取邮件"))
                print(mailmessage_list)
                # 检查是否获取到邮件
                if not mailmessage_list:
                    raise Exception("未获取到邮件")
                    
                html_body = mailmessage_list[0].html_body
                pattern = r'(?:一次性验证码是|Verification code:|【[^】]*】.*?一次性验证码是)\s*(\d{6})'
                match_word = re.search(pattern, html_body)
                
                # 检查是否成功匹配验证码
                if not match_word:
                    raise Exception("未在邮件中找到验证码")
                    
                code = match_word.group(1)
                
                # 输入验证码
                data1 = {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//iframe', '//input']}}
                selector = Selector(data1)
                web_page.find_all(selector)[0].input(code, simulative=True, input_check=True)
                
                # 确认登录
                data2 = {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//iframe', '//button[normalize-space(.)="验证"]']}}
                selector = Selector(data2)
                web_page.find(selector, timeout=20).click()
                
                # 如果执行到这里，说明成功，跳出循环
                print(f"第{attempt + 1}次尝试成功！")
                break
                
            except Exception as e:
                print(f"第{attempt + 1}次尝试失败: {str(e)}")
                
                # 如果是最后一次尝试，抛出异常
                if attempt == max_attempts - 1:
                    raise Exception(f"经过{max_attempts}次尝试后仍然失败: {str(e)}")
                
                # 等待一段时间后重试
                print(f"等待{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                
                # 可以在这里添加一些清理操作，比如刷新页面等
                # web_page.refresh()

    wait_success_xpath = '//img[@alt="aliexpress"]'
    if web_page.wait_appear(gen_selector(wait_success_xpath),timeout=30):
        xbot.logging.info('登陆成功')

    return web_page
        

def test_aliexpress_login():
    """测试速卖通登录功能"""
    if "xbot_extensions" in __file__:
        return
    
    # url = 'https://login.aliexpress.com/user/seller/login?bizSegment=CSP&return_url=http%3A%2F%2Fcsp.aliexpress.com%2Fapps%2Forder%2Findex%3FchannelId%3D1101206'
    web_page = web.get_active(mode='chrome')
    switch_language = 'zh_CN'
    account_user = 'mu.chun@yingdao.com'
    password = ''
    email_type = '126'
    email_username = ''
    authorization_code = 'RRhT9Tzjtz5va2z4'
    email_number = '1'
    aliexpress_login(web_page, switch_language,account_user,password,email_type,email_username,authorization_code,email_number)
    exit()
    
def main(args):
    # 调用测试函数
    test_aliexpress_login()

    # 传入参数
    web_page = args.get('web_page')
    switch_language = args.get('switch_language')
    account_user = args.get('account_user')
    password = args.get('password')
    email_type = args.get('email_type')
    email_username = args.get('email_username')
    authorization_code = args.get('authorization_code')
    email_number = args.get('email_number')
    # 调用主函数
    aliexpress_login(web_page, switch_language,account_user, password,email_type,email_username,authorization_code,email_number)

    # 将文件路径添加到返回参数中
    args['web_page2'] = web_page
    
