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
import re
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
import time
import threading


ROTATE_RE = re.compile(r"rotate\(\s*(-?\d+(?:\.\d+)?)deg\s*\)")


def img_to_base64(image):
    """图片转base64"""
    img_bytes = BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()
    base64_string = base64.b64encode(img_bytes).decode("utf-8")
    return base64_string


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
    # print(response_json)
    return response_json.get("data")


def yd_captcha_recognition(payload: dict):
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
            "aiToolInterfaceCodeId": "jfbym_276502",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": "276502",
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
    # print(response_json)
    return response_json.get("data").get("response")


def _get_rotate_deg_from_style(style_text):
    """从 style 文本里提取 rotate 角度。"""
    if not style_text:
        return None
    matched = ROTATE_RE.search(style_text)
    if not matched:
        return None
    try:
        return float(matched.group(1))
    except Exception:
        return None


def _get_candidate_tile_nodes(container_ele):
    """从整块验证码里直接拿 4 张小图节点。"""
    try:
        nodes = container_ele.find_all_by_xpath('.//*[@class="image-item clickpuzzle"]')
    except Exception:
        nodes = None
    return nodes or []


def _resolve_tile_node_by_offset(container_ele, offset_x, offset_y):
    """根据云码返回的相对坐标，在验证码容器里找到对应小图节点。"""
    try:
        box_x, box_y, _, _ = container_ele.get_bounding(to96dpi=False)
    except Exception:
        return None

    point_x = box_x + offset_x
    point_y = box_y + offset_y
    best_node = None
    best_distance = None

    for node in _get_candidate_tile_nodes(container_ele):
        try:
            x, y, w, h = node.get_bounding(to96dpi=False)
        except Exception:
            continue

        if x <= point_x <= x + w and y <= point_y <= y + h:
            return node

        center_x = x + (w / 2)
        center_y = y + (h / 2)
        distance = abs(center_x - point_x) + abs(center_y - point_y)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_node = node

    return best_node


def _get_rotate_info_by_offset(container_ele, offset_x, offset_y):
    """按云码点击坐标读取对应小图当前 rotate 信息。"""
    tile_node = _resolve_tile_node_by_offset(container_ele, offset_x, offset_y)
    if tile_node is None:
        return {"style": "", "rotate_deg": None}

    try:
        style_text = tile_node.get_attribute("style") or ""
    except Exception:
        style_text = ""

    rotate_deg = _get_rotate_deg_from_style(style_text)
    return {"style": style_text, "rotate_deg": rotate_deg}


def handle_captcha(web_page, image_ele, commit_ele, ym_token, retry_count=5):
    """处理验证码"""
    captcha_type = 276502
    if os.name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache folder: {cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

    for i in range(retry_count):
        image_path = os.path.join(cache_folder, "label_image_ele.png")
        captcha_ele = web_page.find(image_ele)
        b_x, b_y, b_w, b_h = captcha_ele.get_bounding(to96dpi=False)
        xbot.win32.screenshot.save_screen_to_file(
            image_path, "png", b_x, b_y, b_x + b_w, b_y + b_h
        )
        image_ele_base64 = file2base64(image_path)
        # 识别
        payload = {"image": image_ele_base64, "token": ym_token, "type": captcha_type}

        if ym_token:
            data = ym_captcha_recognition(payload)
            data = data.get("data")
        else:
            data = yd_captcha_recognition(payload)
            data = data.get("data")
        # print(data)

        for item in data:
            click_num = int(item.get("angle") / 90)
            if click_num <= 0:
                continue

            move_x = b_x + item.get("pos")[0]
            move_y = b_y + item.get("pos")[1]
            xbot.win32.mouse_move(int(move_x * get_ppi()), int(move_y * get_ppi()))
            xbot.win32.mouse_click()
            sleep(0.35)

            probe_info = _get_rotate_info_by_offset(
                captcha_ele,
                item.get("pos")[0],
                item.get("pos")[1],
            )
            rotate_deg = probe_info.get("rotate_deg")
            if rotate_deg is not None and rotate_deg < 0:
                applied_click_num = (4 - click_num) % 4
                rotate_direction = "counterclockwise"
            else:
                applied_click_num = click_num
                rotate_direction = "clockwise"

            # print(
            #     {
            #         "cloud_clicks": click_num,
            #         "applied_clicks": applied_click_num,
            #         "rotate_direction": rotate_direction,
            #         "probe_rotate_deg": rotate_deg,
            #         "probe_style": probe_info.get("style"),
            #         "pos": item.get("pos"),
            #     }
            # )

            for _ in range(1, applied_click_num):
                xbot.win32.mouse_click()
                sleep(0.15)

        web_page.find(commit_ele).click()
        sleep(1)
        if not xbot_visual.web.browser.element_display(
            browser=web_page, content_type="display", selector=image_ele
        ):
            break

    # return


def test_func():
    if "xbot_extensions" not in __file__:
        web_page = xbot.web.get_active("chrome")
        image_ele = package.selector("zfb_four_image")
        commit_ele = package.selector("zfb_four_commit_ele")
        ym_token = ""
        retry_count = 5
        handle_captcha(web_page, image_ele, commit_ele, ym_token, retry_count)
        exit()


def main(args):
    test_func()
    web_page = args.get("web_page")
    image_ele = args.get("image_ele")
    commit_ele = args.get("commit_ele")
    ym_token = args.get("ym_token")
    retry_count = args.get("retry_count", 5)
    handle_captcha(web_page, image_ele, commit_ele, ym_token, retry_count)
