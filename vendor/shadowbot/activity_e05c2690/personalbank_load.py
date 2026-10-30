# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package

from xbot_extensions.activity_jfbym import std_alphanum_captcha


def personal_bank_login(web_page, load_type:str,sign_method:str,username:str, password:str):
    """兴业银行登录，目前只有个人银行能做
    :param web_page: , 网页对象
    :param load_type: str, 登录方式
    :param sign_method:str 账号登录方式
    :param username: str, 账号
    :param password: str, 密码
    """
    url = "https://personalbank.cib.com.cn/pers/main/loginV7"
    web_page.navigate(url,load_timeout=40)
    
    # 选择登录方式：卡号、登录名、客户号
    sleep(2)
    
    if web_page.is_element_displayed("兴业银行-登录之后的内容提示"):
        raise Exception('兴业银行个人网上银行未检测到安全控件!请根据网页提示安装控件')
    
    web_page.find_by_xpath(f'//ul/li/a[text()="{sign_method}"]').click()
    
    # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
    username_input = web_page.find("兴业银行-登录名或客户号输入框")
    web_page.find("兴业银行-登录名或客户号输入框").click()
    for i in range(1,4):
        username_input.input(username)
        text = username_input.get_text()
        print(text,username)
        if text == username:
            break
        if i == 3:
            raise Exception("账号入失败，请手动登录")

    # 填写密码输入框，并检测密码输入情况，检测三次，避免输入的时候可能会出现多个a的情况
    password_input = web_page.find("兴业银行-密码输入框")
    web_page.find("兴业银行-密码输入框").click()
    for i in range(1,4):
        password_input.input(password)
        text = password_input.get_text()
        if text == password:
            break
        if i == 3:
            raise Exception("密码输入失败，请手动登录")
    # 等待
    sleep(2)
    # 直接登录，好像没有验证码
    web_page.find("兴业银行-登录按钮").click()
        
    # 获取一下登录之后的信息，比如账号或者密码错误啥的
    if web_page.is_element_displayed("兴业银行-登录之后的内容提示"):
        load_message = web_page.find("兴业银行-登录之后的内容提示")
        text = load_message.get_text()
        raise Exception(text)
    


def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    username = args.get("username", "")
    sign_method = args.get("sign_method", "客户号")
    load_type = args.get("load_type", "手机银行账户")
    password = args.get("password", "")
    personal_bank_login(web_page = web_page,
                     sign_method = sign_method,
                     load_type = load_type,
                     username = username,
                     password = password)
