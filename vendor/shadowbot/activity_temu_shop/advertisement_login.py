# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .utils import Tools
import xbot_visual
import time

def advertisement_login(web_page, default_pwd, username, password):
    """temu广告平台登录"""

    # 获取浏览器名称
    browser_mode = Tools.get_web_page_product_name(web_page)

    # 打开登录页面
    url = 'https://ads.temu.com/login.html'
    if url not in web_page.get_url():
        web_page.navigate(url)

    # 等待页面加载完毕
    Tools.wait_loading(web_page)

    # 点击登录
    login_button_xpath = '//span[text()="登录"]'
    web_page.find_by_xpath(login_button_xpath).click()
    
    # 点击跨境登录
    cross_brder_login_xpath = '//div[.="请选择你的登录方式"]/following-sibling::div[2]//span[.="登录"]'
    web_page.find_by_xpath(cross_brder_login_xpath).click()

    # 激活新打开的页面，进行登录
    web_page2 = xbot.web.get_active(mode=browser_mode)

    # 不是默认密码则输入账号密码
    if not default_pwd:
        # 输入账号
        phone_input_xpath = '//input[@placeholder="手机号码"]'
        web_page2.find_by_xpath(phone_input_xpath).input(username)

        # 输入密码
        pwd_input_xpath = '//input[@placeholder="密码"]'
        password_ele = web_page2.find_by_xpath(pwd_input_xpath)
        xbot_visual.web.element.input_password(browser=web_page2, element=password_ele, text=xbot_visual.decrypt(password), simulate=True)
    
    # 点击授权勾选框，进行登录
    empower_svg_xpath = '//*[local-name()="svg"][@data-testid="beast-core-icon-check"]'
    web_page2.find_by_xpath(empower_svg_xpath).click()

    # 点击登录
    empower_login_xpath = '//button/span[.="授权登录"]'
    web_page2.find_by_xpath(empower_login_xpath).click()

    # 循环判断是否还有弹窗出现（最多等待320秒）
    max_wait_time = 20  # 最大等待时间（秒）
    start_time = time.time()
    
    while True:
        # 获取网页信息，若为首页则退出
        if 'https://ads.temu.com/login.html' not in web_page.get_url():
            print(f'{username} 账号登录成功')
            break

        # 检查是否超时
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_wait_time:
            raise Exception(f"{username} 账号登录可能失败，请检查页面是否包含弹窗")

        main_username_xpath_list = [
            '//div[text()="请切换主账号签署协议"]',
            '//div[text()="当前子账号暂无广告平台权限，无法进入。请联系主账号添加相关权限。"]',
            '//span[text()="当前您尚未确认以下文件，请及时阅读并同意"]'
            ]

        # 进行判断
        for main_username_xpath in main_username_xpath_list:
            main_username_sel = Tools.gen_selector(main_username_xpath)
            if web_page.wait_appear(main_username_sel, timeout=3):
                raise Exception("当前子账号无平台登入权限或需切换主账号签署协议")
        
        sleep(1)
 
def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return
    web_page = xbot.web.get_active(mode='chrome')
    username = ''
    password = ''
    default_pwd = False
    advertisement_login(web_page, default_pwd, username, password)


def main(args):
    web_page = args.get('web_page')
    default_pwd = args.get('default_pwd', True)
    username = args.get('username',' ')
    password = args.get('password', ' ')

    advertisement_login(web_page, default_pwd, username, password)