# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package
from xbot_extensions.activity_jfbym import std_alphanum_captcha,std_click_select_captcha,std_slider_captcha
from .utils import get_xbot_activity_cache_folder
import xbot_visual
import os
import base64


def ebankhent_bank_login(web_page, load_type:str, ai_engine:str,username:str,customer:str, password:str,ym_token:str):
    """浦发银行登录
    :param web_page: , 网页对象
    :param load_type:登录方式
    :param ai_engine: str, 验证码识别引擎
    :param customer:str,客户号
    :param username: str, 账号
    :param password: str, 密码
    """

    if load_type=='企业网上银行':
        url = "https://ebankhent.spdb.com.cn/msent-web-login/qryLogin.do"
        web_page.navigate(url,load_timeout=40)
        if web_page.is_element_displayed("浦发银行-企业版密码控件检测"):
            result=web_page.find('浦发银行-企业版密码控件检测').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')

        # 填写客户号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        customer_input = web_page.find("浦发银行-企业版客户号输入框")
        customer_input.click()
        for i in range(1,4):
            customer_input = web_page.find("浦发银行-企业版客户号输入框")
            customer_input.input(customer)
            text = customer_input.get_text()
            if text == customer:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况   
        username_input = web_page.find("浦发银行-企业版用户输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("浦发银行-企业版用户输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")
       
       
       
        password_input = web_page.find("浦发银行-企业版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)
        
        web_page.find("浦发银行-企业版登录按钮").click()
        sleep(3)
        # web_page = xbot.web.get_active('chrome')  
        web_page.wait_appear('浦发银行-企业版验证码背景图')
        # 判断有没有验证码的情况
        for i in range(1,3):
            if web_page.is_element_displayed("浦发银行-企业版验证码背景图"):
                std_slider_captcha.handle_captcha(web_page = web_page,
                                                background_ele_in = package.selector("浦发银行-企业版验证码背景图"),
                                                drag_ele = package.selector("浦发银行-企业版验证码滑块"),
                                                retry_count = 1,
                                                offset = 0 , 
                                                speed = 1,
                                                ym_token = ym_token)
                sleep(2)
                if web_page.is_element_displayed("浦发银行-企业版验证码刷新按钮"):
                    web_page.find('浦发银行-企业版验证码刷新按钮').click()
                else:
                    break
            else:
                break

        if web_page.is_element_displayed("浦发银行-企业版登录之后提示"):
            result=web_page.find('浦发银行-企业版登录之后提示').get_text()
            raise Exception(f'登录失败,提示信息为{result}')

def test_func():
    """测试 ebankhent_bank_login 函数"""
    # 测试参数
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        ai_engine = 'xbot'
        load_type = '企业网上银行'
        username = ''
        customer = ''
        password = ''
        ym_token = ''

        # 调用登录函数
        ebankhent_bank_login(
            web_page=web_page,
            load_type=load_type,
            ai_engine=ai_engine,
            username=username,
            customer=customer,
            password=password,
            ym_token=ym_token
        )
        exit()

def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    test_func()
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    load_type = args.get('load_type','企业网上银行')
    username = args.get("username", "")
    customer = args.get("customer", "")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    ebankhent_bank_login(web_page = web_page,
                    ai_engine = ai_engine,
                    load_type = load_type,
                    username = username,
                    customer = customer,
                    password = password, 
                    ym_token = ym_token)
