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

def login(mode, username, password, token, retry_count):
    if not retry_count:
        retry_count = 3
    url = "https://loginmyseller.taobao.com/"
    cnt = 0
    for _ in range(3):
        try:
            if cnt == 0:
                web_page = xbot.web.create(url, mode=mode, load_timeout=60)
            else:
                web_page.reload(load_timeout=60)
            break
        except:
            cnt += 1
    xbot.win32.manual_motion_on()
    web_page = xbot.web.get_active(mode=mode, silent_running=False, load_timeout=60)
    username_input = web_page.find("qn_uername_input")
    username_input.input(username, force_ime_ENG=True)
    text = username_input.get_text()
    i = 1
    while text != username:
        username_input.input(username, simulative=False)
        text = username_input.get_text()
        i += 1
        if i >3:
            raise Exception("输入失败，请手动登录")
    web_page = xbot.web.get_active(mode=mode, silent_running=False, load_timeout=60)
    password_input = web_page.find("qn_password_input")
    password_input.click()

    try:
        if web_page.is_element_displayed('qn_drag_label'):
            refresh_ele = package.selector('qn_refresh')
            drag_ele = package.selector('qn_drag_ele')
            ali_slider_captcha.handle_verification(web_page, token, refresh_ele, drag_ele, retry_count,offset=-30)
    except:
        pass
        
    web_page = xbot.web.get_active(mode=mode, silent_running=False, load_timeout=60)
    password = xbot_visual.decrypt(password)
    password_input.input(password)
    text = password_input.get_text()
    i = 1
    while text != password:
        password_input.input(password, simulative=False)
        text = password_input.get_text()
        i += 1
        if i >3:
            raise Exception("输入失败，请手动登录")
    web_page = xbot.web.get_active(mode=mode, silent_running=False, load_timeout=60)
    for _ in range(6):
        for _count in range(0, int(retry_count)):
            # if web_page.is_element_displayed('qn_login_verify_error'):
            #     web_page.find('qn_login_verify_error').click()
            if web_page.is_element_displayed('qn_login_verify'):
                x, y, width, height = web_page.find('qn_slide').get_bounding()
                _, _, verify_width, _ = web_page.find('qn_login_verify').get_bounding()
                pos_center_x = x + width / 2
                pos_center_y = y + height / 2
                move_speed = "middle"
                sleep(3)
                win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
                win32.mouse_click(button="left", click_type="down", delay_after=0)
                win32.mouse_move(pos_center_x + verify_width, pos_center_y, move_speed=move_speed)
                win32.mouse_click(button="left", click_type="up")
                sleep(1)
            else:
                # 校验是否失效
                try:
                    error_ele = web_page.find_by_xpath('//div[@class="errloading"]', timeout=2)
                    error_ele.click()
                    sleep(1)
                except:
                    break

        web_page.find("qn_login").click()
        xbot.win32.manual_motion_off()

        try:
            web_page.find("qn_login", timeout=5)
            raise Exception("登录失败")
        except:
            pass
        
        try:
            error_ele = web_page.find_by_xpath('//div[@class="errloading"]', timeout=2)
            error_ele.click()
            sleep(1)
        except:
            break

    login_error_xpath = '//iframe[@id="alibaba-login-box"]>>//div[@class="login-error-msg"]'
    login_error_ele = gen_selector(login_error_xpath, '千牛登录')
    if web_page.is_element_displayed(login_error_ele):
        raise ValueError(web_page.find(login_error_ele).get_text())
        
        
        

def test_func():
    if 'xbot_extensions' not in __file__:
        username = ''
        password = ''
        mode = 'chrome'
        token = ''
        retry_count = 3
        login(mode, username, password,token, retry_count)
        exit()

def main(args):
    test_func()
    username = args.get('username','11')
    password = args.get('password','')
    mode = args.get('mode','chrome')
    token = args.get('token','')
    retry_count = args.get('retry_count',3)
    login(mode, username, password,token, retry_count)
    sleep(2)
    web_page = web.get_active(mode=mode)
    args["web_page"] = web_page
    
