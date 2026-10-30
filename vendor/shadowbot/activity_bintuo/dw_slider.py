# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web, win32
from .import package
from .package import variables as glv
from .utils import bt_captcha_recognition, get_xbot_activity_cache_folder, get_ppi, yd_captcha_recognition, convert_img_to_base64
import xbot_visual
import json

def handle_captcha(web_page, username, password, background_ele, retry, slider_elem, drag_elem):
    for i in range(int(retry)):
        e_a_x, e_a_y, _, _ = web_page.find(background_ele).get_bounding(
            to96dpi=True)
        slider_x, _, slider_w, _ = web_page.find(slider_elem).get_bounding(
            to96dpi=True)

        #点击按下滑块
        drag_element = web_page.find(drag_elem)
        x, y, width, height = drag_element.get_bounding()
        pos_center_x = x + width / 2
        pos_center_y = y + height / 2
        move_speed = "fast"
        win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=0.5, max_time=2)
        win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
        win32.mouse_click(button="left", click_type="down", delay_after=0.1)

        #开始进行滑块逻辑判断
        data = 'false'
        total_distance = pos_center_x
        distance = slider_w // 27
        while data == 'false':
            win32.mouse_move(total_distance + distance, pos_center_y, move_speed=move_speed, delay_after=0.01)
            img64 = convert_img_to_base64(web_page, background_ele)
            if username != '':
                payload = {
                "username": "%s" % username,
                "password": "%s" % password,
                "captchaData": img64,
                "captchaType": 23031
                }
                data = bt_captcha_recognition(payload)
            else:
                payload = {
                "captchaData": img64, #验证码图的base64
                "captchaType": 23031  #类型
                }
                data = yd_captcha_recognition(payload)
            total_distance = distance + total_distance
        win32.mouse_click(button="left", click_type="up", delay_after=0.1)
        win32.manual_motion_off()
        sleep(2)
        if not xbot_visual.web.browser.element_display(
                browser=web_page, content_type="display",
                selector=background_ele):
            break
        
def main(args):
    web_page = args.get("web_page")
    username = args.get("username", '')
    password = args.get("password", '')
    background_ele = args.get("background_ele",'得物拖动验证码的背景元素')
    retry = args.get("retry", 5)
    slider_elem = args.get("slider_elem", '得物拖动验证码的滑条')
    drag_elem = args.get("drag_elem", '得物拖动验证码的滑块')

    # web_page = web.get_active(mode='chrome')
    handle_captcha(web_page, username, password, background_ele, retry, slider_elem, drag_elem)
    
