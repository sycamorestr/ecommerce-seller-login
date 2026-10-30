# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import http
from urllib.parse import urlparse
import json
import base64
import xbot_visual
import os
from io import BytesIO 
from xbot import print, sleep, web 
from . import package 
from .package import variables as glv
from PIL import ImageGrab
from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value


def img_to_base64(image): 
    """图片转base64"""
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    base64_string = base64.b64encode(img_bytes).decode('utf-8')
    return base64_string


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


def handle_captcha(web_page, web_element, ym_token,
                   retry_count,sure_element) -> str:
    """处理验证码"""
    captcha_type = 30330
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名
    if os.name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache folder: {cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

    for i in range(retry_count):
        e_x, e_y, e_w, e_h = web_page.find(web_element).get_bounding(
        to96dpi=False)
        e_a_x, e_a_y, _, _ = web_page.find(web_element).get_bounding(
            to96dpi=False)

        xbot.win32.screenshot.save_screen_to_file(f'{cache_folder}/jd_click_select_captcha.png', 'png', e_a_x, e_a_y, e_a_x + e_w, e_a_y + e_h)
        image_base64 = file2base64(f'{cache_folder}/jd_click_select_captcha.png')

        payload = {"image": image_base64, 'token': ym_token, 'type': captcha_type}

        if ym_token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)
        print(data)
        data = data.get("data").get("data")
        positions = [item.split(",") for item in data.split("|")]
        e_a_x, e_a_y, _, _ = web_page.find(web_element).get_bounding(
            to96dpi=True)
        for t_x, t_y in positions:
            if os.name =='nt':
                target_p_x = e_a_x + int(int(t_x) * get_ppi())
                target_p_y = e_a_y + int(int(t_y) * get_ppi())
            else:
                target_p_x = e_a_x + int(t_x)
                target_p_y = e_a_y + int(t_y)
            xbot.win32.mouse_move(target_p_x, target_p_y)
            xbot.win32.mouse_click()
        
        sleep(2)
        if sure_element:
             web_page.find(sure_element).click()
        sleep(3)
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=web_element):

            break
    
    
    # return 
def test_func():
    if "xbot_extensions" not in __file__:
        web_page = xbot.web.get_active('chrome')
        web_element = package.selector('jd_click_select_captcha_web_element')
        ym_token = ''
        # sure_element = package.selector('jd_click_select_captcha_sure_element')
        sure_element = ''
        retry_count = 5
        handle_captcha(web_page, web_element, ym_token, retry_count,sure_element)
        exit()


def main(args):
    test_func()
    web_page = args.get("web_page")
    web_element = args.get("web_element")
    ym_token = args.get("ym_token", )
    sure_element = args.get("sure_element", )
    retry_count = args.get("retry_count", 5)

    # web_page = web.get_active(mode="chrome")
    # web_element = "jdsureele"
    # sure_element = '确定test'
    # # ym_token = ""


    handle_captcha(web_page, web_element, ym_token, retry_count,sure_element)
