# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import xbot_visual
import base64
import json
import io
import os
import http.client
import random
from urllib.parse import urlparse

from PIL import Image
from io import BytesIO
if os.name == 'nt':
    from ctypes import windll
from xbot.web.element import WebElement

from xbot import print, sleep, win32, web
from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, gen_selector

# ============================================================
# 验证码识别 API（云码 / 增值服务）
# ============================================================

def ym_captcha_recognition(payload: dict, timeout: int = 60):
    """请求云码识别验证码"""
    conn = http.client.HTTPConnection("api.jfbym.com")
    headers = {'Content-Type': 'application/json'}
    conn.timeout = timeout
    data_json = json.dumps(payload)
    conn.request("POST", "/api/YmServer/customApi", body=data_json, headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    return response_json


def yd_captcha_recognition(payload: dict, timeout: int = 60):
    """使用增值服务请求验证码"""
    captcha_type = payload.get("type")
    payload.pop("type")

    common_info = robot.execute("Common.CommonConfig", None)
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
        "model": captcha_type,
        "bizCode": "",
        "bizId": "",
        "bizType": "",
        "thirdPartyReqData": {
            "header": {},
            "params": {},
            "body": {"json": payload.get("json")},
        },
    })
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    conn.request("POST", "/api/v2/aiservice/call", res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()

    data = response_json.get("data")
    if not data:
        raise Exception(f"错误信息: {response_json}")
    return data


# ============================================================
# 图片工具
# ============================================================

def encode_image(image: Image) -> str:
    """图片转base64"""
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')


def decode_image(base64_string: str) -> Image:
    """字符串转图片"""
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    return img.convert('RGBA')


def get_image_size_from_base64(base64_string: str):
    """从 base64 字符串获取图片宽高"""
    img = decode_image(base64_string)
    return img.size


# ============================================================
# 拖动操作
# ============================================================

def drag(drag_ele: WebElement, distance: int):
    """基础拖动：按住滑块中心，向右拖动指定距离"""
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "middle"
    win32.manual_motion_on(
        motion_move=True, motion_click=True, motion_delay=True,
        min_time=0.5, max_time=2
    )
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed=move_speed)
    sleep(0.5)
    win32.mouse_click(button="left", click_type="up")
    win32.manual_motion_off()


# ============================================================
# 辅助函数
# ============================================================

def get_web_page_by_web_page(web_page):
    """刷新 web_page 引用"""
    product_name = getattr(
        web_page, "product_name",
        "cef" if web_page._controller == "CEFBrowser" else "firefox"
    )
    return xbot.web.get_active(mode=product_name)


def get_cache_folder() -> str:
    """获取缓存目录"""
    if os.name == "nt":
        cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME")
        cache_folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
    xbot.logging.info(f"Cache Dir:{cache_folder}")
    return cache_folder


def clean_base64(b64: str) -> str:
    """去掉 base64 的 data:image/...;base64, 前缀"""
    if "," in b64:
        return b64.split(",", 1)[-1]
    return b64


# ============================================================
# 核心逻辑
# ============================================================

def handle_captcha(
    web_page: web.WebBrowser,
    token: str,
    refresh_ele: WebElement,
    drag_ele: WebElement,
    slider_ele: WebElement,
    retry_count: int = 5,
    timeout: int = 60,
    offset: int = 0,
    retry_wait_time: int = 3,
):
    """
    处理旋转验证码

    拖动逻辑: 向右拖拽滑块 -> 外圈不动，内圈顺时针旋转
    识别返回: 外圈不转时，内圈需要顺时针旋转的度数(angle)
    拖动距离: (slider_width - drag_width) * angle / 360 + offset

    参数:
        web_page:        浏览器页面对象
        token:           云码 token（为空则走增值服务）
        refresh_ele:     刷新按钮元素选择器
        drag_ele:        拖拽滑块元素选择器
        slider_ele:      滑轨背景元素选择器
        retry_count:     最大重试次数
        timeout:         识别超时(秒)
        offset:          拖动距离修正偏移量
        retry_wait_time: 重试等待间隔(秒)
    """

    # 写死元素选择器
    outer_ele = gen_selector('//img[@id="tianai-captcha-slider-bg-img"]', 'dxm_outer_ele')
    inner_ele = gen_selector('//img[@id="tianai-captcha-slider-move-img"]', 'dxm_inner_ele')

    _, _, drag_width, _ = web_page.find(drag_ele).get_bounding(to96dpi=True)
    _, _, slider_width, _ = web_page.find(slider_ele).get_bounding(to96dpi=True)

    captcha_type = "20555"

    for _ in range(retry_count):
        # --------------------------------------------------
        # 1. 从元素 src 属性获取外圈和内圈图片的 base64
        # --------------------------------------------------
        outer_src = web_page.find(outer_ele).get_attribute("src")
        inner_src = web_page.find(inner_ele).get_attribute("src")

        outer_b64 = clean_base64(outer_src)
        inner_b64 = clean_base64(inner_src)

        outer_w, outer_h = get_image_size_from_base64(outer_b64)
        inner_w, inner_h = get_image_size_from_base64(inner_b64)

        xbot.logging.info(f"外圈: {outer_w}x{outer_h}, 内圈: {inner_w}x{inner_h}")

        # --------------------------------------------------
        # 3. 构建请求识别
        # --------------------------------------------------
        captcha_json = json.dumps({
            "captcha": {
                "type": "ROTATE",
                "backgroundImage": outer_b64,
                "templateImage": inner_b64,
                "backgroundImageWidth": outer_w,
                "backgroundImageHeight": outer_h,
                "templateImageWidth": inner_w,
                "templateImageHeight": inner_h,
            }
        })

        payload = {
            "token": token,
            "type": captcha_type,
            "json": captcha_json,
        }

        # 将请求参数写入文件(base64内容过长,仅写尺寸信息)
        cache_folder = get_cache_folder()
        captcha_file_path = os.path.join(cache_folder, "dxm_rotate_captcha.json")
        with open(captcha_file_path, "w", encoding="utf-8") as f:
            json.dump({
                "type": captcha_type,
                "outer_size": f"{outer_w}x{outer_h}",
                "inner_size": f"{inner_w}x{inner_h}",
            }, f, ensure_ascii=False, indent=2)
        xbot.logging.info(f"请求参数已写入: {captcha_file_path}")

        if token:
            data = ym_captcha_recognition(payload, timeout)
            data = data.get("data")
        else:
            data = yd_captcha_recognition(payload, timeout)
            if data.get("statusCode") != "200":
                print(data.get("msg"))
                print('识别失败，本次验证不收取费用')
                continue
            data = data.get("response")

        # --------------------------------------------------
        # 4. 解析识别结果: 内圈需要顺时针旋转的度数
        # --------------------------------------------------
        angle = int(data.get("data"))
        xbot.logging.info(f"Angle: {angle}°")

        # 度数 -> 拖动距离: 滑块向右拖，内圈顺时针转
        distance = int((slider_width - drag_width) * angle / 360) + offset
        xbot.logging.info(f"Distance: {distance}px")

        # --------------------------------------------------
        # 5. 执行拖动
        # --------------------------------------------------
        drag_element = web_page.find(drag_ele)
        drag(drag_element, distance)

        # --------------------------------------------------
        # 6. 验证结果
        # --------------------------------------------------
        web_page = get_web_page_by_web_page(web_page)
        sleep(retry_wait_time)

        if not xbot_visual.web.browser.element_display(
            browser=web_page, selector=drag_ele, content_type="display"
        ):
            break

        # 验证失败，刷新验证码后重试
        web_page.find(refresh_ele).click(simulative=False)
        sleep(1)


# ============================================================
# 入口
# ============================================================

def test_func():
    """独立测试入口"""
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        refresh_ele = gen_selector('//div[@class="refresh-btn"]', 'dxm_refresh_ele')
        drag_ele = gen_selector('//div[@class="slider-move-btn"]', 'dxm_drag_ele')
        slider_ele = gen_selector('//div[@class="slider-move-track"]', 'dxm_slider_ele')
        retry_count = 3
        token = ''
        timeout = 60
        offset = 0
        retry_wait_time = 3
        handle_captcha(
            web_page, token, refresh_ele, drag_ele, slider_ele,
            retry_count, timeout, offset, retry_wait_time
        )
        exit()


def main(args):
    test_func()
    web_page = args.get("web_page")
    token = args.get("token")
    refresh_ele = args.get("refresh_ele")
    drag_ele = args.get("drag_ele")
    slider_ele = args.get("slider_ele")
    retry_count = args.get("retry_count", 5)
    timeout = args.get("timeout", 60)
    offset = args.get("offset", 0)
    retry_wait_time = args.get("retry_wait_time", 3)

    handle_captcha(
        web_page, token, refresh_ele, drag_ele, slider_ele,
        retry_count, timeout, offset, retry_wait_time
    )
