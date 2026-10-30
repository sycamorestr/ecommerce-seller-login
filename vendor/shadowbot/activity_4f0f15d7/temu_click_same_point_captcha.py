import ctypes
import os
import random
import tempfile
import time
from pathlib import Path
from xbot import sleep
from xbot import web, print
import xbot
import cv2
import numpy as np
from . import package
from xbot import win32

# ShadowBot 作为同目录模块加载时使用这个导入。
from .find_same_dot_patterns import analyze, read_image, remove_white_frame, write_image


def _log(message):
    try:
        xbot.logging.info(message)
    except Exception:
        print(message)


def _resolve_element(web_page, element, timeout=5):
    """把选择器或影刀网页元素统一解析成网页元素对象。"""
    if hasattr(element, "get_bounding"):
        return element
    if web_page is None or not element:
        return None
    try:
        if isinstance(element, str):
            text = element.strip()
            if text.startswith(("/", "./", "(")):
                return web_page.find_by_xpath(text)
            return web_page.find(element, timeout=timeout)
        return web_page.find(element, timeout=timeout)
    except Exception as exc:
        _log("解析验证码网页元素失败: %s" % exc)
        return None


def _screen_scale():
    """使用示例脚本的 PPI 逻辑获取鼠标坐标缩放比例。"""
    try:
        from .utils import get_ppi

        scale = get_ppi()
    except Exception:
        try:
            from utils import get_ppi

            scale = get_ppi()
        except Exception:
            scale = 1

    try:
        scale = float(scale)
    except (TypeError, ValueError):
        scale = 1.0
    return scale if scale > 0 else 1.0


def _screen_rect(element):
    """获取鼠标点击坐标，严格采用可用示例的点击坐标系。"""
    # 参考 temu_drag_photo_captcha.py：点击使用普通 get_bounding()。
    # to96dpi=False 只用于截屏，不要把它的结果再次乘 PPI，否则会二次缩放。
    x, y, width, height = element.get_bounding()
    return float(x), float(y), float(width), float(height)


def _capture_element(element, path):
    """只截取验证码网页元素，而不是整屏截图。"""
    try:
        x, y, width, height = element.get_bounding(to96dpi=False)
        win32.screenshot.save_screen_to_file(
            str(path),
            "png",
            int(x),
            int(y),
            int(x + width),
            int(y + height),
        )
        return True
    except Exception as exc:
        _log("截图验证码元素失败: %s" % exc)
        return False


def _move_to(point_x, point_y):
    """按示例脚本的方式移动鼠标。"""
    if os.name == "nt":
        ctypes.windll.user32.SetCursorPos(int(point_x), int(point_y))
    else:
        from xbot import win32

        win32.mouse_move(
            point_x=int(point_x), point_y=int(point_y), move_speed="instant"
        )


def _randomized_point(point_x, point_y, offset=15):
    """给点击中心增加独立的随机偏移，默认与示例相同为 ±15 像素。"""
    offset = max(0, int(offset))
    return (
        int(point_x) + random.randint(-offset, offset),
        int(point_y) + random.randint(-offset, offset),
    )


def _click_randomized(point_x, point_y, offset=15):
    from xbot import sleep, win32

    click_x, click_y = _randomized_point(point_x, point_y, offset)
    _move_to(click_x, click_y)
    sleep(random.uniform(0.04, 0.12))
    win32.mouse_click()
    return click_x, click_y


def _analyze_captcha(path):
    """识别截图，并将裁剪白边后的坐标还原到截图坐标。"""
    image = read_image(str(path))
    cropped, (x_offset, y_offset) = remove_white_frame(image)
    results = analyze(cropped)

    for item in results:
        item["center"] = (
            item["center"][0] + x_offset,
            item["center"][1] + y_offset,
        )
        item["dots"] = [(x + x_offset, y + y_offset) for x, y in item["dots"]]
        item["contour"] = item["contour"] + np.array(
            [[[x_offset, y_offset]]], dtype=np.int32
        )
    return image, results


def _matched_items(results):
    """只保留点数出现至少两次的图案。"""
    groups = {}
    for item in results:
        groups.setdefault(item["count"], []).append(item)
    matched = [item for item in results if len(groups[item["count"]]) >= 2]
    matched.sort(key=lambda item: (item["center"][1], item["center"][0]))
    return groups, matched


def _save_debug_image(image, results, path):
    canvas = image.copy()
    for item in results:
        contour = item["contour"]
        center = item["center"]
        cv2.drawContours(canvas, [contour], -1, (0, 0, 255), 2)
        cv2.circle(canvas, center, 4, (255, 0, 0), -1)
        cv2.putText(
            canvas,
            str(item["count"]),
            (center[0] - 8, center[1] + 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )
        for dot in item["dots"]:
            cv2.circle(canvas, dot, 3, (0, 255, 255), 1)
    write_image(str(path), canvas)


def click_same_dot_patterns(
    web_page,
    image_ele,
    confirm_ele=None,
    random_offset=15,
    click_pause=0.25,
    debug_output_path=r"D:\download\temu_1\temu_1\1.png",
):
    """识别并点击所有点数重复的图案。

    image_ele 可以是影刀网页元素，也可以是网页元素选择器/XPath。
    返回值中的 coordinates 是原始验证码截图坐标，screen_coordinates
    是实际点击使用的屏幕坐标。
    """

    element = _resolve_element(web_page, image_ele)
    if element is None:
        raise ValueError("找不到 image_ele 对应的验证码网页元素")

    run_dir = (
        Path(tempfile.gettempdir())
        / "temu_same_dot_patterns"
        / ("run_%d" % int(time.time() * 1000))
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = run_dir / "captcha.png"
    if not _capture_element(element, screenshot_path):
        raise RuntimeError("无法截取验证码网页元素")

    image, results = _analyze_captcha(screenshot_path)
    groups, matched = _matched_items(results)
    if not matched:
        raise RuntimeError("没有找到点数相同的图案")

    if debug_output_path:
        _save_debug_image(image, results, debug_output_path)

    capture_x, capture_y, capture_width, capture_height = element.get_bounding(
        to96dpi=False
    )
    # 截图和鼠标都使用同一个物理屏幕矩形，避免 CSS 坐标与物理像素混用。
    # 这是截图像素到 SetCursorPos 屏幕坐标的直接映射。
    element_x = float(capture_x)
    element_y = float(capture_y)
    element_width = float(capture_width)
    element_height = float(capture_height)
    image_width = image.shape[1]
    image_height = image.shape[0]
    css_x, css_y, css_width, css_height = _screen_rect(element)
    # _log(
    #     "验证码坐标: click_capture=(%s,%s,%s,%s), css=(%s,%s,%s,%s), "
    #     "capture=(%s,%s,%s,%s), "
    #     "ppi_scale=%s, image=%sx%s"
    #     % (
    #         element_x,
    #         element_y,
    #         element_width,
    #         element_height,
    #         css_x,
    #         css_y,
    #         css_width,
    #         css_height,
    #         capture_x,
    #         capture_y,
    #         capture_width,
    #         capture_height,
    #         _screen_scale(),
    #         image_width,
    #         image_height,
    #     )
    # )
    screen_coordinates = []
    for item in matched:
        image_x, image_y = item["center"]
        screen_x = element_x + image_x / image_width * element_width
        screen_y = element_y + image_y / image_height * element_height
        click_x, click_y = _click_randomized(screen_x, screen_y, random_offset)
        # _log(
        #     "图案点击: image=(%s,%s), screen_center=(%.1f,%.1f), "
        #     "random_click=(%s,%s)"
        #     % (image_x, image_y, screen_x, screen_y, click_x, click_y)
        # )
        screen_coordinates.append((click_x, click_y))
        sleep(float(click_pause))

    group_summary = {
        count: [item["center"] for item in items] for count, items in groups.items()
    }

    if confirm_ele:
        web_page.find(confirm_ele).click()


def test():
    if "xbot_extensions" not in __file__:
        web_page = web.get_active("chrome")
        image_ele = package.selector("图片_2")
        # commit_ele = package.selector("temu_2")
        click_same_dot_patterns(web_page, image_ele)
        exit()


def main(args):
    """ShadowBot 自定义指令入口，不使用命令行参数。"""
    test()
    web_page = args.get("web_page")
    image_ele = args.get("image_ele")
    confirm_ele = args.get("confirm_ele")
    if web_page is None or image_ele is None:
        raise ValueError("请传入 web_page 和 image_ele（或 captcha_ele）")
    click_same_dot_patterns(
        web_page=web_page,
        image_ele=image_ele,
        confirm_ele=confirm_ele,
        random_offset=int(args.get("random_offset", 15)),
        click_pause=float(args.get("click_pause", 0.25)),
        debug_output_path=args.get("debug_output_path"),
    )
