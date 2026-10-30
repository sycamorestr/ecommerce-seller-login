# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块


import xbot
from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv
import http
import json
import os
import base64
import time
import ast
import numpy as np
import re
from xbot.web.element import WebElement  # type: ignore
from xbot.selector import Selector
import platform
import sys
import cv2
from pathlib import Path

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


def get_xbot_activity_cache_folder(activity_code):
    """根据指令code 获取本地缓存目录, 不存在则创建"""
    if os.name == 'nt':  # Windows
        local_appdata_path = os.getenv('LOCALAPPDATA')
    else:  # Linux, macOS, etc.
        local_appdata_path = os.path.expanduser("~/.cache")
    
    xbot_app_cache_dir = os.path.join(local_appdata_path, "xbot_app", activity_code)
    if not os.path.exists(xbot_app_cache_dir):
        os.makedirs(xbot_app_cache_dir)
    return xbot_app_cache_dir


def imread_unicode(path, flags=cv2.IMREAD_COLOR):
    # 以二进制方式读取文件
    with open(path, 'rb') as f:
        data = f.read()
    img_array = np.frombuffer(data, np.uint8)
    return cv2.imdecode(img_array, flags)


def get_x(left_image: str, right_image: str) -> int:
    """通过 cv 计算验证码x轴的偏移距离"""
    left_img = imread_unicode(left_image, cv2.IMREAD_GRAYSCALE)
    right_img = imread_unicode(right_image, cv2.IMREAD_GRAYSCALE)

    bg_edge = cv2.Canny(right_img, 150, 152)
    tp_edge = cv2.Canny(left_img, 150, 152)

    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(res)

    return max_loc[0] + int(left_img.shape[1])


def detect_captcha_type(slider_path: str) -> str:
    """检测滑块图片类型，返回 'green' 或 'generic'"""
    img = cv2.imread(slider_path)
    if img is None:
        return 'generic'
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    thresholds = [
        ((45, 80, 120), (85, 255, 255)),
        ((40, 70, 100), (90, 255, 255)),
        ((35, 45, 70), (95, 255, 255)),
    ]
    best_ratio = 0.0
    for lower, upper in thresholds:
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        ratio = np.count_nonzero(mask) / mask.size
        if ratio > best_ratio:
            best_ratio = ratio
    return 'green' if best_ratio > 0.015 else 'generic'


def calculate_slider_distance(background_path: str, slider_path: str, debug: bool = False) -> float:
    """
    计算滑块到缺口的水平滑动距离。

    这批验证码的滑块带绿色描边，背景目标是黑色缺口。主流程会先从滑块
    提取绿色描边形成形状 mask，再在背景暗色区域中做同水平形状匹配。
    """

    def to_bgr(image: np.ndarray):
        if image.ndim == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        if image.shape[2] == 4:
            return image[:, :, :3].copy()
        return image[:, :, :3].copy()

    def normalize_score(score: np.ndarray):
        score = score.astype(np.float32)
        finite = np.isfinite(score)
        if not finite.any():
            return None

        min_val = float(score[finite].min())
        max_val = float(score[finite].max())
        if max_val - min_val < 1e-6:
            return None

        score = np.nan_to_num(score, nan=min_val, posinf=max_val, neginf=min_val)
        return (score - min_val) / (max_val - min_val)

    def subpixel_peak(score_map: np.ndarray, max_loc):
        x, y = max_loc
        x = float(x)
        y = float(y)

        xi, yi = max_loc
        if 0 < xi < score_map.shape[1] - 1:
            left = float(score_map[yi, xi - 1])
            center = float(score_map[yi, xi])
            right = float(score_map[yi, xi + 1])
            denom = left - 2 * center + right
            if abs(denom) > 1e-6:
                x += 0.5 * (left - right) / denom

        if 0 < yi < score_map.shape[0] - 1:
            top = float(score_map[yi - 1, xi])
            center = float(score_map[yi, xi])
            bottom = float(score_map[yi + 1, xi])
            denom = top - 2 * center + bottom
            if abs(denom) > 1e-6:
                y += 0.5 * (top - bottom) / denom

        return x, y

    def peak_margin(score_map: np.ndarray, max_loc, radius: int = 8):
        x, y = max_loc
        masked = score_map.copy()
        y0 = max(0, y - radius)
        y1 = min(masked.shape[0], y + radius + 1)
        x0 = max(0, x - radius)
        x1 = min(masked.shape[1], x + radius + 1)
        masked[y0:y1, x0:x1] = -np.inf
        second = float(np.max(masked)) if np.isfinite(masked).any() else 0.0
        return float(score_map[y, x]) - second

    def extract_slider_shape(slider_bgr: np.ndarray):
        hsv = cv2.cvtColor(slider_bgr, cv2.COLOR_BGR2HSV)
        thresholds = [
            ((45, 80, 120), (85, 255, 255)),
            ((40, 70, 100), (90, 255, 255)),
            ((35, 45, 70), (95, 255, 255)),
        ]
        best = None

        for lower, upper in thresholds:
            green = cv2.inRange(hsv, np.array(lower), np.array(upper))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            green = cv2.morphologyEx(green, cv2.MORPH_CLOSE, kernel, iterations=1)
            contours, _ = cv2.findContours(green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                x, y, w, h = cv2.boundingRect(contour)
                if area < 80 or w < 15 or h < 15:
                    continue
                if w > slider_bgr.shape[1] - 2 or h > slider_bgr.shape[0] - 2:
                    continue

                score = area + w * h * 0.05
                if best is None or score > best[0]:
                    best = (score, contour)

            if best is not None:
                break

        if best is None:
            return None

        shape_mask = np.zeros(slider_bgr.shape[:2], np.uint8)
        cv2.drawContours(shape_mask, [best[1]], -1, 255, -1)
        x, y, w, h = cv2.boundingRect(shape_mask)
        crop = shape_mask[y:y + h, x:x + w]
        return {
            "mask": shape_mask,
            "crop": crop,
            "bbox": (x, y, w, h),
        }

    def dark_mask(gray: np.ndarray, threshold: int):
        mask = (gray < threshold).astype(np.uint8) * 255
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        return mask

    def locate_by_shape(bg_bgr: np.ndarray, shape):
        bg_gray = cv2.cvtColor(bg_bgr, cv2.COLOR_BGR2GRAY)
        template = shape["crop"]
        offset_x, offset_y, template_w, template_h = shape["bbox"]

        if template_h > bg_gray.shape[0] or template_w > bg_gray.shape[1]:
            return None

        best = None
        y_radius = max(6, min(10, template_h // 4))
        thresholds = range(50, 131, 10)

        for threshold in thresholds:
            candidate_mask = dark_mask(bg_gray, threshold)
            score_map = cv2.matchTemplate(candidate_mask, template, cv2.TM_CCOEFF_NORMED)
            score_map = np.nan_to_num(score_map, nan=-1.0, posinf=-1.0, neginf=-1.0)

            y0 = max(0, offset_y - y_radius)
            y1 = min(score_map.shape[0], offset_y + y_radius + 1)
            band_score = np.full_like(score_map, -np.inf, dtype=np.float32)
            band_score[y0:y1, :] = score_map[y0:y1, :]

            _, score, _, loc = cv2.minMaxLoc(band_score)
            if best is None or score > best["score"]:
                x, y = subpixel_peak(score_map, loc)
                best = {
                    "method": "shape",
                    "x": x - offset_x,
                    "y": y - offset_y,
                    "match_x": x,
                    "match_y": y,
                    "score": float(score),
                    "margin": peak_margin(score_map, loc),
                    "threshold": threshold,
                    "band": (y0, y1),
                    "bbox": shape["bbox"],
                }

        if best is None or best["score"] < 0.35:
            return None
        return best

    def edge_image(gray: np.ndarray):
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        median = float(np.median(blurred))
        lower = int(max(20, 0.66 * median))
        upper = int(min(220, 1.33 * median))
        if upper <= lower:
            upper = lower + 40
        return cv2.Canny(blurred, lower, upper)

    def gradient_image(gray: np.ndarray):
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = cv2.magnitude(grad_x, grad_y)
        return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    def locate_by_texture(bg_bgr: np.ndarray, slider_bgr: np.ndarray):
        bg_gray = cv2.cvtColor(bg_bgr, cv2.COLOR_BGR2GRAY)
        slider_gray = cv2.cvtColor(slider_bgr, cv2.COLOR_BGR2GRAY)
        bh, bw = bg_gray.shape
        sh, sw = slider_gray.shape
        if sh > bh or sw > bw:
            return None

        variants = [
            (
                0.45,
                cv2.GaussianBlur(bg_gray, (3, 3), 0),
                cv2.GaussianBlur(slider_gray, (3, 3), 0),
            ),
            (0.35, edge_image(bg_gray), edge_image(slider_gray)),
            (0.20, gradient_image(bg_gray), gradient_image(slider_gray)),
        ]

        score_map = None
        total_weight = 0.0
        for weight, source, template in variants:
            if cv2.countNonZero(template) < 8:
                continue
            raw = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
            normalized = normalize_score(raw)
            if normalized is None:
                continue
            score_map = normalized * weight if score_map is None else score_map + normalized * weight
            total_weight += weight

        if score_map is None or total_weight == 0:
            return None

        score_map = score_map / total_weight
        row_scores = score_map.max(axis=1).astype(np.float32)
        if row_scores.size >= 5:
            row_scores = cv2.GaussianBlur(row_scores.reshape(-1, 1), (1, 5), 0).ravel()
        level_y = int(np.argmax(row_scores))
        band_radius = max(3, min(12, sh // 6))
        y0 = max(0, level_y - band_radius)
        y1 = min(score_map.shape[0], level_y + band_radius + 1)

        band_score = np.full_like(score_map, -np.inf, dtype=np.float32)
        band_score[y0:y1, :] = score_map[y0:y1, :]
        _, score, _, loc = cv2.minMaxLoc(band_score)
        x, y = subpixel_peak(score_map, loc)
        return {
            "method": "texture",
            "x": x,
            "y": y,
            "match_x": x,
            "match_y": y,
            "score": float(score),
            "margin": peak_margin(score_map, loc),
            "threshold": None,
            "band": (y0, y1),
            "bbox": (0, 0, sw, sh),
        }

    def write_debug_image(bg_bgr: np.ndarray, result):
        debug_img = bg_bgr.copy()
        x = int(round(result["x"]))
        y = int(round(result["y"]))
        match_x = int(round(result["match_x"]))
        match_y = int(round(result["match_y"]))
        _, _, w, h = result["bbox"]
        band_y0, band_y1 = result["band"]

        overlay = debug_img.copy()
        cv2.rectangle(overlay, (0, band_y0), (debug_img.shape[1] - 1, band_y1 - 1), (64, 160, 255), -1)
        debug_img = cv2.addWeighted(overlay, 0.14, debug_img, 0.86, 0)
        cv2.rectangle(debug_img, (match_x, match_y), (match_x + w, match_y + h), (0, 255, 255), 1)
        cv2.rectangle(debug_img, (x, y), (x + slider_bgr.shape[1], y + slider_bgr.shape[0]), (0, 255, 0), 1)
        center_y = max(0, min(debug_img.shape[0] - 1, y + slider_bgr.shape[0] // 2))
        cv2.line(debug_img, (0, center_y), (x, center_y), (0, 0, 255), 2)
        cv2.circle(debug_img, (x, center_y), 4, (255, 0, 0), -1)

        label = f"{result['method']} x={result['x']:.1f} s={result['score']:.2f}"
        if result["threshold"] is not None:
            label += f" t={result['threshold']}"
        cv2.putText(debug_img, label, (2, debug_img.shape[0] - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1, cv2.LINE_AA)

        bg_path = Path(background_path)
        debug_path = bg_path.with_name(f"debug_{bg_path.name}")
        cv2.imwrite(str(debug_path), debug_img)
        return str(debug_path)

    bg_raw = cv2.imread(background_path, cv2.IMREAD_UNCHANGED)
    slider_raw = cv2.imread(slider_path, cv2.IMREAD_UNCHANGED)

    if bg_raw is None:
        raise FileNotFoundError(f"背景图未找到: {background_path}")
    if slider_raw is None:
        raise FileNotFoundError(f"滑块图未找到: {slider_path}")

    bg_bgr = to_bgr(bg_raw)
    slider_bgr = to_bgr(slider_raw)

    shape = extract_slider_shape(slider_bgr)
    result = locate_by_shape(bg_bgr, shape) if shape is not None else None
    if result is None:
        result = locate_by_texture(bg_bgr, slider_bgr)
    if result is None:
        raise RuntimeError("无法定位滑块缺口：没有得到有效匹配结果")

    distance = float(result["x"])

    if debug:
        debug_path = write_debug_image(bg_bgr, result)
        basename = Path(background_path).name
        print(
            f"[调试] {basename}: x={distance:.2f}px, method={result['method']}, "
            f"match=({result['match_x']:.2f}, {result['match_y']:.2f}), "
            f"score={result['score']:.3f}, margin={result['margin']:.3f}, debug={debug_path}"
        )

    return distance


def get_ppi():
    """获取屏幕缩放比例（跨平台）"""
    # print(os.name)
    if os.name == 'nt':  # Win
        from ctypes import windll
        """获取屏幕的缩放"""
        LOGPIXELSX = 88
        LOGPIXELSY = 90
        user32 = windll.user32
        user32.SetProcessDPIAware()
        dc = user32.GetDC(0)
        pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
        user32.ReleaseDC(0, dc)
        res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
        return res[1] / res[0]
    else:  # Linux
        res = 1 / float(os.environ['QT_SCREEN_SCALE_FACTORS'])
        return res
        
def drag(drag_ele: WebElement, distance: int, target_ele: Selector, web_page: xbot.web.WebBrowser):
    x, y, width, height = drag_ele.get_bounding()
    drag_start_x = x + width / 2
    drag_start_y = y + height / 2
    drag_ele.hover()
    move_speed = "middle"
    win32.manual_motion_on(
        motion_move=True,
        motion_click=True,
        motion_delay=True,
        min_time=0.1,
        max_time=0.5,
    )
    win32.mouse_move(drag_start_x, drag_start_y, move_speed=move_speed, delay_after=1 / 2000)

    # 获取缺口元素初始位置
    x_1, y_1, width_1, height_1 = web_page.find(target_ele).get_bounding()
    gap_start_x = x_1 + width_1 / 2
    print(f'缺口初始位置 target_distance: {gap_start_x}')
    print(f'目标移动距离 distance: {distance}')

    max_iterations = 30  # 最大拖动次数，防止死循环
    timeout_seconds = 10
    tolerance = 2
    start_time = time.time()
    iteration = 0
    last_gap_moved = 0.0
    stagnant_count = 0

    # 记录已知的"拖动量 -> 缺口移动量"区间，用于后续插值/二分逼近
    lower_drag_total = 0.0
    lower_gap_moved = 0.0
    upper_drag_total = None
    upper_gap_moved = None

    # 第一次先拖一小段，再根据测量结果校正
    next_drag_total = max(6.0, min(float(distance), max(12.0, float(distance) * 0.5)))

    try:
        win32.mouse_click(button="left", click_type="down", delay_after=0)

        current_mouse_x = drag_start_x
        current_mouse_y = drag_start_y

        while iteration < max_iterations:
            iteration += 1

            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                print(f'超时退出：已运行 {elapsed_time:.2f} 秒，超过 {timeout_seconds} 秒限制')
                break

            current_drag_total = current_mouse_x - drag_start_x
            desired_delta = next_drag_total - current_drag_total

            if abs(desired_delta) < 0.5:
                desired_delta = 1.0 if distance > last_gap_moved else -1.0

            # 每次只拖一小段，允许回拉，回拉步长略小一些
            if desired_delta > 0:
                step = max(1.0, min(16.0, desired_delta))
            else:
                step = -max(1.0, min(12.0, abs(desired_delta)))

            next_mouse_x = current_mouse_x + step
            print(f'第{iteration}次循环 - 当前累计拖动: {current_drag_total:.2f}, 本次步长: {step:.2f}, 计划累计拖动: {next_drag_total:.2f}')
            print(f'鼠标当前位置: {current_mouse_x:.2f}, 下一步目标位置: {next_mouse_x:.2f}')
            win32.mouse_move(next_mouse_x, current_mouse_y, move_speed=move_speed, delay_after=1 / 2000)
            current_mouse_x = next_mouse_x
            sleep(0.03)

            # 重新测量缺口元素移动距离
            x_2, y_2, width_2, height_2 = web_page.find(target_ele).get_bounding()
            gap_current_x = x_2 + width_2 / 2
            gap_moved = gap_current_x - gap_start_x
            error = distance - gap_moved
            current_drag_total = current_mouse_x - drag_start_x
            print(f'第{iteration}次测量 - 鼠标累计拖动: {current_drag_total:.2f}, 缺口已移动距离: {gap_moved:.2f}, 当前误差: {error:.2f}')

            if abs(error) <= tolerance:
                print('达到目标位置，退出循环')
                break

            # 更新停滞检测
            if abs(gap_moved - last_gap_moved) < 0.5:
                stagnant_count += 1
            else:
                stagnant_count = 0

            # 根据"鼠标累计拖动 -> 缺口移动距离"的测量结果维护上下边界
            if gap_moved < distance:
                lower_drag_total = current_drag_total
                lower_gap_moved = gap_moved
            else:
                upper_drag_total = current_drag_total
                upper_gap_moved = gap_moved

            # 有上下界时优先在区间内插值/二分；没有上下界时按当前测得比例估算
            if upper_drag_total is not None and upper_gap_moved is not None:
                gap_span = upper_gap_moved - lower_gap_moved
                drag_span = upper_drag_total - lower_drag_total
                if abs(gap_span) > 0.5 and abs(drag_span) > 0.5:
                    next_drag_total = lower_drag_total + (distance - lower_gap_moved) * drag_span / gap_span
                else:
                    next_drag_total = (lower_drag_total + upper_drag_total) / 2

                next_drag_total = max(lower_drag_total + 0.5, min(upper_drag_total - 0.5, next_drag_total))
            else:
                if abs(gap_moved) > 1:
                    drag_gap_ratio = current_drag_total / gap_moved
                else:
                    drag_gap_ratio = 1.0

                next_drag_total = current_drag_total + error * drag_gap_ratio * 0.9

            # 临近目标时进一步缩小调节量，避免刚过线又大幅回拉
            if abs(error) <= 10:
                delta = next_drag_total - current_drag_total
                delta = max(-3.0, min(3.0, delta))
                next_drag_total = current_drag_total + delta

            # 连续停滞时，按误差方向明确给出一个更大的鼠标修正
            if stagnant_count >= 2:
                next_drag_total = current_drag_total + (3.0 if error > 0 else -3.0)
                print(f'检测到位置停滞，强制微调到累计拖动: {next_drag_total:.2f}')

            next_drag_total = max(0.0, next_drag_total)
            last_gap_moved = gap_moved

        else:
            print(f'达到最大拖动次数 {max_iterations}，停止拖动')
    finally:
        sleep(1)
        win32.mouse_click(button="left", click_type="up")
        win32.manual_motion_off()


def handle_slider_captcha(
    web_page: xbot.web.WebBrowser,
    background_ele: str,
    slider_ele: str,
    drag_ele: str,
    offset: int
):
    """Handles slider CAPTCHA with auto-detection of captcha type."""
    cache_folder = get_xbot_activity_cache_folder("xbot_app")

    b_x, b_y, b_w, b_h = web_page.find(background_ele).get_bounding(to96dpi=False)
    s_x, s_y, s_w, s_h = web_page.find(slider_ele).get_bounding(to96dpi=False)

    # 截取滑块区域用于类型检测
    slider_path = os.path.join(cache_folder, "std_captcha_slider.png")
    xbot.win32.screenshot.save_screen_to_file(slider_path, "png", s_x, s_y, s_x + s_w, s_y + s_h)

    captcha_type = detect_captcha_type(slider_path)
    print(f'验证码类型: {captcha_type}')

    if captcha_type == 'green':
        # 绿色边框验证码：使用 HSV 形状匹配
        background_path = os.path.join(cache_folder, "std_captcha_bg.png")
        xbot.win32.screenshot.save_screen_to_file(background_path, "png", s_x + s_w, s_y, b_x + b_w, s_y + s_h)
        data = calculate_slider_distance(background_path, slider_path, debug=True)
        distance = abs(int(data))
        distance = distance + int(offset) + int(s_w)
        if os.name == "nt":
            distance = int(distance * get_ppi())
    else:
        # 通用验证码：使用 Canny 边缘检测
        left_img_path = os.path.join(cache_folder, "std_captcha_left.png")
        right_img_path = os.path.join(cache_folder, "std_captcha_right.png")
        xbot.win32.screenshot.save_screen_to_file(left_img_path, "png", b_x, b_y, b_x + s_w, b_y + b_h)
        xbot.win32.screenshot.save_screen_to_file(right_img_path, "png", s_x + s_w, b_y, b_x + b_w, b_y + b_h)
        distance = get_x(left_img_path, right_img_path)
        distance = int((distance + offset) * get_ppi())

    print(f'计算距离: {distance}')
    drag(web_page.find(drag_ele), distance, slider_ele, web_page)
    


def handle_captcha(web_page, captcha_drag_selector, captcha_slider_selector, captcha_background_selector, refresh_ele, offset, retry):
    """ 滑块走cv接口"""

    scale = get_ppi() # 获取屏幕缩放
    # 获取图片的缓存目录
    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    save_path = os.path.join(cache_folder, "zfb_client.png")

    click_captcha_count = 1 # 仅统计点选验证码的验证次数
    retry = int(retry)
    while 1:
        if click_captcha_count > retry:
            raise Exception("验证码处理失败")

        # 如果验证码元素不存在就退出循环
        if web_page.is_element_displayed(captcha_background_selector):
            handle_slider_captcha(web_page, captcha_background_selector, captcha_slider_selector, captcha_drag_selector, offset)
        else:
            print('验证码不存在或已成功')
            break
        
        if web_page.is_element_displayed(captcha_background_selector):
            click_captcha_count += 1
        else:
            break

        if refresh_ele:
            web_page.find(refresh_ele).click()
        sleep(2)
    
def test_handle_captcha():
    def select_ele(xpath, web_page):
        if "frame" in xpath:
                xpaths = xpath.split(">>")
                data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': xpaths}}
                selector = Selector(data)
                return selector
        else:
            data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': [xpath]}}
            selector = Selector(data)
            return selector
            
    if 'xbot_extensions' in __file__:
        return
    
    web_page = web.get_active('auto')
    # 鲸灵
    # background_ele = select_ele(web_page=web_page, xpath='//div[@id="dx_captcha_basic_bg_1"]')
    # target_ele =  select_ele(web_page=web_page, xpath='//div[@id="dx_captcha_basic_sub-slider_1"]')
    # drag_ele = select_ele(web_page=web_page, xpath='//div[@id="dx_captcha_basic_slider_1"]')
    # refresh_ele = select_ele(web_page=web_page, xpath='//img[@id="dx_captcha_basic_btn-refresh_1"]')

    # 浦发
    background_ele = select_ele(web_page=web_page, xpath='//div[@class="geetest_slicebg geetest_absolute"]/canvas[1]')
    target_ele =  select_ele(web_page=web_page, xpath='//div[@id="dx_captcha_basic_sub-slider_1"]')
    drag_ele = select_ele(web_page=web_page, xpath='//div[@id="dx_captcha_basic_slider_1"]')
    refresh_ele = select_ele(web_page=web_page, xpath='//img[@id="dx_captcha_basic_btn-refresh_1"]')

    retry = 3
    offset = 0

    handle_captcha(web_page, drag_ele, target_ele, background_ele, refresh_ele, offset, retry)
    exit()

def main(args):
    # test_handle_captcha()
    drag_ele = args.get('drag_ele')
    background_ele = args.get('background_ele')
    target_ele = args.get('target_ele')
    web_page = args.get('web_page')
    retry = args.get('retry')
    refresh_ele = args.get('refresh_ele', '')
    offset = args.get('offset')

    handle_captcha(web_page, drag_ele, target_ele, background_ele, refresh_ele, offset, retry)
