# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import math
import random
import os

from xbot import print, sleep
from .import package
from .package import variables as glv

import xbot
import xbot_visual
import base64
import json
import base64
import io
import urllib
import http.client
from urllib.parse import urlparse
import ctypes
import sqlite3
import json
import random
import ast

from PIL import ImageGrab, Image

from PIL import Image
from .xtrace import XTrace
from io import BytesIO
if os.name == 'nt':
    from ctypes import windll
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation

from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv

from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi,upload_captcha_screenshot, report_data, get_boundary_value

def get_data_by_distance(distance, one=True):
    db_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="test_database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if distance <= 50:
        di = 50
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 50")
    elif 50 < distance < 150:
        di = 100
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 100")
    elif 150 <= distance < 200:
        di = 150
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 150")
    else:
        di = 200
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 200")

    rows = cursor.fetchall()

    if one:
        random_index = random.randint(0, len(rows) - 1)

        data = json.loads(rows[random_index][2])
        tmp = []
        for item in data:
            tmp.append([item[0]+random.randint(-1, 1), item[1]+random.randint(-1, 1), item[2]])
        # print("rows[random_index][2]:", rows[random_index][2])
        result = ast.literal_eval(rows[random_index][2])
        for i in range(len(result)):
            result[i][0] = result[i][0] * distance  / di
        result[-1][0] = distance
        # print("result:", result)
        result = json.dumps(result)
        return json.loads(result)
    return [json.loads(row[2]) for row in rows]

def decode_image(base64_string) -> Image:
    """字符串转图片"""
    missing_padding = len(base64_string) % 4
    if missing_padding:
        base64_string += '='* (4 - missing_padding)
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    return img

def encode_image(image):
    """图片转base64"""
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    base64_string = base64.b64encode(img_bytes).decode('utf-8')
    return base64_string

def get_ppi():
    """
    获取屏幕的缩放
    """
    if os.name == 'nt':
        LOGPIXELSX = 88
        LOGPIXELSY = 90
        user32 = windll.user32
        user32.SetProcessDPIAware()
        dc = user32.GetDC(0)
        pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
        user32.ReleaseDC(0, dc)
        res = float.as_integer_ratio(round(pix_per_inch / 96,2))
        return res[1]/res[0]
    else:
        return 1

def ym_recg(token, big_image_base64, small_image_base64):
    """请求云码识别淘"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = { 'Content-Type': 'application/json'}
    data = { 'image': big_image_base64, 'token': token, 'type': 30330 ,"image2":small_image_base64}
    data_json = json.dumps(data)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json

def yd_recg(image_base64, image2_base64):
    common_info = robot.execute(f'Common.CommonConfig', None)
    token = common_info.get("token")
    conn = http.client.HTTPSConnection(urlparse(common_info.get("webApi")).netloc)
    payload = json.dumps({
        "thirdPartyInterfaceCode": "jfbym_30330",
        "data": {},
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": {
                "image": image_base64,
                "image2":image2_base64
            },
            "pathVariable": {}
        },
        "bizType": "rpa-command"
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/api/openapi/v2/thirdParty/interface/call", payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def ease_delta(s, t):
    t = t-1
    return  t * t * ((t + 1) * s + t) + 1

def time_ease(xOffset):
    num_slices = math.floor(xOffset/3) + random.randint(-3,5)
    overshoot = random.random() / 2 + 0.9
    # overshoot = 1.70158
    traces=[]
    for i in range(num_slices):
        delta = math.floor(ease_delta(overshoot, (i+1)/num_slices) * xOffset)
        if len(traces) > 0 and traces[-1][0] == delta:
            continue
        traces.append([delta,(33 + random.randint(-12, 24))/600])
    return traces

def generate_random_point(x1, y1, x2, y2):
    x = random.uniform(x1, x2)
    y = random.uniform(y1, y2)
    return (x, y)

def gen_random_float():
    return random.randint(1,3) + random.uniform(0.0, 1.0)

def drag_x(drag_ele, distance):
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

def gen_move_speed():
    return random.choice(["fast", "middle", "slow"])

def drag_w(drag_ele: WebElement, distance: int):
    """模拟人工拖动
    """
    x, y, width, height = drag_ele.get_bounding()
    # 改动1：拖拽 target 随机点
    pos_center_x, pos_center_y = generate_random_point(
        x + 5, y + 5, x + width - 5, y + height - 5
    )

    win32.manual_motion_on(
        motion_move=True, motion_click=True, motion_delay=True, min_time=1, max_time=1
    )

    # 改动2：移到拖拽块上的速度随机
    move_speed = random.choice(["fast","middle"])
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)

    # 改动3：按下 left 键后，随机延迟
    win32.mouse_click(button="left", click_type="down", delay_after=random.uniform(0.0, 0.5))

    # 改动4：随机加中间点，拖动速度随机
    x = pos_center_x + distance + random.randint(-15, 15)
    y = pos_center_y + distance + random.randint(-100, 100)
    move_speed = random.choice(["slow", "middle"])
    win32.mouse_move(x, y, move_speed=move_speed)

    x = x + random.randint(-10, 10)
    y = y + random.randint(-10, 10)
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed="slow")

    # 改动5：最终点 x，y 随机，拖动速度随机
    x = pos_center_x + distance + random.randint(-5, 7)
    y = pos_center_y + distance + random.randint(-10, 10)
    win32.mouse_move(x, y, move_speed="slow")

    # 改动5：松开左键后，随机延迟
    tt = random.uniform(0.1, 2)
    sleep(tt)
    win32.mouse_click(button="left", click_type="up", delay_after=random.uniform(0.0, 0.5))
    win32.manual_motion_off()


def drag_j(drag_ele:WebElement, distance:int):
    """模拟人工拖动"""
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x, pos_center_y = generate_random_point(x+5, y+5, x+width-5, y+height-5)
    win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=1, max_time=3)
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=gen_move_speed())
    win32.mouse_click(button="left", click_type="down", delay_after=random.uniform(0.0, 1.0))
    
    
    offset = random.randint(int(distance * 0.2), int(distance * 0.3))
    distance_80 = distance - offset
    x = pos_center_x + distance_80
    y = pos_center_y+ random.randint(-int(distance * 0.01), int(distance * 0.01))
    win32.mouse_move(x, y,move_speed=gen_move_speed(), delay_after=random.uniform(0.0, 1.0))
    
    if random.randint(0,1):
        offset = random.randint(int(distance * 0.2), int(distance * 0.3))
        x = pos_center_x + distance + offset
        y = pos_center_y+ random.randint(-int(distance * 0.01), int(distance * 0.01))
        win32.mouse_move(x, y,move_speed=gen_move_speed(), delay_after=random.uniform(0.0, 1.0))
    
    x = pos_center_x + distance + random.randint(-5, 7)
    y = pos_center_y + random.randint(-10, 10)
    win32.mouse_move(pos_center_x + distance, pos_center_y,move_speed=gen_move_speed(), delay_after=random.uniform(0.0, 1.0))
    
    win32.mouse_click(button="left", click_type="up", delay_after=random.uniform(0.0, 1.0))
    win32.manual_motion_off()

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


def drag_g(drag_ele:WebElement, distance:int):
    trace = XTrace()
    _, mouse_pos_path = trace.get_mouse_pos_path(distance)
    # mouse_pos_path -> [[x, y, t], [x, y, t], [x, y, t]], x轴偏移, y轴偏移, t是鼠标移动直接的时间间隔
    x, y, width, height = drag_ele.get_bounding(to96dpi=True)
    point_x = x+ int(width/2)+random.randint(-5, 5)
    point_y = y+ int(height/2)+random.randint(-5, 5)
    win32.mouse_move(point_x=point_x, point_y=point_y, move_speed="middle")
    win32.mouse_click(button="left", click_type="down")

    for offset_x, offset_y, t in mouse_pos_path:
        xPoint = point_x + int(offset_x )
        yPoint = point_y + int(offset_y )
        _moveTo(xPoint, yPoint)
        sleep(t/1000)
    
    sleep(2)
    
    win32.mouse_click(button="left", click_type="up")

def drag_gen(drag_ele:WebElement, distance:int):
    mouse_pos_path = get_data_by_distance(distance)
    xbot.win32.manual_motion_on()
    # drag_ele.hover(simulative=True)

    x, y, width, height = drag_ele.get_bounding()
    point_x = int(x + width / 2) + random.randint(-5, 5)
    point_y = int(y + height / 2) + random.randint(-5, 5)

    xbot.win32.mouse_move(point_x, point_y)
    # point_x, point_y = xbot.win32.get_mouse_position()
    win32.mouse_click(button="left", click_type="down")

    for offset_x, offset_y, t in mouse_pos_path:
        # print(offset_x, offset_y, t)
        xPoint = int((point_x + offset_x) / get_ppi()) 
        yPoint = int((point_y + offset_y) / get_ppi())
        _moveTo(xPoint, yPoint)
        sleep(t/1000)
    
    sleep(2)
    
    win32.mouse_click(button="left", click_type="up")
    xbot.win32.manual_motion_off()    


def get_web_page_by_web_page(web_page):
        product_name = getattr(web_page, "product_name", "cef" if web_page._controller == "CEFBrowser" else "firefox")
        return xbot.web.get_active(mode=product_name)


def handle_verification(web_page:xbot.web.WebBrowser, background_ele, rotate_ele, drag_ele, slider_ele,retry_count: int=5, offset=0, ym_token=None):
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名

    if not retry_count: retry_count=5

    if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=background_ele):
        return


    for i in range(retry_count):
        _, _, rotate_width, rotate_height = web_page.find(rotate_ele).get_bounding(to96dpi=True)
        _, _, slider_width, slider_height = web_page.find(slider_ele).get_bounding(to96dpi=True)
        _, _, drag_width, drag_height = web_page.find(drag_ele).get_bounding(to96dpi=True)
        _, _, background_width, background_height = web_page.find(background_ele).get_bounding(to96dpi=False)
        # print(slider_width-drag_width)

        src_attribute = web_page.find(rotate_ele).get_attribute("src")
        _, rotate_image_ele_base64 = src_attribute.split(",", 1)
        rotate_image_ele_image = decode_image(rotate_image_ele_base64)
        image_width, image_height = rotate_image_ele_image.size

        style_attribute = web_page.find(background_ele).get_attribute("style")
        _, background_ele_base64, _ = style_attribute.split('"')
        _, background_ele_base64 = background_ele_base64.split(",", 1)

        drag_element = web_page.find(drag_ele)



        if ym_token:
            reslut = ym_recg(ym_token, background_ele_base64, rotate_image_ele_base64)
            if reslut.get("msg") != "识别成功":
                raise Exception(reslut)
            data = reslut.get("data").get("data")
        else:
            reslut = yd_recg(background_ele_base64, rotate_image_ele_base64)

            if reslut.get("data").get("msg") != "识别成功":
                raise Exception(reslut)
            data = reslut.get("data").get("data").get("data")

        # distance = int(data)
        distance = (slider_width-drag_width) * data / 360 + offset
        
        # if random.randint(0,1):
        #     drag_w(drag_element, distance)
        # else:
        #     drag_j(drag_element, distance)
        drag_gen(drag_element, distance)
        sleep(3)

        web_page = get_web_page_by_web_page(web_page)

        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=background_ele):

            break

def main(args):
    web_page = args.get("web_page")
    background_ele = args.get("background_ele", "jd_wai")
    rotate_ele = args.get("rotate_ele", "jd_nei")
    drag_ele = args.get("drag_ele", "drag_jd")
    slider_ele = args.get("slider_ele", "slider_jd")
    retry_count = args.get("retry_count", 5)
    offset = args.get("offset", 0)
    ym_token = args.get("ym_token")
    # web_page = web.get_active(mode='chrome')
    handle_verification(web_page, background_ele, rotate_ele, drag_ele, slider_ele,retry_count, offset, ym_token)
