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
import xbot_visual
from . import utils_jc

def icbc_bank_login(web_page, ai_engine:str,load_type:str, username:str, password:str, ym_token:str):
    """工商银行登录
    :param web_page: , 网页对象
    :param ai_engine: str, 验证码识别引擎
    :param load_type: str,登录类型
    :param username: str, 账号
    :param password: str, 密码
    :param ym_token: str, 云码 token
    """ 
    if load_type=='个人网上银行':
    
        url = "https://mybank.icbc.com.cn/icbc/newperbank/perbank3/frame/frame_index.jsp"
        web_page.navigate(url,load_timeout=40)
        web_page.reload(load_timeout=40)
        
        if web_page.is_element_displayed("工商银行-个人版密码控件检测"):
            result=web_page.find('工商银行-个人版密码控件检测').get_text()
            raise Exception(f'当前浏览器可能未安装签名控件,提示信息为{result}') 
        
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("工商银行-个人版账号输入框")
        web_page.find("工商银行-个人版账号输入框").click()
        for i in range(1,4):
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")

        
        # 填写密码输入框，密码输入框无法获取元素信息，暂时不添加检测
        password_input = web_page.find("工商银行-个人版密码输入框")
        password_input.click()
        win32.send_keys(password,hardware_driver_input=True)

        web_page.find("工商银行-个人版复选框").click()   
        # 等待
        sleep(2)
        # 判断验证码是否可见
        if web_page.is_element_displayed("工商银行-个人版验证码背景图"):
            
            captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
                                                                ele = package.selector("工商银行-个人版验证码背景图"),
                                                                captcha_type = '10103',
                                                                token = ym_token, is_trim=True, timeout=20)
            print('验证码识别结果为:',captcha_result)
            captcha_input = web_page.find("工商银行-个人版验证码输入框")    
            web_page.find("工商银行-个人版验证码输入框").click()   
            for i in range(1,4):
                captcha_input.input(captcha_result)
                text = captcha_input.get_text()
                if text == captcha_result:
                    break
                if i == 3:
                    raise Exception("验证码输入失败，请手动登录")
        
        # 点击登录
        web_page.find('工商银行-个人版登录按钮').click()
        sleep(3)
        # 获取一下登录之后的信息，比如账号或者密码错误啥的
        if web_page.is_element_displayed("工商银行-个人版登录之后的提示"):
            load_message = web_page.find("工商银行-个人版登录之后的提示")
            text = load_message.get_text()
            raise Exception(text)

    if load_type=='企业网上银行':
        url = "https://corporbank-simp.icbc.com.cn/frame/web/ebc/index.html"
        web_page.navigate(url,load_timeout=40)
        web_page.reload(load_timeout=40)

        # 点击切换到账号密码输入
        web_page.find('工商银行-企业版普及版登录').click()  

        sleep(1)
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = utils_jc.select_ele('//iframe[@id="iframe"]>>//label[@class="place-holder-index place-holder-alias-index"]', web_page)
        username_input = web_page.find(username_input)
        username_input.input(text=username, anchor=('middleCenter', 10, -10))
  
        # 填写密码输入框，密码输入框无法获取元素信息，暂时不添加检测
        password_input = utils_jc.select_ele('//iframe[@id="iframe"]>>//div[@id="CFCA_safeEdit1"]', web_page)
        # password_input = utils_jc.select_ele('//iframe[@id="iframe"]>>//form//input[@type="password"][@id="safeEdit1"]', web_page)
        password_input = web_page.find(password_input)
        password_input.click(anchor =("TopCenter", 0, 0))
        xbot_visual.win32.send_keys(keys=password, hardware_driver_input=True, force_ime_eng=False, contains_hotkey=False, send_key_delay="50", delay_after="1")
        # 处理验证码
        if web_page.is_element_displayed("工商银行-企业版验证码背景图"):
            captcha_result = xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_alphanum_captcha", package=__name__, inputs={
                "web_page": web_page,
                "engine": "xbot",
                "captcha_type": "10110",
                "ele": package.selector("工商银行-企业版验证码背景图"),
                "token": "",
                "timeout": lambda: 20,
                "is_trim": False,
                }, outputs=[
                "data",
            ])
            #     "recognition_engine": "影刀引擎(付费增值服务)",
            #     "captcha_type": "10110",
            #     "ele": package.selector("工商银行-企业版验证码背景图"),
            #     "token": "",
            #     }, outputs=[
            #     "data",
            # ])
            print('验证码识别结果为:',captcha_result)
            # 验证完之后再次点击登录
            password_input = utils_jc.select_ele('//iframe[@id="iframe"]>>//div[@id="CFCA_KeyPart"]', web_page)
            password_input = web_page.find(password_input)
            password_input.click(anchor =("TopCenter", 0, 0))
            xbot_visual.win32.send_keys(keys=captcha_result, hardware_driver_input=True, force_ime_eng=False, contains_hotkey=False, send_key_delay="50", delay_after="1", _block=("子流程1", 8, "键盘输入"))
            # password_input.input(captcha_result)
        
        # 点击登录
        login_button = utils_jc.select_ele('//iframe[@id="iframe"]>>//div[@id="submitkey"]', web_page)
        web_page.find(login_button).click(anchor =("TopCenter", 0, 0))
        sleep(3)
        
        # 获取一下登录之后的信息，比如账号或者密码错误啥的
        if web_page.is_element_displayed("工商银行-企业版登录之后的提示"):
            load_message = web_page.find("工商银行-企业版登录之后的提示")
            text = load_message.get_text()
            raise Exception(text)

def test_function():
    ''' 测试
    '''
    if 'xbot_extensions' not in __file__:
        web_page = web.get_active('edge')
        ai_engine = 'xbot'
        load_type = '企业网上银行'
        username = ''
        password = ''
        ym_token = ''
        icbc_bank_login(web_page,ai_engine,load_type,username,password,ym_token)
        exit()

def main(args):
    web_page = args.get('web_page',web.get_active(mode='edge'))
    web_page = args.get('web_page', web_page)
    ai_engine = args.get("ai_engine", "xbot")
    load_type = args.get("load_type", "企业网上银行")
    username = args.get("username", "6232711202001961577")
    password = args.get("password", "sxx080203")
    ym_token = args.get("ym_token", "")
    test_function()
    icbc_bank_login(web_page,ai_engine,load_type,username,password,ym_token)
    
