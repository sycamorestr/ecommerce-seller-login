"""Playwright port of 影刀「支付宝登录」.

process20.py calls ``zfb_login.zfb_login``. URLs and xpaths are from
``zfb_login.py``. ``alipay_login.py`` uses the same login URL and stops on
``https://authsa127.alipay.com/login/checkSecurity.htm`` (SMS).

Captcha, in the order ``zfb_login.handle_captcha`` checks them:

- slider: ``#puzzle_backimg`` / ``#puzzle_slot`` / ``div.dv_handler.baseslider``
  (local CV in the source; this port drags only when a distance is supplied
  or OpenCV is installed)
- point-click: ``div.jshield-captcha-click-container.click``, 冰拓 type 1311
  (影刀 client). Without a ``click_recognizer``, this raises NeedsHumanError.
- four-image rotate: ``zfb_four_click_captcha`` Yunma type 276502
"""
from __future__ import annotations

import base64
import os
from typing import Callable, List, Optional, Tuple

from playwright.sync_api import Browser, BrowserContext, Page, Playwright

import captcha_helpers as captcha
from seller_common import (
    CredentialsRejected,
    NeedsHumanError,
    OnError,
    SellerLoginError,
    SellerLoginResult,
    close_result,
    fill_checked,
    finish,
    goto_with_retry,
    mouse_drag,
    open_page,
    sleep,
    visible,
    xpath_visible,
)

LOGIN_URL = "https://auth.alipay.com/login/index.htm"
PHONE_VERIFY_URL = "https://authsa127.alipay.com/login/checkSecurity.htm"

XPATH_ACCOUNT_TAB = '//li[@data-status="show_login"]'
XPATH_USERNAME = '//input[@id="J-input-user"]'
XPATH_PASSWORD = '//input[@id="password_rsainput"]'
XPATH_SUBMIT = '//input[@id="J-login-simulate-btn"]'
XPATH_ERROR = '//div[@id="J-errorBox"]/span[@class="sl-error-text"]'

XPATH_CLICK = '//div[@class="jshield-captcha-click-container click"]'
XPATH_BG = '//img[@id="puzzle_backimg"]'
XPATH_SLOT = '//div[@id="puzzle_slot"]'
XPATH_DRAG = '//div[@class="dv_handler baseslider"]'
XPATH_FEEDBACK = '//div[@class="jshield-feedback-wrapper captcha"]'
XPATH_FEEDBACK_CLOSE = '//img[@class="jshield-feedback-close captcha"]'
XPATH_REFRESH = '(//img[@class="refresh-button-img puzzle"])[2]'
XPATH_FOUR = '//*[@class="image-item clickpuzzle"]'
XPATH_FOUR_BG = '//div[@class="image-container clickpuzzle"]'
XPATH_FOUR_OK = '//div[contains(@class, "confirm-button")]'


def _png(locator) -> str:
    return base64.b64encode(locator.screenshot(type="png")).decode("ascii")


def _count(page: Page, xpath: str) -> int:
    try:
        return page.locator(f"xpath={xpath}").count()
    except Exception:
        return 0


def _solve_four(page: Page, token: str, calls: List[int]) -> None:
    captcha.require_yunma_token(token)
    image_loc = page.locator(f"xpath={XPATH_FOUR_BG}").first
    image = _png(image_loc)
    response = captcha.yunma_post(captcha.zfb_four_click_payload(image, token))
    calls[0] += 1
    data = response.get("data")
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        items = data["data"]
    elif isinstance(data, list):
        items = data
    else:
        items = data if isinstance(data, list) else []
    box = image_loc.bounding_box() or {"x": 0, "y": 0}
    for item in items:
        angle = float(item.get("angle") or 0)
        pos = item.get("pos") or [0, 0]
        style = ""
        try:
            style = page.locator(f"xpath={XPATH_FOUR}").first.get_attribute("style") or ""
        except Exception:
            style = ""
        rotate_deg = captcha.rotate_deg_from_style(style)
        first, extra, _direction = captcha.rotate_click_plan(angle, rotate_deg)
        if first <= 0:
            continue
        x = box["x"] + int(pos[0])
        y = box["y"] + int(pos[1])
        page.mouse.click(x, y)
        sleep(0.35)
        for _ in range(extra):
            page.mouse.click(x, y)
            sleep(0.15)
    if xpath_visible(page, XPATH_FOUR_OK, timeout=2):
        page.locator(f"xpath={XPATH_FOUR_OK}").first.click(timeout=5000)


def _solve_slider(page: Page, distance: Optional[float]) -> None:
    if distance is None:
        distance = _cv_distance(page)
    drag = page.locator(f"xpath={XPATH_DRAG}").first
    box = drag.bounding_box()
    if not box or distance is None:
        return
    x1 = box["x"] + box["width"] / 2
    y1 = box["y"] + box["height"] / 2
    mouse_drag(page, x1, y1, x1 + float(distance), y1)


def _cv_distance(page: Page) -> Optional[float]:
    """Optional OpenCV gap match. The source splits the background around the slot."""
    try:
        import cv2  # type: ignore
        import numpy as np
    except Exception as exc:
        raise SellerLoginError("支付宝滑块需要 opencv-python 计算缺口，或人工处理") from exc
    bg = page.locator(f"xpath={XPATH_BG}").first
    slot = page.locator(f"xpath={XPATH_SLOT}").first
    bg_box = bg.bounding_box()
    slot_box = slot.bounding_box()
    if not bg_box or not slot_box:
        return None
    raw = bg.screenshot(type="png")
    image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return None
    scale = image.shape[1] / bg_box["width"] if bg_box["width"] else 1
    cut = int((slot_box["x"] - bg_box["x"]) * scale)
    cut = max(1, min(cut, image.shape[1] - 2))
    left = image[:, :cut]
    right = image[:, cut:]
    if left.size == 0 or right.size == 0:
        return None
    bg_edge = cv2.Canny(right, 150, 152)
    tp_edge = cv2.Canny(left, 150, 152)
    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
    if tp_pic.shape[0] > bg_pic.shape[0] or tp_pic.shape[1] > bg_pic.shape[1]:
        return None
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    _min, _max, _min_loc, max_loc = cv2.minMaxLoc(res)
    return float(max_loc[0] + left.shape[1]) / scale


def handle_captcha(
    page: Page,
    token: str,
    retry_count: int,
    calls: List[int],
    click_recognizer: Optional[Callable[[str], str]],
) -> None:
    click_count = 0
    for _ in range(max(int(retry_count), 1) * 4):
        if xpath_visible(page, XPATH_FEEDBACK, timeout=0.6):
            try:
                page.locator(f"xpath={XPATH_FEEDBACK_CLOSE}").first.click(timeout=2000)
                page.locator(f"xpath={XPATH_REFRESH}").first.click(timeout=2000)
            except Exception:
                pass
        if xpath_visible(page, XPATH_BG, timeout=0.8):
            _solve_slider(page, None)
        elif xpath_visible(page, XPATH_CLICK, timeout=0.8):
            if click_count >= int(retry_count):
                raise SellerLoginError("支付宝验证码处理失败")
            if click_recognizer is None:
                raise NeedsHumanError("点选验证码")
            image = _png(page.locator(f"xpath={XPATH_CLICK}").first)
            raw = click_recognizer(image)
            box = page.locator(f"xpath={XPATH_CLICK}").first.bounding_box() or {"x": 0, "y": 0}
            for x, y in captcha.click_points_from_origin(box["x"], box["y"], captcha.parse_click_positions(raw)):
                page.mouse.click(x, y)
                sleep(0.3)
            click_count += 1
        elif _count(page, XPATH_FOUR) == 4:
            _solve_four(page, token, calls)
        else:
            break
        sleep(1)


def login(
    account: str,
    password: str,
    token: str,
    retry_count: int,
    page: Optional[Page] = None,
    *,
    click_recognizer: Optional[Callable[[str], str]] = None,
) -> Tuple[Page, int, List[str], Optional[Browser], Optional[BrowserContext], Optional[Playwright]]:
    if not str(retry_count).isdigit() and not isinstance(retry_count, int):
        raise SellerLoginError(f"retry_count 应该是数字, 而不是{retry_count}")
    retry_count = int(retry_count)
    calls = [0]
    shots: List[str] = []
    page, owned = open_page(page, headless=False)
    if LOGIN_URL not in (page.url or ""):
        goto_with_retry(page, LOGIN_URL, attempts=3, timeout_ms=60000)
    if xpath_visible(page, XPATH_ACCOUNT_TAB, timeout=10):
        page.locator(f"xpath={XPATH_ACCOUNT_TAB}").first.click(timeout=10000)
        sleep(1)
    user = page.locator(f"xpath={XPATH_USERNAME}").first
    user.wait_for(state="visible", timeout=20000)
    user.click()
    fill_checked(user, account, limit=3)
    fill_checked(page.locator(f"xpath={XPATH_PASSWORD}").first, password, limit=3)
    page.locator(f"xpath={XPATH_SUBMIT}").first.click(timeout=10000)
    sleep(2)
    handle_captcha(page, token, retry_count, calls, click_recognizer)
    if PHONE_VERIFY_URL in (page.url or ""):
        raise NeedsHumanError("请先填写手机验证码登录")
    if xpath_visible(page, XPATH_ERROR, timeout=2):
        text = (page.locator(f"xpath={XPATH_ERROR}").first.inner_text(timeout=1000) or "").strip()
        if text:
            raise CredentialsRejected(f"登录失败, 错误元素: {text}")
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def alipay_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    retries: int = 10,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
    click_recognizer: Optional[Callable[[str], str]] = None,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("ALIPAY_ACCOUNT", "")
    password = password if password is not None else os.environ.get("ALIPAY_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if not account or not password:
        raise ValueError("缺少支付宝账号或密码")

    def _run(page=None, **_ignored):
        return login(
            account,
            password,
            yunma_token,
            retries,
            page=page,
            click_recognizer=click_recognizer,
        )

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = alipay_login(retries=int(os.environ.get("ALIPAY_RETRIES", "10")))
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
