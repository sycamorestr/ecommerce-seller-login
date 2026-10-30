# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import get_ele
from . import utils
import xbot_visual

def login(web_page, account, password):
    ''' 登录聚水潭
    :params web_page: 网页对象
    :params account: 账号
    :params password: 密码
    '''
    mode = web_page.product_name
    # 跳转网址
    web_page.navigate('https://www.erp321.com/login.aspx')
    web_page.wait_load_completed()

    # 如果不在账号密码登录界面切换成账号密码登录
    choose_pw_ele = get_ele(web_page, '//img[@alt="切换密码"]', '切换账号密码登录')
    if web_page.is_element_displayed(choose_pw_ele):
        web_page.find(choose_pw_ele).click()

    # 静默模式输入
    web_page = web.get_active(mode=mode, silent_running=True)
    
    # 输入账号密码
    account_ele = get_ele(web_page, '//input[@placeholder="邮箱地址/手机号码"]', '账号输入框')
    web_page.find(account_ele).input(account)
    password_ele = get_ele(web_page, '//input[@placeholder="请输入密码"]', '密码输入框')
    password = xbot_visual.decrypt(password)    # 处理资产管理解密
    web_page.find(password_ele).input(password)
    web_page = web.get_active(mode=mode, silent_running=False)

    # 勾选我已阅读并同意
    check_input_ele = get_ele(web_page, '//span[@class="ant-checkbox"]/input', '我已阅读同意')
    web_page.find(check_input_ele).check(mode='check')

    # 点击登录
    login_button_ele = get_ele(web_page, '//button[.="立即登录"]', '登录_按钮')
    web_page.find(login_button_ele).click()

    # 登录成功出现
    login_in_ele = get_ele(web_page, '//div[@role="tab" and .="聚水潭欢迎您"]', '登录成功标志')
    web_page.wait_appear(login_button_ele)

def test_func():
    ''' 测试函数
    '''
    if "xbot_extensions" not in __file__:
        # 获取当前激活的网页对象
        web_page = web.get_active('chrome')
        account = ""
        password = ""
        login(web_page, account, password)
        exit()    

def main(args):
    web_page = args.get('web_page')
    account = args.get('account')
    password = args.get('password')
    test_func()
    login(web_page, account, password)