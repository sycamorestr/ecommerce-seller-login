# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv
from xbot_extensions.activity_jfbym import ali_slider_captcha
from .utils import gen_selector
import xbot_visual
from xbot._core.retry import Retry

def login(mode, engine, username, password, token, retry_count):
    if not retry_count:
        retry_count = 3
    url = "https://login.taobao.com/?redirect_url=https%3A%2F%2Flogin.1688.com%2Fmember%2Fjump.htm%3Ftarget%3Dhttps%253A%252F%252Flogin.1688.com%252Fmember%252FmarketSigninJump.htm%253FDone%253Dhttps%25253A%25252F%25252Fmember.1688.com%25252Fmember%25252Foperations%25252Fmember_operations_jump_engine.htm%25253Ftracelog%25253Dlogin%252526operSceneId%25253Dafter_pass_from_taobao_new%252526defaultTarget%25253Dhttps%2525253A%2525252F%2525252Fwork.1688.com%2525252F%2525253Ftracelog%2525253Dlogin_target_is_blank_1688&style=tao_custom&from=1688web"
    try:
        web_page = xbot.web.get_active(mode=mode)
    except:
        web_page = xbot.web.create(url, mode)
    # 校验url
    for _ in Retry(timeout=10, ignore_exception=True):
        now_url = web_page.get_url()
        if now_url != url:
            web_page = xbot.web.create(url, mode=mode)
        else:
            break
    else:
        raise Exception('切换至登录页面失败')

    # 判断是否存在快速进入元素
    quickly_login_xpath = '//button[.="快速进入"]'
    quickly_login_ele = gen_selector(quickly_login_xpath, '快速进入')
    if web_page.is_element_displayed(quickly_login_ele):
        other_acount_xpath = '//div[.="使用其他账号登录"]'
        other_acount_ele = gen_selector(other_acount_xpath, '其他账号登录')
        web_page.find(other_acount_ele).click()
    
    # 进入密码登录
    password_login_xpath = '//a[.="密码登录"]'
    password_login_ele = gen_selector(password_login_xpath, '密码登录')
    web_page.find(password_login_ele).click()
    
    # 输入账号密码
    xbot.win32.manual_motion_on()
    web_page = xbot.web.get_active(mode=mode, silent_running=False)
    username_input_xpath = '//input[@placeholder="账号名/邮箱/手机号"]'
    username_input_ele = gen_selector(username_input_xpath, '账号输入框')
    username_input = web_page.find(username_input_ele)
    username_input.input(username, force_ime_ENG=True)
    web_page = xbot.web.get_active(mode=mode, silent_running=False)

    password_input_xpath = '//input[@placeholder="请输入登录密码"]'
    password_input_ele = gen_selector(password_input_xpath, '密码输入框')
    password_input = web_page.find(password_input_ele)
    password_input.click()
    web_page = xbot.web.get_active(mode=mode, silent_running=False)
    password = xbot_visual.decrypt(password)
    password_input.input(password)
    web_page = xbot.web.get_active(mode=mode, silent_running=False)
    xbot.win32.manual_motion_off()
    for _count in range(0, int(retry_count)):
        if web_page.is_element_displayed('1688_login_verify_error'):
            web_page.find('1688_login_verify_error').click()
        if web_page.is_element_displayed('1688_login_verify'):
            x, y, width, height = web_page.find('1688_slide').get_bounding()
            _, _, verify_width, _ = web_page.find('1688_login_verify').get_bounding()
            pos_center_x = x + width / 2
            pos_center_y = y + height / 2
            move_speed = "middle"
            win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
            win32.mouse_click(button="left", click_type="down", delay_after=0)
            win32.mouse_move(pos_center_x + verify_width, pos_center_y, move_speed=move_speed)
            win32.mouse_click(button="left", click_type="up", )
        else:
            break

    login_button_xpath = '//button[.="登录"]'
    login_button_ele = gen_selector(login_button_xpath, '登录按钮')
    web_page.find(login_button_ele).click()
    sleep(1)

    msg_error_xpath = '//div[@class="login-error-msg"]'
    msg_error_ele = gen_selector(msg_error_xpath, '报错信息')
    if web_page.is_element_displayed(msg_error_ele):
        raise Exception(web_page.find(msg_error_ele).get_text())
    for _ in Retry(timeout=10, ignore_exception=True):
        if not web_page.is_element_displayed(login_button_ele):
            print('登录成功')
            break
    else:
        raise Exception('登录失败，请手动登录')
    web_page = xbot.web.get_active(mode)
    return web_page

def test_func():
    if 'xbot_extensions' not in __file__:
        username = ''
        password = ''
        mode = 'chrome'
        token = ''
        retry_count = 3
        engine = 'xbot'
        login(mode, engine, username, password,token, retry_count)
        exit()

def main(args):
    test_func()
    username = args.get('username','')
    password = args.get('password','')
    mode = args.get('mode','chrome')
    engine = args.get('engine')
    token = args.get('token','')
    retry_count = args.get('retry_count',3)
    web_page = login(mode, engine, username, password, token, retry_count)
    sleep(2)
    args["web_page"] = web_page
    
