# Shopee similarity move captcha.
# The detector combines silhouette edges, colour, local darkness and texture.

import base64
import json
import math
import os
import platform
import sys

import cv2
import numpy as np
import xbot
from xbot import print, sleep, web, win32
from xbot.selector import Selector

from .utils import _moveTo, get_ppi


machine = platform.machine().lower()
arch = "arm64" if "arm64" in machine or "aarch64" in machine else "x64"
base_path = os.path.dirname(
    os.path.dirname(os.environ.get("PYTHONPATH", os.path.abspath(__file__)))
)
cv_engine_path = os.path.join(base_path, f"support_{arch}/cv-engine/site-packages")
if os.path.exists(cv_engine_path):
    sys.path.append(cv_engine_path)


def decode_data_uri(data_uri: str):
    """Decode a data URI and keep its alpha channel."""
    if not data_uri:
        return None
    encoded = data_uri.split(",", 1)[-1]
    try:
        raw = base64.b64decode(encoded)
        return cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)
    except Exception:
        return None


def _get_image_src(web_page: xbot.web.WebBrowser, ele):
    """Read an image src, with a canvas fallback."""
    element = web_page.find(ele)
    src = element.get_attribute("src")
    if src:
        return src

    width = element.get_attribute("width")
    height = element.get_attribute("height")
    if not width or not height:
        return None
    return web_page.execute_javascript(
        "function(element, args) {"
        "  var d = JSON.parse(args);"
        "  var c = document.querySelector('canvas[width=\"' + d[0] + '\"][height=\"' + d[1] + '\"]');"
        "  return c ? c.toDataURL('image/png') : null;"
        "}",
        json.dumps([width, height]),
    )


def get_captcha_images(web_page: xbot.web.WebBrowser, bg_ele, piece_ele):
    """Extract the background and puzzle images."""
    bg = decode_data_uri(_get_image_src(web_page, bg_ele))
    piece = decode_data_uri(_get_image_src(web_page, piece_ele))
    return bg, piece


def _piece_mask(piece: np.ndarray) -> np.ndarray:
    """Build a foreground mask, preferring alpha."""
    if piece is None or piece.size == 0:
        return np.zeros((1, 1), dtype=np.uint8)

    if piece.ndim == 3 and piece.shape[2] == 4:
        alpha = piece[:, :, 3]
        mask = (alpha > 12).astype(np.uint8)
        if np.count_nonzero(mask) <= 20:
            mask = np.ones(alpha.shape, dtype=np.uint8)
    else:
        bgr = piece[:, :, :3] if piece.ndim == 3 else piece
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY) if bgr.ndim == 3 else bgr
        border = np.concatenate(
            [gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]]
        ).astype(np.float32)
        difference = np.abs(gray.astype(np.float32) - np.median(border))
        threshold = max(8.0, float(np.percentile(difference, 65)))
        mask = (difference > threshold).astype(np.uint8)
        if np.count_nonzero(mask) <= 20:
            mask = np.ones(gray.shape, dtype=np.uint8)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


def _prepare_piece(piece: np.ndarray):
    """Trim transparent padding and return crop, mask and original bbox."""
    mask = _piece_mask(piece)
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return None
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    return piece[y0:y1, x0:x1], mask[y0:y1, x0:x1], (x0, y0, x1 - x0, y1 - y0)


def _bgr(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return image[:, :, :3]


def _gray(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(_bgr(image), cv2.COLOR_BGR2GRAY)


def _edge_response(bg: np.ndarray) -> np.ndarray:
    gray = cv2.GaussianBlur(_gray(bg), (3, 3), 0)
    edges = cv2.Canny(gray, 30, 100)
    distance = cv2.distanceTransform(255 - edges, cv2.DIST_L2, 3)
    return np.exp(-distance / 2.0).astype(np.float32)


def _local_darkness(bg: np.ndarray) -> np.ndarray:
    gray = _gray(bg).astype(np.float32)
    dark = 255.0 - gray
    base = cv2.GaussianBlur(dark, (31, 31), 0)
    anomaly = np.clip(dark - base, 0, None)
    scale = max(float(np.percentile(anomaly, 95)), 1.0)
    return np.clip(anomaly / scale, 0, 1).astype(np.float32)


def _flatness(bg: np.ndarray) -> np.ndarray:
    gray = _gray(bg).astype(np.float32)
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    texture = cv2.GaussianBlur(
        np.sqrt(grad_x * grad_x + grad_y * grad_y), (31, 31), 0
    )
    scale = max(float(np.percentile(texture, 95)), 1.0)
    return (1.0 - np.clip(texture / scale, 0, 1)).astype(np.float32)


def _safe_match(response: np.ndarray, x: int, y: int) -> float:
    if response is None or response.size == 0:
        return 0.0
    value = float(response[y, x])
    return value if math.isfinite(value) else 0.0


def _pick_peaks(response: np.ndarray, count: int, radius: int):
    if response is None or response.size == 0:
        return []
    values = np.nan_to_num(response, nan=-1e6, posinf=-1e6, neginf=-1e6)
    order = np.argsort(values.ravel())[::-1]
    height, width = response.shape[:2]
    selected = []
    for index in order:
        y, x = divmod(int(index), width)
        if all(abs(x - px) > radius or abs(y - py) > radius for px, py in selected):
            selected.append((x, y))
            if len(selected) >= count:
                break
    return selected


def _rank_values(values):
    if not values:
        return []
    values = np.asarray(
        [value if math.isfinite(value) else 0.0 for value in values], dtype=np.float32
    )
    low, high = np.percentile(values, [10, 90])
    scale = max(float(high - low), 1e-6)
    return [float(np.clip((value - low) / scale, 0, 1)) for value in values]


def _template_features(piece: np.ndarray, mask: np.ndarray):
    gray = cv2.GaussianBlur(_gray(piece), (3, 3), 0)
    image_edges = (cv2.Canny(gray, 30, 100) > 0).astype(np.float32)
    mask_edges = (
        cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    ).astype(np.float32)
    edges = np.maximum(image_edges * 0.65, mask_edges)
    return gray, (mask > 0).astype(np.uint8) * 255, cv2.dilate(
        edges, np.ones((3, 3), np.uint8)
    ).astype(np.float32)


def find_similarity_target(bg: np.ndarray, piece: np.ndarray):
    """Find a target position in image coordinates."""
    if bg is None or piece is None:
        return None
    prepared = _prepare_piece(piece)
    if prepared is None:
        return None

    piece_crop, piece_mask, original_bbox = prepared
    bg_gray = cv2.GaussianBlur(_gray(bg), (3, 3), 0)
    edge_map = _edge_response(bg)
    dark_map = _local_darkness(bg)
    flat_map = _flatness(bg)
    bg_height, bg_width = bg_gray.shape[:2]
    candidates = []

    for scale in np.linspace(0.82, 1.10, 15):
        height = max(5, int(round(piece_crop.shape[0] * float(scale))))
        width = max(5, int(round(piece_crop.shape[1] * float(scale))))
        if height > bg_height or width > bg_width:
            continue

        interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
        scaled = cv2.resize(piece_crop, (width, height), interpolation=interpolation)
        scaled_mask = cv2.resize(
            piece_mask, (width, height), interpolation=cv2.INTER_NEAREST
        )
        template_gray, template_mask, template_edges = _template_features(
            scaled, scaled_mask
        )
        edge_weight = max(float(template_edges.sum()), 1.0)
        if edge_weight < 20:
            continue

        edge_scores = cv2.matchTemplate(
            edge_map, template_edges, cv2.TM_CCORR
        ) / edge_weight
        mask_float = template_mask.astype(np.float32) / 255.0
        mask_area = max(float(np.count_nonzero(template_mask)), 1.0)
        dark_scores = cv2.matchTemplate(
            dark_map, mask_float, cv2.TM_CCORR
        ) / mask_area
        flat_scores = cv2.matchTemplate(
            flat_map, mask_float, cv2.TM_CCORR
        ) / mask_area
        try:
            color_scores = cv2.matchTemplate(
                bg_gray, template_gray, cv2.TM_CCORR_NORMED, mask=template_mask
            )
        except cv2.error:
            color_scores = np.zeros_like(edge_scores)
        color_scores = np.nan_to_num(color_scores, nan=0.0, posinf=0.0, neginf=0.0)

        radius = max(8, int(min(width, height) * 0.45))
        locations = _pick_peaks(edge_scores, 8, radius)
        locations += _pick_peaks(color_scores, 5, radius)
        locations += _pick_peaks(dark_scores, 3, radius)
        locations += _pick_peaks(flat_scores, 3, radius)
        scale_prior = math.exp(-abs(math.log(max(float(scale), 1e-6))) / 0.18)
        for x, y in locations:
            candidates.append(
                {
                    "x": int(x),
                    "y": int(y),
                    "width": width,
                    "height": height,
                    "scale": float(scale),
                    "edge": _safe_match(edge_scores, x, y),
                    "color": max(0.0, _safe_match(color_scores, x, y)),
                    "dark": _safe_match(dark_scores, x, y),
                    "flat": _safe_match(flat_scores, x, y),
                    "scale_prior": scale_prior,
                }
            )

    if not candidates:
        return None

    edge_rank = _rank_values([candidate["edge"] for candidate in candidates])
    color_rank = _rank_values([candidate["color"] for candidate in candidates])
    dark_rank = _rank_values([candidate["dark"] for candidate in candidates])
    flat_rank = _rank_values([candidate["flat"] for candidate in candidates])
    for index, candidate in enumerate(candidates):
        candidate["score"] = (
            0.38 * edge_rank[index]
            + 0.20 * color_rank[index]
            + 0.17 * dark_rank[index]
            + 0.15 * flat_rank[index]
            + 0.10 * candidate["scale_prior"]
        )

    best = dict(max(candidates, key=lambda candidate: candidate["score"]))
    best["center"] = (
        best["x"] + best["width"] / 2.0,
        best["y"] + best["height"] / 2.0,
    )
    best["piece_bbox"] = original_bbox
    best["piece_size"] = (int(piece.shape[1]), int(piece.shape[0]))
    return best


def _save_debug_image(bg: np.ndarray, result: dict, path: str):
    """Save a background with the detected target rectangle."""
    if not path or not result:
        return
    image = _bgr(bg).copy()
    x, y = result["x"], result["y"]
    right = x + result["width"]
    bottom = y + result["height"]
    center = tuple(int(round(value)) for value in result["center"])
    cv2.rectangle(image, (x, y), (right, bottom), (0, 220, 0), 2)
    cv2.drawMarker(image, center, (0, 0, 255), cv2.MARKER_CROSS, 13, 2)
    label = f"target {center} score={result['score']:.2f} scale={result['scale']:.2f}"
    cv2.putText(
        image, label, (4, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.38,
        (0, 255, 255), 1, cv2.LINE_AA
    )
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    cv2.imwrite(path, image)


def _element_box(web_page, ele):
    values = web_page.find(ele).get_bounding(to96dpi=False)
    return tuple(float(value) for value in values)


def _target_delta(web_page, bg_ele, piece_ele, bg, result, offset_x, offset_y):
    bg_x, bg_y, bg_width, bg_height = _element_box(web_page, bg_ele)
    piece_x, piece_y, element_width, element_height = _element_box(web_page, piece_ele)
    image_height, image_width = bg.shape[:2]
    target_x = bg_x + result["center"][0] * bg_width / image_width + float(offset_x)
    target_y = bg_y + result["center"][1] * bg_height / image_height + float(offset_y)

    x0, y0, piece_width, piece_height = result["piece_bbox"]
    image_piece_width, image_piece_height = result["piece_size"]
    current_x = piece_x + (x0 + piece_width / 2.0) * element_width / max(image_piece_width, 1)
    current_y = piece_y + (y0 + piece_height / 2.0) * element_height / max(image_piece_height, 1)
    return target_x - current_x, target_y - current_y


def _apply_dpi_compensation(dx, dy, enabled=True):
    """Convert a page-coordinate delta to a pointer-coordinate delta."""
    if not enabled or os.name != "nt":
        return dx, dy
    ppi = get_ppi()
    if not ppi:
        return dx, dy
    return dx / ppi, dy / ppi


def ease_drag(web_page, piece_ele, target_dx: float, target_dy: float = 0.0):
    """Drag in two dimensions with a short eased path."""
    x, y, width, height = _element_box(web_page, piece_ele)
    start_x, start_y = x + width / 2.0, y + height / 2.0
    distance = max(math.hypot(target_dx, target_dy), 1.0)
    steps = max(12, min(60, int(distance / 6.0)))
    pressed = False
    try:
        _moveTo(start_x, start_y)
        sleep(0.1)
        win32.mouse_click(button="left", click_type="down", delay_after=0)
        pressed = True
        sleep(0.16)
        for index in range(1, steps + 1):
            progress = index / float(steps)
            eased = 1.0 - (1.0 - progress) ** 2
            jitter = math.sin(progress * math.pi * 3.0) * 0.45
            _moveTo(
                start_x + target_dx * eased,
                start_y + target_dy * eased + jitter,
            )
            sleep(0.035 if progress < 0.85 else 0.055)
        sleep(0.2)
    finally:
        if pressed:
            win32.mouse_click(button="left", click_type="up")


def _selector_given(selector) -> bool:
    return selector is not None and selector != ""


def _is_visible(web_page, ele) -> bool:
    if not _selector_given(ele):
        return False
    try:
        if not web_page.is_element_displayed(ele):
            return False
        _, _, width, height = web_page.find(ele).get_bounding()
        return float(width) > 0 and float(height) > 0
    except Exception:
        return False


def _wait_piece_hidden(web_page, piece_ele, checks=50, interval=0.5):
    """Treat success only after the piece stays hidden across several checks."""
    for index in range(max(1, int(checks))):
        if _is_visible(web_page, piece_ele):
            return False
        if index + 1 < checks:
            sleep(interval)
    return True


def handle_captcha(
    web_page: xbot.web.WebBrowser,
    bg_ele,
    piece_ele,
    verify_ele="",
    refresh_ele="",
    retry_count: int = 5,
    offset_x: float = 0,
    offset_y: float = 0,
    wait_time: float = 2,
    min_score: float = 0.30,
    debug: bool = False,
    debug_dir: str = "",
    dpi_compensation: bool = True,
    position_correction: bool = True,
):
    """Solve the captcha and return True after a completed attempt."""
    for attempt in range(max(1, int(retry_count))):
        if attempt > 0 and _selector_given(refresh_ele):
            try:
                web_page.find(refresh_ele).click()
            except Exception as error:
                if debug:
                    print(f"[captcha move] refresh failed: {error}")
        sleep(wait_time)

        bg, piece = get_captcha_images(web_page, bg_ele, piece_ele)
        result = find_similarity_target(bg, piece)
        if result is None or result["score"] < float(min_score):
            if debug:
                score = result["score"] if result else 0.0
                print(f"[captcha move] attempt {attempt + 1}: low score {score:.3f}")
            continue

        if debug:
            print(
                f"[captcha move] attempt {attempt + 1}: "
                f"target=({result['center'][0]:.1f}, {result['center'][1]:.1f}) "
                f"score={result['score']:.3f} scale={result['scale']:.2f}"
            )
        if debug_dir:
            _save_debug_image(
                bg, result, os.path.join(debug_dir, f"move_{attempt + 1:02d}.png")
            )

        dx, dy = _target_delta(
            web_page, bg_ele, piece_ele, bg, result, offset_x, offset_y
        )

        raw_dx, raw_dy = dx, dy
        dx, dy = _apply_dpi_compensation(dx, dy, dpi_compensation)
        if debug and (raw_dx != dx or raw_dy != dy):
            print(
                f"[captcha move] coordinate delta: "
                f"({raw_dx:.1f}, {raw_dy:.1f}) -> ({dx:.1f}, {dy:.1f})"
            )
        
        before_box = _element_box(web_page, piece_ele)
        ease_drag(web_page, piece_ele, dx, dy)
        sleep(0.45)

        # Browser drag handlers and display scaling can leave a systematic
        # residual. Measure the real movement and correct it once.
        if position_correction:
            try:
                after_box = _element_box(web_page, piece_ele)
                residual_dx, residual_dy = _target_delta(
                    web_page, bg_ele, piece_ele, bg, result, offset_x, offset_y
                )
                actual_dx = after_box[0] - before_box[0]
                actual_dy = after_box[1] - before_box[1]
                correction_dx = residual_dx
                correction_dy = residual_dy
                if abs(actual_dx) > 1.0 and abs(dx) > 1.0:
                    correction_dx *= dx / actual_dx
                if abs(actual_dy) > 1.0 and abs(dy) > 1.0:
                    correction_dy *= dy / actual_dy
                if math.hypot(residual_dx, residual_dy) > 3.0:
                    if debug:
                        print(
                            f"[captcha move] residual: "
                            f"({residual_dx:.1f}, {residual_dy:.1f}), "
                            f"correction: ({correction_dx:.1f}, {correction_dy:.1f})"
                        )
                    ease_drag(web_page, piece_ele, correction_dx, correction_dy)
                    sleep(0.35)
            except Exception as error:
                if debug:
                    print(f"[captcha move] position correction skipped: {error}")

        if _selector_given(verify_ele):
            try:
                web_page.find(verify_ele).click()
            except Exception as error:
                if debug:
                    print(f"[captcha move] verify click failed: {error}")
        sleep(1.5)

        # A hidden verify button is not proof of success: failed attempts can
        # briefly rebuild or hide that button. Only the draggable piece's
        # stable disappearance ends the retry loop.
        if _wait_piece_hidden(web_page, piece_ele):
            return True
        if debug:
            remaining = int(retry_count) - attempt - 1
            print(f"[captcha move] verification failed; retries left: {max(remaining, 0)}")
    return False


def test_func() -> None:
    """Local example using the selectors from the current Shopee page."""
    if "xbot_extensions" in __file__:
        return
    web_page = web.get_active("chrome")

    def select_ele(xpath):
        data = {
            "id": "captcha-move-local",
            "name": "captcha-move-local",
            "type": "simple",
            "xpath": {"enable": "true", "segments": [xpath]},
        }
        return Selector(data)

    bg_ele = select_ele('/html/body/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div[2]/div[2]/div[1]/div/div[1]/canvas')
    piece_ele = select_ele('/html/body/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div[2]/div[2]/div[1]/div/div[1]/div/img')
    refresh_ele = select_ele('/html/body/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div[2]')
    verify_ele = select_ele('/html/body/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div[2]/div[2]/div[1]/div/div[2]/button')

    return handle_captcha(
        web_page, bg_ele, piece_ele,
        verify_ele=verify_ele, refresh_ele=refresh_ele,
        dpi_compensation=True,position_correction=True)


def main(args):
    # test_func()
    """Workflow entry point."""
    web_page = args.get("web_page")
    return handle_captcha(
        web_page=web_page,
        bg_ele=args.get("bg_ele"),
        piece_ele=args.get("piece_ele"),
        verify_ele=args.get("verify_ele"),
        refresh_ele=args.get("refresh_ele"),
        retry_count=args.get("retry_count", 5),
        offset_x=args.get("offset_x", 0),
        offset_y=args.get("offset_y", 0),
        wait_time=args.get("wait_time", 2),
        min_score=args.get("min_score", 0.30),
        debug=args.get("debug", False),
        debug_dir=args.get("debug_dir", ""),
        dpi_compensation=args.get("dpi_compensation", True),
        position_correction=args.get("position_correction", True),
    )
