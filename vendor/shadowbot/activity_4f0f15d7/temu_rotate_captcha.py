# Usage notes:
# 1. xbot provides automation, browser, logging, mouse and screenshot APIs.
# 2. package provides access to selectors and variables in the current app.
# 3. When this module is used by a visual flow, call main(args).

import math
import os
import re
import json
from urllib.parse import urljoin

import cv2
import numpy as np
import requests
import xbot
import xbot_visual
from xbot import print, sleep, win32, web

from . import package
from .package import variables as glv
from .utils import get_ppi, get_xbot_activity_cache_folder

ROTATE_RE = re.compile(r"rotate\(\s*(-?\d+(?:\.\d+)?)deg\s*\)")
DEFAULT_TILE_XPATH = ".//img"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
URL_RE = re.compile(r"url\((['\"]?)(.*?)\1\)")


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _cache_folder():
    if os.name == "nt":
        folder = get_xbot_activity_cache_folder("activity_jfbym")
    else:
        home_path = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
        folder = os.path.join(home_path, "xbot_app", "activity_jfbym")
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def _get_rotate_deg_from_style(style_text):
    if not style_text:
        return None
    matched = ROTATE_RE.search(style_text)
    if not matched:
        return None
    try:
        return float(matched.group(1))
    except Exception:
        return None


def _get_node_style(node):
    try:
        return node.get_attribute("style") or ""
    except Exception:
        return ""


def _resolve_element(web_page, element, timeout=5):
    if hasattr(element, "get_bounding"):
        return element
    if web_page is None or not element:
        return None
    try:
        if isinstance(element, str):
            text = element.strip()
            if text.startswith("/") or text.startswith("./") or text.startswith("("):
                return web_page.find_by_xpath(text)
            return web_page.find(element, timeout=timeout)
        return web_page.find(element, timeout=timeout)
    except Exception:
        return None


def _get_image_node_from_element(element):
    if element is None:
        return None
    try:
        src = element.get_attribute("src")
        if src:
            return element
    except Exception:
        pass
    try:
        return element.find_by_xpath(".//img[@src or @data-src or @currentSrc]")
    except Exception:
        return None


def _get_node_rotate_deg(node):
    image_node = _get_image_node_from_element(node) or node
    return _get_rotate_deg_from_style(_get_node_style(image_node))


def _angle_delta(before_deg, after_deg):
    if before_deg is None or after_deg is None:
        return None
    delta = after_deg - before_deg
    while delta <= -180:
        delta += 360
    while delta > 180:
        delta -= 360
    return delta


def _click_is_counterclockwise(before_deg, after_deg):
    delta = _angle_delta(before_deg, after_deg)
    if delta is not None and abs(delta) > 1:
        return delta < 0
    if after_deg is not None:
        return after_deg < 0
    return False


def _node_center_96dpi(node):
    x, y, w, h = node.get_bounding(to96dpi=False)
    scale = get_ppi() if os.name == "nt" else 1
    return int((x + w / 2) * scale), int((y + h / 2) * scale)


def _click_node(node):
    x, y = _node_center_96dpi(node)
    win32.mouse_move(x, y)
    win32.mouse_click()


def _find_tile_nodes(container_ele, tile_xpath=None, skip_first=True, max_tiles=6):
    xpath = tile_xpath or DEFAULT_TILE_XPATH
    try:
        nodes = container_ele.find_all_by_xpath(xpath)
    except Exception:
        nodes = []
    nodes = nodes or []

    sortable = []
    for node in nodes:
        try:
            x, y, w, h = node.get_bounding(to96dpi=False)
        except Exception:
            continue
        sortable.append((round(y / 20.0), x, node))
    sortable.sort(key=lambda item: (item[0], item[1]))
    nodes = [item[2] for item in sortable]
    if skip_first and len(nodes) > max_tiles:
        nodes = nodes[1:]
    if max_tiles:
        nodes = nodes[:max_tiles]
    return nodes


def _read_attr(node, name):
    try:
        return node.get_attribute(name)
    except Exception:
        return None


def _get_image_url_from_element(element):
    image_node = _get_image_node_from_element(element) or element
    for attr in ("currentSrc", "src", "data-src", "data-original", "data-lazy-src"):
        value = _read_attr(image_node, attr)
        if value:
            return value

    style = _get_node_style(image_node) or _get_node_style(element)
    matched = URL_RE.search(style or "")
    if matched:
        return matched.group(2)
    return None


def _write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)


def _download_image_to_file(web_page, element, path):
    src = _get_image_url_from_element(element)
    if not src:
        return False, None

    src = src.strip()
    try:
        if src.startswith("data:image/"):
            import base64

            _, encoded = src.split(",", 1)
            _write_bytes(path, base64.b64decode(encoded))
            return True, src[:40] + "..."

        base_url = getattr(web_page, "url", "") or ""
        url = urljoin(base_url, src)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36"
            ),
            "Referer": base_url,
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200 and resp.content:
            _write_bytes(path, resp.content)
            return True, url
    except Exception as exc:
        xbot.logging.info("download tile failed: %s" % exc)
    return False, src


def _capture_element_to_file(element, path):
    x, y, w, h = element.get_bounding(to96dpi=False)
    win32.screenshot.save_screen_to_file(
        path,
        "png",
        int(x),
        int(y),
        int(x + w),
        int(y + h),
    )


def _save_tile_images(web_page, tile_nodes, cache_folder, capture_mode="auto"):
    paths = []
    sources = []
    for idx, node in enumerate(tile_nodes):
        path = os.path.join(cache_folder, "temu_type1_tile_%02d.png" % idx)
        ok = False
        url = None
        source = "download"
        if capture_mode != "screenshot":
            ok, url = _download_image_to_file(web_page, node, path)
        if not ok or imread_any(path) is None:
            _capture_element_to_file(node, path)
            source = "screenshot"
        paths.append(path)
        sources.append({"index": idx, "source": source, "url": url, "path": path})
    return paths, sources


def imread_any(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_UNCHANGED)


def alpha_of(img):
    if img.ndim == 2:
        return np.where(img < 250, 255, 0).astype(np.uint8)
    if img.shape[2] == 4:
        return img[:, :, 3]
    gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
    return np.where(gray < 250, 255, 0).astype(np.uint8)


def rgba_of(img):
    if img.ndim == 2:
        bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        alpha = alpha_of(img)
        return np.dstack([bgr, alpha])
    if img.shape[2] == 4:
        return img
    alpha = alpha_of(img)
    return np.dstack([img[:, :, :3], alpha])


def bbox_from_alpha(alpha):
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def normalize_subject(path, canvas=192):
    img = imread_any(path)
    if img is None:
        raise FileNotFoundError(path)
    rgba = rgba_of(img)
    alpha = rgba[:, :, 3]
    bbox = bbox_from_alpha(alpha)
    if bbox is None:
        return np.zeros((canvas, canvas, 4), np.uint8)

    x0, y0, x1, y1 = bbox
    crop = rgba[y0:y1, x0:x1]
    h, w = crop.shape[:2]
    scale = min((canvas * 0.74) / max(w, h), 1.8)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    crop = cv2.resize(crop, (nw, nh), interpolation=cv2.INTER_AREA)

    out = np.zeros((canvas, canvas, 4), np.uint8)
    x = (canvas - nw) // 2
    y = (canvas - nh) // 2
    out[y : y + nh, x : x + nw] = crop
    return out


def orientation_signature(img, bins=72):
    rgba = img.astype(np.float32) / 255.0
    alpha = rgba[:, :, 3]
    ys, xs = np.where(alpha > 0.05)
    if len(xs) == 0:
        return np.zeros((bins,), dtype=np.float32)

    weights = alpha[ys, xs]
    cx = float((xs * weights).sum() / weights.sum())
    cy = float((ys * weights).sum() / weights.sum())
    dx = xs.astype(np.float32) - cx
    dy = ys.astype(np.float32) - cy
    radius = np.sqrt(dx * dx + dy * dy)
    angle = (np.arctan2(dy, dx) + math.pi) / (2.0 * math.pi)

    gray = cv2.cvtColor((rgba[:, :, :3] * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    gray = gray.astype(np.float32) / 255.0
    radial_weight = 0.35 + 0.65 * radius / (float(radius.max()) + 1e-6)
    color_weight = 0.75 + 0.25 * (1.0 - gray[ys, xs])
    vote = weights * radial_weight * color_weight

    hist = np.zeros((bins,), dtype=np.float32)
    idx = np.floor(angle * bins).astype(np.int32) % bins
    np.add.at(hist, idx, vote)
    for _ in range(2):
        hist = (np.roll(hist, 1) + 2.0 * hist + np.roll(hist, -1)) / 4.0
    return ((hist - hist.mean()) / (hist.std() + 1e-6)).astype(np.float32)


def best_clockwise_clicks(candidate, reference):
    cand_sig = orientation_signature(candidate)
    ref_sig = orientation_signature(reference)
    step = len(ref_sig) // 6
    scores = []
    for orientation_offset in range(6):
        shifted = np.roll(cand_sig, -step * orientation_offset)
        scores.append(float(np.mean((shifted - ref_sig) ** 2)))
    orientation_offset = int(np.argmin(scores))
    clicks = (-orientation_offset) % 6
    confidence = (
        float(sorted(scores)[1] - scores[orientation_offset])
        if len(scores) > 1
        else 0.0
    )
    return int(clicks), float(scores[orientation_offset]), confidence


def solve_tile_clicks(image_paths):
    if not image_paths:
        return [], []
    images = [normalize_subject(path) for path in image_paths]
    reference = images[0]
    clicks = []
    details = []
    for path, img in zip(image_paths, images):
        click_num, score, confidence = best_clockwise_clicks(img, reference)
        all_scores = score_clicks(img, reference)
        clicks.append(click_num)
        details.append(
            {
                "path": path,
                "clicks_clockwise": click_num,
                "score": score,
                "confidence": confidence,
                "scores_by_click": all_scores,
            }
        )
    return clicks, details


def score_clicks(candidate, reference):
    cand_sig = orientation_signature(candidate)
    ref_sig = orientation_signature(reference)
    step = len(ref_sig) // 6
    scores = []
    for orientation_offset in range(6):
        shifted = np.roll(cand_sig, -step * orientation_offset)
        score = float(np.mean((shifted - ref_sig) ** 2))
        clicks = (-orientation_offset) % 6
        scores.append((clicks, score))
    scores.sort(key=lambda item: item[0])
    return [round(score, 6) for _, score in scores]


def _ensure_dir(path):
    if path and not os.path.exists(path):
        os.makedirs(path)
    return path


def _debug_dir(default_root, debug_dir=None):
    if debug_dir:
        return _ensure_dir(os.path.abspath(debug_dir))
    desktop_test_dir = os.path.join(os.path.expanduser("~"), "Desktop", "test")
    if os.path.isdir(desktop_test_dir):
        return _ensure_dir(os.path.join(desktop_test_dir, "temu_type1_debug"))
    return _ensure_dir(os.path.join(default_root, "temu_type1_debug"))


def _copy_debug_image(src_path, dst_path):
    img = imread_any(src_path)
    if img is None:
        return False
    return bool(cv2.imwrite(dst_path, img))


def _write_debug_sheet(image_paths, details, output_path):
    cells = []
    for index, path in enumerate(image_paths):
        img = imread_any(path)
        if img is None:
            continue
        if img.ndim == 2:
            bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            alpha = img[:, :, 3:4].astype(np.float32) / 255.0
            rgb = img[:, :, :3].astype(np.float32)
            bgr = (rgb * alpha + 255.0 * (1.0 - alpha)).astype(np.uint8)
        else:
            bgr = img[:, :, :3]
        thumb = cv2.resize(bgr, (150, 150), interpolation=cv2.INTER_AREA)
        cell = np.full((196, 170, 3), 255, dtype=np.uint8)
        cell[28:178, 10:160] = thumb
        click_text = str(details[index].get("clicks_clockwise", "?")) if index < len(details) else "?"
        cv2.putText(cell, "tile %d click %s" % (index + 1, click_text), (8, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
        cells.append(cell)
    if not cells:
        return False
    sheet = np.hstack(cells)
    return bool(cv2.imwrite(output_path, sheet))


def _write_debug_files(debug_dir, attempt, image_paths, image_sources, details, clicks):
    attempt_dir = _ensure_dir(os.path.join(debug_dir, "attempt_%02d" % attempt))
    copied = []
    for idx, path in enumerate(image_paths):
        dst = os.path.join(attempt_dir, "tile_%02d_input.png" % (idx + 1))
        _copy_debug_image(path, dst)
        copied.append(dst)
    sheet_path = os.path.join(attempt_dir, "debug_sheet.png")
    _write_debug_sheet(image_paths, details, sheet_path)
    report_path = os.path.join(attempt_dir, "debug_report.json")
    report = {
        "attempt": attempt,
        "clicks_clockwise": clicks,
        "image_sources": image_sources,
        "details": details,
        "copied_inputs": copied,
        "debug_sheet": sheet_path,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report_path, sheet_path


def apply_clicks(
    tile_nodes, clockwise_clicks, click_interval=0.15, probe_interval=0.35
):
    applied = []
    for idx, (node, desired_clicks) in enumerate(zip(tile_nodes, clockwise_clicks)):
        desired_clicks = int(desired_clicks) % 6
        if desired_clicks <= 0:
            applied.append(
                {
                    "index": idx,
                    "desired_clockwise": 0,
                    "actual_clicks": 0,
                    "direction": "none",
                }
            )
            continue

        before_deg = _get_node_rotate_deg(node)
        _click_node(node)
        sleep(probe_interval)
        after_deg = _get_node_rotate_deg(node)

        if _click_is_counterclockwise(before_deg, after_deg):
            actual_clicks = (6 - desired_clicks) % 6
            direction = "counterclockwise"
        else:
            actual_clicks = desired_clicks
            direction = "clockwise"

        for _ in range(1, actual_clicks):
            _click_node(node)
            sleep(click_interval)

        applied.append(
            {
                "index": idx,
                "desired_clockwise": desired_clicks,
                "actual_clicks": actual_clicks,
                "direction": direction,
                "before_deg": before_deg,
                "after_probe_deg": after_deg,
            }
        )
    return applied


def handle_captcha(
    web_page,
    image_ele,
    commit_ele=None,
    retry_count=5,
    tile_xpath=None,
    click_interval=0.15,
    skip_first=True,
    max_tiles=6,
    capture_mode="auto",
):
    cache_folder = _cache_folder()
    retry_count = _safe_int(retry_count, 5) or 5
    click_interval = _safe_float(click_interval, 0.15)
    last_result = None

    for attempt in range(retry_count):
        container_ele = _resolve_element(web_page, image_ele)
        if container_ele is None:
            raise Exception("Captcha container not found. Please check image_ele.")
        tile_nodes = _find_tile_nodes(
            container_ele,
            tile_xpath=tile_xpath,
            skip_first=skip_first,
            max_tiles=max_tiles,
        )
        if not tile_nodes:
            raise Exception(
                "No rotatable tile nodes found. Please check image_ele/tile_xpath."
            )
        if len(tile_nodes) < 2:
            raise Exception(
                "Need at least 2 rotatable tile nodes, got %s." % len(tile_nodes)
            )
        image_paths, image_sources = _save_tile_images(
            web_page, tile_nodes, cache_folder, capture_mode=capture_mode
        )
        clockwise_clicks, details = solve_tile_clicks(image_paths)


        applied = apply_clicks(
            tile_nodes,
            clockwise_clicks,
            click_interval=click_interval,
        )

        if commit_ele:
            commit_target = _resolve_element(web_page, commit_ele)
            if commit_target is None:
                raise Exception(
                    "Confirm element not found. Please check commit_ele/confirm_ele."
                )
            commit_target.click()
            sleep(2)
            try:
                if _resolve_element(web_page, image_ele, timeout=3) is None:
                    break
            except Exception:
                break
        else:
            break


def test_func():
    if "xbot_extensions" not in __file__:
        web_page = web.get_active("chrome")
        image_ele = package.selector("temu_1")
        commit_ele = package.selector("temu_2")
        handle_captcha(web_page, image_ele, commit_ele, retry_count=1)
        exit()

def main(args):
    test_func()
    web_page = args.get("web_page")
    image_ele = args.get("image_ele")
    commit_ele = args.get("commit_ele")
    retry_count = args.get("retry_count", 5)
    tile_xpath = args.get("tile_xpath")
    click_interval = args.get("click_interval", 0.15)
    skip_first = args.get("skip_first", True)
    max_tiles = args.get("max_tiles", 6)
    capture_mode = args.get("capture_mode", "auto")

    return handle_captcha(
        web_page,
        image_ele,
        commit_ele=commit_ele,
        retry_count=retry_count,
        tile_xpath=tile_xpath,
        click_interval=click_interval,
        skip_first=skip_first,
        max_tiles=_safe_int(max_tiles, 6),
        capture_mode=capture_mode,
    )
