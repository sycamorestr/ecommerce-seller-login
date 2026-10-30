# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package

from xbot_extensions.activity_jfbym import std_alphanum_captcha,std_click_select_captcha
from .utils import get_xbot_activity_cache_folder
import xbot_visual
import os
import base64


def shanghai_bank_login(web_page, load_type:str, ai_engine:str,username:str, password:str,ym_token:str,try_count:int):
    """上海银行登录
    :param web_page: , 网页对象
    :param load_type:登录方式
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    :param try_count: int 重试次数
    """

    if load_type=='个人网上银行':
        url = "https://ebanks.bankofshanghai.com/pweb/prelogin.do?LoginType=R&_locale=zh_CN"
        web_page.navigate(url,load_timeout=40)
        if web_page.is_element_displayed("上海银行-个人版密码控件提示"):
            result=web_page.find('上海银行-个人版密码控件提示').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')

        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("上海银行-个人版账号输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("上海银行-个人版账号输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        password_input = web_page.find("上海银行-个人版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)
        
        if web_page.is_element_displayed("上海银行-个人版验证码图片"):

            captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
                                                            ele = package.selector("上海银行-个人版验证码图片"),
                                                            captcha_type = '10103',
                                                            token = ym_token, is_trim=True, timeout=20)
            print('验证码识别结果为:',captcha_result)
            captcha_input = web_page.find("上海银行-个人版验证码输入框")    
            web_page.find("上海银行-个人版验证码输入框").click()   
            for i in range(1,4):
                captcha_input.input(captcha_result)
                text = captcha_input.get_text()
                if text == captcha_result:
                    break
                if i == 3:
                    raise Exception("验证码输入失败，请手动登录")
        
        if not web_page.is_element_displayed("上海银行-个人版密码控件提示"):
            web_page.find("上海银行-个人版协议复选框-未选择状态").click()

        web_page.find("上海银行-个人版登录按钮").click()
        sleep(3)
        if web_page.is_element_displayed("上海银行-个人版登录之后的提示"):
            result=web_page.find('上海银行-个人版登录之后的提示').get_text()
            raise Exception(f'登录失败,提示信息为{result}')

    elif load_type=='企业网上银行':
        url = "https://ibank.bosc.cn:6074/eib/?#/login"
        web_page.navigate(url,load_timeout=40)
        sleep(3)
        if web_page.is_element_displayed("上海银行-企业版密码控件安装提示"):
            result=web_page.find('上海银行-企业版密码控件安装提示').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')
        
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("上海银行-企业版用户名输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("上海银行-企业版用户名输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        password_input = web_page.find("上海银行-企业版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)

        web_page.find("上海银行-企业版登录按钮").click()
        sleep(3)
        for i in range(1,try_count+1):
            if web_page.is_element_displayed("上海银行-企业版验证码图片"):
                web_page.find("上海银行-企业版验证码刷新按钮").click()
                sleep(1)
                if web_page.is_element_displayed("上海银行-企业版验证码请点击重试"):
                     web_page.find("上海银行-企业版验证码请点击重试").click()
                     sleep(1)
                try:
                    std_click_select_captcha.handle_captcha(web_page = web_page,
                                            web_element = package.selector("上海银行-企业版验证码识别图"),
                                            direction = 'bottom',
                                            retry_count = 1,
                                            ym_token = ym_token)
                except Exception as e:
                    print(f"当前验证码暂时无法识别,报错日志为{e}")
            else:
                break
        if web_page.is_element_displayed("上海银行-企业版登录后的提示"):
            result =  web_page.find("上海银行-企业版登录之后的提示内容").get_text()
            raise Exception(f"登录失败,提示内容为{result}")
        

def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    load_type = args.get('load_type','企业网上银行')
    username = args.get("username", "")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    try_count = args.get("try_count", 5)
    shanghai_bank_login(web_page = web_page,
                    ai_engine = ai_engine,
                    load_type = load_type,
                    username = username,
                    password = password,
                    ym_token = ym_token,
                    try_count = try_count)
