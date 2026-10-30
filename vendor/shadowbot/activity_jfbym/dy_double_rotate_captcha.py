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


def drag(drag_ele:WebElement, distance:int):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "middle"
    win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=0.1, max_time=0.5)
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="up", )
    win32.manual_motion_off()

def crop_to_circle(image_path):
    """将图片裁剪成圆形"""
    output_path, _ = os.path.splitext(image_path) 
    output_path = output_path + "crop" + ".png"
    image = Image.open(image_path).convert("RGBA")
    diameter = min(image.size)
    size = (diameter, diameter)
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, diameter, diameter), fill=255)
    image = ImageOps.fit(image, size, centering=(0.5, 0.5))
    output = Image.new('RGBA', size, (0, 0, 0, 0))
    output.paste(image, (0, 0), mask=mask)
    output.save(output_path, format="PNG")
    return output_path


def crop_to_ring(image_path, inner_diameter):
    """将图片裁剪成圆环"""
    output_path, _ = os.path.splitext(image_path) 
    output_path = output_path + "crop" + ".png"
    image = Image.open(image_path).convert("RGBA")
    
    outer_diameter = min(image.size)
    size = (outer_diameter, outer_diameter)

    outer_mask = Image.new('L', size, 0)
    inner_mask = Image.new('L', size, 0)
    
    draw_outer = ImageDraw.Draw(outer_mask)
    draw_outer.ellipse((0, 0, outer_diameter, outer_diameter), fill=255)

    inner_radius = inner_diameter // 2
    outer_radius = outer_diameter // 2
    upper_left = (outer_radius - inner_radius, outer_radius - inner_radius)
    lower_right = (outer_radius + inner_radius, outer_radius + inner_radius)
    
    draw_inner = ImageDraw.Draw(inner_mask)
    draw_inner.ellipse([upper_left, lower_right], fill=255)

    ring_mask = ImageChops.subtract(outer_mask, inner_mask)
    
    image = ImageOps.fit(image, size, centering=(0.5, 0.5))
    
    output = Image.new('RGBA', size, (0, 0, 0, 0))
    
    output.paste(image, (0, 0), mask=ring_mask)
    
    output.save(output_path, format="PNG")
    return output_path


def download_file(web_page, url, save_filename):
    """下载文件"""
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
    save_path = os.path.join(cache_folder, save_filename)

    xbot_visual.web_service.download(url=url, save_folder=cache_folder, custom_filename=True, save_filename=save_filename, wait_complete_timeout="300", connect_timeout_seconds="30", send_by_web=True, browser=web_page)
    return save_path


def handle_captcha(web_page:xbot.web.WebBrowser, double_rotate_outer_ele, double_rotate_inner_ele, 
    double_rotate_slider_ele, double_rotate_darg_ele, retry_count: int=5, token=""):
    
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名


    if not retry_count: retry_count=5
    outer_save_name = "double_rotate_outer_ele.png"
    inner_save_name = "double_rotate_inner_ele.png"

    for i in range(retry_count):
        # 使用原图下载数据
        double_rotate_outer_src = web_page.find(double_rotate_outer_ele).get_attribute("src")
        outer_save_path = download_file(web_page, double_rotate_outer_src, outer_save_name)
        double_rotate_inner_src = web_page.find(double_rotate_inner_ele).get_attribute("src")
        inner_save_path = download_file(web_page, double_rotate_inner_src, inner_save_name)

        outer_corp_img_base64 = file2base64(outer_save_path)
        inner_corp_img_base64 = file2base64(inner_save_path)

        payload = { 
            "out_ring_image": outer_corp_img_base64,
            "inner_circle_image": inner_corp_img_base64,
            'token': token, 
            'type': "90004"
        }
        
        if token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)
        if data.get("msg") != "识别成功":
            raise Exception("识别失败, 请重试")

        rotate_angle = int(data.get("data").get("data").get("rotate_angle"))

        s_x, s_y, s_w, s_h = web_page.find(double_rotate_slider_ele).get_bounding(to96dpi=False)
        d_x, d_y, d_w, d_h = web_page.find(double_rotate_darg_ele).get_bounding(to96dpi=False)
        print(rotate_angle)

        slider_aw = s_w - ( d_x + d_w / 2 - s_x) * 2
        if os.name == 'nt':
            distance = int(slider_aw* (rotate_angle/360) * get_ppi()) 
        else:
            distance = int(slider_aw* (rotate_angle/360))
        xbot.logging.info(f"Distant:{distance}")
        drag(web_page.find(double_rotate_darg_ele), distance)
        
        sleep(3)
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=double_rotate_outer_ele):
            break
    
def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active("chrome")
        double_rotate_outer_ele = package.selector('double_rotate_outer_ele')
        double_rotate_inner_ele = package.selector('double_rotate_inner_ele')
        double_rotate_slider_ele = package.selector('double_rotate_slider_ele')
        double_rotate_darg_ele = package.selector('double_rotate_darg_ele')
        retry_count = 3
        offset = 0
        token = ''
        handle_captcha(web_page, double_rotate_outer_ele, double_rotate_inner_ele, 
        double_rotate_slider_ele, double_rotate_darg_ele, retry_count, token)
        exit()

def main(args):
    test_func()
    web_page = args.get("web_page")
    double_rotate_outer_ele = args.get("double_rotate_outer_ele")
    double_rotate_inner_ele = args.get("double_rotate_inner_ele")
    double_rotate_slider_ele = args.get("double_rotate_slider_ele")
    double_rotate_darg_ele = args.get("double_rotate_darg_ele")
    retry_count = args.get("retry_count")
    offset = args.get("offset")
    token = args.get("token")

    # web_page = web.get_active(mode="chrome")

    # double_rotate_inner_ele = "double_rotate_inner_ele"
    # double_rotate_outer_ele = "double_rotate_outer_ele"
    # token = ""

    handle_captcha(web_page, double_rotate_outer_ele, double_rotate_inner_ele, 
    double_rotate_slider_ele, double_rotate_darg_ele, retry_count, token)
