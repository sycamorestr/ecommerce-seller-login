import xbot
import os
import xbot_visual
import json
import base64
import http.client
if os.name == 'nt':
    from ctypes import windll
from xbot.web.element import WebElement
from xbot import print, sleep, win32, web
from xbot._core import robot 
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value
from urllib.parse import urlparse

SCALING_FACTOR = get_ppi()


def get_xbot_client():
    common_info = robot.execute(f'Common.CommonConfig', None)
    return common_info.get("token")

def yd_captcha_recognition(payload:dict, timeout:float=10):
    """使用增值服务请求验证码，支持自定义超时时间"""
    captcha_type = payload.get("type")
    payload.pop("type")
    payload.pop("token")
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
    conn.timeout = timeout
    res_payload = json.dumps(
        {
            "aiToolInterfaceCodeId": f"jfbym_{captcha_type}",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": str(captcha_type),
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": payload,
            },
        }
    )
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/api/v2/aiservice/call", res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    # print(response_data)
    response_json = json.loads(response_data)
    conn.close()
    print(response_json['data']["statusCode"])
    if int(response_json['data']["statusCode"]) != 200:
        raise Exception(f"错误信息: {response_json}")
    return response_json


def ym_captcha_recognition(payload, timeout:float=10):
    """请求云码识别验证码，支持自定义超时时间"""
    conn = http.client.HTTPConnection("api.jfbym.com", timeout=timeout)
    headers = { 'Content-Type': 'application/json'}
    # print(payload.get("type"))
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def handle_captcha(web_page:xbot.web.WebBrowser, background_ele:WebElement, retry_count: int=5, token="", confirm_ele=None, timeout:float=10):
    """处理验证码，支持自定义超时时间
    :param web_page: 网页对象
    :param background_ele: 验证码背景图
    :param retry_count : retry_count：重试次数
    :param token : 云码token，空则表示用使用影刀增值服务请求
    :param timeout : 请求超时时间（秒）
    """

    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名
    os_name = os.name
    #区分系统差异创建文件夹
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
    #开始处理验证码
    for i in range(retry_count):
        x, y, width, height = web_page.find(background_ele).get_bounding(to96dpi=False)
        win32.screenshot.save_screen_to_file(background_ele_save_path, "png", x, y,x+width, y+height)
        background_img_base64 = file2base64(background_ele_save_path) #得到背景图的base64
        payload = { 
            "image": background_img_base64,
            'token': token, 
            'type': "88888",
        }

        data = ''
        if token:
            data = ym_captcha_recognition(payload, timeout=timeout)
            if data.get("msg") != "识别成功":
                raise Exception("识别失败, 请重试")
            data = data.get("data").get("data")
        else:
            data = yd_captcha_recognition(payload, timeout=timeout)
            data = data.get("data").get("response").get("data")
        
        positions = [item.split(",") for item in data.split("|")] #得到点选的坐标位置
        x, y, width, height = web_page.find(background_ele).get_bounding(to96dpi=True)
        for t_x, t_y in positions:
            if os.name =="nt":
                target_p_x = x + int(int(t_x) * SCALING_FACTOR)
                target_p_y = y + int(int(t_y) * SCALING_FACTOR)
            else:
                target_p_x = x + int(t_x)
                target_p_y = y + int(t_y)
            xbot.win32.mouse_move(target_p_x, target_p_y, delay_after=0.5)
            xbot.win32.mouse_click(delay_after=0.3)
        
        if confirm_ele:
            web_page.find(confirm_ele).click()

        sleep(3)
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=background_ele):
            break
    
def main(args):
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    retry_count = args.get("retry_count", 5)
    token = args.get("token", '')
    confirm_ele = args.get("confirm_ele")
    timeout = args.get("timeout", 10)

    # web_page = web.get_active(mode="chrome")
    # background_ele = "space_test"
    # token = ""
    handle_captcha(web_page, background_ele, retry_count, token, confirm_ele, timeout=timeout)
