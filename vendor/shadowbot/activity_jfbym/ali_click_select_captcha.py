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
from ctypes import windll
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation
from PIL import Image, ImageDraw, ImageOps, ImageChops
from urllib.parse import urlparse

from xbot import print, sleep, win32, web
from .import package  
from .package import variables as glv

from xbot._core import robot 
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, start_upload, end_upload

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


def handle_captcha(web_page, background_ele, label_elem, ym_token,
                   retry_count, confirm_ele, refresh_ele) -> str:
    """处理验证码"""
    current_file_path = __file__  
    current_file_name = os.path.basename(current_file_path) #获得当前文件名

    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    xbot.logging.info(f"Cache Dir:{cache_folder}")
    if not retry_count: retry_count=5
    background_ele_save_path = os.path.join(cache_folder, "ali_background.png")
    label_ele_save_path = os.path.join(cache_folder, "ali_label.png")

    for i in range(retry_count):
        #需要传入5个label图
        label_image_list = []
        for i in range(5):
            shotx, shoty, width, height = web_page.find(label_elem).get_bounding(to96dpi=False)
            win32.screenshot.save_screen_to_file(label_ele_save_path, "png1", shotx, shoty, shotx+width, shoty+height)
            label_img_base64 = file2base64(label_ele_save_path)
            label_image_list.append(label_img_base64)
            sleep(1)

        #这里获得第一次传入背景元素，并请求拿到tips的内容
        x, y, width, height = web_page.find(background_ele).get_bounding(to96dpi=False)
        win32.screenshot.save_screen_to_file(background_ele_save_path, "png", x, y,x+width, y+height)
        background_img_base64 = file2base64(background_ele_save_path)
        payload = {
                "token": ym_token,
                "type":"30223",
                'image': background_img_base64,#下面图的base64
                'label_image1':label_image_list[0],#上面的提示信息截图1的base64，
                'label_image2':label_image_list[1],#上面的提示信息截图2的base64，
                'label_image3':label_image_list[2],#上面的提示信息截图3的base64，
                'label_image4':label_image_list[3],#上面的提示信息截图4的base64，
                'label_image5':label_image_list[4],#上面的提示信息截图5的base64，
                "extra":'',#可选参数，第一次返回的Tips的值；extra和label参数都是可选参数，但是二者必须要一个，且extra参数优先级高于label参数
            }

        if ym_token:
            data = ym_captcha_recognition(payload)
        else:
            data = yd_captcha_recognition(payload)

        data = data.get("data").get("data")
        tips = data['tips']
        positions = data['click_pos']

        #拿到鼠标移动并点击的坐标
        mov_x, mov_y, _, _ = web_page.find(background_ele).get_bounding(to96dpi=True)
        #判断最新更新的背景图是否还存有验证元素
        while positions != []:
            posi_x =  mov_x + int(int(positions[0][0]) * get_ppi())
            posi_y =  mov_y + int(int(positions[0][1]) * get_ppi())
            xbot.win32.mouse_move(posi_x, posi_y)
            xbot.win32.mouse_click()
            sleep(1)

            #每一次点击都会带来背景元素的变化，因此需重新请求一次
            win32.screenshot.save_screen_to_file(background_ele_save_path, "png", x, y,x+width, y+height)
            background_img_base64 = file2base64(background_ele_save_path)

            payload = {
                    'image': background_img_base64,#下面图的base64
                    "token": ym_token,
                    "type":"30223",
                    "extra":tips,#可选参数，第一次返回的Tips的值；extra和label参数都是可选参数，但是二者必须要一个，且extra参数优先级高于label参数
                }
            if ym_token:
                data = ym_captcha_recognition(payload)
            else:
                data = yd_captcha_recognition(payload)

            data = data.get("data").get("data")
            positions = data['click_pos']
            if positions == []:
                break
        web_page.find(confirm_ele).click()
        if not xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=background_ele):
            break
        else:
            web_page.find(refresh_ele).click()
        
    
        
        
def main(args):
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    ym_token = args.get("ym_token", '')
    label_elem = args.get("label_elem")
    retry_count = args.get("retry_count", '')
    confirm_ele = args.get('confirm_ele', '')
    refresh_ele = args.get('refresh_ele', '')
    # web_page = web.get_active(mode="chrome")
    # background_ele = "ali_background"
    # label_elem = "ali_label_ele"
    # ym_token = ""
    # confirm_ele = '提交'


    handle_captcha(web_page, background_ele, label_elem, ym_token, retry_count, confirm_ele, refresh_ele)
