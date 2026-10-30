"""Playwright port of 影刀「抖店登录」 process4.py.

Also runs process48 (滑块 process45 → dy_slider_captcha type 20225, and
文字点选 process44 → captcha_type 27) and process49 (邮箱验证码正则).

The 图鉴/影刀点选 HTTP endpoint is not in the source (it goes through
``web_service.captcha``). Pass ``click_recognizer`` to supply ``"x,y|x,y"``.
Without it, a visible point-and-click captcha raises NeedsHumanError.
"""
from __future__ import annotations

import base64
import os
from typing import Callable, List, Optional, Tuple

from playwright.sync_api import Browser, BrowserContext, FrameLocator, Page, Playwright

import captcha_helpers as captcha
from seller_common import (
    NeedsHumanError,
    OnError,
    SellerLoginError,
    SellerLoginResult,
    close_result,
    detect_human_text,
    fill_checked,
    finish,
    goto_with_retry,
    mouse_drag,
    open_page,
    page_text,
    sleep,
    visible,
    xpath_visible,
)

LOGIN_URL = "https://fxg.jinritemai.com/login/common"
LOGIN_URL_SHORT = "https://fxg.jinritemai.com/login"
EMAIL_REQUIRED = "需要进行邮箱验证， 请正确填写【验证邮箱】和【授权码】后重试！"

XPATH_SWITCH = '//*[@class="login-switcher--qr" or @class="login-switcher--cell"]'
XPATH_EMAIL_TAB = '//div[contains(text(), "邮箱登录")]/span/..'
XPATH_EMAIL = "//input[@placeholder='请输入邮箱']"
XPATH_PASSWORD = "//input[@placeholder='密码']"
XPATH_CLICK_BAR = '//*[@id="verify-bar-code"]'
XPATH_CLICK_BOX = '//div[contains(@class, "captcha_verify_container")]'
XPATH_CONFIRM = '//*[text()="确认"]'
XPATH_MAIL_TAB = '//div[text()="邮箱"]'
XPATH_SEND_CODE = '//div[text()="发送验证码"]'
XPATH_CODE_INPUT = '//input[@placeholder="验证码"]'
XPATH_VERIFY_BTN = '//button[text()="验证"]'
XPATH_ENTER_SHOP = '(//div[text()="进入店铺"])[1]'
XPATH_HEADER_SHOP = '//*[contains(@class, "headerShopName")]'

SEL_LOGIN = "button.account-center-action-button"
SEL_AGREE = "input.auxo-checkbox-input"
SEL_TARGET_SLIDER = "div.captcha-slider-btn"
SEL_BG_IFRAME = "img#captcha_verify_image"
SEL_CANVAS_BG = "canvas#captcha-verify-image"
SEL_DRAG_FALLBACK = "div[class*='secsdk-captcha-drag-icon']"
SEL_REFRESH = "div.vc-captcha-refresh"
SEL_BACK = "div[class*='backbar']"
SEL_FIRST_SHOP = "div[class*='roleitem']"


def _frame(page: Page) -> FrameLocator:
    return page.frame_locator("iframe")


def _iframe_slider(page: Page) -> bool:
    try:
        loc = _frame(page).locator(SEL_TARGET_SLIDER).first
        loc.wait_for(state="visible", timeout=800)
        return True
    except Exception:
        return False


def _png_and_scale(locator) -> tuple:
    """Element PNG plus dy_slider pixel_scale (CSS width / image width)."""
    from io import BytesIO

    from PIL import Image

    raw = locator.screenshot(type="png")
    image = Image.open(BytesIO(raw))
    box = locator.bounding_box() or {}
    css_w = float(box.get("width") or image.size[0] or 1)
    scale = css_w / float(image.size[0] or 1)
    return base64.b64encode(raw).decode("ascii"), scale


def _solve_dy_slider(page: Page, token: str, calls: List[int]) -> None:
    captcha.require_yunma_token(token)
    if _iframe_slider(page):
        root = _frame(page)
        background = root.locator(SEL_BG_IFRAME).first
        drag = root.locator(SEL_TARGET_SLIDER).first
    else:
        background = page.locator(SEL_CANVAS_BG).first
        drag = page.locator(SEL_DRAG_FALLBACK).first
    image, pixel_scale = _png_and_scale(background)
    response = captcha.yunma_post(captcha.dy_slider_payload(image, token, gap_left=False))
    calls[0] += 1
    recognized = captcha.dy_recognized_px(response)
    distance = captcha.dy_slider_distance(recognized, pixel_scale=pixel_scale, offset=0)
    drag_box = drag.bounding_box()
    if not drag_box:
        return
    x1 = drag_box["x"] + drag_box["width"] / 2
    y1 = drag_box["y"] + drag_box["height"] / 2
    mouse_drag(page, x1, y1, x1 + distance, y1)


def _solve_click(
    page: Page,
    recognizer: Optional[Callable[[str], str]],
) -> None:
    if not xpath_visible(page, XPATH_CLICK_BAR, timeout=1):
        return
    box_loc = page.locator(f"xpath={XPATH_CLICK_BOX}").first
    try:
        box_loc.wait_for(state="visible", timeout=3000)
    except Exception:
        box_loc = page.locator(f"xpath={XPATH_CLICK_BAR}").first
    if recognizer is None:
        raise NeedsHumanError("文字点选验证")
    image = _png(box_loc)
    raw = recognizer(image)
    positions = captcha.parse_click_positions(raw)
    box = box_loc.bounding_box()
    if not box:
        return
    # process44 hovers the captcha top-left, then moves by each "x,y" from the current mouse.
    for x, y in captcha.click_points_from_origin(box["x"], box["y"], positions):
        page.mouse.click(x, y)
        sleep(0.3)
    if xpath_visible(page, XPATH_CONFIRM, timeout=2):
        page.locator(f"xpath={XPATH_CONFIRM}").first.click(timeout=5000)


def verify_platform(
    page: Page,
    token: str,
    retries: int,
    calls: List[int],
    recognizer: Optional[Callable[[str], str]],
) -> None:
    """process48: slider if 抖店_目标滑块_ifream, else point-select if verify-bar-code."""
    for _ in range(max(int(retries), 1)):
        if _iframe_slider(page) or visible(page, SEL_CANVAS_BG, timeout=0.8):
            _solve_dy_slider(page, token, calls)
            sleep(1)
            if _iframe_slider(page):
                try:
                    _frame(page).locator(SEL_REFRESH).first.click(timeout=1500)
                except Exception:
                    pass
        if xpath_visible(page, XPATH_CLICK_BAR, timeout=0.8):
            _solve_click(page, recognizer)
        if not _iframe_slider(page) and not xpath_visible(page, XPATH_CLICK_BAR, timeout=0.5):
            if not visible(page, SEL_CANVAS_BG, timeout=0.5):
                break


def verify_email(
    page: Page,
    mailbox: str,
    auth_code: str,
    email_code: str,
    token: str,
    retries: int,
    calls: List[int],
    recognizer: Optional[Callable[[str], str]],
) -> None:
    """process49 input/click steps. Mail fetch is not bundled; pass email_code."""
    if xpath_visible(page, XPATH_MAIL_TAB, timeout=2):
        page.locator(f"xpath={XPATH_MAIL_TAB}").first.click(timeout=5000)
    if not xpath_visible(page, XPATH_SEND_CODE, timeout=2):
        return
    if not email_code and (not mailbox or not auth_code):
        raise SellerLoginError(EMAIL_REQUIRED)
    page.locator(f"xpath={XPATH_SEND_CODE}").first.click(timeout=5000)
    code = email_code or ""
    if not code:
        raise NeedsHumanError("邮箱验证")
    code = captcha.extract_email_code(code) or code
    fill_checked(page.locator(f"xpath={XPATH_CODE_INPUT}").first, code, limit=3)
    page.keyboard.press("Enter")
    sleep(1)
    if xpath_visible(page, XPATH_VERIFY_BTN, timeout=3):
        try:
            page.locator(f"xpath={XPATH_VERIFY_BTN}").first.click(timeout=5000)
        except Exception:
            pass
    verify_platform(page, token, retries, calls, recognizer)


def login(
    username: str,
    password: str,
    token: str,
    retry_count: int,
    page: Optional[Page] = None,
    *,
    mailbox: str = "",
    auth_code: str = "",
    email_code: str = "",
    logout_existing: bool = False,
    click_recognizer: Optional[Callable[[str], str]] = None,
) -> Tuple[Page, int, List[str], Optional[Browser], Optional[BrowserContext], Optional[Playwright]]:
    if not retry_count:
        retry_count = 10
    calls = [0]
    shots: List[str] = []
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=3, timeout_ms=60000)

    if logout_existing and xpath_visible(page, XPATH_HEADER_SHOP, timeout=3):
        try:
            page.locator(f"xpath={XPATH_HEADER_SHOP}").first.click(timeout=5000)
            page.get_by_text("退出", exact=False).first.click(timeout=5000)
            page.goto(LOGIN_URL_SHORT, wait_until="domcontentloaded", timeout=120000)
        except Exception as exc:
            raise SellerLoginError("退出已登录失败，检查是否有弹窗出现") from exc

    if visible(page, SEL_BACK, timeout=2):
        try:
            page.locator(SEL_BACK).first.click(timeout=5000)
        except Exception:
            pass

    if not xpath_visible(page, XPATH_EMAIL_TAB, timeout=3):
        if xpath_visible(page, XPATH_SWITCH, timeout=2):
            page.locator(f"xpath={XPATH_SWITCH}").first.click(timeout=5000)
            sleep(0.5)
    if xpath_visible(page, XPATH_EMAIL_TAB, timeout=5):
        page.locator(f"xpath={XPATH_EMAIL_TAB}").first.click(timeout=5000)
    elif not xpath_visible(page, XPATH_EMAIL, timeout=2):
        raise NeedsHumanError("二维码")

    fill_checked(page.locator(f"xpath={XPATH_EMAIL}").first, username, limit=3)
    password = password  # process4 decrypts; plaintext comes from env
    fill_checked(page.locator(f"xpath={XPATH_PASSWORD}").first, password, limit=3)
    if visible(page, SEL_AGREE, timeout=1):
        try:
            box = page.locator(SEL_AGREE).first
            if not box.is_checked():
                box.click(timeout=3000)
        except Exception:
            pass
    if visible(page, SEL_LOGIN, timeout=5):
        page.locator(SEL_LOGIN).first.click(timeout=10000)
    sleep(1)

    human = detect_human_text(page_text(page))
    if human:
        raise NeedsHumanError(human)

    verify_platform(page, token, retry_count, calls, click_recognizer)
    verify_email(
        page,
        mailbox,
        auth_code,
        email_code,
        token,
        retry_count,
        calls,
        click_recognizer,
    )

    if visible(page, SEL_FIRST_SHOP, timeout=2):
        page.locator(SEL_FIRST_SHOP).first.click(timeout=5000)
        sleep(1)
    if xpath_visible(page, XPATH_ENTER_SHOP, timeout=2):
        page.locator(f"xpath={XPATH_ENTER_SHOP}").first.click(timeout=5000)

    url = page.url or ""
    if "/login" in url and not xpath_visible(page, XPATH_HEADER_SHOP, timeout=2):
        raise SellerLoginError("登录流程失败！")
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def doudian_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    mailbox: Optional[str] = None,
    auth_code: Optional[str] = None,
    email_code: Optional[str] = None,
    retries: int = 10,
    logout_existing: bool = False,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
    click_recognizer: Optional[Callable[[str], str]] = None,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("DOUDIAN_ACCOUNT", "")
    password = password if password is not None else os.environ.get("DOUDIAN_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    mailbox = mailbox if mailbox is not None else os.environ.get("DOUDIAN_EMAIL", "")
    auth_code = auth_code if auth_code is not None else os.environ.get("DOUDIAN_EMAIL_AUTH", "")
    email_code = email_code if email_code is not None else os.environ.get("DOUDIAN_EMAIL_CODE", "")
    if not account or not password:
        raise ValueError("缺少抖店账号或密码")

    def _run(page=None, **_ignored):
        return login(
            account,
            password,
            yunma_token,
            retries,
            page=page,
            mailbox=mailbox or "",
            auth_code=auth_code or "",
            email_code=email_code or "",
            logout_existing=logout_existing,
            click_recognizer=click_recognizer,
        )

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = doudian_login()
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
