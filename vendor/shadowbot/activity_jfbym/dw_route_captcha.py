import xbot
import os
import xbot_visual
import base64
import json
import base64
import io
import urllib
import http.client
from urllib.parse import urlparse
from PIL import ImageGrab, Image

from PIL import Image
from io import BytesIO
if os.name == 'nt':
    from ctypes import windll
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation

from xbot import print, sleep, win32, web
from . import package
from .package import variables as glv

from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload, upload_captcha_screenshot, report_data, get_boundary_value

def get_xbot_client():
    common_info = robot.execute(f'Common.CommonConfig', None)
    return common_info.get("token")

def resize(img_path, save_path):
    """将图片重置尺寸(因为只有指定的尺寸才能被识别)
    :param img_path: 输入验证码截图的路径
    :param save_path: 重置的图片保存路径
    """
    ori_img = Image.open(img_path)
    resize_img = ori_img.resize((642, 639))
    resize_img.save(save_path)

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
    data = response_json.get("data")
    if not data:
        raise Exception(f"错误信息: {response_json}")
    return data


def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = {'Content-Type': 'application/json'}
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


def drag(drag_ele: WebElement, distance: int):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "slow"
    win32.manual_motion_on(motion_move=True,
                           motion_click=True,
                           motion_delay=True,
                           min_time=0.5,
                           max_time=2)
    win32.mouse_move(point_x=pos_center_x,
                     point_y=pos_center_y,
                     move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    win32.mouse_move(pos_center_x + distance,
                     pos_center_y,
                     move_speed=move_speed)
    win32.mouse_click(
        button="left",
        click_type="up",
    )
    win32.manual_motion_off()


def handle_captcha(web_page, background_ele, slider_ele, drag_ele, retry_count=int(5), offset=0, token=''):
    current_file_path = __file__
    current_file_name = os.path.basename(current_file_path)  #获得当前文件名


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

    if not retry_count: retry_count = 5
    save_path = os.path.join(cache_folder, "dw_route.png")


    for i in range(retry_count):
        drag_element = web_page.find(drag_ele)
        slider_element = web_page.find(slider_ele)
        x, y, width, height = web_page.find(background_ele).get_bounding(
            to96dpi=False)
        win32.screenshot.save_screen_to_file(save_path, "png", x, y, x + width,
                                             y + height)
        resize(save_path, save_path)
        background_ele_base64 = file2base64(save_path)
        print(background_ele_base64)
        captcha_code = "90003"  
        payload = {
            "image": background_ele_base64,
            'token': token,
            'type': captcha_code
        }

        if token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)
        if data.get("msg") != "识别成功":
            raise Exception("识别失败, 请重试")
        
        angle = data['data']['data']

        _slider_ele_list = slider_element.get_bounding()#得到滑条的位置信息
        _drag_ele_list = drag_element.get_bounding()#得到滑块的位置信息

        #做出点击位置

        x_offset = _drag_ele_list[2]/2
        y_offset = _drag_ele_list[3]/2
        point_x = _drag_ele_list[0] + x_offset
        point_y = _drag_ele_list[1] + y_offset
        
        angle = int(angle)
        #拖动距离 = 云码检测角度距离/360 * 滑条宽度
        slider_longth = _slider_ele_list[2] - (_drag_ele_list[2])
        distance = angle / 360 * slider_longth + int(offset)

        drag(drag_element, distance)
        sleep(2)
        
        if not xbot_visual.web.browser.element_display(
                browser=web_page, content_type="display",
                selector=background_ele):
                
            break


def main(args):
    print(get_xbot_client())
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    slider_ele = args.get("slider_ele")
    drag_ele = args.get("drag_ele")
    retry_count = args.get("retry_count")
    offset = args.get("offset",0)
    token = args.get("token")

    # web_page = web.get_active(mode='edge')
    # background_ele = "dw_route_ele"
    # slider_ele = "dw_slider_ele"
    # drag_ele = "dw_drag_ele"
    # retry_count = 5
    # offset = 0
    # token = ""

    handle_captcha(web_page, background_ele, slider_ele, drag_ele, retry_count, offset,
                   token)
