# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import os
import xbot_visual
import base64
import json
import base64
import io
import urllib
import http.client
from urllib.parse import urlparse
from PIL import ImageGrab, Image
import time

from PIL import Image
from io import BytesIO
from ctypes import windll
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation

from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv

from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi

def yd_recg(image_base64):
    common_info = robot.execute(f'Common.CommonConfig', None)
    token = common_info.get("token")
    conn = http.client.HTTPSConnection(urlparse(common_info.get("webApi")).netloc)
    payload = json.dumps({
        "thirdPartyInterfaceCode": "jfbym_22222",
        "data": {},
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": {
                "image": image_base64
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


def handle_captcha(web_page:xbot.web.WebBrowser, background_ele, drag_ele):
    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    xbot.logging.info(f"Cache Dir:{cache_folder}")
    
    drag_element = web_page.find(drag_ele)
    web_page.find(background_ele).screenshot(cache_folder, filename="std_slider.png")

    image_path = os.path.join(cache_folder, "std_slider.png")
    background_ele_base64 = file2base64(image_path)
    reslut = yd_recg(background_ele_base64)
    
    if not reslut.get("success"):
        raise Exception(reslut.get("msg"))
    
    distance = int(reslut.get("data").get("data").get("data"))
    # distance = int(distance * get_ppi())
    print('云码的识别结果',distance*get_ppi())
    return distance

def drag(web_page:xbot.web.WebBrowser,captcha_result,background_ele, gap_ele,drag_ele):
    # 获取背景图的位置
    background_position = web_page.find(background_ele).get_bounding(relative_to='screen')
    # 获取缺口滑块图的位置
    gap_block = web_page.find(gap_ele).get_bounding(relative_to='screen')
    # 获取偏移量
    offset = gap_block[0] - background_position[0]
    captcha_result = float(captcha_result)-offset-5
    x, y, width, height = web_page.find(drag_ele).get_bounding(relative_to='screen')
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "middle"
    win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=0.1, max_time=0.5)
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    
    # 第一次获取当前缺口滑块的位置
    gap_block_first = web_page.find(gap_ele).get_bounding(relative_to='window')

    # 移动滑块
    win32.mouse_move(point_x = pos_center_x + 25*get_ppi(), point_y=pos_center_y, relative_to='screen',move_speed=move_speed)
    # 第二次获取滑块缺口的位置
    gap_block_second = web_page.find(gap_ele).get_bounding(relative_to='window')
    # 获取加速度
    offset_percent = (gap_block_second[0] - gap_block_first[0])/(25*get_ppi())
    print('加速度:',offset_percent)
    captacha_result = int(((captcha_result/offset_percent)*get_ppi()-(25*get_ppi())))
    print('实际滑动距离',captacha_result+25)
    win32.mouse_move(point_x = captacha_result+5/get_ppi(), point_y=0, relative_to='position',move_speed=move_speed)
    win32.mouse_click(button="left", click_type="up", delay_after=0)
    win32.manual_motion_off()
    time.sleep(2)

def main(args):
    
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    gap_ele = args.get("gap_ele")
    drag_ele = args.get("drag_ele")
    refresh_ele = args.get("refresh_ele")
    retry_count = args.get("retry_count")

    if not retry_count: retry_count=5

    for i in range(retry_count):
        distance = handle_captcha(web_page,background_ele,drag_ele)
        drag(web_page =web_page,captcha_result= distance,background_ele =background_ele,gap_ele=gap_ele,drag_ele=drag_ele)
        if not web_page.is_element_displayed(background_ele):
            break
        else:
            web_page.find(refresh_ele).click()
            time.sleep(2)
