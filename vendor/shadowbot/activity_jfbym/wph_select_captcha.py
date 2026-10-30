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
from io import BytesIO
from xbot import print, sleep, web

if os.name == "nt":
    from ctypes import windll
from . import package
from .package import variables as glv
from PIL import ImageGrab, Image
from xbot._core import robot
import urllib.request
from urllib.parse import urlparse 



def get_ppi():
    """获取屏幕的缩放比"""
    if os.name == 'nt':
        LOGPIXELSX = 88
        LOGPIXELSY = 90
        user32 = windll.user32
        user32.SetProcessDPIAware()
        dc = user32.GetDC(0)
        pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
        user32.ReleaseDC(0, dc)
        res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
        return res[0] / res[1]
    else:
        return 1


def img_to_base64(image):
    """图片转base64"""
    img_bytes = BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()
    base64_string = base64.b64encode(img_bytes).decode("utf-8")
    return base64_string


def image_to_base64(url):
    with urllib.request.urlopen(url) as response:
        data = response.read()
        base64_data = base64.b64encode(data)
        img = Image.open(BytesIO(data))
        width, height = img.size
        base64_string = base64_data.decode("utf-8")
        return base64_string, width, height


def get_xbot_client():
    """获取客户端 token"""
    common_info = robot.execute(f"Common.CommonConfig", None)
    return common_info.get("token")


def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = {"Content-Type": "application/json"}
    # print(payload.get("type"))
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload: dict):
    """使用增值服务请求验证码"""
    captcha_type = payload.get("type")
    payload.pop("type")

    # 判断客户端版本, 是否使用ssl, host, 以及token
    common_info = robot.execute(f"Common.CommonConfig", None)

    token = common_info.get("token")
    web_api = common_info.get("webApi")

    parsed = urlparse(web_api)
    is_ssl = parsed.scheme.lower() == "https"
    host = parsed.hostname


    if is_ssl:
        conn = http.client.HTTPSConnection(host)
    else:
        conn = http.client.HTTPConnection(host)

    res_payload = json.dumps(
        {
            "thirdPartyInterfaceCode": f"jfbym_{captcha_type}",
            "data": {},
            "thirdPartyReqData": {
                "headers": {},
                "params": {},
                "body": payload,
                "pathVariable": {},
            },
            "bizType": "rpa-command",
        }
    )
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    conn.request(
        "POST", "/api/openapi/v2/thirdParty/interface/call", res_payload, headers
    )
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    # print(response_json)
    data = response_json.get("data")
    if not data:
        raise Exception(f"错误信息: {response_json}")
    return data


def handle_captcha(web_page, background_element, tip_element, ym_token, retry_count):
    """处理验证码"""
    captcha_type = 30026

    if not retry_count:
        retry_count = 5

    web_page.find(tip_element).hover()

    for _ in range(int(retry_count)):
        try:
            e_a_x, e_a_y, e_a_w, e_a_h = web_page.find(background_element).get_bounding(
                to96dpi=True
            )

            background_element_url = web_page.find(background_element).get_attribute(
                name="src"
            )
            tip_element_url = web_page.find(tip_element).get_attribute(name="src")
            background_element_base64, background_w, background_h = image_to_base64(background_element_url)
            # print(f'原图背景width：【{background_w}】, 渲染背景width：【{e_a_w}】，比例为：【{e_a_w / background_w}】')
            tip_element_base64, tip_w, tip_h= image_to_base64(tip_element_url)
            payload = {
                "image": tip_element_base64,
                "image2": background_element_base64,
                "token": ym_token,
                "type": captcha_type,
            }
            if ym_token:
                data = ym_captcha_recognition(payload)
            else:
                data = yd_captcha_recognition(payload)

            # 判断云码是否识别成功
            if data.get("msg") != "识别成功":
                raise Exception(f'验证码报错: {data.get("msg")}')

            data = data.get("data").get("data")
            positions = [item.split(",") for item in data.split("|")]
            for t_x, t_y in positions:
                target_p_x = e_a_x + (int(int(t_x)) * (e_a_w / background_w))
                target_p_y = e_a_y + (int(int(t_y)) * (e_a_h / background_h))
                xbot.win32.mouse_move(target_p_x, target_p_y)
                xbot.win32.mouse_click()

            sleep(1)
            if not xbot_visual.web.browser.element_display(
                browser=web_page, content_type="display", selector=background_element
            ):
                return
        except Exception as e:
            print(e)
            continue

    if web_page.is_element_displayed(background_element):
        raise Exception('验证码依旧存在，请重试指令')


def main(args):
    web_page = args.get("web_page")
    background_element = args.get("background_element")
    tip_element = args.get("tip_element")
    ym_token = args.get("ym_token")
    retry_count = args.get("retry_count", 5)

    # web_page = web.get_active(mode="chrome")
    # background_element = "jdsureele"
    # tip_element = '确定test'
    # ym_token = ""

    handle_captcha(web_page, background_element, tip_element, ym_token, retry_count)
