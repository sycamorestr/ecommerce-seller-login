# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import xbot_visual
import base64
import json
import base64    
import io
import os 
import http.client
from urllib.parse import urlparse
from PIL import ImageGrab
import random
import sqlite3
import ast 
if os.name == 'nt':
    from ctypes import windll
from PIL import Image
from io import BytesIO

from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation

from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv  

from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload, upload_captcha_screenshot, report_data, get_boundary_value

def yd_captcha_recognition(payload:dict):
    """使用增值服务请求验证码"""
    captcha_type = payload.get("type")
    payload.pop("type")

    common_info = robot.execute(f'Common.CommonConfig', None)
    token = common_info.get("token")
    conn = http.client.HTTPSConnection(urlparse(common_info.get("webApi")).netloc)
    res_payload = json.dumps({
        "thirdPartyInterfaceCode": f"jfbym_{captcha_type}",
        "data": {},
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": payload,
            "pathVariable": {}
        },
        "bizType": "rpa-command"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/api/openapi/v2/thirdParty/interface/call", res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    # print(response_json)
    data = response_json.get("data")
    if not data:
        raise Exception(f"错误信息: {response_json}")
    return data


def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = { 'Content-Type': 'application/json'}
    # print(payload.get("type"))
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def drag(drag_ele:WebElement, distance:int):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "slow"
    win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=0.5, max_time=2)
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="up", )
    win32.manual_motion_off()


def encode_image(image):
    """图片转base64"""
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    base64_string = base64.b64encode(img_bytes).decode('utf-8')
    return base64_string


def decode_image(base64_string):
    """字符串转图片"""
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    return img.convert('RGBA')


def drag(drag_ele:WebElement, distance:int):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2 + random.randint(-5, 5)
    pos_center_y = y + height / 2 + random.randint(-5, 5)

    move_speed = "middle"


    win32.manual_motion_on()
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)

    poit_x, point_y = win32.get_mouse_position(relative_to="screen")
    win32.mouse_click(button="left", click_type="down")

    right_offset = random.randint(-5, 5)
    left_offset = random.randint(-5, 5)

    win32.mouse_move(pos_center_x + distance + right_offset, pos_center_y, move_speed="fast", delay_after=0)
    sleep(random.uniform(0, 0.5))
    win32.mouse_move(pos_center_x + distance - left_offset, pos_center_y, move_speed="middle",  delay_after=0)
    sleep(random.uniform(0, 0.5))
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed="middle",  delay_after=0)
    win32.manual_motion_off()
    win32.mouse_click(button="left", click_type="up")


def relative_drag(distance:int,move_speed = "fast", up_flag=True):
    poit_x, point_y = win32.get_mouse_position(relative_to="screen")
    win32.mouse_click(button="left", click_type="down")
    win32.manual_motion_on()
    win32.mouse_move(poit_x + distance, point_y, move_speed=move_speed)
    win32.manual_motion_off()
    if up_flag:
        win32.mouse_click(button="left", click_type="up")


def get_web_page_by_web_page(web_page):
    product_name = getattr(web_page, "product_name", "cef" if web_page._controller == "CEFBrowser" else "firefox")
    return xbot.web.get_active(mode=product_name)


def handle_captcha(web_page: web.WebBrowser, token:str, refresh_ele: WebElement,drag_ele:WebElement, slider_ele:WebElement, retry_count: int):
    
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名

    _, _, drag_width, _ = web_page.find(drag_ele).get_bounding(to96dpi=True)

    _, _, slider_width, _ = web_page.find(slider_ele).get_bounding(to96dpi=True)

    if not retry_count: retry_count=5

    for i in range(retry_count):
        inner_image = None
        outer_image= None
        os_name = os.name
        if os_name == "nt":
            cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
            xbot.logging.info(f"Cache Dir:{cache_folder}")
        else:
            home_path = os.environ.get("XDG_CACHE_HOME")
            cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
            if not os.path.exists(cache_folder):
                os.makedirs(cache_folder)

        # 监听获取原图
        web_page.start_monitor_network( resource_type="Image")
        web_page.find(refresh_ele).click(simulative=False)
        sleep(3)
        res_list = web_page.get_responses(resource_type="Image")
        web_page.stop_monitor_network()
        
        for index, res_item in enumerate(res_list):
            image_base64: str = res_item.get("url")
            img = decode_image(image_base64.split(",", 1)[-1])

            # 通过左上角像素判断是 inner outer            
            if sum(img.getpixel((0, 0))) == 0:
                inner_image = img
                path = os.path.join(cache_folder, f"oocl_inner.png")
                img.save(path)
            else:
                outer_image = img
                path = os.path.join(cache_folder, f"oocl_outer.png")
                img.save(path)
           

        if not (inner_image or outer_image):
            raise Exception("未找到验证码图片")

        inner_image_base64 = encode_image(inner_image)
        outer_image_base64 = encode_image(outer_image)

        payload = { 
            "out_ring_image": outer_image_base64,
            "inner_circle_image": inner_image_base64,
            'token': token, 
            'type': "900025"
        }

        if token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)

        if data.get("msg") != "识别成功":
            raise Exception("识别失败, 请重试")
        
        distance = data.get("data").get("data")
        xbot.logging.info(f"Distance: {distance}")

        distance = int((slider_width) * distance / 360)
        drag_element = web_page.find(drag_ele)
        drag(drag_element, distance)

        web_page = get_web_page_by_web_page(web_page)

        sleep(3)
    
        if not xbot_visual.web.browser.element_display(browser=web_page, selector=drag_ele, content_type="display"):
            break
    

def main(args):
    web_page = args.get("web_page")
    token = args.get("ym_token")
    drag_ele = args.get("drag_ele")
    refresh_ele = args.get("refresh_ele")
    retry_count = args.get("retry_count")
    slider_ele = args.get("slider_ele")

    # web_page = web.get_active(mode="chrome")
    # retry_count = 1
    # offset = 0
    # token = ""
    # refresh_ele = 'oocl_refresh'
    # drag_ele = 'oocl_drag'
    # slider_ele = 'oocl_slider'

    handle_captcha(web_page, token, refresh_ele, drag_ele, slider_ele, retry_count)

    pass
