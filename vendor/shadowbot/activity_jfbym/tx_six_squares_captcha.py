# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
import xbot
import http
from urllib.parse import urlparse
import json
import base64 
if os.name == 'nt':
    from ctypes import windll
from xbot._core import robot
from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value


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


def get_ppi():
    """
    获取屏幕的缩放
    """
    if os.name == 'nt':
        LOGPIXELSX = 88
        LOGPIXELSY = 90
        user32 = windll.user32
        user32.SetProcessDPIAware()
        dc = user32.GetDC(0)
        pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
        user32.ReleaseDC(0, dc)
        res = float.as_integer_ratio(round(pix_per_inch / 96,2))
        return res[1]/res[0]
    else:
        return 1


# def recg(token, base64_im):
#     """请求云码识别淘"""
#     conn = http.client.HTTPConnection("api.jfbym.com")
#     headers = { 'Content-Type': 'application/json'}
#     data = { 'image': base64_im, 'token': token, 'type': 30221 }
#     data_json = json.dumps(data)
#     conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
#     response = conn.getresponse()
#     response_data = response.read().decode('utf-8')
#     response_json = json.loads(response_data)
#     conn.close()
#     return response_json


def tx_six_squares_captcha(web_page, tip_ele, background_ele, ok_ele, token, retry_count=5):
    os_name = os.name
    if os_name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache Dir:{cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
    file_name = "tx_six.png"
    save_path = os.path.join(cache_folder, file_name)
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名


        
    xbot.logging.info(f"Cache: {save_path}")
    tip_ele_bounds = web_page.find(tip_ele).get_bounding(to96dpi=False)
    background_ele_bounds = web_page.find(background_ele).get_bounding(to96dpi=False)

    t_x, t_y, _, _  = tip_ele_bounds
    b_x, b_y, b_width, b_height = background_ele_bounds


    for i in range(retry_count):
        try:
            web_page.find(background_ele, timeout=5)
        except Exception as e:
            break
            
        xbot.win32.screenshot.save_screen_to_file(save_path, "png", t_x, t_y, b_x + b_width, b_y + b_height)

        with open(save_path, "rb") as f:
            image_data = f.read()
            base64_str = base64.b64encode(image_data).decode("utf-8")

        
        payload = {'image': base64_str, 'token': token, 'type': 30221}

        if token:
            result = ym_captcha_recognition(payload)
        else:
            result = yd_captcha_recognition(payload)


        if result.get("code") != 10000:
            raise

        data: str = result.get("data").get("data") # 230,298|382,148

        positions = [(int(item.split(",")[0]), int(item.split(",")[1])) for item in data.split("|")]

        for position_x, position_y in positions: 
            if os.name =='nt':
                distance_x = int((t_x+position_x)*get_ppi())
                distance_y = int((t_y+position_y)*get_ppi())
            else:
                distance_x = int(t_x+position_x)
                distance_y = int(t_y+position_y)
            xbot.win32.mouse_move(distance_x, distance_y)
            xbot.win32.mouse_click()

        web_page.find(ok_ele).click()



    
def main(args):
    web_page = args.get("web_page")
    tip_ele = args.get("tip_ele")
    background_ele = args.get("background_ele")
    ok_ele = args.get("ok_ele")
    token = args.get("ym_token")
    retry_count = args.get("retry_count")

    tx_six_squares_captcha(web_page, tip_ele, background_ele, ok_ele, token, retry_count)