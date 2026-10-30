# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package

from xbot_extensions.activity_jfbym import std_alphanum_captcha
from .utils import get_xbot_activity_cache_folder
import xbot_visual
import os
import base64


def ccb_bank_login(web_page, load_type:str, ai_engine:str,username:str, password:str,ym_token:str):
    """中国建设银行登录，目前只有个人版
    :param web_page: , 网页对象
    :param load_type:登录方式
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    """

    if load_type=='个人网上银行':
        url = "https://ebanking1.ccb.com.cn/CCBIS/V6/common/loginNew.jsp"
        web_page.navigate(url,load_timeout=40)
        sleep(3)

        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况  
        if not web_page.is_element_displayed("中国建设银行-账号输入框"):
            web_page.find("中国建设银行-登录切换图片").click()
        
        username_input = web_page.find("中国建设银行-账号输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("中国建设银行-账号输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        password_input = web_page.find("中国建设银行-密码输入框").input(password)

        if web_page.is_element_displayed("中国建设银行-验证码图片"):
            captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
                                                                ele = package.selector("中国建设银行-验证码图片"),
                                                                captcha_type = '10103',
                                                                token = ym_token, is_trim=True, timeout=20)
            print('验证码识别结果为:',captcha_result)
            captcha_input = web_page.find("中国建设银行-验证码输入框")    
            web_page.find("中国建设银行-验证码输入框").click()   
            for i in range(1,4):
                captcha_input.input(captcha_result)
                text = captcha_input.get_text()
                if text == captcha_result:
                    break
                if i == 3:
                    raise Exception("验证码输入失败，请手动登录")   
        
        web_page.find("中国建设银行-登录按钮").click()
        sleep(3)
        if web_page.is_element_displayed("中国建设银行-登录之后的状态"):
            result=web_page.find('中国建设银行-登录之后的提示').get_text()
            raise Exception(f'登录失败,当前网页的提示信息为{result}') 
   


def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    load_type = args.get('load_type','个人网上银行')
    username = args.get("username", "")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    ccb_bank_login(web_page = web_page,
                    ai_engine = ai_engine,
                    load_type = load_type,
                    username = username,
                    password = password,
                    ym_token = ym_token)
