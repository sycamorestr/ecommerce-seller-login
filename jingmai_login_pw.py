"""Playwright port of 影刀「京麦登录」 activity_7bca6d/process56.py.

Login URL and the std_slider_captcha call (Yunma type 22222, offset 0, speed 1)
come from that flow. 图鉴账号/密码 are inputs on the block but process56 does not
pass them into the captcha call; this port keeps the same captcha path.
"""
from __future__ import annotations

import os
from typing import List, Optional, Tuple

from playwright.sync_api import Browser, BrowserContext, Page, Playwright

import captcha_helpers as captcha
from seller_common import (
    CredentialsRejected,
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
)

LOGIN_URL = (
    "https://passport.shop.jd.com/login/index.action/jdm"
    "?ReturnUrl=https%3A%2F%2Fshop.jd.com%2FvcIndex.action"
)
HOME_URL = "https://shop.jd.com/jdm/home"
PASSPORT_MARK = "https://passport.shop.jd.com/login/index.action/jdm"

# Leaf selectors from selectorsV2.xml names used by process56 (0706 set).
SEL_QR = 'div.jm-login-qrcode img[alt="二维码"]'
SEL_SWITCH_PASSWORD = "div.scan-login img.icon"
SEL_USERNAME = 'input.rcd-input__inner[placeholder="请输入账号名/邮箱"]'
SEL_PASSWORD = 'input.rcd-input__inner[type="password"][placeholder="请输入登录密码"]'
SEL_LOGIN = "button.password__submit"
SEL_SLIDER = "#JDJRV-wrap-passwordLoginSlideValidate div.jdjrv-smallimg img"
SEL_BACKGROUND = "#JDJRV-wrap-passwordLoginSlideValidate div.jdjrv-bigimg img"
SEL_DRAG = "#JDJRV-wrap-passwordLoginSlideValidate div.jdjrv-slide-btn"
SEL_REFRESH = "#JDJRV-wrap-passwordLoginSlideValidate div.JDJRV-refresh, #JDJRV-wrap-passwordLoginSlideValidate div.jdjrv-refresh"
SEL_LOGIN_ERROR = "#loginname_error"
SEL_MISMATCH = "div.password__error"


def _drag_std_slider(page: Page, token: str, calls: List[int]) -> None:
    captcha.require_yunma_token(token)
    background = page.locator(SEL_BACKGROUND).first
    drag = page.locator(SEL_DRAG).first
    image = captcha_png_b64(background)
    payload = captcha.std_slider_payload(image, token)
    response = captcha.yunma_post(payload)
    calls[0] += 1
    distance = captcha.std_slider_distance(response.get("data") or {}, offset=0, speed=1)
    box = drag.bounding_box()
    if not box:
        return
    x1 = box["x"] + box["width"] / 2
    y1 = box["y"] + box["height"] / 2
    mouse_drag(page, x1, y1, x1 + distance, y1)


def captcha_png_b64(locator) -> str:
    import base64

    return base64.b64encode(locator.screenshot(type="png")).decode("ascii")


def login(
    account: str,
    password: str,
    token: str,
    retry_count: int,
    page: Optional[Page] = None,
) -> Tuple[Page, int, List[str], Optional[Browser], Optional[BrowserContext], Optional[Playwright]]:
    if not retry_count:
        retry_count = 5
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=3, timeout_ms=60000)
    sleep(1)
    try:
        page.reload(wait_until="domcontentloaded", timeout=20000)
    except Exception:
        pass

    if visible(page, SEL_QR, timeout=2):
        try:
            page.locator(SEL_SWITCH_PASSWORD).first.click(timeout=3000)
            sleep(1)
        except Exception:
            pass

    filled = False
    for index in range(1, 6):
        sleep(1)
        if not visible(page, SEL_USERNAME, timeout=2):
            continue
        user = page.locator(SEL_USERNAME).first
        fill_checked(user, account.strip(), limit=3)
        if captcha_input_equals(user, account.strip()):
            filled = True
            break
        if index == 5:
            raise CredentialsRejected("账号输入框填写失败")
    if not filled and visible(page, SEL_QR, timeout=1) and not visible(page, SEL_USERNAME, timeout=1):
        raise NeedsHumanError("二维码")

    if visible(page, SEL_PASSWORD, timeout=3):
        fill_checked(page.locator(SEL_PASSWORD).first, password, limit=3)

    if visible(page, SEL_LOGIN, timeout=3):
        page.locator(SEL_LOGIN).first.click(timeout=20000)
    sleep(5)

    human = detect_human_text(page_text(page))
    if human:
        raise NeedsHumanError(human)

    slider_seen = visible(page, SEL_SLIDER, timeout=5)
    if not slider_seen:
        if (page.url or "") != LOGIN_URL:
            sleep(2)
            return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
    else:
        for _ in range(int(retry_count)):
            if not visible(page, SEL_SLIDER, timeout=1.5):
                break
            try:
                _drag_std_slider(page, token, calls)
            except Exception as exc:
                print(f"[jingmai] slider failed: {exc}")
                if visible(page, SEL_REFRESH, timeout=1):
                    try:
                        page.locator(SEL_REFRESH).first.click(timeout=3000)
                    except Exception:
                        pass
            sleep(1)
        if visible(page, SEL_SLIDER, timeout=1.5):
            raise SellerLoginError("登录失败")

    if _error_text(page):
        raise CredentialsRejected("账户密码错误")

    human = detect_human_text(page_text(page))
    if human:
        raise NeedsHumanError(human)

    url_now = page.url or ""
    if url_now in PASSPORT_MARK or "shop.jd.com/jdm/home" not in url_now.lower():
        page.goto(HOME_URL, wait_until="domcontentloaded", timeout=20000)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def captcha_input_equals(locator, expected: str) -> bool:
    from seller_common import input_value

    return input_value(locator) == expected


def _error_text(page: Page) -> str:
    for sel in (SEL_MISMATCH, SEL_LOGIN_ERROR):
        if visible(page, sel, timeout=0.8):
            try:
                text = (page.locator(sel).first.inner_text(timeout=1000) or "").strip()
            except Exception:
                text = ""
            if text:
                return text
    return ""


def jingmai_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    retries: int = 5,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("JINGMAI_ACCOUNT", "")
    password = password if password is not None else os.environ.get("JINGMAI_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if not account or not password:
        raise ValueError("缺少京麦账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, retries, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = jingmai_login(retries=int(os.environ.get("JINGMAI_RETRIES", "5")))
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    if result.web_page and result.ok:
        print("URL", result.web_page.url)
    close_result(result)


if __name__ == "__main__":
    main()
