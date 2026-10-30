# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import os
import sys
import platform
import base64
import json
import math
import random
import sqlite3
import ast
import xbot
import xbot_visual
from xbot import sleep, win32, web, print
from xbot.web.element import WebElement
from xbot.selector import Selector
from .package import variables as glv
import numpy as np
import cv2
from .utils import get_ppi, _moveTo

# Shopee 旋转拼图常量：滑块 dx 与拼图旋转角线性耦合
DEG_PER_PX = 0.9

# 使用platform模块来判断架构类型
machine = platform.machine().lower()
if 'x86_64' in machine or 'amd64' in machine:
    arch = 'x64'
elif 'aarch64' in machine or 'arm64' in machine:
    arch = 'arm64'
else:
    arch = 'x64'

# 设置PYTHONPATH
base_path = os.path.dirname(os.path.dirname(os.environ.get('PYTHONPATH', os.path.abspath(__file__))))
cv_engine_path = os.path.join(base_path, f"support_{arch}/cv-engine/site-packages")
if os.path.exists(cv_engine_path):
    sys.path.append(cv_engine_path)


def decode_data_uri(data_uri: str):
    """将 base64 data URI 解码为 OpenCV 图像（保留 alpha 通道）"""
    _, encoded = data_uri.split(",", 1)
    raw = base64.b64decode(encoded)
    return cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)


def _get_image_src(web_page: xbot.web.WebBrowser, ele):
    """提取图片 data URI，优先 src 属性，失败则从 canvas 截取"""
    el = web_page.find(ele)
    src = el.get_attribute("src")
    if src:
        return src
    # src 不存在，尝试 canvas toDataURL
    w = el.get_attribute("width")
    h = el.get_attribute("height")
    if not w or not h:
        return None
    return web_page.execute_javascript(
        "function(element, args) {"
        "  var d = JSON.parse(args);"
        "  var c = document.querySelector('canvas[width=\"' + d[0] + '\"][height=\"' + d[1] + '\"]');"
        "  if (!c) return null;"
        "  return c.toDataURL('image/png');"
        "}",
        json.dumps([w, h])
    )


def get_captcha_images(web_page: xbot.web.WebBrowser, bg_ele, piece_ele):
    """提取验证码的背景图和拼图块（保留 alpha 通道）"""
    bg_src = _get_image_src(web_page, bg_ele)
    piece_src = _get_image_src(web_page, piece_ele)
    if not bg_src or not piece_src:
        return None, None
    bg = decode_data_uri(bg_src)
    piece = decode_data_uri(piece_src)
    return bg, piece


def detect_angle(bg: np.ndarray, piece: np.ndarray):
    """
    轮廓-暗度匹配，搜索最佳旋转角度。
    原理：缺口 = piece 轮廓在目标角度下被压暗的印记。
    在背景"暗度图"上滑动「旋转后的 piece 轮廓」模板，分数最高的角度即目标角度。
    返回 (theta, score)，theta 单位为度。
    """
    alpha = piece[:, :, 3] if piece.shape[2] == 4 else np.full(piece.shape[:2], 255, np.uint8)
    gray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
    dark = cv2.GaussianBlur((255 - gray).astype(np.float32), (3, 3), 0)
    H, W = gray.shape
    ph, pw = alpha.shape
    best = (0, -1.0)
    for theta in range(0, 205, 1):
        M = cv2.getRotationMatrix2D((pw / 2, ph / 2), -theta, 1.0)
        ra = cv2.warpAffine(alpha, M, (pw, ph), flags=cv2.INTER_NEAREST, borderValue=0)
        ys, xs = np.where(ra > 128)
        if len(xs) < 100:
            continue
        tmpl = (ra[ys.min():ys.max() + 1, xs.min():xs.max() + 1] > 128).astype(np.float32)
        th, tw = tmpl.shape
        if th >= H or tw >= W:
            continue
        res = cv2.matchTemplate(dark, tmpl, cv2.TM_CCOEFF_NORMED)
        res[~np.isfinite(res)] = -1
        _, mx, _, _ = cv2.minMaxLoc(res)
        if mx > best[1]:
            best = (theta, float(mx))
    return best


def _get_drag_path_by_distance(distance: int):
    """按目标距离从资源库读取一条人类拖拽轨迹。"""
    db_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="database.db")
    if distance <= 50:
        bucket = 50
    elif distance < 150:
        bucket = 100
    elif distance < 200:
        bucket = 150
    else:
        bucket = 200

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tracker WHERE distance = ?", (bucket,))
        rows = cursor.fetchall()

    if not rows:
        raise ValueError(f"database.db 中未找到距离 {bucket} 的轨迹数据")

    track = ast.literal_eval(random.choice(rows)[2])
    scale = float(distance) / float(bucket)
    result = []
    for offset_x, offset_y, duration in track:
        result.append([offset_x * scale, offset_y, duration])
    result[-1][0] = float(distance)
    return result


def ease_drag(web_page, drag_ele, target_dx):
    """使用资源库轨迹模拟人类拖拽。"""
    drag_element = web_page.find(drag_ele)
    x, y, width, height = drag_element.get_bounding(to96dpi=False)
    sx = int(x + width / 2)
    sy = int(y + height / 2)
    mouse_pos_path = _get_drag_path_by_distance(int(round(target_dx)))

    xbot.win32.manual_motion_on()
    _moveTo(sx, sy)
    sleep(0.1)
    win32.mouse_click(button="left", click_type="down", delay_after=0)

    try:
        for offset_x, offset_y, duration in mouse_pos_path:
            _moveTo(sx + int(offset_x), sy + int(offset_y))
            sleep(float(duration) / 2000)
        sleep(0.3)
    finally:
        win32.mouse_click(button="left", click_type="up")
        xbot.win32.manual_motion_off()

def handle_captcha(
    web_page: xbot.web.WebBrowser,
    drag_ele: str,
    bg_ele: str,
    piece_ele: str,
    retry_count: int = 5,
    offset: int = 0,
    refresh_ele: str = "",
    wait_time: int = 2
):
    """处理 Shopee 旋转拼图验证码"""
    for attempt_num in range(int(retry_count)):
        # 刷新验证码（首次也刷新以清除可能的错误状态）
        web_page.find(refresh_ele).click()
        sleep(wait_time)
        # 提取验证码图片
        bg, piece = get_captcha_images(web_page, bg_ele, piece_ele)
        if bg is None or piece is None:
            continue

        # 检测目标角度
        theta, score = detect_angle(bg, piece)
        target_dx = theta / DEG_PER_PX + float(offset)

        if score < 0.3:
            continue

        # 缩放距离（CSS像素 → 物理像素）
        # data URI 图片是 CSS 分辨率，target_dx 是 CSS 值
        # get_ppi() 返回 96/实际DPI，所以除以它得到物理值
        ppi = get_ppi()
        drag_distance = target_dx

        if os.name == "nt":
            drag_distance = int(drag_distance / ppi)
        else:
            drag_distance = int(drag_distance)

        # 执行拖拽
        ease_drag(web_page, drag_ele, drag_distance)
        sleep(2.5)

        # 检查验证码是否消失
        if web_page.is_element_displayed(drag_ele):
            _, _, w_val, h_val = web_page.find(drag_ele).get_bounding()
            if w_val == 0 and h_val == 0:
                return
        else:
            return

def test_func() -> None:
    if 'xbot_extensions' in __file__:
        return

    web_page = web.get_active('chrome')

    def select_ele(xpath):
        if "frame" in xpath:
            xpaths = xpath.split(">>")
            data = {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple',
                    'xpath': {'enable': 'true', 'segments': xpaths}}
            return Selector(data)
        else:
            data = {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple',
                    'xpath': {'enable': 'true', 'segments': [xpath]}}
            return Selector(data)

    # Shopee 三个元素 (drag_ele 同时用于拖拽和刷新按钮定位)
    drag_ele = select_ele(xpath='/html/body/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div[1]/div[2]/div[3]/div')
    bg_ele = select_ele(xpath='/html/body/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/canvas')
    piece_ele = select_ele(xpath='/html/body/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/canvas')
    retry_count = 5
    offset = 0
    refresh_ele = select_ele(xpath='/html/body/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div[2]/div[2]/button')
    handle_captcha(web_page, drag_ele, bg_ele, piece_ele, retry_count, offset, refresh_ele)
    exit()


def main(args):
    test_func()
    web_page = args.get("web_page")
    drag_ele = args.get("drag_ele")
    bg_ele = args.get("bg_ele")
    piece_ele = args.get("piece_ele")
    retry_count = args.get("retry_count", 5)
    offset = args.get("offset", 0)
    refresh_ele = args.get("refresh_ele", "")
    wait_time = args.get('wait_time', 2)
    handle_captcha(web_page, drag_ele, bg_ele, piece_ele, retry_count, offset, refresh_ele, wait_time)
