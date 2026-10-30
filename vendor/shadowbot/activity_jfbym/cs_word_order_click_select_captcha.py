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
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value
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
    print(f'验证码识别结果为：{response_json}')
    return response_json.get('data')

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
            "aiToolInterfaceCodeId": "jfbym_30114",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": "30114",
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": {"image": payload.get('image'), "extra" :"je4_phrase"},
            },
        }
    )
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    conn.request("POST", "/api/v2/aiservice/call", payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    print(f'验证码识别结果为：{response_json}')
    return response_json.get("data").get('response')

# def yd_captcha_recognition(payload: dict):
#     """使用增值服务请求验证码"""
#     captcha_type = payload.get("type")
#     payload.pop("type")

#     token = get_xbot_client()
#     conn = http.client.HTTPSConnection("api.yingdao.com")
#     res_payload = json.dumps({
#         "thirdPartyInterfaceCode": f"jfbym_{captcha_type}",
#         "data": {},
#         "thirdPartyReqData": {
#             "headers": {},
#             "params": {},
#             "body": payload,
#             "pathVariable": {}
#         },
#         "bizType": "rpa-command"
#     })
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {token}'
#     }
#     conn.request("POST", "/api/openapi/v2/thirdParty/interface/call",
#                  res_payload, headers)
#     res = conn.getresponse()
#     response_data = res.read().decode('utf-8')
#     response_json = json.loads(response_data)
#     conn.close()
#     # print(response_json)
#     data = response_json.get("data")
#     if not data:
#         raise Exception(f"错误信息: {response_json}")
#     return data


def handle_captcha(web_page, web_element, refresh_ele, ok_ele, ym_token, retry_count) -> str:
    """处理验证码"""
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名
    
    
    captcha_type = 30114

    background_boundary_list = get_boundary_value(web_page, web_element)#得到背景图的boundary,锚点


    for i in range(retry_count):
        e_x, e_y, e_w, e_h = web_page.find(web_element).get_bounding(
        to96dpi=False)
        e_a_x, e_a_y, _, _ = web_page.find(web_element).get_bounding(
            to96dpi=True)
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        temp_file = os.path.join(cache_folder, "cs_word_click_temp.png")
        xbot.win32.screenshot.save_screen_to_file(temp_file, "png", e_x, e_y, e_x + e_w, e_y + e_h)
        image_base64 = file2base64(temp_file)
        if os.path.exists(temp_file):
            os.remove(temp_file)
        payload = {"image": image_base64, 'token': ym_token, 'type': captcha_type, "extra" :"je4_phrase"}

        if ym_token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)

        try:
            data = data.get("data")
            positions = [item.split(",") for item in data.split("|")]
            for t_x, t_y in positions:
                if os.name == 'nt':
                    target_p_x = e_a_x + int(int(t_x) * get_ppi())
                    target_p_y = e_a_y + int(int(t_y) * get_ppi())
                else:
                    target_p_x = e_a_x + int(t_x)
                    target_p_y = e_a_y + int(t_y)
                xbot.win32.mouse_move(target_p_x, target_p_y)
                xbot.win32.mouse_click()
            
            sleep(2)

            if ok_ele:
                web_page.find(ok_ele).click()
            
            if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=web_element):
                break
            
        except:
            if refresh_ele:
                web_page.find(refresh_ele).click()
            pass
    
    
    # return 

def test_func():
    if "xbot_extensions" not in __file__:
        web_page = xbot.web.get_active('chrome')
        web_element = package.selector('定制-语序点选-背景')
        ym_token = ''
        refresh_ele = ""
        ok_ele = ''
        retry_count = 3
        handle_captcha(web_page, web_element, refresh_ele, ok_ele,ym_token, retry_count, )
        exit()

def main(args):
    test_func()
    web_page = args.get("web_page")
    web_element = args.get("web_element")
    ym_token = args.get("ym_token", )
    refresh_ele = args.get("refresh_ele", )
    ok_ele = args.get("ok_ele", )

    retry_count = args.get("retry_count", 5)

    # web_page = web.get_active(mode="edge")
    # web_element = "cs_word_order_click_select_captcha_ele"
    # ym_token = ""
    # refresh_ele= "cs_word_order_click_select_captcha_refresh_ele"
    # ok_ele= "cs_word_order_click_select_captcha_ok_ele"


    handle_captcha(web_page, web_element, refresh_ele, ok_ele,ym_token, retry_count, )
