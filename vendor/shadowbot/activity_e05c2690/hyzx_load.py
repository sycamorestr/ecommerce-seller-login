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


def hyzx_bank_login(web_page,  ai_engine:str,username:str,password:str,ym_token:str):
    """杭州银行登录
    :param web_page: , 网页对象
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    """
    url = "https://hyzx.hzbank.com.cn/hykx/logon.jsp"
    web_page.navigate(url,load_timeout=40)


    if web_page.is_element_displayed("杭州银行-控件安装检测提示"):
        result=web_page.find('杭州银行-控件安装检测提示').get_text()
        raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')
    # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
    username_input = web_page.find("杭州银行-账号输入框")
    username_input.click()
    for i in range(1,4):
        username_input = web_page.find("杭州银行-账号输入框")
        username_input.input(username)
        text = username_input.get_text()
        if text == username:
            break
        if i == 3:
            raise Exception("输入失败，请手动登录")

    password_input = web_page.find("杭州银行-密码输入框")
    password_input.click()
    win32.send_keys(password,hardware_driver_input=True)
    
    # 判断有没有验证码的情况
    if web_page.is_element_displayed("杭州银行-验证码图像"):
        
        # 识别验证码
        captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
                                                        ele = package.selector("杭州银行-验证码图像"),
                                                        captcha_type = '10103',
                                                        token = ym_token, is_trim=True, timeout=20)
        print('验证码识别结果为:',captcha_result)
        captcha_input = web_page.find("杭州银行-验证码输入框")    
        web_page.find("杭州银行-验证码输入框").click()   
        for i in range(1,4):
            captcha_input.input(captcha_result)
            text = captcha_input.get_text()
            if text == captcha_result:
                break
            if i == 3:
                raise Exception("验证码输入失败，请手动登录")
        
    web_page.find("杭州银行-登录按钮").click()
    if web_page.is_element_displayed("杭州银行-登录错误提示"):
        result=web_page.find('杭州银行-登录错误提示内容').get_text()
        raise Exception(f'登录失败,提示信息为{result}')




def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    username = args.get("username", "17756164")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    hyzx_bank_login(web_page = web_page,
                    ai_engine = ai_engine,
                    username = username,
                    password = password,
                    ym_token = ym_token)
