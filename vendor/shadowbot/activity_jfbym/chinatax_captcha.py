# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import http
import json
import os
from xbot import print, sleep, web 
from .import package
from .package import variables as glv
from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload, upload_captcha_screenshot, report_data, get_boundary_value
from urllib.parse import urlparse

def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = { 'Content-Type': 'application/json'}
    # print(payload.get("type"))
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json

def yd_captcha_recognition(payload:dict):
    """使用增值服务请求验证码"""
    captcha_type = payload.get("type")
    payload.pop("type")

    common_info = robot.execute(f'Common.CommonConfig', None)
    token = common_info.get("token")
    conn = http.client.HTTPSConnection(urlparse(common_info.get("webApi")).netloc)
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
    conn.request("POST", "/api/openapi/v2/thirdParty/interface/call", res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    # print(response_json)
    data = response_json.get("data")
    if not data:
        raise Exception(f"错误信息: {response_json}")
    return data

def handle_captcha(web_page, ele, token) -> str:
    """处理验证码"""
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名
    try:
        extra = web_page.find_by_xpath("//div[@class='yzm-tips']/font", timeout=3).get_text()
    except:
        extra ='全部'

    e_x, e_y, e_w, e_h = web_page.find(ele).get_bounding(to96dpi=False)
    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    temp_file = os.path.join(cache_folder, "chinatax_temp.png")
    xbot.win32.screenshot.save_screen_to_file(temp_file, "png", e_x, e_y, e_x + e_w, e_y + e_h)
    image_base64 = file2base64(temp_file)
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    payload = { 
        "image": image_base64,
        'token': token, 
        'type': "10201",
        "extra": extra
    }
    # xbot.logging.info(payload)
    
    if token:
        data = ym_captcha_recognition(payload)
    else:
        data = yd_captcha_recognition(payload)
    print(data)
    return data.get("data").get("data")

def main(args):
    web_page = args.get("web_page")
    ele = args.get("ele")
    token = args.get("token")

    # web_page = web.get_active(mode="chrome")
    # # token = ""
    # ele = "std_alphanum_captcha_ele"
    data = handle_captcha(web_page, ele, token)
    # print(data)
    # xbot.logging.info(f"caption code: {data}")
    args["data"] = data
