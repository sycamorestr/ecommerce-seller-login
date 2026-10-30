import glob
import heapq
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

import xbot  # type: ignore
from xbot import print, sleep, win32  # type: ignore
from . import package  # type: ignore
from .utils import get_ppi, get_xbot_activity_cache_folder  # type: ignore


COLORS = ["red", "green", "blue", "yellow"]
BGR_MAP = {
    "red": (0, 0, 255),
    "green": (0, 230, 0),
    "blue": (235, 20, 20),
    "yellow": (0, 245, 255),
}
HSV_MAP = {
    "red": [((0, 120, 120), (12, 255, 255)), ((168, 120, 120), (179, 255, 255))],
    "green": [((35, 100, 100), (85, 255, 255))],
    "blue": [((90, 100, 80), (135, 255, 255))],
    "yellow": [((18, 100, 150), (38, 255, 255))],
}
LINE_WIDTH = 5
ROUTE_CLEARANCE = 14
ARC_MARGIN = 10
GRID_STEP = 5
SMOOTH_ITERS = 3
MOUSE_POINT_STEP = 5


@dataclass(frozen=True)
class Dot:
    color: str
    x: float
    y: float
    radius: float
    area: int


def _as_bool(value, default=True):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip().lower() not in ("0", "false", "no", "off", "")


def _read_image(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR) if data.size else None


def _write_image(path, image):
    ext = Path(path).suffix or ".png"
    ok, buf = cv2.imencode(ext, image)
    if ok:
        buf.tofile(str(path))
    return ok


def segment_colored_dots(image, min_area=700):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    result = {}
    for color, ranges in HSV_MAP.items():
        mask = np.zeros(hsv.shape[:2], np.uint8)
        for lo, hi in ranges:
            mask |= cv2.inRange(hsv, np.array(lo, np.uint8), np.array(hi, np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
        dots = []
        for cid in range(1, count):
            area = int(stats[cid, cv2.CC_STAT_AREA])
            if area < min_area:
                continue
            comp = np.uint8(labels == cid) * 255
            contours, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                continue
            cnt = max(contours, key=cv2.contourArea)
            perim = cv2.arcLength(cnt, True)
            if 4.0 * math.pi * area / max(perim * perim, 1.0) < 0.68:
                continue
            (x, y), r = cv2.minEnclosingCircle(cnt)
            dots.append(Dot(color, float(x), float(y), float(r), area))
        dots.sort(key=lambda d: d.area, reverse=True)
        result[color] = sorted(dots[:2], key=lambda d: (d.x, d.y))
    if any(len(v) != 2 for v in result.values()):
        raise RuntimeError("Expected 2 dots per color, got: %s" %
                           {c: len(v) for c, v in result.items()})
    return result


def detect_circle(image, dots):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 1.5)
    h, w = gray.shape
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1.2,
        minDist=min(h, w) // 3, param1=100, param2=40,
        minRadius=int(min(h, w) * 0.30),
        maxRadius=int(min(h, w) * 0.50),
    )
    if circles is not None:
        scored = []
        for cx, cy, r in circles[0]:
            outside = sum(max(0.0, math.hypot(d.x - cx, d.y - cy) - r - 8.0) for d in dots)
            scored.append((outside, -r, float(cx), float(cy), float(r)))
        return min(scored)[2:]
    cx, cy = w / 2.0, h / 2.0
    r = max(math.hypot(d.x - cx, d.y - cy) for d in dots) + 4.0
    return cx, cy, r


def _chamfer(pts, iters=1):
    c = np.asarray(pts, dtype=np.float64)
    for _ in range(iters):
        if len(c) < 3:
            break
        left = 0.75 * c[:-1] + 0.25 * c[1:]
        right = 0.25 * c[:-1] + 0.75 * c[1:]
        refined = np.empty((len(left) * 2 + 2, 2), dtype=np.float64)
        refined[0] = c[0]
        refined[1:-1:2] = left
        refined[2:-1:2] = right
        refined[-1] = c[-1]
        c = refined
    return c


def _resample_polyline(pts, max_step=5):
    pts = np.asarray(pts, dtype=np.float64)
    if len(pts) <= 1:
        return pts
    sampled = [pts[0]]
    for i in range(1, len(pts)):
        a = pts[i - 1]
        b = pts[i]
        seg_len = float(np.linalg.norm(b - a))
        steps = max(1, int(math.ceil(seg_len / max_step)))
        for k in range(1, steps + 1):
            sampled.append(a + (b - a) * (k / float(steps)))
    return np.asarray(sampled, dtype=np.float64)


def _angle_of(p, cx, cy):
    return math.atan2(p[1] - cy, p[0] - cx) % (2.0 * math.pi)


def _point_at(cx, cy, radius, angle):
    return np.array([cx + radius * math.cos(angle),
                     cy + radius * math.sin(angle)], dtype=np.float64)


def _make_arc(start, end, cx, cy, radius, step_px=8):
    a0 = _angle_of(start, cx, cy)
    a1 = _angle_of(end, cx, cy)
    while a1 <= a0:
        a1 += 2.0 * math.pi
    arc_len = max(1.0, (a1 - a0) * radius)
    n = max(3, int(math.ceil(arc_len / step_px)))
    return np.array([_point_at(cx, cy, radius, a0 + (a1 - a0) * i / n)
                     for i in range(n + 1)], dtype=np.float64)


def _single_path_mask(shape, pts, line_width):
    mask = np.zeros(shape[:2], np.uint8)
    ipts = np.rint(pts).astype(np.int32)
    cv2.polylines(mask, [ipts.reshape(-1, 1, 2)], False, 255,
                  thickness=line_width, lineType=cv2.LINE_AA)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (max(1, line_width), max(1, line_width)))
    return cv2.dilate(mask, kernel)


def _clear_disk(mask, p, radius):
    cv2.circle(mask, tuple(np.rint(p).astype(np.int32)), int(max(1, radius)), 0, -1)


def _build_obstacle(image_shape, cx, cy, radius, dots_by_color, color,
                    route_mask, line_width, clearance):
    h, w = image_shape[:2]
    obstacle = np.zeros((h, w), np.uint8)
    yy, xx = np.indices((h, w))
    inside_circle = (xx - cx) ** 2 + (yy - cy) ** 2 <= (radius - line_width - 2) ** 2
    obstacle[~inside_circle] = 255

    if np.any(route_mask):
        k = max(3, int(clearance * 2 + 1))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        obstacle |= cv2.dilate(route_mask, kernel)

    for c in COLORS:
        if c == color:
            continue
        for dot in dots_by_color[c]:
            cv2.circle(obstacle, (round(dot.x), round(dot.y)),
                       round(dot.radius + clearance), 255, -1)
    return obstacle


def _to_grid_point(p, step):
    return int(round(p[0] / step)), int(round(p[1] / step))


def _line_free(a, b, obstacle):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    length = max(1, int(np.linalg.norm(b - a)))
    for i in range(length + 1):
        p = a + (b - a) * (i / float(length))
        x, y = int(round(p[0])), int(round(p[1]))
        if y < 0 or y >= obstacle.shape[0] or x < 0 or x >= obstacle.shape[1]:
            return False
        if obstacle[y, x] > 0:
            return False
    return True


def _simplify_polyline(pts, obstacle):
    if len(pts) <= 2:
        return pts
    simplified = [pts[0]]
    i = 0
    while i < len(pts) - 1:
        j = len(pts) - 1
        while j > i + 1 and not _line_free(pts[i], pts[j], obstacle):
            j -= 1
        simplified.append(pts[j])
        i = j
    return np.asarray(simplified, dtype=np.float64)


def _astar_route(start, goal, obstacle, step=5):
    h, w = obstacle.shape
    gh = int(math.ceil(h / float(step)))
    gw = int(math.ceil(w / float(step)))
    small = cv2.resize(obstacle, (gw, gh), interpolation=cv2.INTER_AREA)
    blocked = small > 0

    sx, sy = _to_grid_point(start, step)
    gx, gy = _to_grid_point(goal, step)
    sx = min(max(sx, 0), gw - 1)
    gx = min(max(gx, 0), gw - 1)
    sy = min(max(sy, 0), gh - 1)
    gy = min(max(gy, 0), gh - 1)
    blocked[sy, sx] = False
    blocked[gy, gx] = False

    def heuristic(x, y):
        return math.hypot(x - gx, y - gy)

    moves = [
        (1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
        (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)),
        (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2)),
    ]
    open_heap = [(heuristic(sx, sy), 0.0, sx, sy)]
    came = {}
    cost = {(sx, sy): 0.0}
    found = False

    while open_heap:
        _, g, x, y = heapq.heappop(open_heap)
        if (x, y) == (gx, gy):
            found = True
            break
        if g != cost.get((x, y)):
            continue
        for dx, dy, move_cost in moves:
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= gw or ny >= gh or blocked[ny, nx]:
                continue
            ng = g + move_cost
            if ng < cost.get((nx, ny), 1e18):
                cost[(nx, ny)] = ng
                came[(nx, ny)] = (x, y)
                heapq.heappush(open_heap, (ng + heuristic(nx, ny), ng, nx, ny))

    if not found:
        raise RuntimeError("A* cannot route")

    cells = []
    cur = (gx, gy)
    while cur != (sx, sy):
        cells.append(cur)
        cur = came[cur]
    cells.append((sx, sy))
    cells.reverse()

    pts = np.array([[x * step, y * step] for x, y in cells], dtype=np.float64)
    pts[0] = start
    pts[-1] = goal
    return _simplify_polyline(pts, obstacle)


def _count_cross(paths, shape, line_width):
    masks = {}
    for c in COLORS:
        masks[c] = _single_path_mask(shape, paths[c], line_width)
    total = 0
    pairs = {}
    for i, c1 in enumerate(COLORS):
        for c2 in COLORS[i + 1:]:
            overlap = int(np.count_nonzero((masks[c1] > 0) & (masks[c2] > 0)))
            if overlap > 0:
                pairs[f"{c1} x {c2}"] = overlap
                total += overlap
    return total, pairs


def _draw_debug_image(image, paths, output_path, line_width):
    canvas = image.copy()
    for c in COLORS:
        pts = np.rint(paths[c]).astype(np.int32)
        cv2.polylines(canvas, [pts.reshape(-1, 1, 2)], False, BGR_MAP[c],
                      thickness=line_width, lineType=cv2.LINE_AA)
    _write_image(output_path, canvas)


def solve_paths_clockwise(image, line_width=LINE_WIDTH, debug_path=None):
    start_time = time.perf_counter()
    dots_by_color = segment_colored_dots(image)
    all_dots = [d for ds in dots_by_color.values() for d in ds]
    cx, cy, radius = detect_circle(image, all_dots)
    # print(f"Circle: center=({cx:.0f},{cy:.0f}) R={radius:.0f}")

    circ = {}
    inside = {}
    for c in COLORS:
        d1, d2 = dots_by_color[c]
        on1 = abs(math.hypot(d1.x - cx, d1.y - cy) - radius) < 15
        circ[c] = np.array([d1.x, d1.y], dtype=np.float64) if on1 else np.array([d2.x, d2.y], dtype=np.float64)
        inside[c] = np.array([d2.x, d2.y], dtype=np.float64) if on1 else np.array([d1.x, d1.y], dtype=np.float64)
        # print(f"  {c}: circ=({circ[c][0]:.0f},{circ[c][1]:.0f}) in=({inside[c][0]:.0f},{inside[c][1]:.0f})")

    base_order = sorted(COLORS, key=lambda c: _angle_of(circ[c], cx, cy))
    # print(f"Clockwise order: {' -> '.join(base_order)}")

    def route_order(order, clearance_value):
        arc_radius = radius - ARC_MARGIN
        dot_angle_pad = max(0.06, (max(d.radius for d in all_dots) + clearance_value) / arc_radius)
        route_mask = np.zeros(image.shape[:2], np.uint8)
        attempt_paths = {}
        for idx, c in enumerate(order):
            next_c = order[(idx + 1) % len(order)]
            start = circ[c]
            start_angle = _angle_of(start, cx, cy)
            next_angle = _angle_of(circ[next_c], cx, cy)
            while next_angle <= start_angle:
                next_angle += 2.0 * math.pi
            exit_angle = max(start_angle + 0.05, next_angle - dot_angle_pad)
            arc_start = _point_at(cx, cy, arc_radius, start_angle)
            arc_exit = _point_at(cx, cy, arc_radius, exit_angle)
            arc = _make_arc(arc_start, arc_exit, cx, cy, arc_radius)

            obstacle = _build_obstacle(image.shape, cx, cy, radius, dots_by_color, c,
                                       route_mask, line_width, clearance_value)
            _clear_disk(obstacle, arc_exit, clearance_value + line_width * 2)
            for dot in dots_by_color[c]:
                _clear_disk(obstacle, np.array([dot.x, dot.y]), dot.radius + clearance_value + line_width * 2)

            inner = _astar_route(arc_exit, inside[c], obstacle, step=GRID_STEP)
            raw = np.vstack([start.reshape(1, 2), arc, inner[1:]])
            path = _resample_polyline(_chamfer(raw, iters=SMOOTH_ITERS), MOUSE_POINT_STEP)
            attempt_paths[c] = path
            route_mask |= _single_path_mask(image.shape, path, line_width + clearance_value)
        return attempt_paths

    clearances = []
    for value in (ROUTE_CLEARANCE, max(3, ROUTE_CLEARANCE // 2), 2):
        if value not in clearances:
            clearances.append(value)

    best = None
    for clearance_value in clearances:
        for shift in range(len(base_order)):
            order = base_order[shift:] + base_order[:shift]
            try:
                attempt_paths = route_order(order, clearance_value)
            except RuntimeError:
                continue
            cross, pairs = _count_cross(attempt_paths, image.shape, line_width)
            # print(f"Clockwise attempt: clearance={clearance_value}, order={' -> '.join(order)}, cross={cross}px")
            if best is None or cross < best[0]:
                best = (cross, pairs, attempt_paths, order, clearance_value)
            if cross == 0:
                break
        if best is not None and best[0] == 0:
            break

    if best is None:
        raise RuntimeError("顺时针路由失败：没有可完成的候选")

    cross, pairs, paths, order, clearance_value = best
    # print(f"Clockwise chosen: clearance={clearance_value}, order={' -> '.join(order)}")
    # print(f"Clockwise done: cross={cross}px, elapsed={time.perf_counter() - start_time:.2f}s")
    # if pairs:
        # print(f"Clockwise cross pairs: {pairs}")
    if debug_path:
        _draw_debug_image(image, paths, debug_path, line_width)
        # print(f"结果图: {debug_path}")

    coord_lists = []
    for c in order:
        pts = paths[c]
        coord_lists.append([(int(x), int(y)) for x, y in np.rint(pts).astype(np.int32)])
    return coord_lists


def _move_to(x, y):
    import ctypes
    ctypes.windll.user32.SetCursorPos(int(x), int(y))


def _draw_path(coords, base_x, base_y, width, height, ppi,
               point_interval=0.03, click_interval=0.2):
    if not coords:
        return

    screen = []
    for x, y in coords:
        x = min(max(int(x), 0), max(0, int(width) - 1))
        y = min(max(int(y), 0), max(0, int(height) - 1))
        sx = int((float(base_x) + x * ppi) / ppi)
        sy = int((float(base_y) + y * ppi) / ppi)
        screen.append((sx, sy))

    win32.manual_motion_on()
    try:
        sx, sy = screen[0]
        _move_to(sx, sy)
        sleep(0.1)
        win32.mouse_click(button="left", click_type="down", delay_after=0)
        sleep(click_interval)

        for i, (x, y) in enumerate(screen[1:], 1):
            _move_to(x, y)
            px, py = screen[i - 1]
            dist = math.hypot(x - px, y - py)
            sleep(max(0.005, point_interval * dist / 20))

        sleep(0.1)
        win32.mouse_click(button="left", click_type="up")
        sleep(click_interval)
    finally:
        win32.manual_motion_off()


def handle_captcha(web_page, captcha_element, sure_element, lw=LINE_WIDTH,
                   point_interval=0.01, click_interval=0.1, retry=3):

    for _ in range(retry):

        try:
            el = web_page.find(captcha_element, timeout=5)
        except Exception:
            break

        sure_ele = web_page.find(sure_element)

        ex, ey, ew, eh = el.get_bounding(to96dpi=False)
        ax, ay, _, _ = el.get_bounding(to96dpi=True)

        cache = get_xbot_activity_cache_folder("de_router")
        img_path = os.path.join(cache, "puzzle_temp.png")
        debug_path = os.path.join(cache, "puzzle_route_debug.png")
        for old_path in glob.glob(os.path.join(cache, "puzzle_route_debug*.png")):
            try:
                os.remove(old_path)
            except Exception:
                pass
        win32.screenshot.save_screen_to_file(img_path, "png", ex, ey, ex + ew, ey + eh)
        # print(f"截图: {img_path}")
        image = _read_image(Path(img_path))
        if image is None:
            raise RuntimeError("截图失败")
        paths = solve_paths_clockwise(image, line_width=lw, debug_path=debug_path)

        if not paths:
            sure_ele.click()
            sleep(2)
            continue

        ppi = get_ppi() or 1
        # print(f"截图范围: ({ex},{ey},{ew},{eh}), 96dpi基点: ({ax},{ay}), ppi={ppi}, 共{len(paths)}条路径")
        for i, coords in enumerate(paths):
            # print(f"第{i + 1}条: {len(coords)}点")
            _draw_path(coords, ax, ay, ew, eh, ppi, point_interval, click_interval)
        try:
            os.remove(img_path)
        except Exception:
            pass

        # 点击确认按钮
        sure_ele.click()
        sleep(2)


def test_func():
    web_page = xbot.web.get_active("chrome")
    captcha_element = package.selector("图片_1")
    handle_captcha(web_page, captcha_element)
    exit()


def main(args):
    # test_func()
    web_page = args.get("web_page")
    captcha_element = args.get("captcha_element")
    sure_element = args.get("sure_element")
    retry = args.get("retry")
    if not web_page or not captcha_element:
        raise ValueError("web_page 和 captcha_element 参数不能为空")
    handle_captcha(
        web_page=web_page,
        captcha_element=captcha_element,
        sure_element = sure_element,
        lw=int(args.get("lw", LINE_WIDTH)),
        point_interval=float(args.get("point_interval", 0.01)),
        click_interval=float(args.get("click_interval", 0.1)),
        retry=int(retry)
    )
