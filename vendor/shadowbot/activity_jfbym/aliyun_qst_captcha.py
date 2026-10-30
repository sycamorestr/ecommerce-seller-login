# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import xbot_visual
import base64
import json
import base64    
import io
import os
import http.client
from PIL import ImageGrab
import random
import sqlite3
import time
import ast
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse

if os.name == 'nt':
    from ctypes import windll
from xbot.selector import Selector

from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation
import re
from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv  

from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload, get_boundary_value, upload_captcha_screenshot, report_data, gen_selector
import ctypes
from .xtrace import XTrace
from xbot._core import robot
print = [lambda *_, **__: None, print][__package__ == "xbot_robot"]


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
        # print("result:", result)
        result = json.dumps(result)
        return json.loads(result)
    return [json.loads(row[2]) for row in rows]


def drag_gen(drag_ele:WebElement, distance:int):
    mouse_pos_path = get_data_by_distance(distance)
    xbot.win32.manual_motion_on()
    drag_ele.hover(simulative=True)
    point_x, point_y = xbot.win32.get_mouse_position()
    win32.mouse_click(button="left", click_type="down")

    for offset_x, offset_y, t in mouse_pos_path:
        print(offset_x, offset_y, t)
        xPoint = point_x + int(offset_x )
        yPoint = point_y + int(offset_y )
        _moveTo(xPoint, yPoint)
        sleep(t/800)
    
    win32.mouse_click(button="left", click_type="up")
    xbot.win32.manual_motion_off()  


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
    x, y, width, height = drag_ele.get_bounding(to96dpi=True)
    point_x = x+ int(width/2)
    point_y = y+ int(height/2)
    win32.mouse_move(point_x=point_x, point_y=point_y, move_speed="middle")
    win32.mouse_click(button="left", click_type="down")

    for offset_x, offset_y, t in mouse_pos_path:
        xPoint = point_x + int(offset_x )
        yPoint = point_y + int(offset_y )
        _moveTo(xPoint, yPoint)
        sleep(t/1000)
    
    win32.mouse_click(button="left", click_type="up")


def join_images(image1, image2):
    """图片拼接"""
    width1, height1 = image1.size
    width2, height2 = image2.size
    new_image = Image.new('RGB', (max(width1, width2), height1+height2 +11), (255, 255, 255))
    new_image.paste(image1, (0, 0)) 
    new_image.paste(image2, (0, height1+11))
    return new_image


def encode_image(image):
    """图片转base64"""
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    base64_string = base64.b64encode(img_bytes).decode('utf-8')
    return base64_string


def decode_image(base64_string):
    """字符串转图片"""
    missing_padding = len(base64_string) % 4
    if missing_padding:
        base64_string += '=' * (4 - missing_padding)
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    return img.convert('RGBA')


def get_ppi():
    """
    获取屏幕的缩放
    """
    for _ in range(5):
        try:
            if os.name == 'nt':
                LOGPIXELSX = 88
                LOGPIXELSY = 90
                user32 = windll.user32
                user32.SetProcessDPIAware()
                dc = user32.GetDC(0)
                pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
                user32.ReleaseDC(0, dc)
                res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
                return res[1] / res[0]
            else:
                return 1
        except Exception as e:
            sleep(1)
            pass
    else:
        return 1


def recg(token, background_image_base64, slide_image_base64, captcha_type="20333"):
    """请求云码识别（阿里云滑块：背景图 + 滑块图）"""
    conn = http.client.HTTPSConnection("api.jfbym.com", timeout=15)
    headers = {'Content-Type': 'application/json'}
    data = {
        "token": token,
        "type": str(captcha_type),
        "background_image": background_image_base64,
        "slide_image": slide_image_base64,
    }
    data_json = json.dumps(data, ensure_ascii=False)
    try:
        conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
        response = conn.getresponse()
        response_data = response.read().decode("utf-8", errors="ignore")
        if response.status != 200:
            return {"msg": f"HTTP {response.status}", "data": None, "raw": response_data}
        return json.loads(response_data)
    except Exception as e:
        return {"msg": f"请求异常: {e}", "data": None}
    finally:
        conn.close()


def yd_recg(background_image_base64, slide_image_base64):
    captcha_type = 20333

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
                "body": {
                    "background_image": background_image_base64,
                    "slide_image": slide_image_base64
                }
            },
        }
    )
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    conn.request("POST", "/api/v2/aiservice/call", res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def drag(drag_ele: WebElement, distance: int, target_ele: Selector, web_page: xbot.web.WebBrowser):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    drag_ele.hover()
    move_speed = "middle"
    win32.manual_motion_on(
        motion_move=True,
        motion_click=True,
        motion_delay=True,
        min_time=0.1,
        max_time=0.5,
    )
    # win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    
    # 获取缺口元素初始位置
    x_1, y_1, width_1, height_1 = web_page.find(target_ele).get_bounding()
    target_distance = x_1 + width_1 / 2  # 缺口元素初始X坐标
    print(f'缺口初始位置 target_distance: {target_distance}')
    print(f'目标移动距离 distance: {distance}')
    
    # 获取拖拽元素初始位置
    x_drag_init, y_drag_init, width_drag_init, height_drag_init = drag_ele.get_bounding()
    pos_drag_init_x = x_drag_init + width_drag_init / 2
    
    max_iterations = 100  # 最大循环次数，防止死循环
    timeout_seconds = 10  # 超时时间（秒）
    start_time = time.time()  # 记录开始时间
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # 检查是否超时
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout_seconds:
            print(f'超时退出：已运行 {elapsed_time:.2f} 秒，超过 {timeout_seconds} 秒限制')
            break
        
        # 获取缺口元素当前位置
        x_2, y_2, width_2, height_2 = web_page.find(target_ele).get_bounding()
        pos_center_x_2 = x_2 + width_2 / 2
        
        # 获取拖拽元素当前位置
        x_drag, y_drag, width_drag, height_drag = drag_ele.get_bounding()
        pos_center_x_drag = x_drag + width_drag / 2
        pos_center_y_drag = y_drag + height_drag / 2
        
        # 计算缺口实际移动的距离
        gap_moved = pos_center_x_2 - target_distance
        print(f'第{iteration}次循环 - 缺口已移动距离: {gap_moved:.2f}, 目标距离: {distance}')
        
        # 判断是否达到目标位置（允许±2像素误差）
        if abs(gap_moved - distance) <= 2:
            print(f'达到目标位置，退出循环')
            break
        
        # 计算还需要移动的距离
        remaining_distance = distance - gap_moved
        
        # 计算拖拽元素已移动的距离
        drag_moved = pos_center_x_drag - pos_drag_init_x
        
        # 动态计算变速比例（避免除零）
        if abs(gap_moved) > 1:
            speed_ratio = drag_moved / gap_moved
            print(f'当前变速比例: {speed_ratio:.3f}')
        else:
            speed_ratio = 1.0  # 初始假设1:1
        
        # 计算下一步鼠标应该移动到的位置
        # 根据变速比例和剩余距离计算
        next_move = remaining_distance * speed_ratio * 0.8  # 乘以0.8避免过冲
        pos_center_x_in = pos_center_x_drag + next_move
        
        print(f'拖拽元素当前位置: {pos_center_x_drag:.2f}, 下一步目标位置: {pos_center_x_in:.2f}')
        
        # 使用当前拖拽元素的Y坐标（而不是初始Y坐标）
        win32.mouse_move(pos_center_x_in, pos_center_y_drag, move_speed=move_speed, delay_after=1/4000)
        sleep(1/4000)


    sleep(1)
    win32.mouse_click(button="left", click_type="up")
    win32.manual_motion_off()


def handle_verification(web_page: web.WebBrowser, token:str, refresh_ele: WebElement, slider_ele:WebElement, drag_ele:WebElement,retry_count: int, monitor_time=3, background_ele:WebElement = ""):
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名

    _, _, drag_width, _ = web_page.find(drag_ele).get_bounding(to96dpi=True)

    if not retry_count: retry_count=5
    if not monitor_time: monitor_time=3


    captcha_flag = False # 用于判断是否识别成功

    for i in range(retry_count):
        xbot.logging.info(f"第 {i+1} 识别验证码")
        web_page.start_monitor_network(resource_type="Image")
        refresh_element = web_page.find(refresh_ele)
        refresh_element.click(delay_after=0, simulative=False)
        sleep(monitor_time)
        res_list = web_page.get_responses(resource_type="All")
        web_page.stop_monitor_network()
        print(res_list)
        tip_images_base64 = []
        background_image_base64 = None
        background_width = -1

        try:
        
            for res_item in res_list:
                image_base64: str = res_item.get("body")
                img = decode_image(image_base64.split(",", 1)[-1])
                width, height = img.size
                print(width, height)
                if width > background_width:
                    if background_image_base64 is not None:
                        tip_images_base64.append(background_image_base64)
                    background_image_base64 = image_base64
                    background_width = width
                else:
                    tip_images_base64.append(image_base64)
        
        except Exception as e:
            print(e)
            continue

        if not (tip_images_base64 or background_image_base64):
            """
            默认当作成功通过情况
            """
            break

        distance = None

        for index, tip_image_base64 in enumerate(tip_images_base64):
            tip_image = decode_image(tip_image_base64.split(",", 1)[-1])
            background_image = decode_image(background_image_base64.split(",", 1)[-1])
            captcha_image: Image = join_images(tip_image, background_image)

            os_name = os.name
            if os_name == "nt":
                cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
                xbot.logging.info(f"Cache Dir:{cache_folder}")
            else:
                home_path = os.environ.get("XDG_CACHE_HOME")
                cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
                if not os.path.exists(cache_folder):
                    os.makedirs(cache_folder)

            ali_image_captcha_path = os.path.join(cache_folder, f"ali_image_captcha{i}{index}.png")
            xbot.logging.info(f"Cache ALI Captcha Image Path: {ali_image_captcha_path}" )
            with open(ali_image_captcha_path, "wb") as f:
                captcha_image.save(f)

            captcha_image_base64 = encode_image(captcha_image)


            if token:
                reslut = recg(token, background_image_base64, tip_image_base64).get("data")
            else:
                reslut = yd_recg(background_image_base64, tip_image_base64).get("data").get('response')
            # print(reslut)
            distance = reslut.get("data")
            captcha_flag = True
        
        if captcha_flag == False:
            continue

            
        xbot.logging.info(f"Distance: {distance}")


        # 通过监听获取原图去识别, 原图背景的宽度是 300, 高度也是300, 滑块元素的宽度是随机的, 
        # 兼容页面缩放导致的distance不准确问题
        b_x, b_y, b_w, b_h = web_page.find(background_ele).get_bounding(to96dpi=True)
        ppi = b_w / 300
        drag_element = web_page.find(drag_ele)
        distance = int(int(distance) * ppi)
        # exit(0)
        if distance:
            # 滑块具有加速度
            drag(drag_ele=drag_element, distance=distance, target_ele=slider_ele, web_page=web_page)
        sleep(2)
        if not web_page.is_element_displayed(refresh_ele):
            break


def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = web.get_active(mode="chrome")
        token = ''
        retry_count = 5
        slider_ele = gen_selector('//img[@id="aliyunCaptcha-puzzle"]', "阿里云-滑块元素")
        drag_ele = gen_selector('//div[@id="aliyunCaptcha-sliding-slider"]', "阿里云-拖拽元素")
        refresh_ele = gen_selector('//button[@id="aliyunCaptcha-btn-refresh"]', "阿里云-刷新元素")
        monitor_time = 2
        ali_captcha_background = gen_selector('//img[@id="aliyunCaptcha-img"]', '阿里云-背景元素')
        handle_verification(web_page, token, refresh_ele, slider_ele, drag_ele, retry_count, monitor_time, ali_captcha_background)
        exit()


def main(args):
    web_page = args.get("web_page")
    token = args.get("ym_token")
    slider_ele = args.get("slider_ele")
    drag_ele = args.get("drag_ele")
    refresh_ele = args.get("refresh_ele")
    retry_count = args.get("retry_count")
    monitor_time = args.get("monitor_time", 1)
    background_ele = args.get("background_ele")
    test_func()
    handle_verification(web_page, token, refresh_ele, slider_ele, drag_ele, retry_count, monitor_time, background_ele)
    pass
