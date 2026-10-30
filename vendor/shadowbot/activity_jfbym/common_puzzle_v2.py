import os
import json
import http.client


import xbot  # type: ignore
import xbot_visual  # type: ignore
from . import package 

if os.name == "nt":
    from ctypes import windll

from urllib.parse import urlparse
from xbot._core import robot  # type: ignore
from xbot import print, sleep, win32  # type: ignore
from xbot.web.element import WebElement  # type: ignore
import base64
from .package import variables as glv
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi, gen_selector
from xbot._core.retry import Retry
from PIL import Image
import ctypes
from . import common_puzzle_click

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
    scaled_x = int(x / get_ppi())
    scaled_y = int(y / get_ppi())
    if os.name == 'nt':
        ctypes.windll.user32.SetCursorPos(scaled_x, scaled_y)
    else:
        win32.mouse_move(scaled_x, scaled_y, move_speed="instant")

def save_image_from_body(body, file_path):
    # Base64 解码
    if ',' in body:
        body = body.split(',')[1]
    img_data = base64.b64decode(body)
    
    # 写入文件
    with open(file_path, "wb") as f:
        f.write(img_data)

def ym_captcha_recognition(payload):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = {"Content-Type": "application/json"}
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json.get('data')

def yd_captcha_recognition(payload):
    # 判断客户端版本, 是否使用ssl, host, 以及token
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

    payload = json.dumps(
        {
            "aiToolInterfaceCodeId": "jfbym_20555",
            "aiID": "captcha",
            "rule": "jfbym",
            "channel": "jfbym",
            "model": "20555",
            "bizCode": "",
            "bizId": "",
            "bizType": "",
            "thirdPartyReqData": {
                "header": {},
                "params": {},
                "body": {"json": payload.get("json")},
            },
        }
    )
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    conn.request("POST", "/api/v2/aiservice/call", payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode("utf-8")
    response_json = json.loads(response_data)
    conn.close()
    return response_json.get("data")

def drag(drag_ele: WebElement, distance: int):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "middle"
    win32.manual_motion_on(
        motion_move=True,
        motion_click=True,
        motion_delay=True,
        min_time=0.1,
        max_time=0.5,
    )
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="up")
    win32.manual_motion_off()


def handle_captcha(
    web_page: xbot.web.WebBrowser,
    refresh_ele,
    retry_count: int = 5,
    ym_token=""
):
    if os.name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
        xbot.logging.info(f"Cache folder: {cache_folder}")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

    if not retry_count:
        retry_count = 5

    trace_background_selector = gen_selector('//img[@id="tpass-captcha-slider-bg-img"]', 'trace_background_selector')
    trace_inner_selector = gen_selector('//img[@id="tpass-captcha-slider-move-img"]', 'trace_template_selector')
    puzzle_all_selector = gen_selector('//div[@class="tpass-captcha-slider-concat-bg-img"]', 'puzzle_all_selector')
    puzzle_up_selector = gen_selector('//div[@class="tpass-captcha-slider-concat-img-div"]', 'puzzle_up_selector')
    click_web_element = gen_selector('//div[@class="content"]', 'common_puzzle_click_web_element')
    click_prompt_ele = gen_selector('//div[@class="click-tip"]', 'common_puzzle_click_prompt_ele')
    click_confirm = gen_selector('//div[@class="click-confirm-btn"]', 'common_puzzle_click_confirm_ele')

    for _ in range(int(retry_count)):
        # 创建json文件 存储监听到的图片
        puzzle_json_path = os.path.join(cache_folder, "common_puzzle_v2_puzzle.json")
        
        trace_json_path = os.path.join(cache_folder, "common_puzzle_v2_trace.json")
        captcha_type = ''

        # 根据监听长度判断验证码类型
        if web_page.is_element_displayed(puzzle_all_selector):
            # web_page.find(refresh_ele).click()
            # continue
            # 拼接验证 - 覆盖写入
            if os.path.exists(puzzle_json_path):
                os.remove(puzzle_json_path)
            puzzle_img_base64 = web_page.find(puzzle_all_selector).get_attribute('style').split('("')[1].split('")')[0]
            puzzle_img_path = os.path.join(cache_folder, "common_puzzle_v2_puzzle.png")
            save_image_from_body(puzzle_img_base64, puzzle_img_path)
            # 计算randomY值
            all_height = web_page.find(puzzle_all_selector).get_bounding(to96dpi=True)[3]
            resize = all_height / 180
            up_height = web_page.find(puzzle_up_selector).get_bounding(to96dpi=True)[3]
            up_height = up_height / resize
            randomY = round((180 - up_height)*(330/180))
            json_img = {
                "captcha": {
                    "id": "CONCAT_18646a176477473b9e84042249598b39",
                    "type": "CONCAT",
                    "backgroundImage": puzzle_img_base64,
                    "backgroundImageTag": "default",
                    "templateImage": "null",
                    "templateImageTag": "null",
                    "backgroundImageWidth": Image.open(puzzle_img_path).size[0],
                    "backgroundImageHeight": Image.open(puzzle_img_path).size[1],
                    "templateImageWidth": "null",
                    "templateImageHeight": "null",
                    "data":{
                        "randomY": randomY,
                    }
                }
            }
            puzzle_cache_path = os.path.join(cache_folder, "puzzle_cache.json")
            with open(puzzle_cache_path, "w", encoding="utf-8") as f:
                json.dump(json_img, f, ensure_ascii=False, indent=2)
            payload = {
                "token": ym_token,
                "type": "20555",
                "json": json.dumps(json_img)
            }
            captcha_type = 'CONCAT'
        elif web_page.is_element_displayed(trace_inner_selector):
            # 旋转验证 - 覆盖写入
            if os.path.exists(trace_json_path):
                os.remove(trace_json_path)
            # 写死两个元素
            trace_img_background_base64 = web_page.find(trace_background_selector).get_attribute('src')
            trace_img_template_base64 = web_page.find(trace_inner_selector).get_attribute('src')
            trace_img_background_path = os.path.join(cache_folder, "common_puzzle_v2_background.png")
            save_image_from_body(trace_img_background_base64, trace_img_background_path)
            trace_img_template_path = os.path.join(cache_folder, "common_puzzle_v2_inner.png")
            save_image_from_body(trace_img_template_base64, trace_img_template_path)

            json_img = {
                "captcha": {
                    "id": "ROTATE_18646a176477473b9e84042249598b49",
                    "type": "ROTATE",
                    "backgroundImage": trace_img_background_base64,
                    "backgroundImageTag": "default",
                    "templateImage": trace_img_template_base64,
                    "templateImageTag": "default",
                    "backgroundImageWidth": Image.open(trace_img_background_path).size[0],
                    "backgroundImageHeight": Image.open(trace_img_background_path).size[1],
                    "templateImageWidth": Image.open(trace_img_template_path).size[0],
                    "templateImageHeight": Image.open(trace_img_template_path).size[1],
                    "data":""
                }
            }
            trace_cache_path = os.path.join(cache_folder, "trace_cache.json")
            with open(trace_cache_path, "w", encoding="utf-8") as f:
                json.dump(json_img, f, ensure_ascii=False, indent=2)
            captcha_type = 'ROTATE'
            payload = {
                "token": ym_token,
                "type": "20555",
                "json": json.dumps(json_img)
            }
        elif web_page.is_element_displayed(click_prompt_ele):
            common_puzzle_click.handle_captcha(web_page, click_web_element, click_prompt_ele, ym_token, 1, click_confirm)
            continue
        else:
            break
        drag_element = package.selector('拼图拖拽元素_v2')
        drag_width = web_page.find(drag_element).get_bounding(to96dpi=True)[2]
        if ym_token:
            data = ym_captcha_recognition(payload)
            if not data:
                web_page.find(refresh_ele).click()
                continue
            data = data.get("data")
        else:
            data = yd_captcha_recognition(payload)
            if data.get("statusCode") == "500":
                raise Exception('钱包[RPA积分池]余额已耗尽，暂时无法使用相关能力。请联系管理员充值')
            elif data.get("statusCode") != "200":
                web_page.find(refresh_ele).click()
                continue
            data = data.get("response").get('data')
        try:
            distance = int(data)
        except:
            web_page.find(refresh_ele).click()
            continue
        if captcha_type == 'CONCAT':
            slider_width = web_page.find(puzzle_all_selector).get_bounding(to96dpi=True)[2]
            # （整个原图的长度-向左移动的距离）* 网页前端和原图的比值
            distance = (550 - distance) * (slider_width / 550)
            # continue
        elif captcha_type == 'ROTATE':
            slider_width = web_page.find(trace_background_selector).get_bounding(to96dpi=True)[2]
            distance = (distance * (slider_width - drag_width) / 360)
        drag(web_page.find(drag_element), distance)
        sleep(3)
        if not web_page.is_element_displayed(drag_element):
            return
        else:
            continue
    


def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        refresh_ele = package.selector('common_puzzle_v2_refresh_ele')
        retry_count = 5
        ym_token = ''
        handle_captcha(
            web_page,
            refresh_ele,
            retry_count,
            ym_token
        )
        exit()

def main(args):
    test_func()
    web_page = args.get("web_page")
    refresh_ele = args.get('refresh_ele')
    retry_count = args.get("retry_count")
    ym_token = args.get("ym_token", "")

    handle_captcha(
        web_page,
        refresh_ele,
        retry_count,
        ym_token
    )