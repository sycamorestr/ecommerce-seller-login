#!/usr/bin/env python3
"""
同色点连线 —— 差分进化全局优化（影刀模块版）

1. 截图 → HSV 分割检测彩色圆点 + Hough 检测大圆
2. 用户规则确定绕行方向 + scipy 差分进化全局优化航点
3. Chamfer 平滑 → 路径坐标 → 驱动鼠标绘制
"""

import math, os, time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from scipy.optimize import differential_evolution

import xbot  # type: ignore
from xbot import print, sleep, win32  # type: ignore
from . import package  # type: ignore
from .package import variables as glv  # type: ignore
from .utils import get_ppi, get_xbot_activity_cache_folder  # type: ignore

# ── 常量 ──
COLORS = ["red", "green", "blue", "yellow"]
BGR_MAP = {"red": (0, 0, 255), "green": (0, 230, 0),
           "blue": (235, 20, 20), "yellow": (0, 245, 255)}
HSV_MAP = {
    "red":    [((0, 120, 120), (12, 255, 255)), ((168, 120, 120), (179, 255, 255))],
    "green":  [((35, 100, 100), (85, 255, 255))],
    "blue":   [((90, 100, 80), (135, 255, 255))],
    "yellow": [((18, 100, 150), (38, 255, 255))],
}


@dataclass(frozen=True)
class Dot:
    color: str; x: float; y: float; radius: float; area: int


# ── 图像工具 ──
def _read_image(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR) if data.size else None


def _write_image(path, image):
    ext = Path(path).suffix or ".png"
    ok, buf = cv2.imencode(ext, image)
    if ok: buf.tofile(str(path))
    return ok


# ── 检测 ──
def segment_colored_dots(image, min_area=700):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    result = {}
    for color, ranges in HSV_MAP.items():
        mask = np.zeros(hsv.shape[:2], np.uint8)
        for lo, hi in ranges:
            mask |= cv2.inRange(hsv, np.array(lo, np.uint8), np.array(hi, np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
        n, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
        dots = []
        for cid in range(1, n):
            area = int(stats[cid, cv2.CC_STAT_AREA])
            if area < min_area: continue
            comp = np.uint8(labels == cid) * 255
            contours, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours: continue
            cnt = max(contours, key=cv2.contourArea)
            perim = cv2.arcLength(cnt, True)
            if 4.0 * math.pi * area / max(perim * perim, 1.0) < 0.68: continue
            (x, y), r = cv2.minEnclosingCircle(cnt)
            dots.append(Dot(color, float(x), float(y), float(r), area))
        dots.sort(key=lambda d: d.area, reverse=True)
        result[color] = sorted(dots[:2], key=lambda d: (d.x, d.y))
    if any(len(v) != 2 for v in result.values()):
        raise RuntimeError(f"Expected 2 dots per color, got: { {c: len(v) for c, v in result.items()} }")
    return result


def detect_circle(image, dots):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 1.5)
    h, w = gray.shape
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2,
                               minDist=min(h, w) // 3, param1=100, param2=40,
                               minRadius=int(min(h, w) * 0.30),
                               maxRadius=int(min(h, w) * 0.50))
    if circles is not None:
        scored = []
        for cx, cy, r in circles[0]:
            outside = sum(max(0.0, math.hypot(d.x - cx, d.y - cy) - r - 8.0) for d in dots)
            scored.append((outside, -r, float(cx), float(cy), float(r)))
        return min(scored)[2:]
    cx, cy = w / 2.0, h / 2.0
    r = max(math.hypot(d.x - cx, d.y - cy) for d in dots) + 4.0
    return cx, cy, r


# ── 路径工具 ──
def _chamfer(pts, iters=2):
    c = pts.astype(np.float64)
    for _ in range(iters):
        if len(c) < 3: break
        l = 0.75 * c[:-1] + 0.25 * c[1:]
        r = 0.25 * c[:-1] + 0.75 * c[1:]
        ref = np.empty((len(l) * 2 + 2, 2))
        ref[0] = c[0]; ref[1:-1:2] = l; ref[2:-1:2] = r; ref[-1] = c[-1]
        c = ref
    return c


def _build_path(start, end, waypoints):
    wps = sorted(waypoints, key=lambda w: np.dot(w - start, end - start))
    return _chamfer(np.array([start] + wps + [end]), iters=2)


def _count_crossings(paths, shape, lw):
    h, w = shape[:2]
    masks = {}
    for c in COLORS:
        m = np.zeros((h, w), np.uint8)
        pts = np.rint(paths[c]).astype(np.int32)
        cv2.polylines(m, [pts.reshape(-1, 1, 2)], False, 255, thickness=lw, lineType=cv2.LINE_AA)
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lw, lw)))
        masks[c] = m
    total = 0
    for i in range(len(COLORS)):
        for j in range(i + 1, len(COLORS)):
            total += np.count_nonzero((masks[COLORS[i]] > 0) & (masks[COLORS[j]] > 0))
    return total


def _line_cross(c1, c2, circ, inside):
    p1, p2 = circ[c1], inside[c1]
    q1, q2 = circ[c2], inside[c2]
    d1 = (q2[0]-q1[0])*(p1[1]-q1[1]) - (q2[1]-q1[1])*(p1[0]-q1[0])
    d2 = (q2[0]-q1[0])*(p2[1]-q1[1]) - (q2[1]-q1[1])*(p2[0]-q1[0])
    d3 = (p2[0]-p1[0])*(q1[1]-p1[1]) - (p2[1]-p1[1])*(q1[0]-p1[0])
    d4 = (p2[0]-p1[0])*(q2[1]-p1[1]) - (p2[1]-p1[1])*(q2[0]-p1[0])
    if not (d1*d2 < -1e-6 and d3*d4 < -1e-6): return None
    t = abs(d3) / (abs(d3) + abs(d4))
    return np.array([q1[0] + t*(q2[0]-q1[0]), q1[1] + t*(q2[1]-q1[1])])


# ── 核心求解 ──
def solve_paths(image, lw=5, N=5, maxiter=500, popsize=30, seed=42):
    """返回每条颜色的图像像素坐标列表 [{color: [(x,y),...]}, ...]"""
    IH, IW = image.shape[:2]

    dots_raw = segment_colored_dots(image)
    dots_flat = [d for ds in dots_raw.values() for d in ds]
    cx, cy, R = detect_circle(image, dots_flat)

    circ, inside = {}, {}
    for c in COLORS:
        d1, d2 = dots_raw[c]
        on1 = abs(math.hypot(d1.x - cx, d1.y - cy) - R) < 15
        circ[c] = np.array([d1.x, d1.y]) if on1 else np.array([d2.x, d2.y])
        inside[c] = np.array([d2.x, d2.y]) if on1 else np.array([d1.x, d1.y])

    # ── 绕行规则 ──
    bypass_dir = {c: np.zeros(2) for c in COLORS}
    bypass_cnt = {c: 0.0 for c in COLORS}

    for i in range(len(COLORS)):
        for j in range(i + 1, len(COLORS)):
            c1, c2 = COLORS[i], COLORS[j]
            cross = _line_cross(c1, c2, circ, inside)
            if cross is None: continue

            dir1 = inside[c1] - circ[c1]; dir1 = dir1 / np.linalg.norm(dir1)
            dir2 = inside[c2] - circ[c2]; dir2 = dir2 / np.linalg.norm(dir2)

            dists = [(np.linalg.norm(cross - circ[c1]), c1, True),
                     (np.linalg.norm(cross - inside[c1]), c1, False),
                     (np.linalg.norm(cross - circ[c2]), c2, True),
                     (np.linalg.norm(cross - inside[c2]), c2, False)]
            dists.sort(key=lambda x: x[0])
            _, nearest_c, nearest_is_circ = dists[0]
            if nearest_is_circ:
                yield_c = c2 if nearest_c == c1 else c1
            else:
                yield_c = nearest_c
            if yield_c == c1: bypass_dir[c1] += -dir2; bypass_cnt[c1] += 1
            else:             bypass_dir[c2] += -dir1; bypass_cnt[c2] += 1

    for c in COLORS:
        if bypass_cnt[c] > 0:
            bypass_dir[c] = bypass_dir[c] / bypass_cnt[c]
            bypass_dir[c] = bypass_dir[c] / np.linalg.norm(bypass_dir[c])

    # ── 差分进化 ──
    D = N * 2 * len(COLORS)
    bounds = [(cx - R + 15, cx + R - 15) if i % 2 == 0
              else (cy - R + 15, cy + R - 15) for i in range(D)]

    def _decode(x):
        st = {}
        for ci, c in enumerate(COLORS):
            st[c] = [np.array([x[ci * N * 2 + k * 2],
                               x[ci * N * 2 + k * 2 + 1]]) for k in range(N)]
        return st

    def _objective(x):
        st = _decode(x)
        paths = {c: _build_path(circ[c], inside[c], st[c]) for c in COLORS}
        return float(_count_crossings(paths, image.shape, lw))

    rng = np.random.default_rng(seed)
    n_rule = max(1, popsize // 2)
    init_pop = []
    for pi in range(popsize):
        x = np.zeros(D)
        use_rule = (pi < n_rule)
        for ci, c in enumerate(COLORS):
            chord = inside[c] - circ[c]; cl = np.linalg.norm(chord)
            d = bypass_dir[c] if (bypass_cnt[c] > 0 and use_rule) else np.array([0., 0.])
            for k in range(N):
                t = (k + 1) / (N + 1)
                base = circ[c] + chord * t
                if use_rule:
                    wp = base + d * cl * (0.08 + 0.12 * math.sin(t * math.pi)) + rng.normal(0, 5, 2)
                else:
                    wp = base + rng.normal(0, R * 0.25, 2)
                wr = np.linalg.norm(wp - np.array([cx, cy]))
                if wr > R - 10: wp = np.array([cx, cy]) + (wp - np.array([cx, cy])) / wr * (R - 12)
                x[ci * N * 2 + k * 2] = wp[0]
                x[ci * N * 2 + k * 2 + 1] = wp[1]
        init_pop.append(x)

    print(f"DE: {D}D, pop={popsize}, maxiter={maxiter}")
    result = differential_evolution(_objective, bounds, maxiter=maxiter, popsize=popsize,
        mutation=(0.5, 1.5), recombination=0.9, seed=seed, init=np.array(init_pop))
    print(f"Done: {result.fun:.0f}px cross ({result.nfev} evals)")

    # ── 转成坐标列表 ──
    st = _decode(result.x)
    coord_lists = []
    for c in COLORS:
        pts = _chamfer(_build_path(circ[c], inside[c], st[c]), iters=2)
        # 裁剪圆外
        for i in range(len(pts)):
            r = math.hypot(pts[i][0] - cx, pts[i][1] - cy)
            if r > R - 3:
                a = math.atan2(pts[i][1] - cy, pts[i][0] - cx)
                pts[i] = [cx + (R - 4) * math.cos(a), cy + (R - 4) * math.sin(a)]
        coord_lists.append([(int(x), int(y)) for x, y in np.rint(pts).astype(np.int32)])
    return coord_lists


# ── 鼠标操作 ──
def _get_ppi():
    """获取屏幕缩放比。兼容 Win7+。"""
    import ctypes
    from ctypes import windll
    try: ctypes.windll.user32.SetProcessDPIAware()
    except: pass
    hDC = windll.user32.GetDC(0)
    dpi = windll.gdi32.GetDeviceCaps(hDC, 88)
    windll.user32.ReleaseDC(0, hDC)
    ratio = float.as_integer_ratio(round(dpi / 96, 2))
    return ratio[1] / ratio[0]


def _move_to(x, y):
    """通过 SetCursorPos 直接设置鼠标位置，实现平滑移动。"""
    import ctypes
    ctypes.windll.user32.SetCursorPos(x, y)


def _draw_path(coords, scale, base_x, base_y, point_interval=0.03, click_interval=0.2):
    """沿坐标列表拖拽鼠标画线。coords 是图像像素坐标。"""
    if not coords: return
    ppi = _get_ppi()

    # 图像坐标 → 屏幕绝对坐标
    screen = [(base_x + int(x * scale / ppi), base_y + int(y * scale / ppi)) for x, y in coords]

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


# ── 影刀入口 ──
def handle_captcha(web_page, captcha_element, lw=5, maxiter=500, popsize=30, seed=42,
                   move_speed="middle", point_interval=0.03, click_interval=0.2):
    """截图 → 识别 → 规划 → 画线"""
    if hasattr(captcha_element, 'get_bounding'):
        el = captcha_element
    else:
        el = web_page.find(captcha_element)

    ex, ey, ew, eh = el.get_bounding(to96dpi=False)
    ax, ay, _, _ = el.get_bounding(to96dpi=True)

    cache = get_xbot_activity_cache_folder("de_router")
    img_path = os.path.join(cache, "puzzle_temp.png")
    win32.screenshot.save_screen_to_file(img_path, "png", ex, ey, ex + ew, ey + eh)
    print(f"截图: {img_path}")

    image = _read_image(Path(img_path))
    if image is None: raise RuntimeError("截图失败")

    paths = solve_paths(image, lw=lw, maxiter=maxiter, popsize=popsize, seed=seed)
    scale = get_ppi()
    print(f"缩放: {scale}, 共{len(paths)}条路径")

    for i, coords in enumerate(paths):
        print(f"第{i+1}条: {len(coords)}点")
        _draw_path(coords, scale, ax, ay, point_interval, click_interval)

    try: os.remove(img_path)
    except: pass
    print("完成")
    return paths


def test_func():
    web_page = xbot.web.get_active("chrome")
    captcha_element = package.selector("图片_1")
    handle_captcha(web_page, captcha_element)
    exit()


def main(args):
    test_func()
    web_page = args.get("web_page")
    captcha_element = args.get("captcha_element")
    if not web_page or not captcha_element:
        raise ValueError("web_page 和 captcha_element 参数不能为空")
    handle_captcha(
        web_page=web_page, 
        captcha_element=captcha_element,
        lw=int(args.get("lw", 5)),
        maxiter=int(args.get("maxiter", 500)),
        popsize=int(args.get("popsize", 30)),
        seed=int(args.get("seed", 42)),
        move_speed=str(args.get("move_speed", "middle")),
        point_interval=float(args.get("point_interval", 0.03)),
        click_interval=float(args.get("click_interval", 0.2)),
    )
