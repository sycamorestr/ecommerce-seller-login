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


def enbcb__login(web_page, load_type:str, ai_engine:str,username:str, password:str,customer:str,ym_token:str,tujian_username:str,tujian_password:str):
    """宁波登录
    :param web_page: , 网页对象
    :param load_type:登录方式
    :param ai_engine: str, 验证码识别引擎
    :param customer:str,客户号
    :param username: str, 账号
    :param password: str, 密码
    :param ym_token: str, 云码Token
    :param tujian_username: str, 图鉴账户
    :param tujian_password: str, 图鉴密码：
    """
    if load_type=='个人网上银行':
        url = "https://e.nbcb.com.cn/#/main"
        web_page.navigate(url,load_timeout=40)
        sleep(3)
  
        if web_page.is_element_displayed("宁波银行-个人版控件检测"):
            result=web_page.find('宁波银行-个人版控件检测').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')
        
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况   
        username_input = web_page.find("宁波银行-个人版账号输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("宁波银行-个人版账号输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        
        # 填写密码框，这部分需要使用驱动输入，文档中需要注明
        password_input = web_page.find("宁波银行-个人版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)

    
        if web_page.is_element_displayed("宁波银行-个人版登录复选框"):
            web_page.find("宁波银行-个人版登录复选框").click()
        
      
        # sleep(3)
        if web_page.is_element_displayed("宁波银行-个人版验证码背景图"):
            # 宁波银行要先点击一下滑块
            web_page.find('宁波银行-个人版验证码滑块').click()
            # ele = web_page.find('宁波银行-个人版验证码滑块')
            
            # ele.click()
            ele = web_page.find('宁波银行-个人版验证码缺口图片')
            ele.set_attribute('style','display:block;opacity:1;')
            # win32.mouse_click(click_type='up')
            web_page.find('宁波银行-个人版验证码背景图').hover()
            sleep(2)
            for i in range(1,3):
                try :
                    std_slider_captcha.handle_captcha(web_page = web_page,
                                                    background_ele = package.selector("宁波银行-个人版验证码背景图"),
                                                    drag_ele = package.selector("宁波银行-个人版验证码滑块"),
                                                    retry_count = 1,
                                                    offset = 0 , 
                                                    speed = 1,
                                                    ym_token = ym_token)
                except Exception as e:
                    print(e,"点击刷新重试图片中")
                    web_page.find("宁波银行-个人版账号输入框").click()
                    sleep(0.5)
                    web_page.find("宁波银行-个人版密码输入框").click()

                    if web_page.is_element_displayed("宁波银行-个人版验证码请重试"):
                        web_page.find("宁波银行-个人版验证码请重试").click()

                    if i ==3:
                        raise Exception(f'登录失败,当前网页的提示信息为{result}') 

                if web_page.is_element_displayed("宁波银行-个人版验证码验证成功"):
                    break
                elif web_page.is_element_displayed("宁波银行-个人版验证码请重试"):
                    web_page.find("宁波银行-个人版验证码请重试").click()
                    sleep(1)

     
        web_page.find("宁波银行-个人版登录按钮").click()
        

        if web_page.is_element_displayed("宁波银行-个人版登录之后的提示"):
            result=web_page.find('宁波银行-个人版登录之后的提示内容').get_text()
            raise Exception(f'登录失败,当前网页的提示信息为{result}') 

    elif load_type=='企业网上银行':
        url = "https://cb.nbcb.com.cn/microbase/microhome/index.html?v=1730441864266#/browserQueryLogin"
        web_page.navigate(url,load_timeout=40)

        # 输入客户号
        customer_input = web_page.find("宁波银行-企业版客户号输入框")
        customer_input.click()
        for i in range(1,4):
            customer_input = web_page.find("宁波银行-企业版客户号输入框")
            customer_input.input(customer)
            text = customer_input.get_text()
            if text == customer:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        # 输入用户号
        username_input = web_page.find("宁波银行-企业版用户号输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("宁波银行-企业版用户号输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")
        
        # 填写密码框，这部分需要使用驱动输入，文档中需要注明
        password_input = web_page.find("宁波银行-企业版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)
        sleep(2)

        # 点击登录
        web_page.find("宁波银行-企业版登录按钮").click()
        
        # 判断验证码是否可见
        for i in range(1,5):
                                
            if web_page.is_element_displayed("宁波银行-企业版点选验证码背景图"):
            
                xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.process21", package=__name__, inputs={
                "网页对象": web_page,
                "识别模式": "点选3~5个坐标",
                "验证码图片": package.selector("宁波银行-企业版点选验证码背景图"),
                "点选提示": package.selector("宁波银行-企业版点选验证码提示图"),
                "图鉴账号": tujian_username,
                "图鉴密码": tujian_password,
                },
                outputs=[]
            )
                web_page.find("宁波银行-企业版验证码验证按钮").click()
                sleep(2)
            else:
                break
        if web_page.is_element_displayed("宁波银行-企业版登录之后的提示"):
            result=web_page.find('宁波银行-企业版登录之后的提示内容').get_text()
            raise Exception(result)
        

   


def main(args):
    
    web_page = args.get('web_page',web.get_active(mode='chrome'))
    ai_engine = args.get("ai_engine","xbot")ad_type = args.get('load_type','企业网上银行')
    customer = args.get('customer','3234555544')
    username = args.get("username", "177")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    tujian_username = args.get("tujian_username", "")
    tujian_password = args.get("tujian_password", "")
    enbcb__login(web_page = web_page,
                    ai_e    e = ai_engine,
                    load    e = load_type,
                    cust     = customer,
                    user     = username,
                    pass     = password,
                    ym_t     = ym_token,
                    tuji    sername = tujian_username,
                    tuji    assword = tujian_password)
