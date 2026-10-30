# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import http
import json
import base64
import xbot_visual
import os
from xbot import print, sleep, web 
from . import package 
from .package import variables as glv
from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value
from urllib.parse import urlparse

import random


SCALING_FACTOR = get_ppi()


def get_xbot_client():
    """获取客户端 token"""
    common_info = robot.execute(f'Common.CommonConfig', None)
    return common_info.get("token")


def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = {'Content-Type': 'application/json'}
    # print(payload.get("type"))
    data_json = json.dumps(payload)
    conn.request("POST",
                 "/api/YmServer/customApi",
                 body=data_json,
                 headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload: dict):
    """使用增值服务请求验证码"""
    captcha_type = payload.get("type")
    payload.pop("type")
    payload.pop("token")
    common_info = robot.execute(f"Common.CommonConfig", None)

    token = common_info.get("token")
    web_api = common_info.get("webApi")

    parsed = urlparse(web_api)
    is_ssl = parsed.scheme.lower() == "https"
    host = parsed.netloc


    if is_ssl:
        conn = http.client.HTTPSConnection(host)
    else:
        conn = http.client.HTTPConnection(host)

    res_payload = json.dumps(
        {
            "aiToolInterfaceCodeId": f"jfbym_{captcha_type}",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": str(captcha_type),
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": payload,
            },
        }
    )

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/api/v2/aiservice/call",
                 res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    # print(response_json)
    data = response_json.get("data")
    if not data:
        raise Exception(f"错误信息: {response_json}")
    return data


def handle_captcha(web_page, web_element, direction,ym_token,
                   retry_count, confirm) -> str:
    """处理验证码"""
    captcha_type = 30332
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名

    for i in range(retry_count):
        e_x, e_y, e_w, e_h = web_page.find(web_element).get_bounding(
        to96dpi=False)
        e_a_x, e_a_y, _, _ = web_page.find(web_element).get_bounding(
            to96dpi=True)
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        temp_file = os.path.join(cache_folder, "std_click_temp.png")
        xbot.win32.screenshot.save_screen_to_file(temp_file, "png", e_x, e_y, e_x + e_w, e_y + e_h)
        image_base64 = file2base64(temp_file)
        if os.path.exists(temp_file):
            os.remove(temp_file)
        payload = {"image": image_base64, 'token': ym_token, 'type': captcha_type, "direction":direction}

        if ym_token:
            data = ym_captcha_recognition(payload)
            data = data.get("data").get("data")
        else:
            data = yd_captcha_recognition(payload)
            data = data.get("response").get("data")

        
        positions = [item.split(",") for item in data.split("|")]
        xbot.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=1, max_time=1)
        
        for t_x, t_y in positions:
            if os.name =='nt':
                target_p_x = e_a_x + int(int(t_x) * SCALING_FACTOR) + random.randint(-8,8)
                target_p_y = e_a_y + int(int(t_y) * SCALING_FACTOR) + random.randint(-8,8)
            else:
                target_p_x = e_a_x + int(t_x)
                target_p_y = e_a_y + int(t_y)
            xbot.win32.mouse_move(target_p_x, target_p_y, delay_after=random.random(),move_speed="fast")
            xbot.win32.mouse_click(delay_after=random.random())
           
        if confirm:

            # web_page.find(confirm).hover(delay_after=random.random())
            e_c_x, e_c_y, e_c_w, e_c_h = web_page.find(confirm).get_bounding(
            to96dpi=True)
            xbot.win32.mouse_move(int(e_c_x+e_c_w/2), int(e_c_y+e_c_h/2), delay_after=random.random())
            xbot.win32.mouse_click(delay_after=random.random())

        sleep(4)
        
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=web_element):

            break
        xbot.win32.manual_motion_off()
    
    # return 


def main(args):
    web_page = args.get("web_page")
    web_element = args.get("web_element")
    direction = args.get("direction", "bottom")
    ym_token = args.get("ym_token", )
    confirm = args.get("confirm",'')
    retry_count = args.get("retry_count", 5)

    # web_page = web.get_active(mode="chrome")
    # web_element = "click_select_element"
    # ym_token = ""


    handle_captcha(web_page, web_element, direction,ym_token, retry_count, confirm)
