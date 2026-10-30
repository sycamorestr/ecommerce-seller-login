# 使用提醒:
# 1. xbot 包提供浏览器和鼠标自动化能力
# 2. 可视化流程中可通过“调用模块”执行 main(args)
# 3. 部署时把 captcha_vision.py 一并放入相同模块目录。
# 4. rotation_ele 可选：旋转容器选择器；不传则从 piece_ele 向上找旋转容器。

import base64
import json
import time

import cv2
import numpy as np
import xbot
from xbot import sleep, web, win32, print
from xbot.selector import Selector


MAX_TRIES = 10

JS_ROT = r"""
function(element, args) {
  if (!element || element.isConnected === false) throw new Error('Rotation element is missing');
  // The image may rotate itself, or sit inside a rotating wrapper.
  for (let d = element; d; d = d.parentElement) {
    const m = (d.style.transform || '').match(/rotate\(([-\d.]+)deg\)/);
    if (m) return m[1];
  }
  return '0';
}
"""

JS_STATE = """
function(element, args) {
  if (!element || element.isConnected === false || !element.parentElement)
    return JSON.stringify({present:false});
  const kr = element.getBoundingClientRect();
  const br = element.parentElement.getBoundingClientRect();
  return JSON.stringify({
    present:true,
    maxDx:Math.max(1, br.width - kr.width + 5)
  });
}
"""


def decode(data_uri, flags):
    return cv2.imdecode(
        np.frombuffer(base64.b64decode(data_uri.split(",", 1)[1]), np.uint8), flags
    )


def get_captcha_images(web_page, bg_ele, piece_ele):
    bg_src = web_page.find(bg_ele).get_attribute("src")
    piece_src = web_page.find(piece_ele).get_attribute("src")
    if not bg_src or not piece_src:
        return None, None
    return decode(bg_src, cv2.IMREAD_COLOR), decode(piece_src, cv2.IMREAD_UNCHANGED)


try:
    from .captcha_vision import detect_angle, rotate_mask, piece_mask, select_target
except ImportError:  # Direct script execution, outside an XBot package.
    from captcha_vision import detect_angle, rotate_mask, piece_mask, select_target


def current_rotation(rotation_element):
    return float(rotation_element.execute_javascript(JS_ROT, "[]"))


def fit_line(points):
    """最小二乘拟合 rotate = slope * dx + intercept。"""
    mx = sum(x for x, _ in points) / len(points)
    my = sum(y for _, y in points) / len(points)
    den = sum((x - mx) ** 2 for x, _ in points)
    slope = sum((x - mx) * (y - my) for x, y in points) / den
    return slope, my - slope * mx


def solve_drag(web_page, drag_ele, max_dx, scores, piece_ele, rotation_ele=None):
    """连续完成四点探测和目标拖动，到位后立即松手。"""
    x, y, width, height = web_page.find(drag_ele).get_bounding()
    # Resolve before pressing; reuse the element for every probe (no repeated find).
    rotation_element = web_page.find(rotation_ele if rotation_ele is not None else piece_ele)
    start_x, start_y = int(x + width / 2), int(y + height / 2)
    pressed = False
    diagnostic = None
    xbot.win32.manual_motion_on()
    try:
        win32.mouse_move(point_x=start_x, point_y=start_y, move_speed="instant", delay_after=0)
        win32.mouse_click(button="left", click_type="down", delay_after=0)
        pressed = True

        samples = [(0.0, current_rotation(rotation_element))]
        for dx in (6.0, 18.0, 36.0):
            win32.mouse_move(
                point_x=start_x + int(dx), point_y=start_y, move_speed="fast", delay_after=0
            )
            samples.append((dx, current_rotation(rotation_element)))
        slope, intercept = fit_line(samples)
        residual = max(abs(rotation - (slope * dx + intercept)) for dx, rotation in samples)
        if abs(slope) < 0.02 or residual > 1.0:
            diagnostic = f"stopped: invalid_calibration slope={slope:.6f}, residual={residual:.3f}, samples={samples}"
            return False

        best, reason = select_target(scores, slope, intercept, max_dx)
        if best is None:
            diagnostic = f"stopped: {reason}; slope={slope:.6f}, intercept={intercept:.2f}, max_dx={max_dx:.1f}"
            return False
        best_score, target, _ = best
        diagnostic = f"target: angle={target:.2f}, score={best_score:.3f}"

        dx = (target - intercept) / slope
        win32.mouse_move(
            point_x=start_x + int(round(dx)), point_y=start_y, move_speed="fast", delay_after=0
        )
        rotation = current_rotation(rotation_element)
        if abs(rotation - target) > 0.35:
            corrected = max(1, min(max_dx, dx + (target - rotation) / slope))
            if abs(corrected - dx) >= 1:
                dx = corrected
                win32.mouse_move(
                    point_x=start_x + int(round(dx)), point_y=start_y, move_speed="fast", delay_after=0
                )
                rotation = current_rotation(rotation_element)
        win32.mouse_click(button="left", click_type="up", delay_after=0)
        pressed = False
        return abs(rotation - target) <= 0.75
    finally:
        if pressed:
            win32.mouse_click(button="left", click_type="up", delay_after=0)
        xbot.win32.manual_motion_off()


def captcha_present(web_page, drag_ele):
    try:
        if not web_page.is_element_displayed(drag_ele):
            return False
        _, _, width, height = web_page.find(drag_ele).get_bounding()
        return width > 0 and height > 0
    except Exception:
        return False


def handle_captcha(
    web_page,
    drag_ele,
    bg_ele,
    piece_ele,
    refresh_ele,
    retry_count=MAX_TRIES,
    wait_time=1.5,
    rotation_ele=None,
):
    """处理天津平台旋转拼图验证码。"""
    for attempt in range(1, int(retry_count) + 1):
        if not captcha_present(web_page, drag_ele):
            print("验证码已消失（已通过或未弹出）")
            return True

        state = json.loads(web_page.find(drag_ele).execute_javascript(JS_STATE, "[]"))
        if not state["present"]:
            return True
        bg, piece = get_captcha_images(web_page, bg_ele, piece_ele)
        max_dx = state["maxDx"]
        # Filter using this attempt's measured slope, never a fixed nominal slope.
        started = time.perf_counter()
        scores = (detect_angle(bg, piece)
                  if bg is not None and piece is not None else None)
        print(f"attempt {attempt}/{retry_count}: recognition={(time.perf_counter()-started)*1000:.0f} ms")
        if scores:
            # print(f"top3: {[(round(score, 3), angle) for score, angle, _ in scores[:3]]}")
            if solve_drag(web_page, drag_ele, max_dx, scores, piece_ele, rotation_ele):
                sleep(2)
                if not captcha_present(web_page, drag_ele):
                    print("验证码通过")
                    return True

        if captcha_present(web_page, drag_ele):
            web_page.find(refresh_ele).click()
            sleep(float(wait_time))
    print("多次尝试未通过")
    return False


def self_check():
    mask = np.zeros((52, 64), np.uint8)
    cv2.rectangle(mask, (9, 8), (54, 44), 1, -1)
    cv2.circle(mask, (32, 8), 8, 1, -1)
    cv2.circle(mask, (9, 28), 7, 0, -1)
    cv2.circle(mask, (48, 44), 6, 1, -1)
    target = 23.4
    hole = rotate_mask(mask, target)
    gray = np.tile(np.linspace(140, 205, 220, dtype=np.uint8), (150, 1))
    y, x = 45, 90
    roi = gray[y:y + hole.shape[0], x:x + hole.shape[1]]
    roi[hole > 0] = np.maximum(roi[hole > 0], 75) - 70
    piece = np.zeros((*mask.shape, 4), np.uint8)
    piece[:, :, 3] = mask * 255
    best = detect_angle(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), piece)[0][1]
    assert abs(best - target) <= 0.5, (best, target)
    # print(f"self-check OK: angle={best:.1f}")


def select_ele(xpath):
    return Selector({
        "id": "xpath",
        "name": "xpath",
        "type": "simple",
        "xpath": {"enable": "true", "segments": [xpath]},
    })


def test_func():
    """仅供手动调用的固定页面示例；main(args) 不调用此函数。"""
    if "xbot_extensions" in __file__:
        return
    web_page = web.get_active("chrome")
    handle_captcha(
        web_page,
        select_ele('//*[@id="tianai-captcha-slider-move-btn"]'),
        select_ele('//*[@id="tianai-captcha-slider-bg-img"]'),
        select_ele('//*[@id="tianai-captcha-slider-move-img"]'),
        select_ele('//*[@id="tianai-captcha-slider-refresh-btn"]'),
    )
    # self_check()
    exit()


def main(args):
    """Use caller selectors; optional rotation_ele selects the rotating wrapper explicitly."""
    web_page = args.get("web_page")
    drag_ele = args.get("drag_ele")
    bg_ele = args.get("bg_ele")
    piece_ele = args.get("piece_ele")
    refresh_ele = args.get("refresh_ele")
    retry_count = args.get("retry_count", 5)
    wait_time = args.get("wait_time", 2)
    rotation_ele = args.get("rotation_ele")

    return handle_captcha(
        web_page,
        drag_ele,
        bg_ele,
        piece_ele,
        refresh_ele,
        retry_count,
        wait_time,
        rotation_ele,
    )
