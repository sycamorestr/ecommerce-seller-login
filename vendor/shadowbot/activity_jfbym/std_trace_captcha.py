# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import os
import http
from urllib.parse import urlparse
import json
import xbot_visual

from xbot import print, sleep, web
from .import package
from .package import variables as glv
from xbot.web.browser import WebBrowser, WebElement
from .utils import get_xbot_activity_cache_folder, file2base64, start_upload, end_upload,upload_captcha_screenshot, report_data, get_boundary_value
from xbot._core import robot
import ctypes
import time

def _moveTo(x, y):
    """Send the mouse move event to Windows by calling SetCursorPos() win32
    function.

    Args:
      button (str): The mouse button, either 'left', 'middle', or 'right'
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.

    Returns:
      None
    """
    if os.name == 'nt':
        ctypes.windll.user32.SetCursorPos(x, y)
    else:
        xbot.win32.mouse_move(x, y, move_speed="instant")


def recg(token, base64_im):
    """请求云码识别淘"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = { 'Content-Type': 'application/json'}
    data = { 'image': base64_im, 'token': token, 'type': 100016 }
    data_json = json.dumps(data)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json
def yd_recg(image_base64):
    common_info = robot.execute(f'Common.CommonConfig', None)
    token = common_info.get("token")
    conn = http.client.HTTPSConnection(urlparse(common_info.get("webApi")).netloc)
    payload = json.dumps({
        "thirdPartyInterfaceCode": "jfbym_100016",
        "data": {},
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": {
                "image": image_base64
            },
            "pathVariable": {}
        },
        "bizType": "rpa-command"
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/api/openapi/v2/thirdParty/interface/call", payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def handle_captcha(web_page, background_ele, ym_token, retry_count):

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


    for i in range(int(retry_count)):
        current_time = int(time.time()*1000)
        filename = f"std_trace_{current_time}.png"
        web_page.find(background_ele).screenshot(cache_folder, filename=filename)
        image_path = os.path.join(cache_folder, filename)
        image_base64 = file2base64(image_path)

        # 2. 识别验证码
        if ym_token:
            res = recg(ym_token, image_base64)
            if res.get("msg") != "识别成功":
                raise Exception("验证码识别失败")
            data = res.get("data").get("data")
        else:
            res = yd_recg(image_base64)
            if res.get("data").get("msg") != "识别成功":
                raise Exception("识别失败, 请重试")
            data = res.get("data").get("data").get("data")

        trace_positions = [list(map(int, item.split(","))) for item in data.split("|")]
        xbot.logging.info(f"Rxecg Result: {trace_positions}")

        # 3. 按照轨迹拖动滑块
        x, y, _, _ = web_page.find(background_ele).get_bounding(to96dpi=False)
        xbot.win32.mouse_move(x, y)

        for index,(offset_x, offset_y) in enumerate(trace_positions):

            current_x = x+int(offset_x)
            current_y = y+int(offset_y)
            _moveTo(current_x, current_y)

            if index == 0:
                xbot.win32.mouse_click(click_type="down", delay_after=0)
        
            # xbot.win32.mouse_move(current_x,current_y,delay_after=0, move_speed="fast")
            
            sleep(0.01)
        xbot.win32.mouse_click(click_type="up", delay_after=0)

        sleep(3)

        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=background_ele):
            break
       


def main(args):

    web_page: WebBrowser = args.get("web_page")
    background_ele: WebElement = args.get("background_ele")
    ym_token: str = args.get("ym_token")
    retry_count: str = args.get("retry_count")

    handle_captcha(web_page, background_ele, ym_token, retry_count)

    pass
