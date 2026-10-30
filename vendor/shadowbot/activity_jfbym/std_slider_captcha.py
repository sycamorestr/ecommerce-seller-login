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
from .import package  
from .package import variables as glv
from xbot.web.chromium import ChromiumElement
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, gen_selector


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
            "aiToolInterfaceCodeId": "jfbym_22222",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": "22222",
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": {"image": payload.get("image")},
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
    background_ele_in,
    drag_ele,
    retry_count: int = 5,
    offset=0,
    speed=1,
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
        if web_page is None:
            break
            # 判断元素类型
        if type(background_ele_in) != ChromiumElement:
            background_ele = web_page.find(background_ele_in)
        if type(drag_ele) != ChromiumElement:
            drag_element = web_page.find(drag_ele)
        else:
            drag_element = drag_ele

        # 截图
        image_path = os.path.join(cache_folder, "std_slider.png")

        b_x, b_y, b_w, b_h = background_ele.get_bounding(to96dpi=False)
        xbot.win32.screenshot.save_screen_to_file(
            image_path, "png", b_x, b_y, b_x + b_w, b_y + b_h
        )

        background_ele_base64 = file2base64(image_path)

        # 识别
        payload = {"image": background_ele_base64, "token": ym_token, "type": 22222}

        # with open(image_path, "w") as f:
        #     json.dump(payload, f, ensure_ascii=False)
        #     f.close()

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

        if data.get("success"):
            raise Exception(data.get("msg"))

        distance = int(data.get("data"))

        # 拖拽
        distance = (distance + int(offset)) / speed
        if os.name == "nt":
            distance = int(distance * get_ppi())
        xbot.logging.info(f"Distant:{distance}")
        drag(drag_element, distance)

        sleep(3)

        try:
            _, _, width, height = drag_element.get_bounding()
            if width and height == 0:
                break
        except:
            pass

        if not xbot_visual.web.browser.element_display(
            browser=web_page, selector=background_ele_in, content_type="display"
        ):
            break
        
        if refresh_elem and type(refresh_elem) != ChromiumElement:
            refresh_elem = web_page.find(refresh_elem)
            
        if refresh_elem != "" and refresh_elem != None:
            refresh_elem.click()

def test_func():
    if "xbot_extensions" not in __file__:
        web_page = xbot.web.get_active('chrome')
        # background_ele = package.selector('std_slider_captcha_background')
        # slider_ele = package.selector('std_slider_captcha_drag')
        background_ele = gen_selector('//iframe[@name="dialogIframe"]>>//img[@id="main_img"]', '背景元素')
        slider_ele = gen_selector('//iframe[@name="dialogIframe"]>>//div[@class="local_footer"]/img', '拖拽元素')
        retry_count = 5
        offset = 0
        speed = 1
        ym_token = ''
        refresh_elem = gen_selector('//iframe[@name="dialogIframe"]>>//span[.="刷新"]', '刷新元素')
        handle_captcha(
            web_page,
            background_ele,
            slider_ele,
            retry_count,
            offset,
            speed,
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
    speed = args.get("speed", 1)
    ym_token = args.get("ym_token", "")
    refresh_elem = args.get("refresh_elem", "")

    # web_page = web.get_active(mode="chrome")
    # background_ele = "std_slider_captcha_background"
    # slider_ele = "std_slider_captcha_drag"
    # retry_count = 5
    # offset = 0
    # ym_token = ""

    handle_captcha(
        web_page,
        background_ele,
        slider_ele,
        retry_count,
        offset,
        speed,
        ym_token,
        refresh_elem,
    )
