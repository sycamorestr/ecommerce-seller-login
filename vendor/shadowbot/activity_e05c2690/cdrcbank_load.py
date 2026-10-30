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


def cdrc_bank_login(web_page, load_type:str, ai_engine:str,username:str, password:str):
    """成都农商银行登录，用影刀的标准指令识别gif验证码
    :param web_page: , 网页对象
    :param load_type:登录
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    """
    # 创建一个存放gif验证码的文件
    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    if load_type=='个人网上银行':
        url = "https://ebank.cdrcbank.com/perbank/"
        web_page.navigate(url,load_timeout=40)
        sleep(3)
        # 首先检测公告界面
        if web_page.is_element_displayed("成都农商银行-个人网银-网银公告"):
            web_page.find('成都农商银行-个人网银-公告关闭按钮').click()
      
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("成都农商银行-个人网银-账号输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("成都农商银行-个人网银-账号输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        # 填写密码框，这部分需要使用驱动输入，文档中需要注明
        password_input = web_page.find("成都农商银行-个人网银-密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)

        # 识别验证码
        web_page.start_monitor_network(url='https://ebank.cdrcbank.com/perbank/VerifyImage?update=*',use_wildcard=True)
        web_page.find('成都农商银行-个人网银-验证码图片').click()
        result = web_page.get_responses()
        web_page.stop_monitor_network()
        captcha_base64 =result[0]['body'] 
        captcha_path = os.path.join(cache_folder, "std_slider.gif")
        captcha_data = base64.b64decode(captcha_base64)
        with open(captcha_path, 'wb') as f:
            f.write(captcha_data)
        captcha_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="4", third_party_code="ttshitu_4_predict", image_source="image_file", image_file=captcha_path, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None)
        captcha_input = web_page.find("成都农商银行-个人网银-验证码输入框").input(captcha_result)
        # 点击登录
        web_page.find("成都农商银行-个人网银-登录按钮").click()
        if web_page.is_element_displayed("成都农商银行-个人网银-登录失败原因"):
            load_result=web_page.find('成都农商银行-个人网银-错误说明').get_text()
            raise Exception(f'登录失败，原因为{load_result}')
    elif load_type=='企业网上银行':
        url = "https://ebank.cdrcbank.com/corporbank/index.jsp"
        web_page.navigate(url,load_timeout=40)
        sleep(3)
        # 首先检测公告界面
        if web_page.is_element_displayed("成都农商银行-企业网银-网银公告"):
            web_page.find('成都农商银行-个人网银-公告关闭按钮').click()

        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("成都农商银行-企业网银-账号输入框")
        username_input.click()
        for i in range(1,4):
            username_input = web_page.find("成都农商银行-企业网银-账号输入框")
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        # 填写密码框，这部分需要使用驱动输入，文档中需要注明
        password_input = web_page.find("成都农商银行-企业网银-密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)

        # 识别验证码
        web_page.start_monitor_network(url='https://ebank.cdrcbank.com/corporbank/VerifyImage?update=*',use_wildcard=True)
        web_page.find('成都农商银行-企业网银-验证码图片').click()
        result = web_page.get_responses()
        web_page.stop_monitor_network()
        captcha_base64 =result[0]['body'] 
        captcha_path = os.path.join(cache_folder, "std_slider.gif")
        captcha_data = base64.b64decode(captcha_base64)
        with open(captcha_path, 'wb') as f:
            f.write(captcha_data)
        captcha_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="4", third_party_code="ttshitu_4_predict", image_source="image_file", image_file=captcha_path, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None)
        captcha_input = web_page.find("成都农商银行-企业网银-验证码输入框").input(captcha_result)
        # 点击登录
        web_page.find("成都农商银行-企业网银-登录按钮").click()
        # 需要插入uk,暂时无法判断是否登录成功

   



def main(args):
    web_page = args.get('web_page','')
    web_page = args.get('web_page',web.get_active(mode='chrome'))
    ai_engine = args.get("ai_engine", "xbot")
    load_type = args.get('load_type','企业网上银行')
    username = args.get("username", "@qq.com")
    password = args.get("password", "")
    cdrc_bank_login(web_page = web_page,
                    ai_engine = ai_engine,
                    load_type = load_type,
                    username = username,
                    password = password)
