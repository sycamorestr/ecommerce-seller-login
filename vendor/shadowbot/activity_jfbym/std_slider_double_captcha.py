import xbot
import os
import json
import http.client
from urllib.parse import urlparse


import xbot_visual
from xbot.web.element import WebElement
from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv
from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi

def recg(token, slide_image_base64, background_image_base64):
    """请求云码识别淘"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = { 'Content-Type': 'application/json'}
    data = { 
        "slide_image": slide_image_base64,
        "background_image": background_image_base64,
        'token': token, 
        'type': 11268
    }

    data_json = json.dumps(data)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json

def yd_recg(slide_image_base64, background_image_base64):
    common_info = robot.execute(f'Common.CommonConfig', None)
    token = common_info.get("token")
    conn = http.client.HTTPSConnection(urlparse(common_info.get("webApi")).netloc)
    payload = json.dumps({
        "thirdPartyInterfaceCode": "jfbym_20111",
        "data": {},
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": {
                "slide_image": slide_image_base64,
                "background_image": background_image_base64
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
    win32.mouse_click(button="left", click_type="up")
    win32.manual_motion_off()

def _moveTo(x, y):
    """Send the mouse move event to Windows by calling SetCursorPos() win32
    function.

    Args:
      button (str): The mouse button, either 'left', 'middle', or 'right'
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.

    Returns:
      None
    """
    if os.name == 'nt':
        import ctypes
        ctypes.windll.user32.SetCursorPos(x, y)
    else:
        win32.mouse_move(x, y, move_speed="instant")


def handle_captcha(web_page:xbot.web.WebBrowser, background_ele, slider_ele, retry_count: int=5, offset=0, token=None):
    
    # xbot.logging.info(f"Cache Dir:{cache_folder}")
    
    if not retry_count: retry_count=5
    
    for i in range(retry_count):
        # slider_ele = web_page.find(slider_ele)
        s_x, s_y, s_w, s_h = web_page.find(slider_ele).get_bounding(to96dpi=False)
        b_x, b_y, b_w, b_h = web_page.find(background_ele).get_bounding(to96dpi=False)

        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")

        # screen background
        bg_temp_file = os.path.join(cache_folder, "slider_double_bg_temp.png")
        xbot.win32.screenshot.save_screen_to_file(bg_temp_file, "png", b_x, b_y, b_x + b_w, b_y + b_h)
        background_image_base64 = file2base64(bg_temp_file)
        if os.path.exists(bg_temp_file):
            os.remove(bg_temp_file)

        # screen slider
        slider_temp_file = os.path.join(cache_folder, "slider_double_slider_temp.png")
        xbot.win32.screenshot.save_screen_to_file(slider_temp_file, "png", s_x, s_y, s_x + s_w, s_y + s_h)
        slider_image_base64 = file2base64(slider_temp_file)
        if os.path.exists(slider_temp_file):
            os.remove(slider_temp_file)

        if not token:
            # 影刀暂时不支持
            data = yd_recg(slider_image_base64, background_image_base64)
            data = data.get("data")
        else:
            data = recg(token, slider_image_base64, background_image_base64)
        
        if data.get("msg") != "识别成功":
            raise Exception("识别失败, 请重试")

        data_x, data_y = json.loads(data.get("data").get("data"))
        xbot.logging.info(f"Distant:{data_x}, {data_y}")

        # move
        # move to start position

        s_x, s_y, s_w, s_h = web_page.find(slider_ele).get_bounding(to96dpi=True)
        b_x, b_y, b_w, b_h = web_page.find(background_ele).get_bounding(to96dpi=False)
        ppi = get_ppi()
        xbot.win32.mouse_move(int(s_x + s_w/2), int(s_y + s_h/2))
        xbot.win32.mouse_click(button="left", click_type="down")
        xbot.win32.mouse_move(int(s_x + s_w/2 + data_x * ppi), int(s_y + s_h/2 + data_y*ppi))
        xbot.win32.mouse_click(button="left", click_type="up")

        sleep(3)
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=background_ele):
            break

def main(args):
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    slider_ele = args.get("slider_ele")
    retry_count = args.get("retry_count")
    offset = args.get("offset")

    web_page = web.get_active(mode="chrome")
    background_ele = "std_slider_double_background_ele"
    slider_ele = "std_slider_double_slider_ele"
    retry_count = 5
    offset = 0
    token = ""
    handle_captcha(web_page, background_ele, slider_ele, retry_count, offset, token)
