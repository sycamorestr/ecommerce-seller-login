# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package
from .package import variables as glv
from .orangebank_slider_captcha import deal_deal_handle_captcha
from xbot_extensions.activity_jfbym import std_alphanum_captcha,std_click_select_captcha


def nper_bank__login(web_page,load_type:str, username:str, password:str):
    """民生银行登录
    :param web_page: , 网页对象
    :param load_type: str,登录类型
    :param username: str, 账号
    :param password: str, 密码
    """
    
    if load_type=='个人网上银行':
    
        url = "https://nper.cmbc.com.cn/pweb/static/login.html#"
        web_page.navigate(url,load_timeout=40)
        web_page.reload(load_timeout=40)
        
        if web_page.is_element_displayed("民生银行-个人版密码控件检测"):
            result=web_page.find('民生银行-个人版密码控件检测').get_text()
            raise Exception(f'登录失败，当前浏览器可能未安装签名控件') 
        
        # 民生银行输入框有点问题，检测不到输入内容，因此不做检测
        username_input = web_page.find("民生银行-个人版账号输入框")
        web_page.find("民生银行-个人版账号输入框").click()
        username_input.input(username)
       
        # 填写密码输入框，密码输入框无法获取元素信息，暂时不添加检测
        password_input = web_page.find("民生银行-个人版密码输入框")
        password_input.hover()
        win32.mouse_click()
        win32.send_keys(password,hardware_driver_input=True)
        # 点击复选框
        sleep(1)
        # 点击登录
        web_page.find('民生银行-个人版登录按钮').click()
        sleep(3)
        # 获取一下登录之后的信息，比如账号或者密码错误啥的
        if web_page.is_element_displayed("民生银行-个人版登录之后的错误提示"):
            load_message = web_page.find("民生银行-个人版登录之后的错误提示")
            text = load_message.get_text()
            raise Exception(text)


def main(args):
    # web_page = args.get('web_page',web.get_active(mode='edge'))
    web_page = args.get('web_page','')
    load_type = args.get("load_type", "个人网上银行")
    username = args.get("username", "@qq.com")
    password = args.get("password", "")
    nper_bank__login(web_page,load_type,username,password)
