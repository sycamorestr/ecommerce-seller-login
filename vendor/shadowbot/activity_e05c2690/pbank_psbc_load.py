# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package

from xbot_extensions.activity_jfbym import std_alphanum_captcha,std_slider_captcha
from .utils import get_xbot_activity_cache_folder
import xbot_visual
import os
import base64


def pbank_psbc_login(web_page, load_type:str, ai_engine:str,username:str, password:str,ym_token:str):
    """中国邮政储蓄银行，目前只有个人版
    :param web_page: , 网页对象
    :param load_type:登录方式
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    """
    if load_type=='个人网上银行':
        url = "https://pbank.psbc.com/perbank/"
        web_page.navigate(url,load_timeout=40)
        sleep(3)

        if web_page.is_element_displayed("中国邮政储蓄银行-个人版控件安装提示"):
            result=web_page.find('中国邮政储蓄银行-个人版控件安装提示').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')
        
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况   
        username_input = web_page.find("中国邮政储蓄银行-个人版账号输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("中国邮政储蓄银行-个人版账号输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        
        # 填写密码框，这部分需要使用驱动输入，文档中需要注明
        password_input = web_page.find("中国邮政储蓄银行-个人版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)

        web_page.find("中国邮政储蓄银行-个人版登录按钮").click()
        sleep(3)
        if web_page.is_element_displayed("中国邮政储蓄银行-个人版滑块验证码背景图"):
            std_slider_captcha.handle_captcha(web_page = web_page,
                                            background_ele = package.selector("中国邮政储蓄银行-个人版滑块验证码背景图"),
                                            drag_ele = package.selector("中国邮政储蓄银行-个人版验证码滑块"),
                                            retry_count = 5,
                                            offset = 0 , 
                                            speed = 1,
                                            ym_token = ym_token)

        
        if web_page.is_element_displayed("中国邮政储蓄银行-个人版登录之后状态提示"):
            result=web_page.find('中国邮政储蓄银行-个人版登录之后状态提示内容').get_text()
            raise Exception(f'登录失败,当前网页的提示信息为{result}') 
    
def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    load_type = args.get('load_type','个人网上银行')
    username = args.get("username", "")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    pbank_psbc_login(web_page = web_page,
                    ai_engine = ai_engine,
                    load_type = load_type,
                    username = username,
                    password = password,
                    ym_token = ym_token)
