"""Captcha payload and distance helpers taken from activity_jfbym.

Types are the ones in the ShadowBot sources. This module does not add
alternate captcha products or login URLs.

- std_slider_captcha / bank_captcha / jd slider: Yunma type 22222
- cs_temu_captcha (拼多多空间点选): type "9999"
- dy_slider_captcha: type "20225"
- zfb_four_click_captcha: type 276502, plus rotate() style parsing
- orangebank_slider_captcha: 影刀接口码 jfbym_22222 (no login flow shipped)
- 支付宝点选冰拓: captchaType 1311 (client host is not hardcoded here)
- 抖音文字点选: 影刀 web_service captcha_type 27 / ttshitu_27_predict
"""
from __future__ import annotations

import http.client
import json
import math
import re
from typing import List, Optional, Sequence, Tuple

from seller_common import SellerLoginError

YUNMA_HOST = "api.jfbym.com"
YUNMA_PATH = "/api/YmServer/customApi"

YUNMA_TYPE_STD_SLIDER = 22222
YUNMA_TYPE_BANK_SLIDER = 22222
YUNMA_TYPE_CS_TEMU = "9999"
YUNMA_TYPE_DY_SLIDER = "20225"
YUNMA_TYPE_ZFB_FOUR_CLICK = 276502
ORANGEBANK_INTERFACE_CODE = "jfbym_22222"
ZFB_BINGTOP_CLICK_TYPE = 1311
DOUYIN_TTSHITU_CLICK_TYPE = "27"
DOUYIN_TTSHITU_THIRD_PARTY = "ttshitu_27_predict"

ROTATE_RE = re.compile(r"rotate\(\s*(-?\d+(?:\.\d+)?)deg\s*\)")

EMAIL_CODE_RE_6 = re.compile(
    r"(?<![a-zA-Z0-9])([a-zA-Z0-9~`!@#$%^&*]{6})(?![a-zA-Z0-9])"
)
EMAIL_CODE_RE_4 = re.compile(
    r"(?<![a-zA-Z0-9])([a-zA-Z0-9~`!@#$%^&*]{4})(?![a-zA-Z0-9])"
)


def yunma_post(payload: dict, *, timeout: int = 60) -> dict:
    """POST api.jfbym.com/api/YmServer/customApi. Same host/path as std_slider."""
    conn = http.client.HTTPConnection(YUNMA_HOST, timeout=timeout)
    try:
        conn.request(
            "POST",
            YUNMA_PATH,
            body=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        response = conn.getresponse()
        raw = response.read().decode("utf-8")
    finally:
        conn.close()
    return json.loads(raw)


def std_slider_payload(image_b64: str, token: str) -> dict:
    return {"image": image_b64, "token": token, "type": YUNMA_TYPE_STD_SLIDER}


def std_slider_distance(unwrapped: dict, offset: int = 0, speed: float = 1) -> float:
    """Distance after ``ym_captcha_recognition(...).get('data')``.

    std_slider_captcha raises when the unwrapped object has ``success`` set,
    then uses ``int(data)`` and ``(distance + offset) / speed``.
    """
    if not isinstance(unwrapped, dict):
        raise SellerLoginError("云码返回缺少 data")
    if unwrapped.get("success"):
        raise SellerLoginError(str(unwrapped.get("msg") or "识别失败"))
    distance = int(unwrapped.get("data"))
    speed = speed or 1
    return (distance + int(offset)) / speed


def cs_temu_payload(image_b64: str, token: str, extra: str) -> dict:
    return {
        "image": image_b64,
        "token": token,
        "type": YUNMA_TYPE_CS_TEMU,
        "extra": extra,
    }


def parse_click_positions(data: str) -> List[Tuple[str, str]]:
    """``"x,y|x,y"`` as used by cs_temu_captcha and 抖音点选."""
    positions: List[Tuple[str, str]] = []
    for item in (data or "").split("|"):
        if not item:
            continue
        parts = item.split(",")
        if len(parts) < 2:
            continue
        positions.append((parts[0], parts[1]))
    return positions


def cs_temu_positions(response: dict) -> List[Tuple[str, str]]:
    if not isinstance(response, dict) or response.get("msg") != "识别成功":
        raise SellerLoginError("识别失败, 请重试")
    return parse_click_positions(response.get("data", {}).get("data") or "")


def dy_slider_payload(image_b64: str, token: str, *, gap_left: bool = False) -> dict:
    payload = {"image": image_b64, "token": token, "type": YUNMA_TYPE_DY_SLIDER}
    if gap_left:
        payload["extra"] = "true"
    return payload


def dy_recognized_px(response: dict) -> float:
    if not isinstance(response, dict) or response.get("msg") != "识别成功":
        raise SellerLoginError("识别服务未返回成功结果，未拖动")
    try:
        return float(response["data"]["data"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SellerLoginError("识别服务未返回有效距离数值，未拖动") from exc


def dy_slider_distance(
    recognized_px: float,
    pixel_scale: float,
    offset: float = 0,
    *,
    background_x: Optional[float] = None,
    piece_left: Optional[float] = None,
) -> float:
    """dy_slider_captcha: recognized_px * pixel_scale + offset, optional gap_left."""
    distance = float(recognized_px) * float(pixel_scale) + float(offset)
    if piece_left is not None:
        if background_x is None:
            raise SellerLoginError("gap_left 模式必须提供背景左边界")
        distance += float(background_x) - float(piece_left)
    if not math.isfinite(distance) or distance <= 0:
        raise SellerLoginError("换算后的拖动距离无效，未拖动")
    return distance


def zfb_four_click_payload(image_b64: str, token: str) -> dict:
    return {"image": image_b64, "token": token, "type": YUNMA_TYPE_ZFB_FOUR_CLICK}


def rotate_deg_from_style(style_text: str) -> Optional[float]:
    if not style_text:
        return None
    matched = ROTATE_RE.search(style_text)
    if not matched:
        return None
    try:
        return float(matched.group(1))
    except Exception:
        return None


def rotate_click_plan(angle: float, rotate_deg: Optional[float]) -> Tuple[int, int, Optional[str]]:
    """Match zfb_four_click_captcha: one click, then ``range(1, applied)``.

    Returns ``(first_clicks, extra_clicks, direction)``. ``first_clicks`` is 0
    when ``angle/90`` is not positive.
    """
    click_num = int(angle / 90)
    if click_num <= 0:
        return 0, 0, None
    if rotate_deg is not None and rotate_deg < 0:
        applied = (4 - click_num) % 4
        direction = "counterclockwise"
    else:
        applied = click_num
        direction = "clockwise"
    extra = max(applied - 1, 0) if applied >= 1 else 0
    return 1, extra, direction


def bank_slider_payload(image_b64: str, token: str) -> dict:
    return {"image": image_b64, "token": token, "type": YUNMA_TYPE_BANK_SLIDER}


def bank_slider_distance(response: dict, offset: int = 0, speed: float = 1) -> float:
    """bank_captcha checks ``msg == 识别成功`` on the full Yunma body."""
    if not isinstance(response, dict) or response.get("msg") != "识别成功":
        raise SellerLoginError(str((response or {}).get("msg") or "识别失败"))
    distance = int(response.get("data", {}).get("data"))
    speed = speed or 1
    return (distance + int(offset)) / speed


def orangebank_drag_px(
    captcha_result: float,
    gap_offset: float,
    offset_percent: float,
    ppi: float = 1.0,
) -> int:
    """orangebank_slider_captcha.drag after the 25px probe.

    ``captcha_result - gap_offset - 5``, then
    ``int((adjusted / offset_percent) * ppi - 25 * ppi)``.
    """
    adjusted = float(captcha_result) - float(gap_offset) - 5
    return int((adjusted / float(offset_percent)) * ppi - (25 * ppi))


def orangebank_yd_body(image_b64: str) -> dict:
    """Body shape of orangebank yd_recg (host comes from the 影刀 client)."""
    return {
        "thirdPartyInterfaceCode": ORANGEBANK_INTERFACE_CODE,
        "data": {},
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": {"image": image_b64},
            "pathVariable": {},
        },
        "bizType": "rpa-command",
    }


def bingtop_click_body(image_b64: str, captcha_type: int = ZFB_BINGTOP_CLICK_TYPE) -> dict:
    """zfb_login.handle_click_captcha payload before the 影刀 client wrapper."""
    return {"captchaData": image_b64, "captchaType": captcha_type}


def bingtop_interface_code(captcha_type: int = ZFB_BINGTOP_CLICK_TYPE) -> str:
    return f"captcha_bingtop_bingtop_{captcha_type}"


def douyin_click_service_args() -> dict:
    """Arguments process44 passes to xbot web_service.captcha. No endpoint URL."""
    return {
        "engine_type": "shadowbot",
        "captcha_type": DOUYIN_TTSHITU_CLICK_TYPE,
        "third_party_code": DOUYIN_TTSHITU_THIRD_PARTY,
        "image_source": "web_element",
    }


def extract_email_code(text: str) -> str:
    """process49: 6-char token, else 4-char token."""
    if not text:
        return ""
    found = EMAIL_CODE_RE_6.search(text)
    if found:
        return found.group(1)
    found = EMAIL_CODE_RE_4.search(text)
    return found.group(1) if found else ""


def require_yunma_token(token: str) -> str:
    if not token:
        raise SellerLoginError("云码 token 为空，无法识别验证码")
    return token


def click_points_from_origin(
    origin_x: float,
    origin_y: float,
    positions: Sequence[Tuple[str, str]],
) -> List[Tuple[float, float]]:
    points: List[Tuple[float, float]] = []
    for raw_x, raw_y in positions:
        points.append((origin_x + int(raw_x), origin_y + int(raw_y)))
    return points


# ---- types used by the remaining activity_7bca6d login blocks ----

YUNMA_TYPE_ALI_SLIDER = 20226
YUNMA_TYPE_ALPHANUM = "10103"
YUNMA_TYPE_KINGDEE_ALPHANUM = "10110"
ALPHANUM_CASE_EXTRA = "需要区分大小写"
TTSHITU_CDRCBANK_TYPE = "4"
TTSHITU_CDRCBANK_CODE = "ttshitu_4_predict"
TTSHITU_MYCCBANK_TYPE = "66"
TTSHITU_MYCCBANK_CODE = "ttshitu_66_predict"
YUNMA_TYPE_JD_CLICK = 30330
YUNMA_TYPE_JD_ROTATE = 30330
YUNMA_TYPE_JD_TRACE = 100015
YUNMA_TYPE_STD_CLICK_PLUS = 30009
STD_CLICK_PLUS_DIRECTION = "bottom"

TTSHITU_JD_LEGACY_SLIDER_TYPE = "18"
TTSHITU_JD_LEGACY_SLIDER_CODE = "ttshitu_18_predict"
TTSHITU_PDD_ONE_CLICK_TYPE = "19"
TTSHITU_PDD_ONE_CLICK_CODE = "ttshitu_19_predict"
TTSHITU_WANGDIANTONG_TYPE = "3"
TTSHITU_WANGDIANTONG_CODE = "ttshitu_3_predict"

AIKUCUN_FREE_SLIDER_OFFSET = -4
AIKUCUN_FREE_SLIDER_SPEED = "fast"
WALMART_HOLD_SECONDS = 7
MEITUAN_TRACE_SKIP = 25

_IMAGE_LEFT_RE = re.compile(r"(\d+),")


def alphanum_payload(image_b64: str, token: str, captcha_type: str = YUNMA_TYPE_ALPHANUM, *, case_sensitive: bool = False) -> dict:
    """std_alphanum_captcha body. Banks pass type 10103; 金蝶 uses 10110.

    When ``is_trim`` is true the source sets extra to 需要区分大小写.
    """
    payload = {"image": image_b64, "token": token, "type": captcha_type}
    if case_sensitive:
        payload["extra"] = ALPHANUM_CASE_EXTRA
    return payload


def orangebank_gap_offset(background_x: float, gap_x: float) -> float:
    """orangebank_slider_captcha.drag: gap left minus background left."""
    return float(gap_x) - float(background_x)


def ali_slider_payload(image_b64: str, token: str) -> dict:
    """ali_slider_captcha.recg body. Same type as the 千牛 port (20226)."""
    return {"image": image_b64, "token": token, "type": YUNMA_TYPE_ALI_SLIDER}


def jd_click_payload(image_b64: str, token: str) -> dict:
    """jd_click_select_captcha: type 30330, single image."""
    return {"image": image_b64, "token": token, "type": YUNMA_TYPE_JD_CLICK}


def jd_rotate_payload(big_b64: str, small_b64: str, token: str) -> dict:
    """jd_rotate_captcha: type 30330 plus image2."""
    return {
        "image": big_b64,
        "token": token,
        "type": YUNMA_TYPE_JD_ROTATE,
        "image2": small_b64,
    }


def jd_trace_payload(image_b64: str, token: str) -> dict:
    """jd_trace_captcha: type 100015. Not called by process6; kept for that module."""
    return {"image": image_b64, "token": token, "type": YUNMA_TYPE_JD_TRACE}


def std_click_plus_payload(image_b64: str, token: str, direction: str = STD_CLICK_PLUS_DIRECTION) -> dict:
    """std_click_select_captcha_plus.handle_captcha. process6 passes direction bottom."""
    return {
        "image": image_b64,
        "token": token,
        "type": YUNMA_TYPE_STD_CLICK_PLUS,
        "direction": direction,
    }


def jd_legacy_slider_distance(captcha_text: str, slider_width: float, ppi: float = 1.0) -> float:
    """process2: first ``(\\d+),`` plus the piece width, then times ppi."""
    matched = _IMAGE_LEFT_RE.search(captcha_text or "")
    if not matched:
        raise SellerLoginError("计算滑块距离未返回坐标")
    return (int(matched.group(1)) + float(slider_width)) * float(ppi)


def canny_match_x(background_png: bytes, piece_png: bytes) -> int:
    """activity_4f0f15d7.slider_captcha.get_x: Canny 150/152, TM_CCOEFF_NORMED."""
    import cv2
    import numpy as np

    bg_img = cv2.imdecode(np.frombuffer(background_png, np.uint8), cv2.IMREAD_UNCHANGED)
    tp_img = cv2.imdecode(np.frombuffer(piece_png, np.uint8), cv2.IMREAD_UNCHANGED)
    bg_edge = cv2.Canny(bg_img[:, :, :3], 150, 152)
    tp_edge = cv2.Canny(tp_img[:, :, :3], 150, 152)
    _score, _max_val, _min_loc, max_loc = cv2.minMaxLoc(
        cv2.matchTemplate(bg_edge, tp_edge, cv2.TM_CCOEFF_NORMED)
    )
    return int(max_loc[0])


def free_slider_drag_distance(
    match_x: float,
    offset: float,
    ppi: float = 1.0,
    *,
    windows: bool = False,
) -> int:
    """activity_4f0f15d7.slider_captcha: ``distance * ppi + offset``, then int.

    On Windows the source divides by ppi again before the int cast.
    """
    drag = float(match_x) * float(ppi) + float(offset)
    if windows:
        drag = drag / float(ppi or 1)
    return int(drag)


def meituan_slider_distance(background_width: float, slider_width: float) -> float:
    """process65: ``bound.width - bound_1.width``."""
    return float(background_width) - float(slider_width)


def meituan_trace_points(points: Sequence) -> list:
    """process65 replays ``time_ease(...)[25:]``. The easing function itself
    lives in ``resources.trace_api``, which is not in the export.
    """
    return list(points)[25:]


def legacy_click_point(
    raw_x: str,
    raw_y: str,
    prompt_left: float,
    prompt_top: float,
    bg_left: float,
    bg_top: float,
    ppi: float = 1.0,
) -> Tuple[int, int]:
    """activity_4db973e3.process21 点选1个坐标 screen point."""
    x = int(float(raw_x) * float(ppi)) + min(prompt_left, bg_left)
    y = int(float(raw_y) * float(ppi)) + min(prompt_top, bg_top)
    return int(x), int(y)
