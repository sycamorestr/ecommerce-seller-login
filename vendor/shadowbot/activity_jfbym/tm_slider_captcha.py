import os
import json
import http.client


import xbot  # type: ignore
import xbot_visual  # type: ignore


if os.name == "nt":
    from ctypes import windll

from urllib.parse import urlparse
from xbot._core import robot  # type: ignore
from xbot import print, sleep, win32  # type: ignore
from xbot.web.element import WebElement  # type: ignore

from .package import variables as glv
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi
from . import package

def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = {"Content-Type": "application/json"}
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload):
    # 判断客户端版本, 是否使用ssl, host, 以及token
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

    payload = json.dumps(
        {
            "aiToolInterfaceCodeId": "jfbym_22229",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": "22229",
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": {"captcha_response": payload.get('captcha_response'), "ki_response": payload.get('ki_response')},
            },
        }
    )
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    conn.request("POST", "/api/v2/aiservice/call", payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json.get("data")


def drag(drag_ele: WebElement, distance: int):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "middle"
    win32.manual_motion_on(
        motion_move=True,
        motion_click=True,
        motion_delay=True,
        min_time=0.1,
        max_time=0.5,
    )
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="up")
    win32.manual_motion_off()


def handle_captcha(
    web_page: xbot.web.WebBrowser,
    background_ele,
    drag_ele,
    retry_count: int = 5,
    offset=0,
    ym_token="",
    refresh_elem=None,
):

    if os.name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache folder: {cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

    if not retry_count:
        retry_count = 5

    for _ in range(retry_count):
        web_page.start_monitor_network()
        web_page.find(refresh_elem).click()
        while True:
            vc_mid_cip = web_page.get_responses(url='https://www.temu.com/api/phantom/vc_mid_cip', resource_type='XHR')
            obtain_captcha = web_page.get_responses(url='https://www.temu.com/api/phantom/obtain_captcha', resource_type='XHR')
            if vc_mid_cip and obtain_captcha:
                break
            sleep(1)
        web_page.stop_monitor_network()
        captcha_response = obtain_captcha[0]['body']
        ki_response = vc_mid_cip[0]['body']
        print(ki_response)
        print(captcha_response)
        drag_element = drag_ele


        # 识别
        payload = {"captcha_response": captcha_response, "ki_response": ki_response, "token": ym_token, "type": 22229}

        if ym_token:
            data = ym_captcha_recognition(payload)
            data = data.get("data")
        else:
            data = yd_captcha_recognition(payload)
            if data.get("statusCode") != "200":
                print(data.get("msg"))
                print('识别失败，本次验证不收取费用')
                continue
            data = data.get("response")
        print(data)

        distance = int(data.get("data").get('slide_button_left'))

        # 拖拽
        distance = (distance + int(offset))
        if os.name == "nt":
            distance = int(distance)
        xbot.logging.info(f"Distant:{distance}")
        drag(web_page.find(drag_element), distance)

        sleep(3)

        try:
            _, _, width, height = drag_element.get_bounding()
            if width and height == 0:
                break
        except:
            pass

        if not xbot_visual.web.browser.element_display(
            browser=web_page, selector=background_ele, content_type="display"
        ):
            break

def test_func():
    if 'xbot_extensions'not  in __file__:
        web_page = xbot.web.get_active('chrome')
        background_ele = package.selector('Temu_弧形验证_背景元素')
        slider_ele = package.selector('Temu_弧形验证_滑块元素')
        retry_count = 5
        refresh_elem = package.selector('Temu_弧形验证_刷新元素')
        offset = 0
        ym_token = ''
        handle_captcha(
            web_page,
            background_ele,
            slider_ele,
            retry_count,
            offset,
            ym_token,
            refresh_elem,
        )
        exit()

def main(args):
    test_func()
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    slider_ele = args.get("slider_ele")
    retry_count = args.get("retry_count")
    offset = args.get("offset")
    ym_token = args.get("ym_token", "")
    refresh_elem = args.get("refresh_elem", "")

    handle_captcha(
        web_page,
        background_ele,
        slider_ele,
        retry_count,
        offset,
        ym_token,
        refresh_elem,
    )
