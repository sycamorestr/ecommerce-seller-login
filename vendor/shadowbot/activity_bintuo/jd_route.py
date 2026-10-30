# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import bt_captcha_recognition, get_xbot_activity_cache_folder, get_ppi, yd_captcha_recognition, convert_img_to_base64, drag
import xbot_visual

def handle_captcha(web_page, username, password, background_ele, retry, slider_elem, drag_elem):
    for i in range(int(retry)):
        img64 = convert_img_to_base64(web_page, background_ele)
        e_a_x, e_a_y, _, _ = web_page.find(background_ele).get_bounding(
            to96dpi=True)
        if username != '':
            payload = {
            "username": "%s" % username,
            "password": "%s" % password,
            "captchaData": img64,
            "captchaType": 1123
            }
            data = bt_captcha_recognition(payload)
        else:
            payload = {
            "captchaData": img64, #验证码图的base64
            "captchaType": 1123  #类型
            }
            data = yd_captcha_recognition(payload)
        data = int(data)
        # if int(data) < 0:
        #     data =  data * -1
        print(data)
        if data < 0:
            data = 360 - (data*-1)
        slider_width = web_page.find(slider_elem).get_bounding(to96dpi=True)[2]
        drag_width = web_page.find(drag_elem).get_bounding(to96dpi=True)[2]
        distance = int((slider_width-drag_width) * int(data) / 360)
        drag_element = web_page.find(drag_elem)
        drag(drag_element, distance)

        sleep(2)
        if not xbot_visual.web.browser.element_display(
                browser=web_page, content_type="display",
                selector=background_ele):
                
            break
        
def main(args):
    web_page = args.get("web_page")
    username = args.get("username", '')
    password = args.get("password", '')
    background_ele = args.get("background_ele",'jd_test')
    retry = args.get("retry", 5)
    slider_elem = args.get("slider_elem", 'xxxx')
    drag_elem = args.get("drag_elem", 'slider')

    # web_page = web.get_active(mode='edge')

    handle_captcha(web_page, username, password, background_ele, retry, slider_elem, drag_elem)
    
