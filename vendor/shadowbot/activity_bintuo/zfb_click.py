# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import bt_captcha_recognition, get_xbot_activity_cache_folder, get_ppi, yd_captcha_recognition, convert_img_to_base64, gen_selector
import xbot_visual
import random
import os

PPI = get_ppi()

def handle_captcha(web_page, username, password, background_ele, retry, engine):
    # 处理支付宝的弹窗
    close_xpath = '//img[@class="jshield-feedback-close captcha"]'
    close_ele = gen_selector(close_xpath)
    for i in range(int(retry)):
        if web_page.is_element_displayed(close_ele):
            web_page.find(close_ele).click()
        img64 = convert_img_to_base64(web_page, background_ele)
        e_a_x, e_a_y, _, _ = web_page.find(background_ele).get_bounding(
            to96dpi=True)
        if engine == 'bintuo':
            payload = {
            "username": "%s" % username,
            "password": "%s" % password,
            "captchaData": img64,
            "captchaType": 1311
            }
            data = bt_captcha_recognition(payload)
        else:
            payload = {
            "captchaData": img64, #验证码图的base64
            "captchaType": 1311  #类型
            }
            data = yd_captcha_recognition(payload)
        
        xbot.win32.manual_motion_on()
        positions = [item.split(",") for item in data.split("|")]
        for t_x, t_y in positions:
            if os.name =='nt':
                target_p_x = e_a_x + int(int(t_x) * PPI) + random.randint(-10, 10)
                target_p_y = e_a_y + int(int(t_y) * PPI) + random.randint(-10, 10)
            else:
                target_p_x = e_a_x + int(t_x) + random.randint(-10, 10)
                target_p_y = e_a_y + int(t_y) + random.randint(-10, 10)
            speed = ['slow', 'middle']
            xbot.win32.mouse_move(target_p_x, target_p_y, move_speed=speed[random.randint(0, 1)])
            sleep(random.randint(1, 3))
            xbot.win32.mouse_click()
        xbot.win32.manual_motion_off()
        sleep(3)
        if not xbot_visual.web.browser.element_display(
                browser=web_page, content_type="display",
                selector=background_ele):
                
            break
        
def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = web.get_active('chrome')
        username = ''
        password = ''
        background_ele = '请在下图依次点击'
        retry = 5
        engine = 'xbot'
        handle_captcha(web_page, username, password, background_ele, retry, engine)
        exit()

def main(args):
    web_page = args.get("web_page")
    username = args.get("username", '')
    password = args.get("password", '')
    background_ele = args.get("background_ele",'请在下图依次点击')
    retry = args.get("retry", 5)
    engine = args.get('engine', 'xbot')
    # web_page = web.get_active(mode='chrome')
    test_func()
    handle_captcha(web_page, username, password, background_ele, retry, engine)
    
