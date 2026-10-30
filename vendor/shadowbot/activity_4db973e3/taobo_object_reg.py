# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import xbot_visual
import base64
import json
import base64    
import io
import http.client
from PIL import ImageGrab

from PIL import Image
from io import BytesIO
if os.name =='nt':
    from ctypes import windll
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation

from xbot import print, sleep, win32
from .import package
from .resources import trace_api
from .package import variables as glv  

from xbot._core import robot


def join_images(image1, image2):
    """图片拼接"""
    width1, height1 = image1.size
    width2, height2 = image2.size
    new_image = Image.new('RGB', (max(width1, width2), height1+height2), (255, 255, 255))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (0, height1))
    return new_image


def encode_image(image):
    """图片转base64"""
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    base64_string = base64.b64encode(img_bytes).decode('utf-8')
    return base64_string


def decode_image(base64_string):
    """字符串转图片"""
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    return img.convert('RGBA')


def get_ppi():
    """
    获取屏幕的缩放
    """
    LOGPIXELSX = 88
    LOGPIXELSY = 90
    user32 = windll.user32
    user32.SetProcessDPIAware()
    dc = user32.GetDC(0)   
    pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
    user32.ReleaseDC(0, dc)
    res = float.as_integer_ratio(round(pix_per_inch / 96,2))
    return res[1]/res[0]


def recg(token, base64_im):
    """请求云码识别淘"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = { 'Content-Type': 'application/json'}
    data = { 'image': base64_im, 'token': token, 'type': 20226 }
    data_json = json.dumps(data)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def get_xbot_client():
    common_info = robot.execute(f'Common.CommonConfig', None)
    return common_info.get("token")


def yd_recg(base64_im):
    token = get_xbot_client()
    conn = http.client.HTTPSConnection("api.yingdao.com")
    payload = json.dumps({
        "thirdPartyInterfaceCode": "jfbym_20226",
        "data": {},
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": {
            "image": base64_im
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


def drag(drag_ele:WebElement, distance:int):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2

    move_speed = "middle"

    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)

    poit_x, point_y = win32.get_mouse_position(relative_to="screen")
    win32.mouse_click(button="left", click_type="down")
    win32.manual_motion_on()
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed="middle")
    win32.manual_motion_off()
    win32.mouse_click(button="left", click_type="up")


def relative_drag(distance:int,move_speed = "fast", up_flag=True):
    poit_x, point_y = win32.get_mouse_position(relative_to="screen")
    win32.mouse_click(button="left", click_type="down")
    win32.manual_motion_on()
    win32.mouse_move(poit_x + distance, point_y, move_speed=move_speed)
    win32.manual_motion_off()
    if up_flag:
        win32.mouse_click(button="left", click_type="up")


def handle_verification(web_page, token:str, background_ele: WebElement, tip_ele: WebElement, drag_ele:WebElement, slider_ele:WebElement ,retry_count: int, offset=0):
    
    if not retry_count: retry_count=5
    t_x, t_y, _, _ = web_page.find(tip_ele).get_bounding(to96dpi=False)
    d_x, _, d_width, _ = web_page.find(drag_ele).get_bounding(to96dpi=False)
    b_x, b_y, b_width, b_height = web_page.find(background_ele).get_bounding(to96dpi=False)
    p = d_x + d_width - b_x

    for i in range(retry_count):
        drag_element = web_page.find(drag_ele)

        drag_element.hover()
        _, _, slider_width, _ = web_page.find(slider_ele).get_bounding(to96dpi=False)
        _, _, drag_width, _ = web_page.find(drag_ele).get_bounding(to96dpi=False)
        
        if os.name =='nt':
            distance = int((slider_width - drag_width) * get_ppi())
        else:
            distance = int((slider_width - drag_width)
        relative_drag(distance, move_speed="middle", up_flag=False)
        for i in range(100):
            try:
                xbot.win32.clipboard.clear()
                xbot.win32.screenshot.save_screen_to_clipboard(t_x, t_y, b_x + b_width, b_y + b_height)
                background_img = ImageGrab.grabclipboard()
                xbot.win32.clipboard.clear()
                concatenated_base64_image  = encode_image(background_img)
                break
            except Exception as e:
                print(e)
                sleep(0.5)

        if token:
            reslut = recg(token, concatenated_base64_image)
        else:
            reslut = yd_recg(concatenated_base64_image).get("data")
        if reslut.get("msg") != "识别成功":
            raise Exception("识别失败, 请重试")
        
        distance = reslut.get("data").get("data")
        distance = int((int(distance)-(slider_width- drag_width/2) + offset) * get_ppi())
        relative_drag(distance, move_speed="middle")
        
        sleep(3)
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=background_ele):
            break
        sleep(3)


def main(args):
    web_page = args.get("web_page")
    token = args.get("token")
    background_ele = args.get("background_ele")
    tip_ele = args.get("tip_ele")
    drag_ele = args.get("drag_ele")
    slider_ele = args.get("slider_ele")
    retry_count = args.get("retry_count")
    offset = args.get("offset")

    handle_verification(web_page, token, background_ele, tip_ele, drag_ele, slider_ele, retry_count, offset)

    pass
