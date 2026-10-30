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
from xbot import print, sleep, web 
from . import package 
from .package import variables as glv
from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi
import re, urllib
 
ppi = get_ppi()

from urllib.parse import urlparse
def get_xbot_client():
    """获取客户端 token"""
    common_info = robot.execute(f'Common.CommonConfig', None)
    return common_info.get("token")


def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = {'Content-Type': 'application/json'}
    # print(payload.get("type"))
    data_json = json.dumps(payload)
    conn.request("POST",
                 "/api/YmServer/customApi",
                 body=data_json,
                 headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload: dict):
    """使用增值服务请求验证码"""
    captcha_type = payload.get("type")
    payload.pop("type")
    
    # 判断客户端版本, 是否使用ssl, host, 以及token
    common_info = robot.execute(f'Common.CommonConfig', None)
    
    token = common_info.get("token")
    web_api = common_info.get("webApi")

    parsed = urlparse(web_api)
    is_ssl = parsed.scheme.lower() == 'https'
    host = parsed.netloc 
    

    if is_ssl:
        conn = http.client.HTTPSConnection(host)
    else:
        conn = http.client.HTTPConnection(host)


    res_payload = json.dumps({
        "thirdPartyInterfaceCode": f"jfbym_{captcha_type}",
        "data": {},
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": payload,
            "pathVariable": {}
        },
        "bizType": "rpa-command"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/api/openapi/v2/thirdParty/interface/call",
                 res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    # print(response_json)
    data = response_json.get("data")
    if not data:
        raise Exception(f"错误信息: {response_json}")
    return data

def down_img(url):
    with urllib.request.urlopen(url) as response:
        image_data = response.read()  # 读取图片数据
        img_base64 = base64.b64encode(image_data).decode('utf-8')  # 转换为Base64编码
    return img_base64

def handle_captcha(web_page, bg_elem, top_ele, ym_token, confirm, retry_count):
    """处理验证码"""
    captcha_type = "30332"

    for i in range(retry_count):
        b_x, b_y, b_w, b_h = web_page.find(bg_elem).get_bounding(to96dpi=False)
        _, t_y, _, _ = web_page.find(top_ele).get_bounding(to96dpi=False)

        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        temp_file = os.path.join(cache_folder, "wb_point_temp.png")
        xbot.win32.screenshot.save_screen_to_file(temp_file, "png", b_x, t_y, b_x + b_w, b_y + b_h)
        image_base64 = file2base64(temp_file)
        if os.path.exists(temp_file):
            os.remove(temp_file)
        payload = {"image": image_base64, 'token': ym_token, 'type': captcha_type, "direction": "top", "num": 3}

        if ym_token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)

        # 判断云码是否识别成功
        if data.get("msg") != "识别成功":
            raise Exception(f'验证码报错: {data.get("msg")}')
        
        data = data.get("data").get("data")

        positions = [item.split(",") for item in data.split("|")]
        for o_x, o_y in positions:
            target_p_x = int((b_x + int(o_x)) * ppi)
            target_p_y = int((t_y + int(o_y)) * ppi)
            xbot.win32.mouse_move(target_p_x, target_p_y)
            xbot.win32.mouse_click()
        if confirm:
            web_page.find(confirm).click()
        sleep(3)
    
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=bg_elem):
            break

    # return 


def main(args):
    web_page = args.get("web_page")
    bg_elem = args.get("bg_elem")
    top_elem = args.get("top_elem")
  
    ym_token = args.get("ym_token", )
    confirm = args.get("confirm",'')
    retry_count = args.get("retry_count", 5)

    # test
    # web_page = xbot.web.get_active(mode="chrome")
    # top_elem = "sina_top_ele"
    # bg_elem = "sina_background_ele"

    handle_captcha(web_page, bg_elem, top_elem, ym_token, confirm, retry_count)
