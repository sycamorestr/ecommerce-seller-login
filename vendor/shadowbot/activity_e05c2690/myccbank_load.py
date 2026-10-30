# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package

from xbot_extensions.activity_jfbym import chinatax_captcha
from .utils import get_xbot_activity_cache_folder
import xbot_visual
import os
import base64


def mycc_bank_login(web_page, load_type:str, ai_engine:str,username:str, password:str):
    """绵阳市商业银行登录
    :param web_page: , 网页对象
    :param load_type:登录方式
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    """
    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")   

    if load_type=='个人网上银行':
        url = "https://pweb.mycc-bank.com/pweb/vx_zh_CN/index.html#/loginapp/UserLogin"
        web_page.navigate(url,load_timeout=40)
    elif load_type=='企业网上银行':
        url = "https://eweb.mycc-bank.com/eweb/vx_zh_CN/index.html#/loginapp/UserLogin"
        web_page.navigate(url,load_timeout=40)  

    sleep(3)
    
    # 判断是否需要安装控件
    if web_page.is_element_displayed("绵阳市商业银行-企业网页提示"):
        result=web_page.find('绵阳市商业银行-企业网页提示内容').get_text()
        raise Exception(f'当前浏览器可能安装签名控件,提示信息为{result}')
    
    # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
    username_input = web_page.find("绵阳市商业银行-账户输入框")
    username_input.click()
    for i in range(1,4):
        username_input = web_page.find("绵阳市商业银行-账户输入框")
        username_input.input(username)
        text = username_input.get_text()
        if text == username:
            break
        if i == 3:
            raise Exception("输入失败，请手动登录")

    # 填写密码框，这部分需要使用驱动输入，文档中需要注明
    password_input = web_page.find("绵阳市商业银行-密码输入框").input(password)
    
    # 识别验证码
    if web_page.is_element_displayed("绵阳市商业银行-验证码图片"):
        # 先点击刷新验证码
        web_page.find("绵阳市商业银行-验证码图片").click()
        # 再点击验证码输入框
        web_page.find("绵阳市商业银行-验证码输入框").click()
        # 这部分需要将验证码和验证码提示框拼接，然后用影刀自带的验证码识别的去做，识别类型为问答模式
        captcha_x,captcha_y,captcha_width,captcha_height = web_page.find('绵阳市商业银行-验证码图片大框').get_bounding(relative_to='screen')
        tip_x,tip_y,tip_width,tip_height = web_page.find('绵阳市商业银行-验证码提示大框').get_bounding(relative_to='screen')       
        captcha_path = os.path.join(cache_folder, "screen_img.png")   
        xbot.win32.screenshot.save_screen_to_file(captcha_path, "png", captcha_x, captcha_y, captcha_x + captcha_width, tip_y + tip_height)     
        captcha_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="66", third_party_code="ttshitu_66_predict", image_source="image_file", 
                                                        image_file=captcha_path, image_browser=None, image_web_selector=None, image_window=None, image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser=None, imageback_web_selector=None, imageback_window=None, imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark="")
        
        web_page.find('绵阳市商业银行-验证码输入框').input(captcha_result)  
    
    # 点击登录 
    web_page.find("绵阳市商业银行-登录按钮").click()

    if web_page.is_element_displayed("绵阳市商业银行-登录之后的提示"):
        result=web_page.find('绵阳市商业银行-登录之后信息提示内容').get_text()
        raise Exception(f'登录失败,提示信息为{result}')


def main(args):
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    load_type = args.get('load_type','企业网上银行')
    username = args.get("username", "")
    password = args.get("password", "")
    mycc_bank_login(web_page = web_page,
                    ai_engine = ai_engine,
                    load_type = load_type,
                    username = username,
                    password = password)
