# 使用提醒:
# 1. xbot 包提供软件自动化、网页、截图、鼠标等功能
# 2. 当此模块作为流程独立运行时执行 main 函数
# 3. 可视化流程中可以通过“调用模块”指令使用此模块

import xbot
import os
import xbot_visual
import json
import base64
import http.client
import tempfile
import subprocess
import ctypes

if os.name == "nt":
    from ctypes import windll  # noqa: F401

from xbot.web.element import WebElement
from xbot import sleep, win32, web, print
from xbot._core import robot
from urllib.parse import urlparse
from xbot.selector import Selector


def file2base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_scale_factor():
    try:
        result = subprocess.run(
            [
                "qdbus",
                "com.deepin.daemon.Appearance",
                "/com/deepin/daemon/Appearance",
                "com.deepin.daemon.Appearance.GetScaleFactor",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return None


def get_scaling() -> float:
    if os.name == "nt":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass

        user32 = ctypes.WinDLL("user32.dll")
        gdi32 = ctypes.WinDLL("gdi32.dll")

        try:
            dpi = user32.GetDpiForSystem()
        except AttributeError:
            dc = user32.GetDC(None)
            dpi = gdi32.GetDeviceCaps(dc, 88)
            user32.ReleaseDC(None, dc)

        return round((dpi / 96), 2)

    proportion = get_scale_factor()
    if not proportion:
        return 1.0
    return proportion


def get_xbot_activity_cache_folder(folder_name: str) -> str:
    base_temp = tempfile.gettempdir()
    cache_folder = os.path.join(base_temp, "xbot_app", folder_name)
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    return cache_folder


def ym_captcha_recognition(payload: dict, timeout: float = 10):
    """请求云码识别验证码，支持自定义超时时间。"""
    conn = http.client.HTTPConnection("api.jfbym.com", timeout=timeout)
    headers = {"Content-Type": "application/json"}
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload: dict, timeout: float = 10):
    """使用影刀 AI 服务请求验证码。"""
    captcha_type = payload.get("type")
    payload = dict(payload)
    payload.pop("type", None)
    payload.pop("token", None)

    common_info = robot.execute("Common.CommonConfig", None)
    token = common_info.get("token")
    web_api = common_info.get("webApi")

    parsed = urlparse(web_api)
    is_ssl = parsed.scheme.lower() == "https"
    host = parsed.netloc

    if is_ssl:
        conn = http.client.HTTPSConnection(host, timeout=timeout)
    else:
        conn = http.client.HTTPConnection(host, timeout=timeout)

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
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    conn.request("POST", "/api/v2/aiservice/call", res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()

    data = response_json.get("data")
    if not isinstance(data, dict):
        raise Exception(f"错误信息: {response_json}")

    status_code = int(data.get("statusCode") or 500)
    if status_code != 200:
        raise Exception(f"错误信息: {response_json}")
    return response_json


def extract_position_data(response_json):
    """兼容云码直连和增值服务两种返回结构。"""
    data = response_json.get("data")
    if isinstance(data, dict):
        if "response" in data and isinstance(data.get("response"), dict):
            return data.get("response", {}).get("data")
        if "data" in data:
            return data.get("data")
    return data


def parse_positions(raw_data):
    """
    支持以下几种格式:
    1. '12,34|56,78'
    2. [{'x': 12, 'y': 34}, {'x': 56, 'y': 78}]
    3. [[12, 34], [56, 78]]
    """
    if not raw_data:
        raise Exception("识别结果为空")

    if isinstance(raw_data, str):
        positions = []
        for item in raw_data.split("|"):
            item = item.strip()
            if not item:
                continue
            x_str, y_str = item.split(",", 1)
            positions.append((int(float(x_str)), int(float(y_str))))
        if not positions:
            raise Exception(f"无法解析坐标字符串: {raw_data}")
        return positions

    if isinstance(raw_data, list):
        positions = []
        for item in raw_data:
            if isinstance(item, dict):
                positions.append((int(float(item["x"])), int(float(item["y"]))))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                positions.append((int(float(item[0])), int(float(item[1]))))
        if not positions:
            raise Exception(f"无法解析坐标数组: {raw_data}")
        return positions

    raise Exception(f"不支持的识别结果格式: {raw_data}")


def resolve_element(web_page, web_element):
    if hasattr(web_element, "get_bounding"):
        return web_element
    if isinstance(web_element, str):
        text = web_element.strip()
        if text.startswith("/") or text.startswith("./") or text.startswith("("):
            return web_page.find_by_xpath(text)
        return web_page.find(text)
    return web_page.find(web_element)


def click_positions(element, positions):
    bounding = element.get_bounding()
    ppi = get_scaling()
    for offset_x, offset_y in positions:
        target_x = (float(offset_x) / ppi) + bounding[0]
        target_y = (float(offset_y) / ppi) + bounding[1]
        xbot.win32.mouse_move(target_x, target_y, delay_after=0.5)
        xbot.win32.mouse_click(delay_after=0.3)


def handle_captcha(
    web_page: xbot.web.WebBrowser,
    background_ele: WebElement,
    retry_count: int = 5,
    token="",
    extra="",
    confirm_ele=None,
    timeout: float = 10,
):
    """
    处理云码 30119 类型验证码。

    :param web_page: 网页对象
    :param background_ele: 验证码背景图
    :param retry_count: 重试次数
    :param token: 云码 token，空则表示使用影刀增值服务请求
    :param extra: 非必选，顺序说明字符串
    :param confirm_ele: 点选完成后的确认元素
    :param timeout: 请求超时时间（秒）
    """
    if not retry_count:
        retry_count = 5

    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    background_ele_save_path = os.path.join(cache_folder, "captcha_30119.png")

    for _ in range(retry_count):
        element = resolve_element(web_page, background_ele)
        x, y, width, height = element.get_bounding(to96dpi=False)
        win32.screenshot.save_screen_to_file(
            background_ele_save_path,
            "png",
            x,
            y,
            x + width,
            y + height,
        )
        background_img_base64 = file2base64(background_ele_save_path)
        payload = {
            "image": background_img_base64,
            "token": token,
            "type": "30119",
        }
        if extra:
            payload["extra"] = str(extra)

        if token:
            response_json = ym_captcha_recognition(payload, timeout=timeout)
            print(response_json)
            if response_json.get("msg") != "识别成功":
                raise Exception("识别失败, 请重试")
        else:
            response_json = yd_captcha_recognition(payload)

        raw_data = extract_position_data(response_json)
        positions = parse_positions(raw_data)
        click_positions(element, positions)

        if confirm_ele:
            resolve_element(web_page, confirm_ele).click()

        sleep(8)

        if not xbot_visual.web.browser.element_display(
            browser=web_page,
            content_type="display",
            selector=background_ele,
        ):
            break



def test():
    """本地调试入口，按需自行修改选择器和 token。"""
    # if "xbot_extension" in __file__:
    #     return

    web_page = web.get_active(mode="edge")
    # background_ele = '//div[contains(@class, "detail-page-container")]'
    captcha_refresh_selector_data = {
        "id": "zhf",
        "name": "zfb",
        "type": "simple",
        "xpath": {
            "enable": "true",
            "segments": ['//div[contains(@class, "detail-page-container")]'],
        },
    }
    background_ele = Selector(captcha_refresh_selector_data)
    # token = "REDACTED"
    token = ""
    extra = ""
    confirm_ele = ""

    handle_captcha(
        web_page=web_page,
        background_ele=background_ele,
        retry_count=5,
        token=token,
        extra=extra,
        confirm_ele=confirm_ele,
        timeout=10,
    )
    exit()


def main(args):
    handle_captcha(
        web_page=args.get("web_page"),
        background_ele=args.get("background_ele"),
        retry_count=args.get("retry_count", 5),
        token=args.get("token", ""),
        extra=args.get("extra", ""),
        confirm_ele=args.get("confirm_ele"),
        timeout=float(args.get("timeout", 10)),
    )
