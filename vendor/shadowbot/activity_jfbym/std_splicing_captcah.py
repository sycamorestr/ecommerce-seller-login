# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import os
import json
import http.client


import xbot  # type: ignore
import xbot_visual  # type: ignore
from . import package 

if os.name == "nt":
    from ctypes import windll

from urllib.parse import urlparse
from xbot._core import robot  # type: ignore
from xbot import print, sleep, win32  # type: ignore
from xbot.web.element import WebElement  # type: ignore
from xbot.web.chromium import ChromiumElement

from .package import variables as glv
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi
from PIL import Image
from io import BytesIO
import base64    
from xbot.selector import Selector
import random
import ctypes
from PIL import Image

def get_proportion(web_page_width, img_path):
    img = Image.open(img_path)
    # 获取宽度和高度
    width, height = img.size
    return web_page_width / width

def get_element(web_page, target):
    if isinstance(target, ChromiumElement):
        # 已经是 ChromiumElement，直接返回
        return Exception('暂不支持传入网页元素变量')

def save_image_from_body(body, file_path):
    # Base64 解码
    img_data = base64.b64decode(body)
    
    # 写入文件
    with open(file_path, "wb") as f:
        f.write(img_data)

def image_to_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

def recg(ym_token, drag_base64, background_base64):
    """请求云码识别淘"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = { 'Content-Type': 'application/json'}
    data = { 'slide_image': drag_base64, "background_image":background_base64, 'token': ym_token, 'type': 11268 }
    data_json = json.dumps(data)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json

def yd_recg(drag_base64, background_base64):
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
            "aiToolInterfaceCodeId": f"jfbym_11268",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": 11268,
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": {'slide_image': drag_base64, "background_image":background_base64},
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

def drag(web_page, drag_ele, distance):
    ''' 拖拽元素
    '''
    d_x, d_y, d_w, d_h = web_page.find(drag_ele).get_bounding()
    pos_center_x = d_x + d_w / 2 + random.randint(-5, 5)
    pos_center_y = d_y + d_h / 2 + random.randint(-5, 5)

    win32.manual_motion_on()
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed="instant", relative_to='screen')
    poit_x, point_y = win32.get_mouse_position(relative_to="screen")
    win32.mouse_click(button="left", click_type="down", delay_after=1)

    right_offset = random.randint(-5, 5)
    left_offset = random.randint(-5, 5)
    print(distance[0] + (d_w / 2), distance[1] + (d_h / 2))
    win32.mouse_move(int(distance[0] + (d_w / 2)), int(distance[1] + (d_h / 2)), move_speed="middle", delay_after=0)
    win32.mouse_click(button="left", click_type="up", delay_after=0)
    win32.manual_motion_off()
    

def handle_captcha(web_page, drag_ele, background_ele, refresh_ele, retry_count=3, monitor_time=3, ym_token=""):
    ''' 处理验证码
    '''
    captcha_flag = False # 用于判断是否识别成功
    # 校验元素
    assert isinstance(drag_ele, Selector), '暂不支持传入网页元素变量'
    assert isinstance(background_ele, Selector), '暂不支持传入网页元素变量'
    assert isinstance(refresh_ele, Selector), '暂不支持传入网页元素变量'

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
    for _ in range(int(retry_count)):
        # sleep(3)
        if not web_page.is_element_displayed(drag_ele):
            break
        # 处理一下distance distance是基于背景图左上角的坐标
        b_x, b_y, b_w, b_h = web_page.find(background_ele).get_bounding()

        # 通过监听网络请求获取图片
        drag_path = os.path.join(cache_folder, "drag.png")
        background_path = os.path.join(cache_folder, "background.png")
        web_page.start_monitor_network(resource_type="Image")
        # web_page.find(refresh_ele).click(delay_after=0, simulative=False)
        drag(web_page, drag_ele, [b_x+10, b_y+10])

        sleep(monitor_time)
        res_list = web_page.get_responses(resource_type="All")
        web_page.stop_monitor_network()
        # 比较两个body的长度判断谁是背景图
        complete_base64_length = ''
        for res in res_list:
            if len(res['body']) > len(complete_base64_length):
                background_img_base64 = res['body']
                complete_base64_length = res['body']
            else:
                drag_img_base64 = res['body']
        save_image_from_body(background_img_base64, background_path)
        save_image_from_body(drag_img_base64, drag_path)
        # print(f"背景图保存路径: {background_path}")
        # print(f"拖动块保存路径: {drag_path}")

        # 打开图片为base64
        background_base64 = image_to_base64(background_path)
        drag_base64 = image_to_base64(drag_path)
        distance = 0
        if ym_token:
            reslut = recg(ym_token, drag_base64, background_base64)
            if reslut.get("msg") != "识别成功":
                print("识别失败, 请重试, 本次不计费")
                continue
            distance = reslut.get("data").get("data")
        else:
            reslut = yd_recg(drag_base64, background_base64).get("data")
            if reslut.get("code") != 0.0:
                print("识别失败, 请重试, 本次不计费")
                continue
            distance = reslut.get("data")
        print(reslut)
        distance = json.loads(distance)
        # distance = [int(_*get_ppi()) for _ in distance]
        captcha_flag = True
        
        if not captcha_flag:
            continue
        
        # 获取比例
        proportion = get_proportion(b_w, background_path)
        distance=[int(distance[0] * proportion)+ b_x] + [int(distance[1] * proportion) + b_y]
        print(distance)
        drag(web_page, drag_ele, distance)
        web_page.wait_disappear(drag_ele, 3)

        
def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('edge')
        drag_ele = package.selector('通用拼接_拖拽元素')
        background_ele = package.selector('通用拼接_背景元素')
        refresh_ele = package.selector('通用拼接_刷新元素')
        retry_count = 3
        monitor_time = 3
        ym_token = ""
        handle_captcha(web_page, drag_ele, background_ele, refresh_ele, retry_count, monitor_time, ym_token)
        exit(0)

def main(args):
    test_func()
    web_page = args.get('web_page')
    drag_ele = args.get('drag_ele')
    background_ele = args.get('background_ele')
    refresh_ele = args.get('refresh_ele')
    retry_count = args.get('retry_count', 5)
    monitor_time = args.get('monitor_time', 3)
    ym_token = args.get("ym_token", "")
    handle_captcha(web_page, drag_ele, background_ele, refresh_ele, retry_count, monitor_time, ym_token)
    

