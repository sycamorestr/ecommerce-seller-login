# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

from turtle import distance
import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
import os
import json
import http.client
from urllib.parse import urlparse

if os.name == "nt":
    from ctypes import windll
from xbot._core import robot  # type: ignore

def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = {"Content-Type": "application/json"}
    data_json = json.dumps(payload)
    print(data_json)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    print(response_json)
    return response_json

def yd_captcha_recognition(payload):
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
            "aiToolInterfaceCodeId": "jfbym_66",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": "66",
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
    return response_json.get("data")

def move_simulated(web_page, slider_ele, distance_x, end_point, ym_token):
    ''' 模拟人工拖动
    :param web_page: 网页对象
    :param slider_ele: 必填，滑动元素对象
    :param end_point: 可选，二选一，待滑动终点坐标，传字符串格式，如：'100,200'
    :param distance_x: 可选，二选一, 距离x，如：100
    :param token: 选填，验证码token
    '''
    x, y, w, h = web_page.find(slider_ele).get_bounding()
    begin_point = f'{int(x+w/2)},{int(y+h/2)}'
    payload = {
        "token":ym_token,  
        "type":"66",
        "begin_point": begin_point,
    }
    if end_point and distance_x:
        raise Exception("end_point和distance_x不能同时存在")
        
    if end_point:
        payload["end_point"] = end_point
    if distance_x:
        payload["distance_x"] = distance_x
        
    if ym_token:
        data = ym_captcha_recognition(payload)
        data = data.get("data")

    else:
        data = yd_captcha_recognition(payload)
        if data.get("statusCode") != "200":
            print(data.get("msg"))
            print('识别失败，本次验证不收取费用')
            return 
        data = data.get("response")
    distance_list = data.get('data')
    print(distance_list)
    xbot.win32.manual_motion_on()
    xbot.win32.mouse_move(x+w/2, y+h/2, move_speed="middle")
    xbot.win32.mouse_click(button="left", click_type="down", delay_after=0)
    for distance_ in distance_list:
        xbot.win32.mouse_move(distance_[0], distance_[1], move_speed="instant", delay_after=0.016)
    xbot.win32.mouse_click(button="left", click_type="up", delay_after=0)
    xbot.win32.manual_motion_off()

def test_func():
    if "xbot_extensions" not in __file__:
        web_page = xbot.web.get_active('chrome')
        slider_ele = package.selector('move_simulated_slider')
        distance_x = '390'
        end_point = ''
        ym_token = ''
        move_simulated(web_page, slider_ele, distance_x, end_point, ym_token)
        exit()

def main(args):
    test_func()
    web_page = args.get('web_page')
    slider_ele = args.get('slider_ele')
    distance_x = args.get("distance_x")
    end_point = args.get('end_point')
    token = args.get('token')
    move_simulated(web_page, slider_ele, distance_x, end_point, token)