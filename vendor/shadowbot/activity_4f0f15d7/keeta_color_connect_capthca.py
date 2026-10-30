"""影刀模块：读取元素 style 背景图片和英文颜色提示，拖拽连接两个同色圆点。"""

import base64
import ctypes
import math
import os
import re
from pathlib import Path

import cv2
import numpy as np
from xbot import print, sleep, web, win32
from xbot.web.element import WebElement
from xbot.selector import Selector

# OpenCV uint8 HSV: H=0..179, S/V=0..255. Calibrated on 图片/1..20.png.
HSV_RANGES = {
    "red": [((0, 80, 80), (7, 255, 255)), ((170, 80, 80), (179, 255, 255))],
    "orange": [((8, 80, 210), (20, 255, 255))],
    "yellow": [((21, 80, 80), (38, 255, 255))],
    "green": [((39, 80, 80), (85, 255, 255))],
    "blue": [((95, 80, 80), (124, 255, 255))],
    "purple": [((125, 80, 80), (159, 255, 255))],
    "brown": [((8, 80, 80), (20, 255, 209))],
}


def read_image(path):
    """Read BGR pixels, including from Windows paths with Chinese characters."""
    image = cv2.imdecode(np.fromfile(Path(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot decode image: {path}")
    return image


def detect_color_points(image):
    """Return {English color: [(x, y), ...]} for a path or uint8 BGR array.

    Coordinates are floating-point pixels in the original image. Each list is
    sorted by x then y. Missing colors have empty lists.
    """
    if isinstance(image, (str, Path)):
        image = read_image(image)
    if (not isinstance(image, np.ndarray) or image.dtype != np.uint8
            or image.ndim != 3 or image.shape[2] != 3 or image.size == 0):
        raise ValueError("image must be a file path or a nonempty uint8 BGR image")

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    foreground = cv2.inRange(hsv, (0, 80, 80), (179, 255, 255))
    contours, _ = cv2.findContours(foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = {color: [] for color in HSV_RANGES}
    image_area = image.shape[0] * image.shape[1]

    # ponytail: isolated dots on a neutral background; touching/connected dots
    # need a distance transform or circle fitting if that input is introduced.
    for contour in contours:
        area = cv2.contourArea(contour)
        if not 0.0005 * image_area <= area <= 0.03 * image_area:
            continue
        x, y, width, height = cv2.boundingRect(contour)
        perimeter = cv2.arcLength(contour, True)
        if (not 0.8 <= width / height <= 1.25 or perimeter == 0
                or 4 * np.pi * area / perimeter**2 < 0.75):
            continue

        # Sample inside the shape, avoiding antialiased background edge pixels.
        inside = np.zeros((height, width), np.uint8)
        local_contour = contour - np.array([x, y], dtype=np.int32)
        cv2.drawContours(inside, [local_contour], -1, 255, cv2.FILLED)
        inside = cv2.erode(inside, np.ones((3, 3), np.uint8),
                           borderType=cv2.BORDER_CONSTANT, borderValue=0)
        pixels = hsv[y:y + height, x:x + width][inside > 0]
        if len(pixels) == 0:
            continue
        # Red straddles the hue seam: map 170..179 to -10..-1 before median.
        pixels = pixels.astype(np.float32)
        pixels[pixels[:, 0] >= 170, 0] -= 180
        median = np.median(pixels, axis=0)
        median[0] = round(float(median[0])) % 180
        for color, ranges in HSV_RANGES.items():
            if any(np.all(median >= low) and np.all(median <= high)
                   for low, high in ranges):
                moments = cv2.moments(contour)
                result[color].append((moments["m10"] / moments["m00"],
                                      moments["m01"] / moments["m00"]))
                break

    return {color: sorted(points) for color, points in result.items()}


def find_color_points(image, color):
    """Return exactly two (x, y) centers; raise ValueError otherwise."""
    if not isinstance(color, str) or color.strip().lower() not in HSV_RANGES:
        raise ValueError(f"Unsupported color. Choose from: {', '.join(HSV_RANGES)}")
    color = color.strip().lower()
    points = detect_color_points(image)[color]
    if len(points) != 2:
        raise ValueError(f"Expected 2 {color} dots, found {len(points)}: {points}")
    return points



def _read_style_image(element):
    """提取传入元素 inline style 中 background-image 的 Base64 图片。"""
    style = element.get_attribute('style') or ''
    declaration = re.search(
        r'(?:^|;)\s*background-image\s*:\s*(url\(.*?\))\s*(?:!important\s*)?(?:;|$)',
        style, flags=re.IGNORECASE | re.DOTALL)
    if declaration is None:
        raise ValueError('目标元素 style 中没有单张 background-image，请传入 sudoku-image 元素')
    match = re.fullmatch(
        r"""url\(\s*(?P<quote>['"]?)(?P<uri>data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=\s]+)(?P=quote)\s*\)""",
        declaration.group(1), flags=re.IGNORECASE)
    if match is None:
        raise ValueError('background-image 必须是 Base64 PNG/JPEG/WebP 图片')
    encoded = re.sub(r'\s+', '', match.group('uri').split(',', 1)[1])
    raw = base64.b64decode(encoded, validate=True)
    if not raw:
        raise ValueError('background-image 图片数据为空')
    image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError('background-image 图片解码失败')
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:
        alpha = image[:, :, 3:4].astype(np.float32) / 255
        image = np.rint(image[:, :, :3] * alpha + 255 * (1 - alpha)).astype(np.uint8)
    # ponytail: 当前题图完整铺满 sudoku-image；若 CSS 存在留白/裁切/平铺，
    # 需按 background-size、background-position 和 background-origin 换算。
    return image, [0, 0, 1, 1]



def _parse_color(text):
    """从提示语提取标准英文颜色词，忽略大小写，不匹配单词片段。"""
    colors = set(re.findall(r'\b(?:' + '|'.join(HSV_RANGES) + r')\b',
                            text or '', flags=re.IGNORECASE | re.ASCII))
    colors = {color.lower() for color in colors}
    if len(colors) != 1:
        raise ValueError(f'提示词应包含唯一一种支持的英文颜色，实际读到：{text!r}')
    return colors.pop()


def get_ppi():
    """沿用参考 utils：启用 DPI 感知，返回 96 / 实际 DPI。"""
    if os.name != 'nt':
        return 1.0
    user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
    user32.SetProcessDPIAware()
    # HDC 是指针，显式声明以兼容 64 位影刀 Python。
    user32.GetDC.argtypes = (ctypes.c_void_p,)
    user32.GetDC.restype = ctypes.c_void_p
    user32.ReleaseDC.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
    gdi32.GetDeviceCaps.argtypes = (ctypes.c_void_p, ctypes.c_int)
    dc = user32.GetDC(0)
    if not dc:
        raise RuntimeError('获取屏幕 DPI 失败：GetDC 返回空句柄')
    try:
        dpi = gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
    finally:
        user32.ReleaseDC(0, dc)
    if dpi <= 0:
        raise RuntimeError(f'获取屏幕 DPI 失败：{dpi}')
    return 96.0 / dpi


def _moveTo(x, y):
    """沿用参考 utils 的移动接口；在 get_ppi() 初始化 DPI 感知后使用。"""
    if os.name == 'nt':
        if not ctypes.windll.user32.SetCursorPos(int(x), int(y)):
            raise RuntimeError(f'SetCursorPos 移动失败：({x}, {y})')
    else:
        win32.mouse_move(int(x), int(y), move_speed='instant', delay_after=0)


def _screen_points(points, shape, bounds, content, ppi=None, logical_size=None):
    """把原图像素按目标元素的实际屏幕矩形换算为物理屏幕坐标。

    ``bounds`` 来自 ``get_bounding(to96dpi=False)``，所以已经是给
    ``SetCursorPos`` 使用的坐标。``logical_size`` 只用于校验/日志，不能再
    用它除以 DPI，否则 150% 缩放会被重复处理。
    """
    height, width = shape[:2]
    x, y, displayed_width, displayed_height = bounds
    left, top, fraction_width, fraction_height = content
    if logical_size is None:
        logical_size = (displayed_width, displayed_height)
    if (not all(math.isfinite(v) for v in (*bounds, *content, *logical_size))
            or min(displayed_width, displayed_height, fraction_width, fraction_height,
                   logical_size[0], logical_size[1]) <= 0):
        raise ValueError('图片元素尺寸或 DPI 缩放值无效')
    return [(round(x + displayed_width * (left + px / width * fraction_width)),
             round(y + displayed_height * (top + py / height * fraction_height)))
            for px, py in points]


def _drag(start, end):
    """参考 ease_drag：开启模拟 → 起点 → 按下 → 连续移动 → 松开 → 关闭模拟。"""
    if start == end:
        raise ValueError('两个圆心的屏幕坐标相同，无法拖动')
    win32.manual_motion_on(
        motion_move=True, motion_click=True, motion_delay=True,
        min_time=0.1, max_time=0.5,
    )
    try:
        _moveTo(*start)
        sleep(0.1)
        try:
            win32.mouse_click(button='left', click_type='down', delay_after=0)
            sleep(0.1)
            # print(f'已执行左键按下，开始从 {start} 移动到 {end}')
            # 两个方向都插值，兼容水平、竖直和斜向连线，最后一步精确落在终点。
            distance = math.hypot(end[0] - start[0], end[1] - start[1])
            steps = max(20, math.ceil(distance / 4))
            for step in range(1, steps + 1):
                ratio = step / steps
                _moveTo(round(start[0] + (end[0] - start[0]) * ratio),
                        round(start[1] + (end[1] - start[1]) * ratio))
                sleep(0.02)
            sleep(0.3)
            # print(f'已移动到终点 {end}，准备松开左键')
        finally:
            win32.mouse_click(button='left', click_type='up', delay_after=0)
    finally:
        win32.manual_motion_off()


def handle_color_captcha(web_page, target_ele, color_hint_ele, retry_count=5, wait_time=2):
    """连接提示颜色的两个点，目标图片元素消失/隐藏后返回识别结果。

    web_page: 流程传入的 xbot 网页对象。
    target_ele: 含 background-image 的图片元素名称、Selector 或 WebElement。
    color_hint_ele: 英文颜色提示文本的元素库名称、Selector 或 WebElement。
    retry_count: 最大尝试次数（包含首次），正整数。
    wait_time: 每次读取前等待图片加载的秒数，非负数。
    选择器查找及完成判断统一使用传入的 web_page。
    """
    if isinstance(retry_count, bool) or not re.fullmatch(r'[1-9]\d*', str(retry_count)):
        raise ValueError('重试次数必须是正整数（包含首次尝试）')
    retry_count = int(retry_count)
    if isinstance(wait_time, bool):
        raise ValueError('等待图片加载时间必须是非负秒数')
    wait_time = float(wait_time)
    if not math.isfinite(wait_time) or wait_time < 0:
        raise ValueError('等待图片加载时间必须是非负秒数')
    if target_ele is None or color_hint_ele is None:
        raise ValueError('目标元素和目标颜色提示词元素不能为空')

    if web_page is None:
        raise ValueError('web_page 网页对象不能为空')
    last_error = None
    attempted_drag = False
    result = None
    for attempt in range(1, retry_count + 1):
        try:
            sleep(wait_time)
            # 前一次拖拽的验证可能延迟完成，不把首次缺失元素算作成功。
            if attempted_drag and not web_page.is_element_displayed(target_ele):
                return result
            target = target_ele if isinstance(target_ele, WebElement) else web_page.find(target_ele)
            hint = color_hint_ele if isinstance(color_hint_ele, WebElement) else web_page.find(color_hint_ele)
            target.execute_javascript("""function(element, args) {
                element.scrollIntoView({block: 'center', inline: 'center', behavior: 'instant'});
            }""")
            color = _parse_color(hint.get_text())
            image, content = _read_style_image(target)
            points = find_color_points(image, color)
            # 先初始化 DPI 感知，再取元素矩形；与参考代码的 get_ppi/_moveTo 配套。
            ppi = get_ppi()
            bounds = target.get_bounding(to96dpi=False, relative_to='screen')
            logical_size = target.get_bounding(to96dpi=True, relative_to='screen')[2:4]
            screen_points = _screen_points(points, image.shape, bounds, content, ppi, logical_size)
            physical_scale = bounds[2] / logical_size[0]
            # print(f'系统缩放（由元素矩形推算）：{physical_scale:.0%}，DPI API比例：{1 / ppi:.0%}，物理矩形：{bounds}，96 DPI 显示尺寸：{logical_size}')
            print(f'目标颜色：{color}，原图圆心：{points}，物理屏幕拖动：{screen_points[0]} → {screen_points[1]}')
            _drag(*screen_points)
            attempted_drag = True
            result = {'color': color, 'image_points': points,
                      'screen_points': screen_points, 'attempt': attempt}
            sleep(2.5)
            # 需根据该页面的成功标记修改此判断，不能仅凭鼠标动作宣称通过。
            if not web_page.is_element_displayed(target_ele):
                return result
            last_error = RuntimeError('拖拽后目标图片元素仍可见，未确认完成')
        except Exception as exc:
            last_error = exc
        print(f'图片连线第 {attempt}/{retry_count} 次尝试未完成：{last_error}')
    raise RuntimeError(f'图片连线失败，已尝试 {retry_count} 次：{last_error}') from last_error


def test_func():
    """影刀内独立调试：填写两个真实 XPath 后运行此模块。"""
    if 'xbot_extensions' in __file__:
        return

    # 填写实际页面 XPath；iframe 多段路径使用 >> 分隔，与参考文件一致。
    target_xpath = '//div[@class="sudoku-image"]'  # 含背景图的元素
    color_hint_xpath = '//div[@class="sudoku-title "]'   # 例如包含 “Connect the red dots” 的提示文字元素
    retry_count = 5
    wait_time = 2
    if not target_xpath.strip() or not color_hint_xpath.strip():
        raise ValueError('请先在 test_func() 中填写 target_xpath 和 color_hint_xpath')

    def select_ele(xpath, name):
        return Selector({
            'id': name, 'name': name, 'type': 'simple',
            'xpath': {'enable': 'true', 'segments': [part.strip() for part in xpath.split('>>')]},
        })

    web_page = web.get_active('chrome')
    handle_color_captcha(
        web_page=web_page,
        target_ele=select_ele(target_xpath, 'color-image'),
        color_hint_ele=select_ele(color_hint_xpath, 'color-hint'),
        retry_count=retry_count,
        wait_time=wait_time,
    )
    exit()


def main(args):
    test_func()
    web_paga = args.get('web_page')
    target_ele = args.get('target_ele')
    color_hint_ele = args.get('color_hint_ele')
    retry_count = args.get('retry_count', 5)
    wait_time = args.get('wait_time', 3)
    handle_color_captcha(
        web_page=web_paga,
        target_ele=target_ele,
        color_hint_ele=color_hint_ele,
        retry_count=retry_count,
        wait_time=wait_time,
    )
