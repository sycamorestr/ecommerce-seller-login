# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package

from xbot_extensions.activity_jfbym import std_alphanum_captcha


def hkbea_bank_login(web_page, load_type:str,ai_engine:str, retry_count:int,username:str, password:str, ym_token:str):
    """东亚银行银行登录，目前只有个人银行能做
    :param web_page: , 网页对象
    :param load_type: str, 登录方式
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    :param ym_token: str, 云码 token
    """
    url = "https://ebank.hkbea.com.cn/Perbank/#/login"
    web_page.navigate(url,load_timeout=40)
    
    # 选择登录方式
    web_page.find("东亚银行-登录方式选择").click()
    sleep(2)
    if load_type =='账号':
        web_page.find_by_xpath(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]/li/span[text()="－－－账    号－－－"]').click()
    else:
        web_page.find_by_xpath(f'//ul[@class="el-scrollbar__view el-select-dropdown__list"]/li/span[contains(text(), "'+load_type+'")]').click()

    
    # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
    username_input = web_page.find("东亚银行-账号输入框")
    web_page.find("东亚银行-账号输入框").click()
    for i in range(1,4):
        username_input.input(username)
        text = username_input.get_text()
        print(text,username)
        if text == username:
            break
        if i == 3:
            raise Exception("输入失败，请手动登录")

    
    # 填写密码框，这部分需要使用驱动输入，文档中需要注明
    password_input = web_page.find("东亚银行-密码输入框")
    password_input.click()
    # password_input.input(password)
    win32.send_keys(password,hardware_driver_input=True)
    # 等待
    sleep(2)
    # 判断验证码是否可见
    for i in range(1,retry_count+1):
        if web_page.is_element_displayed("东亚银行-验证码图像"):
            # 调用云码识别验证码的结果
            web_page.find("东亚银行-验证码输入框").click()
            sleep(1)
            captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
                                                    ele = package.selector("东亚银行-验证码图像"),
                                                    captcha_type = '10103',
                                                    token = ym_token, is_trim=True, timeout=20)
            
            print('验证码识别结果为:',captcha_result)
            captcha_input = web_page.find("东亚银行-验证码输入框")
            web_page.find("东亚银行-验证码输入框").click()
            for i in range(1,4):
                captcha_input.input(captcha_result)
                text = captcha_input.get_text()
                if text == captcha_result:
                    break
                if i == 3:
                    raise Exception("验证码输入失败，请手动登录")       
        
        # 处理是否要点选复选框
        if not web_page.is_element_displayed("东亚银行-电子渠道政策复选框"):
            web_page.find("东亚银行-登录复选框").click()
        
        # 点击登录
        web_page.find('东亚银行-登录按钮').click()
        sleep(3)
        if web_page.is_element_displayed("东亚银行-登录之后验证码错误提示"):
            web_page.find("东亚银行-验证码错误返回按钮").click()
            sleep(2)
            web_page.find("东亚银行-验证码图像").click()
        else:
            break
    
    # 获取一下登录之后的信息，比如账号或者密码错误啥的
    if web_page.is_element_displayed("东亚银行-登录之后的状态"):
        load_message = web_page.find("东亚银行-登录失败的提示")
        text = load_message.get_text()
        raise Exception(text)
    if web_page.is_element_displayed("东亚银行-登录之后的提示"):
        load_message = web_page.find("东亚银行-登录之后的提示")
        text = load_message.get_text()
        raise Exception(text)
    


def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    username = args.get("username", "")
    load_type = args.get("load_type", "手机银行账户")
    password = args.get("password", "")
    retry_count = args.get("retry_count",3)
    ym_token = args.get("ym_token", "")
    hkbea_bank_login(web_page = web_page,
                     ai_engine = ai_engine,
                     load_type = load_type,
                     username = username,
                     password = password,
                     retry_count = retry_count,
                     ym_token = ym_token)
