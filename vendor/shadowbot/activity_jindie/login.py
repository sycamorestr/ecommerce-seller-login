# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

from xbot import web
import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .utils import gen_selector
from xbot.web import WebBrowser
from xbot_extensions.activity_jfbym import std_alphanum_captcha

def login(web_page: WebBrowser, account: str, password: str, platform: str, login_now: bool = True):
    ''' 登录金蝶星空
    :param web_page: 网页对象
    :param account: 账号
    :param password: 密码
    :param platform: 平台
    :param login_now: 是否立即登录
    '''
    # 初始化元素选择器
    account_input_xpath = '//input[@id="user"]'
    account_input = gen_selector(account_input_xpath, '账号输入框')
    password_input_xpath = '//input[@id="password"]'
    password_input = gen_selector(password_input_xpath, '密码输入框')
    login_button_xpath = '//button[@id="btnLogin"]'
    login_button = gen_selector(login_button_xpath, '登录按钮')
    captcha_img_xpath = '//img[@id="img_VelidationCode"]'
    captcha_img = gen_selector(captcha_img_xpath, '验证码图片')
    captcha_input_xpath = '//input[@id="velidationCode"]'
    captcha_input = gen_selector(captcha_input_xpath, '验证码输入框')
    platform_click_xpath = '//div[@id="datacenter_ct"]//span[@class="toolTip"]'
    platform_click = gen_selector(platform_click_xpath, '平台触发按钮')
    platform_select_xpath = f'//ul/li[contains(., "{platform.strip()}")]'
    platform_select = gen_selector(platform_select_xpath, '平台选择')
    login_now_xpath = '//span[.="该帐号已登录在线，确认让对方下线,"]'
    login_now_ele = gen_selector(login_now_xpath, '立即登录按钮')
    login_now_button_xpath = '//div[@class="kd-mouseover-el"][contains(.,"确认")]'
    login_now_button = gen_selector(login_now_button_xpath, '让对方下线按钮')
    login_now_no_button_xpath = '//div[@class="kd-mouseover-el"][contains(.,"取消")]'
    login_now_no_button = gen_selector(login_now_button_xpath, '不下线按钮')
    
    # 检验是否存在账号输入框，判断是否打开登录页面
    if not web_page.is_element_displayed(account_input):
        raise Exception('账号输入框不存在，请检查是否打开登录页面')
    
    # 选择平台
    if platform:
        web_page.find(platform_click).click()
        web_page.find(platform_select).click()

    # 开始输入账号密码
    web_page.find(account_input).input(account)
    xbot.win32.send_keys(keys='{tab}')
    web_page.find(password_input).input(password,simulative=False)

    # 处理验证码
    if web_page.is_element_displayed(captcha_img):
        captcha_data = std_alphanum_captcha.handle_captcha(web_page, captcha_img, "", "10110", False, 20)
        web_page.find(captcha_input).input(captcha_data)
    # 点击登录按钮
    web_page.find(login_button).click()

    # 判断是否存在立即登录框出现
    if web_page.is_element_displayed(login_now_ele):
        if login_now:
            web_page.find(login_now_button).click()
        else:
            web_page.find(login_now_no_button).click()
            return web_page
    # 等待登录按钮消失，在规定时间没有消失则判断失败
    login_disappear_result = web_page.wait_disappear(login_button, timeout=10)
    if not login_disappear_result:
        raise Exception('登录失败，登录按钮在规定时间没有消失')
    

    return web_page


def test_func():
    if "xbot_extensions" not in __file__:
        account = ""
        password = ""
        web_page = web.get_active('cef')
        web_page = login(web_page, account, password, " 69测试(20250325)", True)
        exit()

def main(args):
    test_func()
    web_page = args.get('web_page')
    account = args.get('account')
    password = args.get('password')
    platform = args.get('platform', " 69测试(20250325)")
    login_now = args.get('login_now', True)
    args['out_web_page'] = login(web_page, account, password, platform, login_now)