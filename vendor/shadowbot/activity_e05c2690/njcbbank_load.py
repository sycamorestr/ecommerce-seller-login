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


def nj_bank_login(web_page, load_type:str,username:str, password:str):
    """南京银行登录
    :param web_page: , 网页对象
    :param load_type:登录方式
    :param username: str, 账号
    :param password: str, 密码
    """
    if load_type=='个人网上银行':
        url = "https://ebank.njcb.com.cn/perbank/login.jsp"
        web_page.navigate(url,load_timeout=40)
        
        if web_page.is_element_displayed("南京银行-个人版控件安装检测"):
            result=web_page.find('南京银行-个人版控件安装检测').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')

        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("南京银行-个人版账号输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("南京银行-个人版账号输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        password_input = web_page.find("南京银行-个人版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)
        
        web_page.find("南京银行-个人版登录按钮").click()
        
        if web_page.is_element_displayed("南京银行-个人版滑动验证码"):
            for i in range(1,5):
            # 获取滑块长度
                x_1,y_1,width_1,height_1 = web_page.find("南京银行-个人版验证码滑块").get_bounding()
                # 获取滑条长度
                x_2,y_2,width_2,height_2 = web_page.find("南京银行-个人版验证码滑条").get_bounding()
                pos_center_x = x_1 + width_1 / 2
                pos_center_y = y_1 + height_1 / 2
                win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed='middle')
                win32.mouse_click(button="left", click_type="down")
                win32.manual_motion_on()
                win32.mouse_move(pos_center_x +width_2, pos_center_y, move_speed="middle")
                win32.manual_motion_off()
                win32.mouse_click(button="left", click_type="up")      

                sleep(3)
                if not web_page.is_element_displayed("南京银行-个人版滑动验证码"):
                    break

    elif load_type=='企业网上银行':
        url = "https://ebank.njcb.com.cn/corporbank/public/login.jsp"
        web_page.navigate(url,load_timeout=40)
        sleep(3)
        if web_page.is_element_displayed("南京银行-企业版控件安装检测"):
            result=web_page.find('南京银行-企业版控件安装检测').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("南京银行-企业版账号输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("南京银行-企业版账号输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")
      
        password_input = web_page.find("南京银行-企业版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)
      
        web_page.find("南京银行-企业版登录按钮").click()
        
        if web_page.is_element_displayed("南京银行-企业版错误提示"):
            result =  web_page.find("南京银行-企业版错误提示").get_text()
            raise Exception(f"登录失败,提示内容为{result}")
        

def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    load_type = args.get('load_type','个人网上银行')
    username = args.get("username", "12333332323")
    password = args.get("password", "11212121")
    nj_bank_login(web_page = web_page,
                    load_type = load_type,
                    username = username,
                    password = password,)
