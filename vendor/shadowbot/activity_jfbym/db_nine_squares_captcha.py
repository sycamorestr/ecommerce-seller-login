# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
import xbot
import http.client
import json
import base64

if os.name == 'nt':
    from ctypes import windll
from xbot._core import robot
from xbot import print, sleep, win32, web
from . import package
from .package import variables as glv
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi
from urllib.parse import urlparse


SCALING_FACTOR = get_ppi()


def get_xbot_client():
    common_info = robot.execute(f'Common.CommonConfig', None)
    return common_info.get("token")


def ym_captcha_recognition(payload, timeout=10):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com", timeout=timeout)
    headers = {"Content-Type": "application/json"}
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload, timeout=10):
    """使用增值服务请求验证码"""
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
 
    res_payload = json.dumps({
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
    })
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    conn.request("POST", "/api/v2/aiservice/call", res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()

    if int(response_json["data"]["statusCode"]) != 200:
        raise Exception(f"错误信息: {response_json}")
    return response_json


def get_ppi():
    """获取屏幕的缩放"""
    if os.name == "nt":
        LOGPIXELSX = 88
        LOGPIXELSY = 90
        user32 = windll.user32
        user32.SetProcessDPIAware()
        dc = user32.GetDC(0)
        pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
        user32.ReleaseDC(0, dc)
        res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
        return res[1] / res[0]
    else:
        return 1


def drag_image_to_target(web_page, source_x, source_y, target_ele):
    """将图片从源位置拖拽到目标元素中心"""
    target_bounds = web_page.find(target_ele).get_bounding(to96dpi=True)
    target_x = target_bounds[0] + target_bounds[2] / 2
    target_y = target_bounds[1] + target_bounds[3] / 2

    if os.name == "nt":
        source_x = int(source_x * SCALING_FACTOR)
        source_y = int(source_y * SCALING_FACTOR)
        target_x = int(target_x)
        target_y = int(target_y)
    else:
        source_x = int(source_x)
        source_y = int(source_y)
        target_x = int(target_x)
        target_y = int(target_y)

    win32.manual_motion_on(
        motion_move=True,
        motion_click=True,
        motion_delay=True,
        min_time=0.1,
        max_time=0.5
    )

    win32.mouse_move(source_x, source_y)
    win32.mouse_click(button="left", click_type="down")
    win32.mouse_move(target_x, target_y, 'screen', "middle")
    sleep(1)
    win32.mouse_click(button="left", click_type="up")

    win32.manual_motion_off()


def handle_captcha(web_page, background_ele, drag_target_ele, retry_count=5, token="", confirm_ele=None):
    """处理九宫格拖拽验证码

    :param web_page: 网页对象
    :param background_ele: 九宫格背景元素
    :param drag_target_ele: 拖拽目标元素（固定目标）
    :param retry_count: 重试次数
    :param token: 云码token，为空则使用影刀
    :param confirm_ele: 确认提交按钮
    """
    os_name = os.name
    if os_name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache Dir: {cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

    if not retry_count:
        retry_count = 5

    background_save_path = os.path.join(cache_folder, "db_nine_squares_bg.png")

    for _ in range(retry_count):
        try:
            bg_ele = web_page.find(background_ele)
        except Exception:
            xbot.logging.info("验证码已消失或通过")
            break

        b_x, b_y, b_width, b_height = bg_ele.get_bounding(to96dpi=False)
        win32.screenshot.save_screen_to_file(
            background_save_path, "png", b_x, b_y, b_x + b_width, b_y + b_height
        )

        background_base64 = file2base64(background_save_path)
        payload = {
            "image": background_base64,
            "token": token,
            "type": 88888,
        }

        if token:
            result = ym_captcha_recognition(payload)
            if result.get("msg") != "识别成功":
                raise Exception("识别失败, 请重试")
            data = result.get("data", {}).get("data", "")
        else:
            result = yd_captcha_recognition(payload)
            data = result.get("data", {}).get("response", {}).get("data", "")

        if not data:
            raise Exception("识别返回数据为空")

        positions = [(int(item.split(",")[0]), int(item.split(",")[1])) for item in data.split("|")]

        for pos_x, pos_y in positions:
            abs_x = b_x + pos_x
            abs_y = b_y + pos_y
            drag_image_to_target(web_page, abs_x, abs_y, drag_target_ele)
            sleep(0.5)

        if confirm_ele:
            web_page.find(confirm_ele).click()

        sleep(2)

        try:
            web_page.find(background_ele, timeout=2)
        except Exception:
            xbot.logging.info("验证码已通过")
            break


def test_func():
    if "xbot_extensions" not in __file__:
        web_page = xbot.web.get_active("chrome")
        background_ele = package.selector("db_nine_squares_background")
        drag_target_ele = package.selector("db_nine_squares_drag_target")
        confirm_ele = package.selector("db_nine_squares_confirm")
        token = ""
        retry_count = 5
        handle_captcha(web_page, background_ele, drag_target_ele, retry_count, token, confirm_ele)
        exit()


def main(args):
    test_func()
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    drag_target_ele = args.get("drag_target_ele")
    confirm_ele = args.get("confirm_ele")
    retry_count = args.get("retry_count", 5)
    token = args.get("token", "")

    handle_captcha(web_page, background_ele, drag_target_ele, retry_count, token, confirm_ele)