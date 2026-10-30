# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web,win32
from .import package
from .package import variables as glv
from xbot_extensions.activity_jfbym import std_slider_captcha,std_alphanum_captcha


def bankodchina_login(web_page, ai_engine:str, username:str, password:str, ym_token:str,drag_distance = 0):
    """中国银行登录
    :param web_page: , 网页对象
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    :param ym_token: str, 云码 token
    :param drag_distance: int, 额外滑动距离 
    """
    # 因为中国银行的验证码是需要刷新网页才会重置，如果过不了的话就刷新网页
    for i in range(1,5):
        # 网页地址
        url = "https://netc1.igtb.bankofchina.com/#/login-page?redirect=%2Findex"
        web_page.navigate(url,load_timeout=40)
        web_page.reload(load_timeout=40)
        sleep(2)
        # 先等待弹窗消失
        web_page.wait_disappear('中国银行-页面打开提示文案', timeout=20)
        # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
        username_input = web_page.find("中国银行-账号输入框")
        web_page.find("中国银行-账号输入框").click()
        for i in range(1,4):
            username_input.input(username)
            text = username_input.get_text()
            if text == username:
                break
            if i == 3:
                raise Exception("输入失败，请手动登录")
        # 填写密码输入框，密码输入框无法获取元素信息，暂时不添加检测
        password_input = web_page.find("中国银行-密码输入框").click()
        win32.send_keys(password)
        # 将鼠标悬停在验证码上面,并设置验证码的背景图
        if web_page.is_element_displayed("中国银行-验证码滑块"):
            web_page.find('中国银行-验证码滑块').hover()
            win32.mouse_click(click_type='down')
            ele = web_page.find('中国银行-验证码背景图')
            win32.mouse_click(click_type='up')
            ele.set_attribute('style','display:block;opacity:1;')
            sleep(1)
            # 处理验证码
            std_slider_captcha.handle_captcha(web_page = web_page,
                                            background_ele = package.selector("中国银行-验证码背景图"),
                                            drag_ele = package.selector("中国银行-验证码滑块"),
                                            retry_count = 5,
                                            offset = 0 , 
                                            speed = 1,
                                            ym_token = ym_token)
        
            if web_page.is_element_displayed("中国银行-验证码验证成功"):
                web_page.find('中国银行-登录按钮').click()
                sleep(2)
        elif web_page.is_element_displayed("中国银行-企业版数英验证码图片"):
                captcha_result = std_alphanum_captcha.handle_captcha(web_page = web_page,
                                                            ele = package.selector("中国银行-企业版数英验证码图片"),
                                                            captcha_type = '10103',
                                                            token = ym_token, is_trim=True, timeout=20)
                print('验证码识别结果为:',captcha_result)
                captcha_input = web_page.find("中国银行-企业版数英验证码输入框")    
                web_page.find("中国银行-企业版数英验证码输入框").click()   
                for i in range(1,4):
                    captcha_input.input(captcha_result)
                    text = captcha_input.get_text()
                    if text == captcha_result:
                        break
                    if i == 3:
                        raise Exception("验证码输入失败，请手动登录") 
                sleep(1)
                web_page.find('中国银行-登录按钮').click()
                sleep(2)
        # 账户密码错误会出现弹窗
        if web_page.is_element_displayed("中国银行-登录失败提示"):
            raise Exception('中国银行-登录失败提示')
        # 可能会出现一些特殊情况的提示
        if web_page.is_element_displayed("中国银行-登录之后的提示"):
            load_message = web_page.find("中国银行-登录之后的提示")
            text = load_message.get_text()
            raise Exception(text)
        break




def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    username = args.get("username", "@qq.com")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    drag_distance = args.get("drag_distance")
    bankodchina_login(web_page,ai_engine,username,password,ym_token,drag_distance=drag_distance)
