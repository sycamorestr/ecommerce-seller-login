"""Playwright port of 影刀「有赞登录」 activity_7bca6d/process5.py.

Slider is std_slider_captcha type 22222, offset 0, speed 1, up to 5 tries.
A still-visible 有赞_登录 button is treated as a phone/password gate.
"""
from __future__ import annotations

import os
from typing import List, Optional

from playwright.sync_api import Page

from . import captcha
from .helpers import (
    NeedsHumanError,
    OnError,
    SellerLoginResult,
    close_result,
    fill_checked,
    finish,
    goto_with_retry,
    mouse_drag,
    open_page,
    sleep,
    visible,
)

LOGIN_URL = "https://account.youzan.com/login"
SEL_SCAN = "span.login-qrcode__title__right"
SEL_PASSWORD_TAB = "span.bold.js-tab-password-login"
SEL_ACCOUNT_TAB = "span.login-qrcode__title__right"
SEL_PHONE = "input.zent-input"
SEL_PASSWORD = 'input.zent-input[placeholder="输入登录密码"]'
SEL_AGREE = "input.zent-checkbox-input, input[type='checkbox']"
SEL_LOGIN = "button.js-login-btn"
SEL_BG = "div.captcha-bg, #slideBgRef"
SEL_DRAG = "#slideIconRef"
SEL_REFRESH = "div.captcha-refresh"
PHONE_GATE = "登录失败，当前可能需要验证手机号或账号未设置密码登录"


def _slider(page: Page, token: str, calls: List[int]) -> None:
    captcha.require_yunma_token(token)
    background = page.locator(SEL_BG).first
    drag = page.locator(SEL_DRAG).first
    image = __import__("base64").b64encode(background.screenshot(type="png")).decode("ascii")
    response = captcha.yunma_post(captcha.std_slider_payload(image, token))
    calls[0] += 1
    distance = captcha.std_slider_distance(response.get("data") or {}, offset=0, speed=1)
    box = drag.bounding_box()
    if not box:
        return
    x1 = box["x"] + box["width"] / 2
    y1 = box["y"] + box["height"] / 2
    mouse_drag(page, x1, y1, x1 + distance, y1)


def login(account: str, password: str, token: str, *, page: Optional[Page] = None):
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=4, timeout_ms=60000)
    sleep(2)
    if (page.url or "") != LOGIN_URL:
        for sel in ("a.introjs-donebutton", "div.user-nickname", "span.exit-link"):
            if visible(page, sel, timeout=0.5):
                try:
                    page.locator(sel).first.click(timeout=3000)
                except Exception:
                    pass
    if visible(page, SEL_SCAN, timeout=5):
        if visible(page, "img.js-tab-password-login, img[class*='password']", timeout=1):
            page.locator("img.js-tab-password-login, img[class*='password']").first.click(timeout=5000)
    if visible(page, SEL_ACCOUNT_TAB, timeout=5):
        try:
            page.locator(SEL_ACCOUNT_TAB).first.click(timeout=5000)
        except Exception:
            pass
    page.locator(SEL_PASSWORD_TAB).first.click(timeout=20000)
    sleep(1)
    phones = page.locator(SEL_PHONE)
    fill_checked(phones.first, account, limit=3)
    fill_checked(page.locator(SEL_PASSWORD).first, password, limit=3)
    if visible(page, SEL_AGREE, timeout=1):
        box = page.locator(SEL_AGREE).first
        try:
            if not box.is_checked():
                box.check(timeout=3000)
        except Exception:
            box.click(timeout=3000)
    page.locator(SEL_LOGIN).first.click(timeout=20000)
    sleep(2)
    for _ in range(5):
        if not visible(page, SEL_BG, timeout=1.5):
            break
        try:
            _slider(page, token, calls)
        except Exception:
            if visible(page, SEL_REFRESH, timeout=1):
                page.locator(SEL_REFRESH).first.click(timeout=3000)
        sleep(2)
    if visible(page, SEL_LOGIN, timeout=1):
        raise NeedsHumanError(PHONE_GATE)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def youzan_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("YOUZAN_ACCOUNT", "")
    password = password if password is not None else os.environ.get("YOUZAN_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if not account or not password:
        raise ValueError("缺少有赞账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = youzan_login()
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
