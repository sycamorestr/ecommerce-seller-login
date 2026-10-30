# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,web, win32
from .import package
from .package import variables as glv
from .orangebank_slider_captcha import deal_deal_handle_captcha, _ocr_by_path_or_url
from xbot._core.retry import Retry 
import os
 

def orange_bank_login(web_page, ai_engine:str, username:str, password:str, ym_token:str,drag_distance:int):
    """平安银行登录
    :param web_page: , 网页对象
    :param ai_engine: str, 验证码识别引擎
    :param username: str, 账号
    :param password: str, 密码
    :param ym_token: str, 云码 token
    :param drag_distance: int, 额外滑动距离 
    """
    url = "https://auth.orangebank.com.cn/cimp-ccs-pc/#/p/ebank-login"
    web_page.navigate(url,load_timeout=40)
    web_page.reload(load_timeout=40)
    
    # 填写账号输入框，并检测账号输入情况，检测三次，避免输入的时候可能会出现多个a的情况
    username_input = web_page.find("平安银行-账号输入框")
    web_page.find("平安银行-账号输入框").click()
    for i in range(1,4):
        username_input.input(username)
        text = username_input.get_text()
        if text == username:
            break
        if i == 3:
            raise Exception("输入失败，请手动登录")

    
    # 填写密码输入框，密码输入框无法获取元素信息，暂时不添加检测
    password_input = web_page.find("平安银行-密码输入框")
    password_input.click(button='left',simulative=False)
    password_input.click(button='left')
    password_input.input(password)
    
    try:
        home_dir = os.path.expanduser("~")
        downloads_path = os.path.join(home_dir, "Downloads")
        web_page.find_by_xpath('//form[contains(@class, "login-form")]//div[contains(@class, "img-code-wrap")][contains(@class, "pa-interwork-block")]', timeout=10).screenshot(folder_path = downloads_path, filename="temp.png")
        path = os.path.join(downloads_path, "temp.png")
        result = _ocr_by_path_or_url(path)
        captch_input = web_page.find("平安银行_验证码输入框")
        captch_input.click(button='left',simulative=False)
        captch_input.click(button='left')
        captch_input.input(result)       
    except:
        pass

    # 点击登录
    web_page.find('平安银行-登录按钮').click()

    # 等待
    for _ in Retry(timeout=7, ignore_exception=True):
        if web_page.is_element_displayed("平安银行-验证码背景图"):
            break
    
    # 判断验证码是否可见
    if web_page.is_element_displayed("平安银行-验证码背景图"):
        
        deal_deal_handle_captcha(web_page = web_page,
                                background_ele = '平安银行-验证码背景图',
                                drag_ele = '平安银行-验证码滑块图',
                                gap_ele = '平安银行-验证码缺口图片',
                                refresh_ele = '平安银行-验证码刷新图片',
                                retry_count = 5,
                                ym_token = ym_token,
                                drag_distance = drag_distance)
    
    sleep(3)
    # 获取一下登录之后的信息，比如账号或者密码错误啥的
    if web_page.is_element_displayed("平安银行-登录信息"):
        load_message = web_page.find("平安银行-登录信息")
        text = load_message.get_text()
        raise Exception(text)


def main(args):
    # web_page = args.get('web_page',web.get_active(mode='chrome'))
    web_page = args.get('web_page','')
    ai_engine = args.get("ai_engine", "xbot")
    username = args.get("username", "@qq.com")
    password = args.get("password", "")
    ym_token = args.get("ym_token", "")
    drag_distance = args.get("drag_distance")
    orange_bank_login(web_page,ai_engine,username,password,ym_token,drag_distance=drag_distance)
