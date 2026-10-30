# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package
from .package import variables as glv
from .orangebank_slider_captcha import deal_deal_handle_captcha
from xbot_extensions.activity_jfbym import std_alphanum_captcha,std_click_select_captcha


def czbank_bank_login(web_page, ai_engine:str,load_type:str, username:str, password:str, ym_token:str):
    """浙商银行登录
    :param web_page: , 网页对象
    :param ai_engine: str, 验证码识别引擎
    :param load_type: str,登录类型
    :param username: str, 账号
    :param password: str, 密码
    :param ym_token: str, 云码 token
    """
    
    if load_type=='个人网上银行':
    
        url = "https://perbank.czbank.com/PERBANK/logon.jsp"
        web_page.navigate(url,load_timeout=40)
        web_page.reload(load_timeout=40)
        
        if web_page.is_element_displayed("浙商银行-个人版密码控件检测"):
            result=web_page.find('浙商银行-个人版密码控件检测').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}') 
        
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("浙商银行-个人版账号输入框")
        web_page.find("浙商银行-个人版账号输入框").click()
        for i in range(1,4):
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")
       
        # 填写密码输入框，密码输入框无法获取元素信息，暂时不添加检测
        password_input = web_page.find("浙商银行-个人版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)
        # 等待
        sleep(2)
        # 判断验证码是否可见
        if web_page.is_element_displayed("浙商银行-个人版验证码图像"):
            
            captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
                                                                ele = package.selector("浙商银行-个人版验证码图像"),
                                                                captcha_type = '10103',
                                                                token = ym_token, is_trim=True, timeout=20)
            print('验证码识别结果为:',captcha_result)
            captcha_input = web_page.find("浙商银行-个人版验证码输入框")    
            web_page.find("浙商银行-个人版验证码输入框").click()   
            for i in range(1,4):
                captcha_input.input(captcha_result)
                text = captcha_input.get_text()
                if text == captcha_result:
                    break
                if i == 3:
                    raise Exception("验证码输入失败，请手动登录")
        
        # 点击登录
        web_page.find('浙商银行-个人版登录按钮').click()
        sleep(3)
        # 获取一下登录之后的信息，比如账号或者密码错误啥的
        if web_page.is_element_displayed("浙商银行-个人版登录之后的提示"):
            load_message = web_page.find("浙商银行-个人版登录之后的提示内容")
            text = load_message.get_text()
            raise Exception(text)

    if load_type=='企业网上银行':
        url = "https://corbank.czbank.com/CORPORBANK/logon.jsp"
        web_page.navigate(url,load_timeout=40)
        web_page.reload(load_timeout=40)


        if web_page.is_element_displayed("浙商银行-企业版密码控件检测"):
            result=web_page.find('浙商银行-企业版密码控件检测').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}') 
        
        # 点击切换到账号密码输入
        web_page.find('浙商银行-企业版登录号登录').click()  

        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("浙商银行-企业版账号输入框")
        web_page.find("浙商银行-企业版账号输入框").click()
        for i in range(1,4):
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        # 填写密码输入框，密码输入框无法获取元素信息，暂时不添加检测
        password_input = web_page.find("浙商银行-企业版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)

        # 勾选策略
        web_page.find('浙商银行-请先阅读并同意-勾选框').check(mode='check')
            # 点击登录
        web_page.find('浙商银行-企业版登录按钮').click()
     
        sleep(3)
        # 获取一下登录之后的信息，比如账号或者密码错误啥的
        if web_page.is_element_displayed("浙商银行-企业版登录之后提示"):
            load_message = web_page.find("浙商银行-企业版登录之后提示内容")
            text = load_message.get_text()
            raise Exception(text)
        
        





def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    load_type = args.get("load_type", "企业网上银行")
    username = args.get("username", "@qq.com")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    czbank_bank_login(web_page,ai_engine,load_type,username,password,ym_token)
