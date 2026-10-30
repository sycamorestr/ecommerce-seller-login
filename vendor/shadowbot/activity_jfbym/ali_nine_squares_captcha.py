# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
from cProfile import label
import os
import xbot
import http
import json
import base64
import random

from xbot.web.automation import WebBrowser 
if os.name == 'nt':
    from ctypes import windll
from xbot._core import robot
from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value
from xbot._core.retry import Retry
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

def tip_base64(tip_ele, web_page:WebBrowser) -> str:
    label_images = []
    tip_id = web_page.find(tip_ele).get_attribute("id")
    js_code = '''
        function (context, args){
            const el = document.getElementById(%s);
            return el ? el.toDataURL() : null;
        }
    ''' % json.dumps(tip_id)
    
    for _ in Retry(timeout=5, ignore_exception=True):
        result = web_page.find(tip_ele).execute_javascript(js_code, execution_world='MAIN')
        if not result:
            sleep(0.1)
            continue
        if result not in label_images:
            label_images.append(result)
            if len(label_images) >= 2:
                return label_images[0], label_images[1]
        sleep(0.1)

    raise Exception("未在超时时间内获取到两个不同的标签图片")

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


def handle_captcha(web_page, tip_ele, background_ele, ok_ele, token, retry_count=5, single_click_count=5, refresh_ele=None):
    retry_count = int(retry_count or 5)
    single_click_count = int(single_click_count or 5)
    os_name = os.name
    if os_name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache Dir:{cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
    file_name = "ali_nine.png"
    save_path = os.path.join(cache_folder, file_name)
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名


        
    xbot.logging.info(f"Cache: {save_path}")
    solved = False
    json_save_path = os.path.join(os.path.dirname(__file__), "ali_nine_squares_captcha.json")

    # 外层控制总轮次：最多执行 retry_count 轮 single_click_count
    for _ in range(retry_count):
        try:
            web_page.find(background_ele, timeout=2)
        except Exception:
            solved = True
            break
        tips_text = ""
        first_request = True

        # 内层控制单次操作验证码次数：最多 single_click_count 次
        for _ in range(single_click_count):
            try:
                bg_ele = web_page.find(background_ele, timeout=2)
            except Exception:
                solved = True
                break

            b_x, b_y, b_width, b_height = bg_ele.get_bounding(to96dpi=False)
            shot_left = int(round(b_x))
            shot_top = int(round(b_y))
            shot_right = int(round(b_x + b_width))
            shot_bottom = int(round(b_y + b_height))
            if shot_right <= shot_left:
                shot_right = shot_left + 1
            if shot_bottom <= shot_top:
                shot_bottom = shot_top + 1

            xbot.win32.screenshot.save_screen_to_file(
                save_path, "png", shot_left, shot_top, shot_right, shot_bottom
            )
            with open(save_path, "rb") as f:
                base64_str = base64.b64encode(f.read()).decode("utf-8")

            if first_request:
                label_image1, label_image2 = tip_base64(tip_ele, web_page)
                payload = {
                    "image": base64_str,
                    "token": token,
                    "type": 30223,
                    "label_image1": label_image1,
                    "label_image2": label_image2,
                }
            else:
                payload = {
                    "image": base64_str,
                    "token": token,
                    "type": 30223,
                    "extra": tips_text,
                }

            result = ym_captcha_recognition(payload) if token else yd_captcha_recognition(payload)
            with open(json_save_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            # if result.get("code") != 10000:
            #     continue

            result_data = result.get("data") or {}
            # print(f'{result_data}')
            captcha_data = result_data.get("data") or {}
            serial_number = captcha_data.get("serial_number") or []
            click_pos = captcha_data.get("click_pos") or []
            tips_text = captcha_data.get("tips") or tips_text

            # serial_number 为空列表时，点击确定并退出内层循环
            if not serial_number:
                web_page.find(ok_ele).click()
                break

            if not click_pos:
                continue

            # click_pos 相对 background_ele 左上角，每次只点第一个
            position_x, position_y = click_pos[0]
            if os.name == "nt":
                distance_x = int((b_x + int(position_x)) * get_ppi()) + int(random.randint(-5, 5))
                distance_y = int((b_y + int(position_y)) * get_ppi()) + int(random.randint(-5, 5))
            else:
                distance_x = int(b_x + int(position_x)) + int(random.randint(-5, 5))
                distance_y = int(b_y + int(position_y)) + int(random.randint(-5, 5))
            xbot.win32.mouse_move(distance_x, distance_y, move_speed='middle')
            xbot.win32.mouse_click()
            first_request = False
            sleep(1)

        # 通过 background_ele 是否存在判断验证码是否已解决，控制外层循环退出
        if not web_page.is_element_displayed(background_ele):
            solved = True
            break
        else:
            web_page.find(refresh_ele).click()
            sleep(2)

    if not solved:
        raise Exception(f"验证码未在限定次数内完成: retry_count={retry_count}, single_click_count={single_click_count}")
    

def test_func():
    if "xbot_extensions" not in __file__:
        web_page = xbot.web.get_active('chrome')
        tip_ele = package.selector('ali_nine_squares_captcha_tip_ele')
        background_ele = package.selector('ali_nine_squares_captcha_background_ele')
        ok_ele = package.selector('ali_nine_squares_captcha_ok_ele')
        refresh_ele = package.selector('ali_nine_squares_captcha_refresh_ele')
        token = ''
        retry_count = 5
        single_click_count = 5
        handle_captcha(web_page, tip_ele, background_ele, ok_ele, token, retry_count, single_click_count, refresh_ele)
        exit()

    
def main(args):
    test_func()
    web_page = args.get("web_page")
    tip_ele = args.get("tip_ele")
    background_ele = args.get("background_ele")
    ok_ele = args.get("ok_ele")
    refresh_ele = args.get("refresh_ele")
    token = args.get("ym_token")
    retry_count = args.get("retry_count")
    single_click_count = args.get("single_click_count")

    handle_captcha(web_page, tip_ele, background_ele, ok_ele, token, retry_count, single_click_count, refresh_ele)