import xbot
import os
import xbot_visual
import base64
import json
import base64
import io
import urllib
import http.client
from PIL import ImageGrab, Image

from PIL import Image
from io import BytesIO
if os.name == 'nt':
    from ctypes import windll
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation
from PIL import Image, ImageDraw, ImageOps, ImageChops
from urllib.parse import urlparse

from xbot import print, sleep, win32, web
from .import package  
from .package import variables as glv

from xbot._core import robot 
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value

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



def handle_captcha(web_page:xbot.web.WebBrowser, background_ele, extra_ele, retry_count: int=5, token=""):
    
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名
    
    os_name = os.name
    if os_name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache Dir:{cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
            
    xbot.logging.info(f"Cache Dir:{cache_folder}")
    if not retry_count: retry_count=5
    background_ele_save_path = os.path.join(cache_folder, "cs_space_same_object_background.png")
    
    for i in range(retry_count):
        x, y, width, height = web_page.find(background_ele).get_bounding(to96dpi=False)
        win32.screenshot.save_screen_to_file(background_ele_save_path, "png", x, y,x+width, y+height)

        background_img_base64 = file2base64(background_ele_save_path)
        payload = { 
            "image": background_img_base64,
            'token': token, 
            'type': "50009",
            "extra": extra_ele
        }
        
        if token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)
        print(data)
        if data.get("msg") != "识别成功":
            raise Exception("识别失败, 请重试")

        data = data.get("data").get("data")
        positions = [item.split(",") for item in data.split("|")]
        x, y, width, height = web_page.find(background_ele).get_bounding(to96dpi=True)
        for t_x, t_y in positions:
            if os.name =="nt":
                target_p_x = x + int(int(t_x) * get_ppi())
                target_p_y = y + int(int(t_y) * get_ppi())
            else:
                target_p_x = x + int(t_x)
                target_p_y = y + int(t_y)
            xbot.win32.mouse_move(target_p_x, target_p_y)
            xbot.win32.mouse_click()
    
        # web_page.find(confirm_ele).click()
        sleep(3)
        
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=background_ele):
            break
    
def main(args):
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    text = web_page.find(args.get('text_ele')).get_text()
    retry_count = args.get("retry_count", 5)
    token = args.get("token")

    # web_page = web.get_active(mode="chrome")
    # background_ele = "space_test"
    # text = web_page.find("extra").get_text()
    # token = ""
    handle_captcha(web_page,background_ele, text, retry_count, token)
