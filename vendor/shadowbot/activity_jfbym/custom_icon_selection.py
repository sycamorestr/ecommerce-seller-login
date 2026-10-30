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

def download_image(image_url, file_path):
    """下载图片"""
    parsed_url = urlparse(image_url)

    if not all([parsed_url.scheme, parsed_url.netloc]):
        raise ValueError("无效的URL")

    if parsed_url.scheme == 'https':
        conn = http.client.HTTPSConnection(parsed_url.netloc)
    elif parsed_url.scheme == 'http':
        conn = http.client.HTTPConnection(parsed_url.netloc)
    else:
        raise ValueError(f"不支持的协议: {parsed_url.scheme}")

    full_path = parsed_url.path
    if parsed_url.query:
        full_path += "?" + parsed_url.query

    conn.request("GET", full_path)
    response = conn.getresponse()

    if response.status == 200:
        base64_data = response.read()

    with open(file_path, "wb") as f:
        f.write(base64_data)
    
def get_proportion(web_page_width, img_path):
    img = Image.open(img_path)
    # 获取宽度和高度
    width, height = img.size
    return web_page_width / width


def image_to_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

def recg(ym_token, img_base64, image_label1, image_label2, image_label3):
    """请求云码识别淘"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = { 'Content-Type': 'application/json'}
    data = {'token': ym_token, 'type': 31112, 'image': img_base64, 'image_label1': image_label1, 'image_label2': image_label2, 'image_label3': image_label3}
    data_json = json.dumps(data)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json

def yd_recg(img_base64, image_label1, image_label2, image_label3):
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
            "aiToolInterfaceCodeId": f"jfbym_31112",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": 31112,
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": {'image': img_base64, 'image_label1': image_label1, 'image_label2': image_label2, 'image_label3': image_label3},
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


def handle_captcha(web_page, image_big, image_label1, image_label2, image_label3, confirm_ele, retry_count=3, ym_token=''):
    ''' 处理验证码
    '''
    captcha_flag = False # 用于判断是否识别成功
    # 校验元素
    assert isinstance(image_big, Selector), '暂不支持传入网页元素变量'
    assert isinstance(image_label1, Selector), '暂不支持传入网页元素变量'
    assert isinstance(image_label2, Selector), '暂不支持传入网页元素变量'
    assert isinstance(image_label3, Selector), '暂不支持传入网页元素变量'

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
    # web_page = xbot.web.get_active('chrome')
    for _ in range(int(retry_count)):
        # sleep(3)
        if not web_page.is_element_displayed(image_big):
            break
        
        # 缓存图片
        image_big_path = os.path.join(cache_folder, "大图.png")
        image_label1_path = os.path.join(cache_folder, "小图1.png")
        image_label2_path = os.path.join(cache_folder, "小图2.png")
        image_label3_path = os.path.join(cache_folder, "小图3.png")
        # 获取图片url
        image_big_url = web_page.find(image_big).get_attribute("style").split('"')[1]
        image_label1_url = web_page.find(image_label1).get_attribute("src")
        image_label2_url = web_page.find(image_label2).get_attribute("src")
        image_label3_url = web_page.find(image_label3).get_attribute("src")
        # 下载图片
        download_image(image_big_url, image_big_path)
        # 小图url转化为base64
        image_label1_base64 = base64.b64encode(image_label1_url.encode()).decode()
        image_label2_base64 = base64.b64encode(image_label2_url.encode()).decode()
        image_label3_base64 = base64.b64encode(image_label3_url.encode()).decode()
        # 打开图片为base64
        image_big_base64 = image_to_base64(image_big_path)
        
        distance = 0
        if ym_token:
            reslut = recg(ym_token, image_big_base64, image_label1_base64, image_label2_base64, image_label3_base64)
            if reslut.get("msg") != "识别成功":
                print("识别失败, 请重试, 本次不计费")
                continue
            distance = reslut.get("data").get("data")
        else:
            reslut = yd_recg(image_big_base64, image_label1_base64, image_label2_base64, image_label3_base64).get("data")
            if reslut.get("code") != 0.0:
                print("识别失败, 请重试, 本次不计费")
                continue
            distance = reslut.get("data")
        distance_list = [i.split(',') for i in distance.split('|')]
        captcha_flag = True
        
        if not captcha_flag:
            continue
            
        # 处理一下distance distance是基于背景图左上角的坐标
        b_x, b_y, b_w, b_h = web_page.find(image_big).get_bounding()
        # 获取比例
        proportion = get_proportion(b_w, image_big_path)
        distance_list = [[int(item) * proportion for item in sublist] for sublist in distance_list]
        # 点击坐标
        for dis in distance_list:
            win32.mouse_move(b_x + int(dis[0]), b_y + int(dis[1]))
            win32.mouse_click()
        
        # distance=[int(distance[0] * proportion)+ b_x] + [int(distance[1] * proportion) + b_y]

        web_page.find(confirm_ele).click()
        sleep(1)

        
def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        image_big = package.selector('jy4_icon_direct_background_ele')
        image_label1 = package.selector('jy4_icon_direct_label1_ele')
        image_label2 = package.selector('jy4_icon_direct_label2_ele')
        image_label3 = package.selector('jy4_icon_direct_label3_ele')
        confirm_ele = package.selector('jy4_icon_direct_confirm_ele')
        retry_count = 3
        ym_token = ""
        handle_captcha(web_page, image_big, image_label1, image_label2, image_label3, confirm_ele, retry_count, ym_token)
        exit(0)

def main(args):
    test_func()
    web_page = args.get('web_page')
    image_big = args.get('image_big')
    image_label1 = args.get('image_label1')
    image_label2 = args.get('image_label2')
    image_label3 = args.get('image_label3')
    confirm_ele = args.get('confirm_ele')
    retry_count = args.get('retry_count', 5)
    ym_token = args.get("ym_token", "")
    handle_captcha(web_page, image_big, image_label1, image_label2, image_label3, confirm_ele, retry_count, ym_token)
    

