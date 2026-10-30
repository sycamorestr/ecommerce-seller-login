# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package

from xbot_extensions.activity_jfbym import std_alphanum_captcha,std_slider_captcha
from .orangebank_slider_captcha import deal_deal_handle_captcha
from .utils import get_xbot_activity_cache_folder
import xbot_visual
import os
import base64


def beijing_bank_login(web_page, load_type:str, ai_engine:str,username:str, password:str,
                       ym_token:str,try_count:int,drag_distance:int,
                       tujian_username:int,
                       tujian_password:int):
    """北京银行登录,区分企业版和个人版
    :param web_page: , 网页对象
    :param load_type:登录方式
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    :param try_count: int 重试次数
    """
    if load_type=='个人网上银行':
        url = "https://ibank.bankofbeijing.com.cn/login?redirect=%2F"
        web_page.navigate(url,load_timeout=40)
        if web_page.is_element_displayed("北京银行-个人版登录界面引导提示"):
            result=web_page.find('北京银行-个人版登录界面引导提示').click()

        if web_page.is_element_displayed("北京银行-个人版安装控件提示"):
            result=web_page.find('北京银行-个人版安装控件提示').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')

        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("北京银行-个人版账号输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("北京银行-个人版账号输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        password_input = web_page.find("北京银行-个人版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)
        
        web_page.find("北京银行-个人版登录按钮").click()
        sleep(3)
        
        # 判断验证码是否可见
        if web_page.is_element_displayed("北京银行-个人版验证码背景图"):
        
            deal_deal_handle_captcha(web_page = web_page,
                                    background_ele = '北京银行-个人版验证码背景图',
                                    drag_ele = '北京银行-个人版验证码滑块图',
                                    gap_ele = '北京银行-个人版验证码缺口图',
                                    refresh_ele = '北京银行-个人版验证码刷新图',
                                    retry_count = try_count,
                                    ym_token = ym_token,
                                    drag_distance = drag_distance)
        
        if web_page.is_element_displayed("北京银行-个人版登录之后的提示"):
            result=web_page.find('北京银行-个人版登录之后的提示内容').get_text()
            raise Exception(f'登录失败,提示信息为{result}')

    elif load_type=='企业网上银行':
        for i in range(1,5):
            url = "https://cbank.bankofbeijing.com.cn/login?version=query"
            web_page.navigate(url,load_timeout=40)
            sleep(3)
            if web_page.is_element_displayed('北京银行登录_提示'):
                web_page.find('北京银行登录_提示取消').click()
            web_page.find("北京银行-企业版网银查询版").click()

            if web_page.is_element_displayed("北京银行-企业版控件安装提示"):
                result=web_page.find('北京银行-企业版控件安装提示').get_text()
                raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}')
            
            # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
            username_input = web_page.find("北京银行-企业版账号输入框")
            username_input.click()
            for i in range(1,4):
                username_input = web_page.find("北京银行-企业版账号输入框")
                username_input.input(username)
                text = username_input.get_text()
                if text == username:
                    break
                if i == 3:
                    raise Exception("输入失败，请手动登录")

            password_input = web_page.find("北京银行-企业版密码输入框")
            password_input.click()
            win32.send_keys(password,hardware_driver_input=True)

            # 将鼠标悬停在验证码上面,并设置验证码的背景图
            web_page.find('北京银行-企业版验证码滑块').hover()
            ele = web_page.find('北京银行-企业版验证码容器')
            ele.set_attribute('style','display:block;opacity:1;')
            sleep(1)
            # 处理验证码
            deal_deal_handle_captcha(web_page = web_page,
                                    background_ele = '北京银行-企业版验证码背景图',
                                    drag_ele = '北京银行-企业版验证码滑块',
                                    gap_ele = '北京银行-企业版验证码缺口图片',
                                    refresh_ele = '',
                                    retry_count = try_count,
                                    ym_token = ym_token,
                                    drag_distance = drag_distance)
            
                    
            if web_page.is_element_displayed("北京银行-企业版点选验证码背景图"):
            
                xbot_visual.process.run(process="xbot_extensions.activity_4db973e3.process21", package=__name__, inputs={
                "网页对象": web_page,
                "识别模式": "点选1~4个坐标",
                "验证码图片": package.selector("北京银行-企业版点选验证码背景图"),
                "点选提示": package.selector("北京银行-企业版点选验证码提示"),
                "图鉴账号": tujian_username,
                "图鉴密码": tujian_password,
                },
                outputs=[]
            )
                 
            if web_page.is_element_displayed("北京银行-企业版验证码验证成功"):
                web_page.find('北京银行-企业版登录按钮').click()
                sleep(2)
                # 账户密码错误会出现弹窗
                # 可能会出现一些特殊情况的提示
                if web_page.is_element_displayed("北京银行-企业版登录失败提示"):
                    load_message = web_page.find("北京银行-企业版登录失败内容")
                    text = load_message.get_text()
                    raise Exception(text)
                break


def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page', web.get_active(mode='chrome'))
    ai_engine = args.get("ai_engine", "xbot")
    load_type = args.get('load_type','企业网上银行')
    username = args.get("username", "")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    tujian_username = args.get("tujian_username", "")
    tujian_password = args.get("tujian_password", "")
    try_count = args.get("try_count", 5)
    drag_distance =  args.get("drag_distance", 0)
    beijing_bank_login(web_page = web_page,
                    ai_engine = ai_engine,
                    load_type = load_type,
                    username = username,
                    password = password,
                    ym_token = ym_token,
                    tujian_username = tujian_username,
                    tujian_password = tujian_password,
                    try_count = try_count,
                    drag_distance = drag_distance)
