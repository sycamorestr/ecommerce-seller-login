import xbot
import os
import xbot_visual
import base64
import json
import base64
import io
import urllib
import http.client
from urllib.parse import urlparse


from PIL import ImageGrab, Image

from PIL import Image
from io import BytesIO
if os.name == 'nt':
    from ctypes import windll
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation 

from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv
from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value
from xbot._core import robot

def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = { 'Content-Type': 'application/json'}
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload):
    common_info = robot.execute(f'Common.CommonConfig', None)
    token = common_info.get("token")
    conn = http.client.HTTPSConnection(urlparse(common_info.get("webApi")).netloc)
    payload = json.dumps({
        "thirdPartyInterfaceCode": "jfbym_22222",
        "data": {},
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": {
                "image": payload.get("image")
            },
            "pathVariable": {}
        },
        "bizType": "rpa-command"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/api/openapi/v2/thirdParty/interface/call", payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def drag(drag_ele:WebElement, distance:int):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "middle"
    win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=0.1, max_time=0.5)
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="up", )
    win32.manual_motion_off()


def handle_captcha(web_page:xbot.web.WebBrowser, background_ele, drag_ele, 
            retry_count: int=5, offset=0, speed=1, ym_token='', refresh_elem=None):
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名

    os_name = os.name
    if os_name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache Dir:{cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
    xbot.logging.info(f"Cache Dir:{cache_folder}")
    if not retry_count: retry_count=5


    for i in range(retry_count):
        if refresh_elem != '' and refresh_elem != None:
            web_page.find(refresh_elem).click()
        drag_element = drag_ele
        # 截图
        image_path = os.path.join(cache_folder, "std_slider.png")
        b_x, b_y, b_w, b_h = web_page.find(background_ele).get_bounding(to96dpi=False)
        s_x, s_y, s_w, s_h = web_page.find(drag_ele).get_bounding(to96dpi=False)
        xbot.win32.screenshot.save_screen_to_file(image_path, "png", b_x, b_y, b_x + b_w, b_y + b_h)
        background_ele_base64 = file2base64(image_path)
        

        # 识别
        payload = { 
            "image": background_ele_base64,
            'token': ym_token, 
            'type': 22222
        }

        if ym_token:
            data = ym_captcha_recognition(payload)
            
        else:
            data = yd_captcha_recognition(payload)
            if not data.get("success"):
                raise Exception(data.get("msg"))
            data = data.get("data")
        
        # print(data)
        
        if data.get("msg") != "识别成功":
            raise Exception(data.get("msg"))
        
        distance = int(data.get("data").get("data"))
    
        # 拖拽
        distance = (distance + int(offset)) / speed
        if os.name =='nt':
            distance = int(distance * get_ppi()) 
        xbot.logging.info(f"Distant:{distance}")
        drag(web_page.find(drag_element), distance)
        # drag_gen(drag_element, distance-3)
        
        sleep(3)
        try:
            x, y, width, height = drag_element.get_bounding()
            if width and height == 0:
                print("页面已无验证码，现在退出")
                break
        except:
            pass
        if not xbot_visual.web.browser.element_display(browser=web_page, selector=background_ele, content_type="display"):
            break

    

def main(args):
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    slider_ele = args.get("slider_ele")
    retry_count = args.get("retry_count")
    offset = args.get("offset")
    speed = args.get("speed", 1)
    ym_token = args.get("ym_token", "")
    refresh_elem = args.get("refresh_elem", "")


    # web_page = web.get_active(mode="chrome")
    # background_ele = "std_slider_captcha_background"
    # slider_ele = "std_slider_captcha_drag"
    # retry_count = 5
    # offset = 0
    # ym_token = ""


    handle_captcha(web_page, background_ele, slider_ele, retry_count, offset, speed, ym_token, refresh_elem)
