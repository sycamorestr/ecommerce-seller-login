# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, win32
from .import package
from .package import variables as glv
import json
import os
import cv2
import numpy as np
from PIL import Image
import tempfile
import requests
import base64
import xbot_visual
import random

import sqlite3
import ast
if os.name == 'nt':
    from ctypes import windll
import ctypes

NANG = 1440          # angular bins (0.25 deg)
NRAD = 150           # radial bins (1 px)
SEAM = 100
CV_SIGN = 1          # cv2.getRotationMatrix2D(center, +angle) aligns disc


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
        win32.mouse_move(x, y, move_speed="instant")


def get_data_by_distance(distance, one=True):
    db_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if distance <= 50:
        di = 50
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 50")
    elif 50 < distance < 150:
        di = 100
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 100")
    elif 150 <= distance < 200:
        di = 150
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 150")
    else:
        di = 200
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 200")

    rows = cursor.fetchall()

    if one:
        random_index = random.randint(0, len(rows) - 1)

        data = json.loads(rows[random_index][2])
        result = ast.literal_eval(rows[random_index][2])
        for i in range(len(result)):
            result[i][0] = result[i][0] * distance / di
        result[-1][0] = distance
        result = json.dumps(result)
        return json.loads(result)
    return [json.loads(row[2]) for row in rows]


def _get_image_node_from_element(element):
    """获取当前块对应的 img 节点，便于读取 style 中的旋转角度。"""
    if element is None:
        return None

    try:
        src = element.get_attribute("src")
        if src:
            return element
    except Exception:
        pass

    try:
        return element.find_by_xpath(".//img[@src]")
    except Exception:
        return None

def drag_gen(drag_ele:xbot.web.WebElement, distance:int):
    mouse_pos_path = get_data_by_distance(distance)
    xbot.win32.manual_motion_on()

    x, y, width, height = drag_ele.get_bounding()
    point_x = int(x + width / 2)
    point_y = int(y + height / 2)
    xbot.win32.mouse_move(point_x, point_y)
    win32.mouse_click(button="left", click_type="down")

    for offset_x, offset_y, t in mouse_pos_path:
        xPoint = point_x + int(offset_x) 
        yPoint = point_y + int(offset_y)
        _moveTo(xPoint, yPoint)
        sleep(t/2000)

    sleep(1)
    
    win32.mouse_click(button="left", click_type="up")
    xbot.win32.manual_motion_off()    

def _capture_picture_images(web_page, picture_elements):
    """支持 src 为 http URL 或 data:image;base64。"""
    images = []

    with tempfile.TemporaryDirectory() as group_folder:
        for i, element in enumerate(picture_elements, 1):
            image = None
            src = None

            try:
                src = element.get_attribute("src")
            except Exception:
                src = None

            if src:
                # print("  图片%s SRC: %s" % (i, src[:120]))

                try:
                    if src.startswith("data:image"):
                        # data:image/png;base64,xxxx
                        header, b64_data = src.split(",", 1)
                        img_bytes = base64.b64decode(b64_data)

                        img_path = os.path.join(group_folder, "img_%s.png" % i)
                        with open(img_path, "wb") as f:
                            f.write(img_bytes)

                        # print("  已从 base64 保存: %s" % img_path)
                        image = load(img_path)

                    else:
                        # 普通网络图片 URL
                        headers = {
                            "User-Agent": (
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36"
                            ),
                            "Referer": web_page.url if getattr(web_page, "url", "") else "",
                        }

                        resp = requests.get(src, headers=headers, timeout=10)
                        if resp.status_code == 200:
                            img_path = os.path.join(group_folder, "img_%s.png" % i)
                            with open(img_path, "wb") as f:
                                f.write(resp.content)

                            # print("  已下载保存: %s" % img_path)
                            image = load(img_path)

                except Exception as result:
                    # print(result)
                    image = None

            if image is None:
                return None

            images.append(image)

    return images

def _resolve_element(web_page, element):
    """把传入的元素参数统一解析成真实可操作的页面元素。"""
    if hasattr(element, "get_bounding"):
        return element
    if web_page is None or not element:
        return None
    try:
        if isinstance(element, str):
            element = element.strip()
            if (
                element.startswith("/")
                or element.startswith("./")
                or element.startswith("(")
            ):
                return web_page.find_by_xpath(element,timeout=1)
            return web_page.find(element, timeout=1)
        return web_page.find(element, timeout=1)
    except Exception:
        return None


def load(path):
    return np.asarray(Image.open(path).convert("RGBA"))


def comp_white(rgba):
    rgb = rgba[:, :, :3].astype(np.float32)
    alpha = rgba[:, :, 3:4] / 255.0
    return (rgb * alpha + 255 * (1 - alpha)).astype(np.uint8)


def center_of(rgba):
    mask = (rgba[:, :, 3] > 128).astype(np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("No alpha contour found in image")
    contour = max(contours, key=cv2.contourArea)
    (x, y), _ = cv2.minEnclosingCircle(contour)
    return (float(x), float(y))


def to_polar(rgba, center):
    comp = comp_white(rgba)
    return cv2.warpPolar(
        comp,
        (NRAD, NANG),
        center,
        NRAD,
        cv2.WARP_POLAR_LINEAR + cv2.INTER_LINEAR,
    )


def high_pass(values, kernel):
    pad = np.concatenate([values[-kernel:], values, values[:kernel]], 0)
    cumulative = np.cumsum(pad, 0)
    moving_avg = (cumulative[2 * kernel:] - cumulative[:-2 * kernel]) / (2 * kernel)
    return values - moving_avg[: values.shape[0]]


def hue_feat(polar, r0, r1):
    segment = polar[:, r0:r1, :]
    hsv = cv2.cvtColor(segment, cv2.COLOR_RGB2HSV).astype(np.float32)
    hue = hsv[:, :, 0] / 180 * 2 * np.pi
    saturation = hsv[:, :, 1] / 255.0
    fx = (np.cos(hue) * saturation).mean(1)
    fy = (np.sin(hue) * saturation).mean(1)
    return np.stack([fx, fy], 1)


def edge_feat(polar, r0, r1):
    segment = polar[:, r0:r1, :]
    value = cv2.cvtColor(segment, cv2.COLOR_RGB2HSV).astype(np.float32)[:, :, 2].mean(1) / 255.0
    return high_pass(value, NANG // 36)[:, None]


def circular_corr(a, b):
    """Circular cross-correlation curve; high c[m] means a[p] matches b[p-m]."""
    a_norm = a - a.mean(0)
    b_norm = b - b.mean(0)
    a_norm /= np.linalg.norm(a_norm) + 1e-8
    b_norm /= np.linalg.norm(b_norm) + 1e-8
    curve = np.zeros(NANG)
    for channel in range(a.shape[1]):
        curve += np.fft.irfft(
            np.fft.rfft(a_norm[:, channel]) * np.conj(np.fft.rfft(b_norm[:, channel])),
            n=NANG,
        )
    return curve


def znorm(curve):
    return (curve - curve.mean()) / (curve.std() + 1e-8)


def argmax(curve):
    return int(np.argmax(curve))


def circdiff(a, b):
    return abs(((a - b + NANG // 2) % NANG) - NANG // 2) / NANG * 360

def solve(web_page: xbot.web.WebBrowser, inner_ele_, out_ele_, drag_ele_, slider_ele_, retry_time):
    """
    inner_ele:  内圈元素
    out_ele:    外圈元素
    drag_ele:   滑块元素
    slider_ele: 滑动条元素

    页面旋转逻辑：
    内圈顺时针：+ angle / 2
    外圈逆时针：- angle / 2
    """
    if not retry_time:
        retry_time = 1

    retry_time = int(retry_time)

    for _ in range(retry_time):
        inner_ele = _resolve_element(web_page, inner_ele_)
        out_ele = _resolve_element(web_page, out_ele_)
        drag_ele = _resolve_element(web_page, drag_ele_)
        slider_ele = _resolve_element(web_page, slider_ele_)

        inner_img_ele = _get_image_node_from_element(inner_ele)
        out_img_ele = _get_image_node_from_element(out_ele)

        images = _capture_picture_images(web_page, [inner_img_ele, out_img_ele])
        if not images or len(images) != 2:
            raise ValueError("获取内圈/外圈图片失败")

        inner, out = images

        center_inner = center_of(inner)
        center_out = center_of(out)

        polar_inner = to_polar(inner, center_inner)
        polar_out = to_polar(out, center_out)

        curve_inner = znorm(
            circular_corr(
                hue_feat(polar_inner, 84, 91),
                hue_feat(polar_out, 103, 110),
            )
        )
        curve_outer = znorm(
            circular_corr(
                hue_feat(polar_inner, 91, 98),
                hue_feat(polar_out, 110, 117),
            )
        )
        curve = curve_inner + curve_outer

        shift = argmax(curve)
        y0, y1, y2 = curve[(shift - 1) % NANG], curve[shift], curve[(shift + 1) % NANG]
        denom = y0 - 2 * y1 + y2
        sub = float(np.clip(0.5 * (y0 - y2) / denom, -1, 1)) if denom != 0 else 0.0
        shift_ref = shift + sub

        window = NANG // 45
        mask = np.ones(NANG, bool)
        for offset in range(-window, window + 1):
            mask[(shift + offset) % NANG] = False

        prom = float((curve[shift] - curve[mask].mean()) / (curve[mask].std() + 1e-8))
        agree = circdiff(argmax(curve_inner), argmax(curve_outer))

        # 两张图之间需要补偿的相对角度
        angle = shift_ref / NANG * 360.0

        # 获取 slider 元素的长度信息
        slider_bounding = slider_ele.get_bounding()
        width = slider_bounding[2]
        x, y, width_other, height_other = drag_ele.get_bounding()

        # 计算移动的距离
        distance = int(width * (360 - angle) / 360) - width_other / 2
        drag_gen(drag_ele, distance)
        sleep(2)
        try:
            _resolve_element(web_page, inner_ele_)
        except:
            break

        
def confidence(prom, agree_deg):
    if prom >= 6 and agree_deg <= 4:
        return "high"
    if prom >= 4.5 and agree_deg <= 10:
        return "med"
    return "low"

def rotate_disc(bg_white, center, angle):
    matrix = cv2.getRotationMatrix2D(center, CV_SIGN * angle, 1.0)
    return cv2.warpAffine(bg_white, matrix, (300, 300), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))

def render_seam(result):
    shift = result["shift"]
    polar_bg = result["pbg"]
    polar_block = result["pbk"]
    disc = np.roll(polar_bg[:, 78:99, :], -shift, 0)
    ring = polar_block[:, 101:122, :]
    gap = np.zeros((NANG, 3, 3), np.uint8)
    strip = np.concatenate([disc, gap, ring], 1).astype(np.uint8)
    img = np.transpose(strip, (1, 0, 2))
    return cv2.resize(img, (720, img.shape[0] * 3), interpolation=cv2.INTER_NEAREST)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main(args):
    web_page = args.get("web_page")
    inner_ele = args.get("inner_ele")
    out_ele = args.get("out_ele")
    drag_ele = args.get("drag_ele")
    slider_ele = args.get("slider_ele")
    retry_time = args.get("retry_time")
    solve(web_page, inner_ele, out_ele, drag_ele, slider_ele, retry_time)


