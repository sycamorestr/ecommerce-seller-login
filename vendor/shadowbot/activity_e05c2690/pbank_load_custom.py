# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package

from xbot_extensions.activity_jfbym import std_alphanum_captcha,std_slider_captcha, std_slider_change_captcha
from .utils import get_xbot_activity_cache_folder
import xbot_visual
import os
import base64


def pbank_bank_login(web_page, ai_engine:str,custome_num:str,user_num:str, password:str,ym_token:str,retry_count:int,offset:int):
    """交通银行登录
    :param web_page: , 网页对象
    :param load_type:登录方式
    :param ai_engine: str, 验证码识别引擎
    :param custome_num: str, 客户号
    :param user_num: str, 用户号
    :param password: str, 密码
    :param retry_count : int,重试次数
    :param offset : int,偏移距离
    """

    url = "https://ebank.bankcomm.cn/NEBS/CLG/CNLGAAA01?loginType=1"
    web_page.navigate(url,load_timeout=40)
    sleep(3)
    if web_page.is_element_displayed("交通银行-企业版控件检测"):
        result=web_page.find('交通银行-企业版控件检测').get_text()
        raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')
    
    # 切换到客户号登录
    web_page.find("交通银行-企业版客户号登录").click()
            
    # 填写客户号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
    customer_input = web_page.find("交通银行-企业版客户号输入框")
    customer_input.click()
    customer_input = web_page.find("交通银行-企业版客户号输入框")
    customer_input.input(custome_num)
        
    # 填写用户号
    username_input = web_page.find('交通银行-企业版用户编号输入')
    username_input.click()
    username_input = web_page.find("交通银行-企业版用户编号输入")
    username_input.input(user_num)
    
    password_input = web_page.find("交通银行-企业版客户号密码输入框")
    password_input.click()
    win32.send_keys(password,hardware_driver_input=True)
    
    web_page.find("交通银行-企业版登录按钮").click()
    
    # 判断有没有验证码的情况
    for i in range(1,retry_count+1):
        if i == retry_count+1:
            raise Exception('验证码识别失败，请手动登录')
        if web_page.is_element_displayed("交通银行-企业版验证码背景图"):
            
            # 验证码的重试机制
            std_slider_change_captcha.handle_captcha(web_page=web_page,
                                                    background_ele=package.selector("交通银行-企业版验证码背景图"),
                                                    drag_ele=package.selector("交通银行-企业版验证码滑块"),
                                                    retry_count=1,
                                                    offset=offset,
                                                    ym_token=ym_token,
                                                    refresh_elem=package.selector("交通银行-企业版验证码刷新按钮"),
                                                    target_ele=package.selector("交通银行-企业版验证码目标元素"))
            if web_page.is_element_displayed("交通银行-企业版验证码识别结果"):
                web_page.find("交通银行-企业版验证码确定按钮").click()
                sleep(1)
                web_page.find("交通银行-企业版验证码刷新按钮").click()
        else:
            break

    web_page.find("交通银行-企业版登录按钮").click()
    if web_page.is_element_displayed("交通银行-企业版客户号登录之后提示"):
        result=web_page.find('交通银行-企业版客户号登录之后提示内容').get_text()
        raise Exception(f'登录失败,提示信息为{result}')

def test_func():
    if "xbot_extensions" not in __file__:
        web_page = web.get_active(mode='chrome')
        ai_engine = "ym"
        custome_num = ""
        user_num = ""
        password = ""
        ym_token = ""
        retry_count = 3
        offset = 0
        pbank_bank_login(web_page = web_page,
                        ai_engine = ai_engine,
                        custome_num = custome_num,
                        user_num = user_num,
                        password = password,
                        ym_token = ym_token,
                        retry_count = retry_count,
                        offset = offset)
        exit()

def main(args):
    test_func()
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    custome_num = args.get("custome_num", "")
    user_num = args.get("user_num", "")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    retry_count = args.get("retry_count",3)
    offset = args.get("offset",-5)
    pbank_bank_login(web_page = web_page,
                    ai_engine = ai_engine,
                    custome_num = custome_num,
                    user_num = user_num,
                    password = password,
                    ym_token = ym_token,
                    retry_count = retry_count,
                    offset = offset)
