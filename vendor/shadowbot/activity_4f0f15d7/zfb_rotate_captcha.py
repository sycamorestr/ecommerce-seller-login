# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import json
import os
import re
import tempfile
import cv2
import requests
import xbot
from xbot import sleep
import time
from .resources.rotation_solver import (
    DEFAULT_BAND,
    DEFAULT_SOLVE_SIZE,
    load_bgr_image,
    solve_tiles,
)



def solve(images, solve_size=DEFAULT_SOLVE_SIZE, band=DEFAULT_BAND):
    """识别 4 张已拆好的支付宝旋转验证码小图，并返回每张图需要点击的次数。

    images 必须是长度为 4 的列表或元组，顺序固定为：
    1. 左上
    2. 右上
    3. 左下
    4. 右下
    """
    try:
        if not isinstance(images, (list, tuple)) or len(images) != 4:
            raise ValueError("images 必须是包含 4 张图的列表或元组")

        source_images = [load_bgr_image(image) for image in images]
        clicks, score, second_score = solve_tiles(
            source_images,
            solve_size=solve_size,
            band=band,
        )
        gap_percent = 0.0
        if second_score is not None and score > 0:
            gap_percent = ((second_score - score) / score) * 100.0

        return {
            "ok": True,
            "clicks": clicks,
            "result": ",".join(str(item) for item in clicks),
            "score": round(score, 6),
            "second_score": None if second_score is None else round(second_score, 6),
            "gap_percent": round(gap_percent, 3),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error": str(exc),
            "clicks": [],
            "result": "",
            "score": None,
            "second_score": None,
            "gap_percent": None,
        }


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
                return web_page.find_by_xpath(element)
            return web_page.find(element, timeout=5)
        return web_page.find(element, timeout=5)
    except Exception:
        return None


def _resolve_picture_elements(
    web_page,
    picture_eles=None,
    picture_ele_1=None,
    picture_ele_2=None,
    picture_ele_3=None,
    picture_ele_4=None,
):
    """把 4 张小图元素统一整理成固定顺序的列表。"""
    if picture_eles:
        resolved = [_resolve_element(web_page, item) for item in picture_eles]
        if len(resolved) == 4 and not any(item is None for item in resolved):
            return resolved

    resolved = [
        _resolve_element(web_page, picture_ele_1),
        _resolve_element(web_page, picture_ele_2),
        _resolve_element(web_page, picture_ele_3),
        _resolve_element(web_page, picture_ele_4),
    ]

    if len(resolved) != 4 or any(item is None for item in resolved):
        return None

    return resolved


def _get_current_picture_elements(
    web_page, picture_eles, picture_ele_1, picture_ele_2, picture_ele_3, picture_ele_4
):
    """按当前页面状态重新获取 4 张验证码小图元素。"""
    return _resolve_picture_elements(
        web_page,
        picture_eles=picture_eles,
        picture_ele_1=picture_ele_1,
        picture_ele_2=picture_ele_2,
        picture_ele_3=picture_ele_3,
        picture_ele_4=picture_ele_4,
    )


def _capture_element_image(web_page, element):
    """对单个小图元素截图，并返回 OpenCV 使用的 BGR 图片。"""
    target = _resolve_element(web_page, element)
    if target is None:
        return None

    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = os.path.join(temp_dir, "captcha.png")
        x, y, w, h = target.get_bounding(to96dpi=False)
        xbot.win32.screenshot.save_screen_to_file(
            image_path,
            "png",
            x,
            y,
            x + w,
            y + h,
        )
        return cv2.imread(image_path)


def _capture_picture_images(web_page, picture_elements):
    """优先通过 src 下载 4 张小图；失败时再回退到截图。"""
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
                print("  图片%s URL: %s" % (i, src))
                try:
                    headers = {
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36"
                        ),
                        "Referer": web_page.url if getattr(web_page, "url", "") else "",
                    }
                    resp = requests.get(src, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        img_path = os.path.join(group_folder, "img_%s.jpg" % i)
                        with open(img_path, "wb") as f:
                            f.write(resp.content)
                        print("  已保存: %s" % img_path)
                        image = cv2.imread(img_path)
                except Exception:
                    image = None

            if image is None:
                image = _capture_element_image(web_page, element)

            if image is None:
                return None

            images.append(image)

    return images


def _picture_group_exists(web_page, picture_elements):
    """判断 4 张小图是否仍然存在，只要任意一张存在就认为验证码还在。"""
    if not picture_elements:
        return False
    for element in picture_elements:
        target = _resolve_element(web_page, element)
        if target is None:
            continue
        try:
            target.get_bounding(to96dpi=False)
            return True
        except Exception:
            continue
    return False


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


def _get_rotate_info(element):
    """读取图片节点的 style，解析 rotate(...) 里的角度。"""
    image_node = _get_image_node_from_element(element)
    if image_node is None:
        return {"style": "", "rotate_deg": None}

    try:
        style = image_node.get_attribute("style") or ""
    except Exception:
        style = ""

    matched = re.search(r"rotate\(\s*(-?\d+(?:\.\d+)?)deg\s*\)", style)
    if not matched:
        return {"style": style, "rotate_deg": None}

    try:
        rotate_deg = float(matched.group(1))
    except Exception:
        rotate_deg = None
    return {"style": style, "rotate_deg": rotate_deg}


def _write_debug_image(images, result, debug_path):
    """把 4 张已拆小图拼成调试图，方便核对顺序。"""
    if not debug_path or not result.get("ok"):
        return

    debug_path = os.path.abspath(debug_path)
    root, ext = os.path.splitext(debug_path)
    if not ext:
        debug_path = debug_path + ".png"

    normalized = [
        cv2.resize(load_bgr_image(image), (180, 180), interpolation=cv2.INTER_AREA)
        for image in images
    ]
    gap = 4
    canvas = 255 * cv2.cvtColor(
        cv2.UMat(364, 364, cv2.CV_8UC1).get(), cv2.COLOR_GRAY2BGR
    )
    positions = [(0, 0), (184, 0), (0, 184), (184, 184)]

    for index, (image, (x, y)) in enumerate(zip(normalized, positions), start=1):
        canvas[y : y + 180, x : x + 180] = image
        cv2.rectangle(canvas, (x, y), (x + 179, y + 179), (0, 255, 0), 2)
        cv2.putText(
            canvas,
            str(index),
            (x + 8, y + 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )

    ok = cv2.imwrite(debug_path, canvas)
    if not ok:
        raise RuntimeError("调试图片写出失败，请检查 debug_path 是否带有有效图片后缀")


def _click_element(element, click_interval=0.15):
    """点击单个小图元素中心点。"""
    x, y, w, h = element.get_bounding()
    point_x = x + (w / 2)
    point_y = y + (h / 2)
    xbot.win32.mouse_move(
        point_x=point_x,
        point_y=point_y,
        move_speed="middle",
    )
    xbot.win32.mouse_click(button="left", click_type="click")
    sleep(click_interval)
    return {
        "x": round(point_x, 2),
        "y": round(point_y, 2),
    }


def _click_solution(picture_elements, result, click_interval=0.15):
    """按识别结果依次点击 4 张小图，并兼容顺/逆时针旋转。"""
    if not result.get("ok"):
        return []
    if len(picture_elements) != 4 or len(result["clicks"]) != 4:
        raise RuntimeError("点击输入异常，必须提供 4 张小图和 4 个点击结果")

    actions = []
    probe_wait = 0.35
    xbot.win32.manual_motion_on(
        motion_move=True,
        motion_click=True,
        motion_delay=True,
        min_time=0.05,
        max_time=0.2,
    )
    try:
        for index, (element, click_count) in enumerate(
            zip(picture_elements, result["clicks"]), start=1
        ):
            if click_count <= 0:
                continue
            x, y, w, h = element.get_bounding()
            point_x = x + (w / 2)
            point_y = y + (h / 2)
            xbot.win32.mouse_move(
                point_x=point_x,
                point_y=point_y,
                move_speed="middle",
            )

            xbot.win32.mouse_click(button="left", click_type="click")
            sleep(probe_wait)
            probe_info = _get_rotate_info(element)
            rotate_deg = probe_info["rotate_deg"]

            if rotate_deg is not None and rotate_deg < 0:
                rotate_direction = "counterclockwise"
                applied_clicks = (4 - click_count) % 4
            else:
                rotate_direction = "clockwise"
                applied_clicks = click_count

            actions.append(
                {
                    "quadrant_index": index,
                    "click_index": 1,
                    "total_clicks": applied_clicks,
                    "raw_clicks": click_count,
                    "rotate_direction": rotate_direction,
                    "probe_style": probe_info["style"],
                    "probe_rotate_deg": rotate_deg,
                    "x": round(point_x, 2),
                    "y": round(point_y, 2),
                }
            )

            for current_click in range(1, applied_clicks):
                xbot.win32.mouse_click(button="left", click_type="click")
                sleep(click_interval)
                actions.append(
                    {
                        "quadrant_index": index,
                        "click_index": current_click + 1,
                        "total_clicks": applied_clicks,
                        "raw_clicks": click_count,
                        "rotate_direction": rotate_direction,
                        "probe_style": probe_info["style"],
                        "probe_rotate_deg": rotate_deg,
                        "x": round(point_x, 2),
                        "y": round(point_y, 2),
                    }
                )
    finally:
        xbot.win32.manual_motion_off()
    return actions


def _wait_until_pictures_disappear(
    web_page,
    picture_eles=None,
    picture_ele_1=None,
    picture_ele_2=None,
    picture_ele_3=None,
    picture_ele_4=None,
    wait_seconds=2.0,
    poll_interval=0.3,
):
    """等待 4 张小图都消失。"""
    end_at = time.time() + max(float(wait_seconds or 0), 0.1)
    while time.time() < end_at:
        picture_elements = _get_current_picture_elements(
            web_page,
            picture_eles,
            picture_ele_1,
            picture_ele_2,
            picture_ele_3,
            picture_ele_4,
        )
        if not _picture_group_exists(web_page, picture_elements):
            return "success"
        sleep(poll_interval)
    picture_elements = _get_current_picture_elements(
        web_page,
        picture_eles,
        picture_ele_1,
        picture_ele_2,
        picture_ele_3,
        picture_ele_4,
    )
    if not _picture_group_exists(web_page, picture_elements):
        return "success"
    return "retry"


def handle_captcha(
    web_page,
    picture_eles=None,
    picture_ele_1=None,
    picture_ele_2=None,
    picture_ele_3=None,
    picture_ele_4=None,
    sure_ele=None,
    solve_size=DEFAULT_SOLVE_SIZE,
    band=DEFAULT_BAND,
    debug_path=None,
    click_interval=0.15,
    retry_times=2,
    wait_seconds=2.0,
):
    """处理整套验证码流程：截图 4 张小图、识别、点击确认、等待校验通过。"""
    retry_times = max(1, int(retry_times or 1))

    picture_elements = _get_current_picture_elements(
        web_page,
        picture_eles,
        picture_ele_1=picture_ele_1,
        picture_ele_2=picture_ele_2,
        picture_ele_3=picture_ele_3,
        picture_ele_4=picture_ele_4,
    )
    if picture_elements is None:
        raise Exception("未找到 4 张验证码小图元素")

    if not _picture_group_exists(web_page, picture_elements):
        raise Exception("验证码图片元素不存在")

    for attempt in range(1, retry_times + 1):
        picture_elements = _get_current_picture_elements(
            web_page,
            picture_eles,
            picture_ele_1,
            picture_ele_2,
            picture_ele_3,
            picture_ele_4,
        )
        if picture_elements is None:
            raise Exception("重试时未重新获取到 4 张验证码小图元素")

        images = _capture_picture_images(web_page, picture_elements)

        if images is None:
            raise Exception("验证码截图失败")

        solve_result = solve(images, solve_size=solve_size, band=band)

        if debug_path:
            debug_root, debug_ext = os.path.splitext(debug_path)
            attempt_debug_path = f"{debug_root}_attempt{attempt}{debug_ext or '.png'}"
            _write_debug_image(images, solve_result, attempt_debug_path)

        if not solve_result["ok"]:
            raise Exception(solve_result.get("error") or "验证码识别失败")

        _click_solution(
            picture_elements,
            solve_result,
            click_interval=click_interval,
        )

        sure_target = _resolve_element(web_page, sure_ele)

        if sure_target is None:
            raise Exception("未找到确认按钮元素")

        xbot.win32.manual_motion_on(
            motion_move=True,
            motion_click=True,
            motion_delay=True,
            min_time=0.05,
            max_time=0.2,
        )
        try:
            sure_action = _click_element(
                sure_target, click_interval=click_interval
            )
        finally:
            xbot.win32.manual_motion_off()

        verify_status = _wait_until_pictures_disappear(
            web_page,
            picture_eles=picture_eles,
            picture_ele_1=picture_ele_1,
            picture_ele_2=picture_ele_2,
            picture_ele_3=picture_ele_3,
            picture_ele_4=picture_ele_4,
            wait_seconds=wait_seconds,
        )

        if verify_status == "success":
            return
        
        sleep(2)

    raise Exception("验证码点击后未通过校验: %s" % verify_status)


def test():
    """本地调试入口。默认要求页面上已有 4 张拆好的小图。"""
    if "xbot_extension" in __file__:
        return

    web_page = xbot.web.get_active("chrome")
    handle_captcha(
        web_page=web_page,
        picture_eles=None,
        picture_ele_1=web_page.find("图片1"),
        picture_ele_2=web_page.find("图片2"),
        picture_ele_3=web_page.find("图片3"),
        picture_ele_4=web_page.find("图片4"),
        sure_ele=web_page.find("确认按钮"),
        solve_size=DEFAULT_SOLVE_SIZE,
        band=DEFAULT_BAND,
        debug_path=None,
        click_interval=0.15,
        retry_times=2,
        wait_seconds=2.0,
    )
    exit()


def main(args):
    """可视化流程正式入口，把处理结果回写到 args。"""
    test()
    handle_captcha(
        web_page=args.get("web_page"),
        picture_eles=args.get("picture_eles"),
        picture_ele_1=args.get("picture_ele_1"),
        picture_ele_2=args.get("picture_ele_2"),
        picture_ele_3=args.get("picture_ele_3"),
        picture_ele_4=args.get("picture_ele_4"),
        sure_ele=args.get("sure_ele"),
        solve_size=int(args.get("solve_size") or DEFAULT_SOLVE_SIZE),
        band=int(args.get("band") or DEFAULT_BAND),
        debug_path=args.get("debug_path"),
        click_interval=float(args.get("click_interval") or 0.15),
        retry_times=int(args.get("retry_times") or args.get("retry_count") or 2),
        wait_seconds=float(args.get("wait_seconds") or 2.0),
    )
