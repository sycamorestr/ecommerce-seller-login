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


def ym_captcha_recognition(payload, timeout):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    conn.timeout = timeout
    headers = {"Content-Type": "application/json"}
    # print(payload.get("type"))
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)

    response = conn.getresponse()
    response_data = response.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload: dict, timeout: int):
    """使用增值服务请求验证码"""
    captcha_type = payload.get("type")
    payload.pop("type")

    common_info = robot.execute(f"Common.CommonConfig", None)

    token = common_info.get("token")
    web_api = common_info.get("webApi")

    parsed = urlparse(web_api)
    is_ssl = parsed.scheme.lower() == "https"
    host = parsed.netloc

    if is_ssl:
        conn = http.client.HTTPSConnection(host, timeout=30)
    else:
        conn = http.client.HTTPConnection(host, timeout=30)
    conn.timeout = timeout
    if captcha_type not in ["131781"]:
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
    else:
        res_payload = json.dumps(
            {
                "aiToolInterfaceCodeId": f"captcha_jfbym_jfbym_{captcha_type}",
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
    if not flag or not response_json.get("data").get("response").get("data"):
        raise Exception(f"错误信息: {response_json}")
    return {"data": response_json.get("data").get("response")}


def handle_captcha(web_page, ele, token, captcha_type, is_trim, timeout) -> str:
    """处理验证码"""
    # current_file_path = __file__
    # current_file_name = os.path.basename(current_file_path) #获得当前文件名
    # if isinstance(captcha_type, int):
    #     captcha_type = int(captcha_type)
    # e_x, e_y, e_w, e_h = web_page.find(ele).get_bounding(to96dpi=False)
    # xbot.win32.clipboard.clear()
    # xbot.win32.screenshot.save_screen_to_clipboard(e_x, e_y, e_x + e_w, e_y + e_h)
    # background_img = ImageGrab.grabclipboard()
    # xbot.win32.clipboard.clear()
    # image_base64  = img_to_base64(background_img)

    if isinstance(captcha_type, int):
        captcha_type = int(captcha_type)
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
    web_page.find(ele).screenshot(folder_path=cache_folder, filename="temp.png")
    background_ele_base64 = file2base64(save_path)

    payload = {"image": background_ele_base64, "token": token, "type": captcha_type}
    # xbot.logging.info(payload)
    if is_trim:
        payload['extra'] = "需要区分大小写"
        
    if token:
        data = ym_captcha_recognition(payload, timeout)
        print(f"传入token, token的值为: {token}")
    else:
        data = yd_captcha_recognition(payload, timeout)
        print(f"走影刀")

    try:
        return data.get("data").get("data")
    except Exception as e:
        xbot.logging.warning(f"调用接口异常, 接口返回值: {data}")
        raise


def main(args):
    web_page = args.get("web_page")
    ele = args.get("ele")
    captcha_type = args.get("captcha_type")
    token = args.get("token")
    is_trim = args.get('is_trim')
    timeout = args.get('timeout', 20)
    # web_page = web.get_active(mode="edge")
    # token = ""
    # ele = "std_alphanum_captcha_ele"
    # captcha_type = "10110"
    data = handle_captcha(web_page, ele, token, captcha_type, is_trim, timeout)
    # print(data)
    # xbot.logging.info(f"caption code: {data}")
    args["data"] = data
