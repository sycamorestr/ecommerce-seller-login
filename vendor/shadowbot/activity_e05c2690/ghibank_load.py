# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package

from xbot_extensions.activity_jfbym import std_alphanum_captcha


def ghi_bank_login(web_page, ai_engine:str, username:str, password:str, ym_token:str):
    """广东华兴银行登录
    :param web_page: , 网页对象
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    :param ym_token: str, 云码 token
    """
    url = "https://www.ghibank.com.cn/eweb/#/index"
    web_page.navigate(url,load_timeout=40)
    web_page.reload(load_timeout=40)
    
    # 点击用户登录
    web_page.find("广东华兴银行-用户登录").click()
    sleep(2)
    # 先检测用户有没有安装控件，从密码输入框的提示可以判断是否安装控件
    if web_page.is_element_displayed("广东华兴银行-请点此安装控件"):
        raise Exception('当前环境为安装银行控件，请检查控件是否安装')
    
    # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
    username_input = web_page.find("广东华兴银行-账号输入框")
    web_page.find("广东华兴银行-账号输入框").click()
    for i in range(1,4):
        username_input.input(username)
        text = username_input.get_text()
        if text == username:
            break
        if i == 3:
            raise Exception("输入失败，请手动登录")

    
    # 填写密码框，这部分需要使用驱动输入，文档中需要注明
    password_input = web_page.find("广东华兴银行-密码输入框")
    password_input.click()
    win32.send_keys(password,hardware_driver_input=True)
    # 等待
    sleep(2)
    # 判断验证码是否可见
    if web_page.is_element_displayed("广东华兴银行-验证码图像"):
        # 调用云码识别验证码的结果
        captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
                                                  ele = package.selector("广东华兴银行-验证码图像"),
                                                  captcha_type = '10103',
                                                  token = ym_token, is_trim=True, timeout=20)
        
        captcha_input = web_page.find("广东华兴银行-验证码输入框")
        web_page.find("广东华兴银行-验证码输入框").click()
        for i in range(1,4):
            captcha_input.input(captcha_result)
            text = captcha_input.get_text()
            if text == captcha_result:
                break
            if i == 3:
                raise Exception("验证码输入失败，请手动登录")
    
    # 点击登录
    web_page.find('广东华兴银行-登录按钮').click()
    sleep(3)
    # 获取一下登录之后的信息，比如账号或者密码错误啥的
    if web_page.is_element_displayed("广东华心银行-登录之后提示的日志"):
        load_message = web_page.find("广东华心银行-登录之后提示的日志")
        text = load_message.get_text()
        raise Exception(text)



def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    username = args.get("username", "@qq.com")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    ghi_bank_login(web_page,ai_engine,username,password,ym_token)
