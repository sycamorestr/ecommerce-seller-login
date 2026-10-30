# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import os
import sys
import platform
import math
import random
import sqlite3
import time
from contextlib import closing
from pathlib import Path
from PIL import Image  # ImageGrab不支持Linux
from io import BytesIO
import http.client
import base64
import json
import xbot
import xbot_visual
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation
from xbot import print, sleep, win32, web
from . import package
from .package import variables as glv
import re
import numpy as np
import cv2
from .utils import get_ppi


_used = {}
_last_move_target = None


def contains_chinese(text):
    if not isinstance(text, str):
        return False
    pattern = re.compile(r"[\u4e00-\u9fa5]")
    return pattern.search(text) is not None


def create_cache_dir():
    """创建本地缓存文件夹，跨平台兼容"""
    if os.name == "nt":  # Windows
        local_appdata_path = os.getenv("LOCALAPPDATA")
        if not local_appdata_path:
            local_appdata_path = os.path.expanduser("~\\AppData\\Local")
    else:  # Linux / UOS / macOS
        # 遵循 XDG Base Directory 规范
        local_appdata_path = os.getenv("XDG_CACHE_HOME")
        if not local_appdata_path:
            local_appdata_path = os.path.expanduser("~/.cache")

    # 确保路径是字符串（防御性编程）
    if not isinstance(local_appdata_path, str):
        local_appdata_path = "/tmp"

    # 构建缓存目录
    xbot_app_cache_dir = os.path.join(
        local_appdata_path, "xbot_activity", "activity_4f0f15d7"
    )

    # 如果路径含中文，为避免某些库（如 OpenCV）对中文路径支持不佳，可选 fallback 到 /tmp
    if contains_chinese(xbot_app_cache_dir):
        xbot_app_cache_dir = os.path.join("/tmp", "xbot_activity", "activity_4f0f15d7")

    # 创建目录
    os.makedirs(xbot_app_cache_dir, exist_ok=True)

    return xbot_app_cache_dir


# 使用platform模块来判断架构类型
machine = platform.machine().lower()
if "x86_64" in machine or "amd64" in machine:
    arch = "x64"
elif "aarch64" in machine or "arm64" in machine:
    arch = "arm64"
else:
    arch = "x64"

# 设置PYTHONPATH
base_path = os.path.dirname(
    os.path.dirname(os.environ.get("PYTHONPATH", os.path.abspath(__file__)))
)
cv_engine_path = os.path.join(base_path, f"support_{arch}/cv-engine/site-packages")
if os.path.exists(cv_engine_path):
    sys.path.append(cv_engine_path)


def get_ppi_local():
    """获取屏幕缩放比例（跨平台）"""
    # print(os.name)
    try:
        if os.name == "nt":  # Win
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
            res = 1 / float(os.environ["QT_SCREEN_SCALE_FACTORS"])
            return res
    except:
        return 1


def generate_trajectory(distance, db_path=None, max_points=14, probe_dx=8.0):
    """按目标距离选择真人轨迹，返回 (累计x, 累计y, 累计毫秒) 列表。"""
    target = float(distance)
    wanted = round(target)
    path = Path(db_path) if db_path is not None else Path(package.resources.get_path("dy-database.db"))
    path = path.resolve()
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(tracker)")}
        query = "SELECT id, distance, data FROM tracker"
        if "source" in columns:
            query += " WHERE source='human_ui'"
            if "quality" in columns:
                query += " AND (quality IS NULL OR quality='ok')"
        rows = conn.execute(query).fetchall()

    trajectories = []
    for tid, recorded_distance, data in rows:
        try:
            pts = [tuple(map(float, row)) for row in json.loads(data)]
            if len(pts) < 8 or any(len(p) != 3 for p in pts):
                continue
            if any(not math.isfinite(v) for p in pts for v in p):
                continue
            if any(p[2] < 0 for p in pts) or not 100 <= sum(p[2] for p in pts) <= 10000:
                continue
            if abs(math.fsum(p[0] for p in pts)) < 1e-9:
                continue
            trajectories.append((tid, int(recorded_distance), pts))
        except (ValueError, TypeError, OverflowError):
            continue
    if not trajectories:
        raise ValueError("数据库中没有可用的真人轨迹")

    used = _used.setdefault(str(path), set())
    available = [t for t in trajectories if t[0] not in used]
    if not available:
        used.clear()
        available = trajectories
    near = [t for t in available if abs(t[1] - wanted) <= 3]
    tid, _, pts = random.choice(near) if near else min(available, key=lambda t: abs(t[1] - wanted))
    scale = wanted / math.fsum(p[0] for p in pts)
    points = [[round(dx * scale, 2), dy, dt] for dx, dy, dt in pts]
    points[0] = [0.0, 0.0, 0.0]
    result = build_waypoints(points, max_points, probe_dx, target)
    used.add(tid)
    return result


def build_waypoints(points, max_points=14, probe_dx=8.0, target_distance=None):
    """将 [dx, dy, dt_ms] 增量流变为累计轨迹。"""
    if not isinstance(max_points, int) or max_points < 1:
        raise ValueError("max_points must be a positive integer")
    rows = [tuple(float(v) for v in row) for row in points]
    if len(rows) < 2 or any(len(row) != 3 for row in rows):
        raise ValueError("expected origin followed by dx/dy/dt rows")
    if any(not math.isfinite(v) for row in rows for v in row):
        raise ValueError("trajectory must contain finite values")
    if rows[0] != (0.0, 0.0, 0.0) or any(row[2] < 0 for row in rows):
        raise ValueError("expected zero origin and nonnegative time increments")
    total_x = math.fsum(row[0] for row in rows[1:])
    target = total_x if target_distance is None else float(target_distance)
    probe = float(probe_dx)
    if not math.isfinite(target) or not math.isfinite(probe) or abs(total_x) < 1e-9:
        raise ValueError("invalid target, probe or zero displacement")
    if target <= probe or probe < 0:
        raise ValueError("rightward target must exceed nonnegative probe")
    scale = (target - probe) / total_x
    cumulative = []
    x = y = elapsed = 0.0
    for dx, dy, dt in rows[1:]:
        x += dx
        y += dy
        elapsed += dt
        cumulative.append((probe + x * scale, y, elapsed))
    count = len(cumulative)
    n = min(max_points, count)
    indices = [math.ceil((i + 1) * count / n) - 1 for i in range(n)]
    result = [cumulative[i] for i in indices]
    result[-1] = (target, result[-1][1], result[-1][2])
    return result


def drag(
    drag_ele: WebElement, slider_ele: WebElement, distance: int, move_speed="middle"
):
    """使用 dy-database.db 真人轨迹，并按速度档位调整回放时间。"""
    def move(x, y, speed="instant"):
        global _last_move_target
        target = (int(x), int(y))
        if target != _last_move_target:
            _last_move_target = target
            win32.mouse_move(*target, relative_to="screen", move_speed=speed, delay_after=0)

    physical = tuple(drag_ele.get_bounding(to96dpi=False))
    logical = tuple(drag_ele.get_bounding(to96dpi=True))
    if (not all(math.isfinite(v) for v in physical + logical)
            or min(physical[2], physical[3], logical[2], logical[3]) <= 0):
        raise ValueError("拖动元素边界无效")

    add_x, _, add_width, _ = slider_ele.get_bounding(to96dpi=False)
    physical_start_x = int(physical[0] + physical[2] / 2)
    target_dx = int(add_x + add_width / 2 + distance + add_width - physical_start_x)

    x, y, width, height = logical
    start_x, start_y = int(x + width / 2), int(y + height / 2)
    scale_x = physical[2] / width
    sdk_distance = target_dx / scale_x
    db_path = package.resources.get_path("dy-database.db")
    points = generate_trajectory(sdk_distance, db_path=db_path,
                                 max_points=10000, probe_dx=0.0)

    variable_speed = move_speed == "variable"
    time_scale = {"fast": 1.0, "middle": 2.0, "slow": 4.0}.get(move_speed, 2.0)
    source_ms = points[-1][2]
    report = {"planned_physical_dx": target_dx, "planned_sdk_dx": sdk_distance,
              "bounds_scale_x": scale_x, "waypoints": len(points),
              "replay": "original_samples", "move_speed": move_speed,
              "source_duration_ms": source_ms,
              "planned_replay_ms": None if variable_speed else source_ms * time_scale}
    # xbot.logging.info("Drag plan:" + json.dumps(report))

    held = False
    try:
        if _last_move_target == (start_x, start_y):
            move(start_x + 1, start_y, "fast")
        move(start_x, start_y, "fast")
        time.sleep(0.15)
        before_physical_x = drag_ele.get_bounding(to96dpi=False)[0]
        if not math.isfinite(before_physical_x):
            raise ValueError("拖动前滑块位置无效")
        held = True
        win32.mouse_click(button="left", click_type="down", delay_after=0)
        pressed_at = time.monotonic()
        time.sleep(0.08)

        started = time.monotonic()
        replay_elapsed_ms = previous_elapsed_ms = 0.0
        for dx, dy, elapsed_ms in points:
            if variable_speed:
                replay_elapsed_ms += (elapsed_ms - previous_elapsed_ms) * random.uniform(1.0, 4.0)
            else:
                replay_elapsed_ms = elapsed_ms * time_scale
            previous_elapsed_ms = elapsed_ms
            wait = replay_elapsed_ms / 1000.0 - (time.monotonic() - started)
            if wait > 0:
                time.sleep(wait)
            move(start_x + dx, start_y + dy)

        time.sleep(0.12)
        final_physical_x = drag_ele.get_bounding(to96dpi=False)[0]
        if not math.isfinite(final_physical_x):
            raise RuntimeError("无法读取松手前的拖动按钮位置")
        report["actual_handle_physical_dx"] = final_physical_x - before_physical_x
        report["handle_error_physical_px"] = target_dx - report["actual_handle_physical_dx"]
        report["actual_replay_ms"] = (time.monotonic() - started) * 1000.0
        report["held_ms"] = (time.monotonic() - pressed_at) * 1000.0
        # xbot.logging.info("Drag end:" + json.dumps(report))
    finally:
        if held:
            win32.mouse_click(button="left", click_type="up", delay_after=0)


def get_x(
    background_image: str, slider_image: str, out_image: str = "result.png"
) -> int:
    bg_img = cv2.imread(background_image, cv2.IMREAD_UNCHANGED)
    tp_img = cv2.imread(slider_image, cv2.IMREAD_UNCHANGED)

    bg_bgr = bg_img[:, :, :3]
    tp_bgr = tp_img[:, :, :3]

    bg_edge = cv2.Canny(bg_bgr, 150, 152)
    tp_edge = cv2.Canny(tp_bgr, 150, 152)

    res = cv2.matchTemplate(bg_edge, tp_edge, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    x, y = max_loc
    h, w = tp_edge.shape[:2]

    result = bg_bgr.copy()
    cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.putText(
        result,
        f"x={x}, y={y}, score={max_val:.3f}",
        (5, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        1,
    )

    cv2.imwrite(out_image, result)

    return x


def handle_captcha(
    web_page: xbot.web.WebBrowser,
    background_ele: str,
    slider_ele: str,
    drag_ele: str,
    retry_count: int,
    offset: int,
    move_speed: str,
):
    """Handles slider CAPTCHA by calculating and simulating the drag distance."""
    cache_folder = create_cache_dir()
    if not move_speed:
        move_speed = "fast"
    for _ in range(int(retry_count)):
        drag_element = web_page.find(drag_ele)

        left_img_path = os.path.join(cache_folder, "std_captcha_left.png")
        rigt_img_path = os.path.join(cache_folder, "std_captcha_right.png")
        b_x, b_y, b_w, b_h = web_page.find(background_ele).get_bounding(to96dpi=False)
        s_x, s_y, s_w, s_h = web_page.find(slider_ele).get_bounding(to96dpi=False)

        xbot.win32.screenshot.save_screen_to_file(
            left_img_path, "png", s_x + s_w, s_y, b_x + b_w, s_y + s_h
        )
        xbot.win32.screenshot.save_screen_to_file(
            rigt_img_path, "png", s_x, s_y, s_x + s_w, s_y + s_h
        )

        distance = get_x(
            left_img_path,
            rigt_img_path,
            r"C:\Users\think\AppData\Local\xbot_activity\activity_4f0f15d7\result.png",
        )
        ppi = get_ppi()
        drag_distance = distance * ppi + float(offset)
        if os.name == "nt":
            drag_distance = int(drag_distance / ppi)
        else:
            drag_distance = int(drag_distance)

        drag(drag_element, web_page.find(slider_ele), drag_distance, move_speed)
        sleep(3)

        try:
            x, y, width, height = drag_element.get_bounding()
            if width == 0 and height == 0:
                break
        except:
            pass

        if not xbot_visual.web.browser.element_display(
            browser=web_page, selector=background_ele, content_type="display"
        ):
            break
    if web_page.is_element_displayed(drag_ele):
        raise Exception("当前滑块仍然存在，请增加指令重试次数")


def test_func() -> None:
    if "xbot_extensions" in __file__:
        return
    web_page = web.get_active("chrome")
    background_ele = "删除 - 抖音背景"
    slider_ele = "删除 - 抖音滑块"
    drag_ele = "删除 - 抖音拖拽"
    retry_count = 3
    offset = 0
    move_speed = "fast"

    handle_captcha(
        web_page, background_ele, slider_ele, drag_ele, retry_count, offset, move_speed
    )
    exit()


def main(args):
    test_func()

    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    slider_ele = args.get("slider_ele")
    drag_ele = args.get("drag_ele")
    retry_count = args.get("retry_count")
    offset = args.get("offset")
    move_speed = args.get("move_speed")
    handle_captcha(
        web_page, background_ele, slider_ele, drag_ele, retry_count, offset, move_speed
    )
