# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import http
import json
import base64
import os
from io import BytesIO
from xbot import print, sleep, web
from . import package
from .package import variables as glv
from PIL import ImageGrab
from xbot._core import robot
from .utils import (
    get_xbot_activity_cache_folder,
    file2base64,
    get_ppi,
    start_upload,
    end_upload,
    upload_captcha_screenshot,
    report_data,
    get_boundary_value,
)

from urllib.parse import urlparse

def save_image_from_body(body, file_path):
    # Base64 解码
    img_data = base64.b64decode(body)
    
    # 写入文件
    with open(file_path, "wb") as f:
        f.write(img_data)

def img_to_base64(image):
    """图片转base64"""
    img_bytes = BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()
    base64_string = base64.b64encode(img_bytes).decode("utf-8")
    return base64_string


def get_xbot_client():
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
            "aiToolInterfaceCodeId": f"jfbym_{captcha_type}",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": captcha_type,
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
    conn.request("POST", "/api/v2/aiservice/call", res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    # print(response_json)
    flag = response_json.get("success")
    if not flag:
        raise Exception(f"错误信息: {response_json}")
    return {"data": response_json.get("data").get("response")}


def handle_captcha(web_page, ele, token, refresh_ele) -> str:
    """处理验证码"""
    os_name = os.name
    if os_name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache Dir:{cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

    save_path = os.path.join(cache_folder, "temp.png")

    # 通过监听获取原图
    web_page.start_monitor_network(resource_type="Image")
    web_page.find(refresh_ele).click(delay_after=0, simulative=True)
    sleep(3)
    res_list = web_page.get_responses(resource_type="All")
    web_page.stop_monitor_network()
    background_img_base64 = res_list[0]['body']
    save_image_from_body(background_img_base64, save_path)
    background_ele_base64 = file2base64(save_path)

    payload = {"image": background_ele_base64, "token": token, "type": 10103}
    # xbot.logging.info(payload)

    if token:
        data = ym_captcha_recognition(payload)
    else:
        data = yd_captcha_recognition(payload)

    try:
        return data.get("data").get("data")
    except Exception as e:
        xbot.logging.warning(f"调用接口异常, 接口返回值: {data}")
        raise

def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        ele = package.selector('定制数英_背景元素')
        refresh_ele = package.selector('定制数英_刷新元素')
        token = ''
        data = handle_captcha(web_page, ele, token, refresh_ele)
        print(data)
        exit()

def main(args):
    test_func()
    web_page = args.get("web_page")
    ele = args.get("ele")
    refresh_ele = args.get('refresh_ele')
    token = args.get("token")
    data = handle_captcha(web_page, ele, token, refresh_ele)
    args["data"] = data
