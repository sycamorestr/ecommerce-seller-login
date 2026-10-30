# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package

from xbot_extensions.activity_jfbym import std_alphanum_captcha


def ebankp_wzbank_login(web_page,load_type:str, username:str, password:str):
    """温州银行登录,企业版暂无法驱动输入
    :param web_page: , 网页对象
    :param load_type:登录方式
    :param username: str, 账号
    :param password: str, 密码
    """

    if load_type=='个人网上银行':
        url = "https://ebankp.wzbank.cn/ebank/static/index.html#/home"
        web_page.navigate(url,load_timeout=40)
        web_page.reload(load_timeout=40)
        
        # 点击用户登录
        web_page.find("温州银行-个人版用户登录按钮").click()
        sleep(2)
        # 先检测用户有没有安装控件，从密码输入框的提示可以判断是否安装控件
        if web_page.is_element_displayed("温州银行-个人版密码控件检测"):
            raise Exception('温州银行-个人版密码控件检测')
        
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("温州银行-个人版用户名输入框")
        web_page.find("温州银行-个人版用户名输入框").click()
        for i in range(1,4):
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")
       
        # 填写密码框，这部分需要使用驱动输入，文档中需要注明
        password_input = web_page.find("温州银行-个人版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)

        web_page.find('温州银行-个人版登录按钮').click()

        # 获取一下登录之后的信息，比如账号或者密码错误啥的
        if web_page.is_element_displayed("温州银行-个人版登录之后的提示"):
            load_message = web_page.find("温州银行-个人版登录之后的提示内容")
            text = load_message.get_text()
            raise Exception(text)

def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    load_type = args.get('load_type','个人网上银行') 
    username = args.get("username", "")
    password = args.get("password", "")
    ebankp_wzbank_login(web_page = web_page,
                    load_type = load_type,
                    username = username,
                    password = password)

