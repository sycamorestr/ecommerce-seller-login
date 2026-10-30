import io
import os
import base64
import xbot
import json
import base64
import urllib
import ctypes
import sqlite3
import random
import xbot_visual
import http.client
from urllib.parse import urlparse
import ast

if os.name == "nt":
    from ctypes import windll

from xbot._core import robot
from xbot import print, sleep, win32, web

from . import package
from .package import variables as glv
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi

from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation

from io import BytesIO
from PIL import ImageGrab, Image


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
    common_info = robot.execute(f'Common.CommonConfig', None)
    token = common_info.get("token")
    conn = http.client.HTTPSConnection(urlparse(common_info.get("webApi")).netloc)
    payload = json.dumps(
        {
            "thirdPartyInterfaceCode": "jfbym_22222",
            "data": {},
            "thirdPartyReqData": {
                "headers": {},
                "params": {},
                "body": {"image": payload.get("image")},
                "pathVariable": {},
            },
            "bizType": "rpa-command",
        }
    )
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    conn.request("POST", "/api/openapi/v2/thirdParty/interface/call", payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json


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
        ctypes.windll.user32.SetCursorPos(x, y)
    else:
        win32.mouse_move(x, y, move_speed="instant")


def get_data_by_distance(distance, one=True):
    db_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if distance < 50:
        di = 50
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 50")
    elif 50 < distance < 150:
        di = 100
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 100")
    else:
        di = 150
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 150")

    rows = cursor.fetchall()

    if one:
        random_index = random.randint(0, len(rows) - 1)

        data = json.loads(rows[random_index][2])
        tmp = []
        for item in data:
            tmp.append([item[0], item[1] + random.randint(-2, 2), item[2]])
        # print("rows[random_index][2]:", rows[random_index][2])
        result = ast.literal_eval(rows[random_index][2])
        for i in range(len(result)):
            result[i][0] = result[i][0] / di * distance

        print("result:", result)
        result = json.dumps(result)
        return json.loads(result)
    return [json.loads(row[2]) for row in rows]


def drag_gen(drag_ele: WebElement, slider_ele: WebElement, distance: int):
    """模拟人工拖拽"""

    start_x, _, w, _ = slider_ele.get_bounding(to96dpi=False)
    start_x = int(start_x + w / 2)

    mouse_pos_path = get_data_by_distance(int(distance))

    new_mouse_pos_path = []
    for i in range(1, len(mouse_pos_path)):
        diff = mouse_pos_path[i][0] - mouse_pos_path[i - 1][0]
        if 0.5 < diff < 3:
            new_mouse_pos_path.append(
                [diff, mouse_pos_path[i][1], mouse_pos_path[i][2]]
            )
    # print(f"new_mouse_pos_path: {new_mouse_pos_path}")

    # print(f"mouse_pos_path: {mouse_pos_path}")
    xbot.win32.manual_motion_on()

    point_x, point_y, w, h = drag_ele.get_bounding(to96dpi=True)
    point_x = int(point_x + (w / 2))
    point_y = int(point_y + (h / 2))
    xbot.win32.mouse_move(point_x, point_y, delay_after=0.1)
    win32.mouse_click(button="left", click_type="down")

    point_x, point_y, w, h = drag_ele.get_bounding(to96dpi=False)
    point_x = int(point_x + (w / 2))
    point_y = int(point_y + (h / 2))

    # 1. 先将 drag_ele 移动到识别处理的位置
    for offset_x, offset_y, t in mouse_pos_path[:-10]:
        xPoint = int(point_x + int(offset_x))
        yPoint = int(point_y + int(offset_y))
        _moveTo(xPoint, yPoint)
        sleep(t / 4000)

    # 2. 判断 slider 是否与拖拽距离一致

    while 1:
        s_x, s_y, w, _ = slider_ele.get_bounding(to96dpi=False)
        s_x = int(s_x + w / 2)
        d_x, d_y, w, h = drag_ele.get_bounding(to96dpi=False)
        d_x = int(d_x + w / 2)
        d_y = int(d_y + h / 2)

        distance_flag = s_x - start_x - distance

        # print(
        #     f"slider_x: {s_x}, start_x: {start_x}, distant, {distance}, offset, {distance_flag}"
        # )

        if abs(distance_flag) < 3:
            break

        # 按照差值方向, 2个像素的移动

        random_item = random.choice(new_mouse_pos_path)

        o_x, o_y, o_t = random_item
        # print(f"o_x: {o_x}, o_y: {o_y}, o_t: {o_t}")

        if distance_flag > 0:
            # print("left")
            o_x = -abs(o_x)
        else:
            # print("right")
            o_x = abs(o_x)

        _moveTo(int(d_x + o_x * random.randint(2, 3)), int(d_y + o_y))

        sleep(o_t / 1200)

    win32.mouse_click(button="left", click_type="up")
    xbot.win32.manual_motion_off()


def handle_captcha(
    web_page: xbot.web.WebBrowser,
    background_ele,
    slider_ele,
    drag_ele,
    retry_count: int = 5,
    offset=0,
    ym_token="",
):
    current_file_path = __file__
    current_file_name = os.path.basename(current_file_path)  # 获得当前文件名

    os_name = os.name
    if os_name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache Dir:{cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
    xbot.logging.info(f"Cache Dir:{cache_folder}")
    if not retry_count:
        retry_count = 5

    for i in range(retry_count):
        # 截图
        image_path = os.path.join(cache_folder, "std_slider.png")
        b_x, b_y, b_w, b_h = web_page.find(background_ele).get_bounding(to96dpi=False)
        s_x, s_y, s_w, s_h = web_page.find(drag_ele).get_bounding(to96dpi=False)
        xbot.win32.screenshot.save_screen_to_file(
            image_path, "png", b_x, b_y, b_x + b_w, b_y + b_h
        )
        background_ele_base64 = file2base64(image_path)

        # 识别
        payload = {"image": background_ele_base64, "token": ym_token, "type": 22222}

        if ym_token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)
            if not data.get("success"):
                raise Exception(data.get("msg"))
            data = data.get("data")

        # print(data)

        if data.get("msg") != "识别成功":
            raise Exception(data.get("msg"))

        distance = int(data.get("data").get("data"))

        # 拖拽
        distance = distance + int(offset)

        xbot.logging.info(f"Distant:{distance}")
        drag_gen(web_page.find(drag_ele), web_page.find(slider_ele), distance)

        sleep(3)
        try:
            x, y, width, height = drag_ele.get_bounding()
            if width and height == 0:
                print("页面已无验证码，现在退出")
                break
        except:
            pass

        if not xbot_visual.web.browser.element_display(
            browser=web_page, selector=background_ele, content_type="display"
        ):
            break


def main(args):
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    slider_ele = args.get("slider_ele")
    drag_ele = args.get("drag_ele")
    retry_count = args.get("retry_count")
    offset = args.get("offset")
    speed = args.get("speed", 1)
    ym_token = args.get("ym_token", "")
    refresh_elem = args.get("refresh_elem", "")

    # web_page = web.get_active(mode="chrome")
    # background_ele = "jd_slider_captcha_background"
    # drag_ele = "jd_slider_captcha_drag"
    # slider_ele = "jd_slider_ele2"
    # retry_count = 10
    # offset = 0
    # ym_token = ""

    handle_captcha(
        web_page, background_ele, slider_ele, drag_ele, retry_count, offset, ym_token
    )
