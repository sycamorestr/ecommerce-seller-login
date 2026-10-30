# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, win32
from .import package
from .package import variables as glv   
import http
import json
import os
import base64
if os.name == 'nt': 
    from ctypes import windll
from xbot._core import robot

from urllib.parse import urlparse
import uuid
from xbot.selector import Selector
 
def gen_selector(xpath):
    if isinstance(xpath, str):
        xpath = [xpath]
    uid = str(uuid.uuid4())

    data = {'id': uid, 'name': uid, 'type': 'simple', 'xpath': {'enable': 'true', 'segments': xpath}}

    return Selector(data)

def get_xbot_client():
    """获取客户端 token"""
    common_info = robot.execute(f'Common.CommonConfig', None)
    return common_info.get("token")

def yd_captcha_recognition(payload: dict):
    """使用增值服务请求验证码
    :param payload: 冰拓body参数(除去username和password)
    """
    captcha_type = payload.get("captchaType")
    payload.pop("captchaType")
    common_info = robot.execute(f"Common.CommonConfig", None)

    token = common_info.get("token")
    web_api = common_info.get("webApi")
    is_publish_client = common_info.get("isPublicClient")

    parsed = urlparse(web_api)
    is_ssl = parsed.scheme.lower() == "https"
    host = parsed.hostname

    # 公有云客户端
    if is_publish_client:
        host = "api.yingdao.com"
        is_ssl = True

    if is_ssl:
        conn = http.client.HTTPSConnection(host)
    else:
        conn = http.client.HTTPConnection(host)

    res_payload = json.dumps({
        "aiToolInterfaceCodeId": f"captcha_bingtop_bingtop_{captcha_type}",
        "aiID": "captcha",
        "rule": "bingtop",
        "channel": "bingtop",
        "model": captcha_type,
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": payload,
        },
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/api/v2/aiservice/call/captcha",
                 res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    data = response_json.get("data")
    if not data:
        raise Exception(f"错误信息: {response_json}")
    return data["response"]["recognition"]

def get_xbot_activity_cache_folder(activity_code):
    """根据指令code 获取本地缓存目录, 不存在则创建"""
    if os.name == 'nt':
        local_appdata_path = os.getenv('LOCALAPPDATA')
        xbot_app_cache_dir = os.path.join(local_appdata_path, "xbot_app", activity_code)
        if not os.path.exists(xbot_app_cache_dir):
            os.makedirs(xbot_app_cache_dir)
        return xbot_app_cache_dir
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
        return cache_folder

def convert_img_to_base64(web_page, image):
    """对元素截图并转为base64
    :param web_page: 网页对象
    :param image: 网页图片元素
    """
    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    save_path = os.path.join(cache_folder, "dw_slider.png")
    x, y, width, height = web_page.find(image).get_bounding(
        to96dpi=False)
    win32.screenshot.save_screen_to_file(save_path, "png", x, y, x + width,
                                            y + height)
    with open(save_path, 'rb') as pic_file:
        img_data = pic_file.read()
        img64 = base64.b64encode(img_data).decode('utf-8')

    return img64


def bt_captcha_recognition(payload):
    """请求冰拓识别验证码
    :param payload: 冰拓body参数
    """
    conn = http.client.HTTPConnection("www.bingtop.com")
    headers = {'Content-Type': 'application/json'}
    data_json = json.dumps(payload)
    conn.request("POST",
                 "/ocr/upload/",
                 body=data_json,
                 headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    print(response_json)
    return response_json["data"].get("recognition", '')

def get_ppi():
    """获取屏幕的缩放"""
    LOGPIXELSX = 88
    LOGPIXELSY = 90
    user32 = windll.user32
    user32.SetProcessDPIAware()
    dc = user32.GetDC(0)
    pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
    user32.ReleaseDC(0, dc)
    res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
    return res[1] / res[0]

def drag(drag_ele, distance:int):
    """拖动滑块
    :param drag_ele: 滑块元素
    :param distance: 滑动的距离
    """
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "fast"
    win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=0.5, max_time=2)
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0.1)
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed=move_speed, delay_after=0.1)
    win32.mouse_move(pos_center_x + distance-2, pos_center_y, move_speed=move_speed, delay_after=0)
    win32.mouse_move(pos_center_x + distance+3, pos_center_y, move_speed=move_speed, delay_after=0)
    win32.mouse_move(pos_center_x + distance-1, pos_center_y, move_speed=move_speed, delay_after=0.1)
    win32.mouse_click(button="left", click_type="up", )
    win32.manual_motion_off()


def main(args):
    pass
