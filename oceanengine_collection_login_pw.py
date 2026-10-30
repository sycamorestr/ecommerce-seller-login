"""登陆拓展合集「巨量引擎登录」 activity_52aea4a0/process1.py.

Distinct from activity_7bca6d oceanengine_login_pw (no appKey) and
oceanengine_email_login_pw (process47). This flow uses appKey=51, logs out
through navigator-user-account-info, and retries dy_slider up to 7 times.
"""
from __future__ import annotations

import os
from typing import List, Optional

from playwright.sync_api import Page

import captcha_helpers as captcha
from seller_common import (
    OnError,
    SellerLoginResult,
    fill_checked,
    finish,
    goto_with_retry,
    mouse_drag,
    open_page,
    sleep,
    visible,
    xpath_visible,
)

LOGIN_URL = "https://business.oceanengine.com/login?appKey=51"
HOME_MARK = "https://business.oceanengine.com/"
SOURCE = "activity_52aea4a0/process1.py"
XPATH_ACCOUNT_NEW = '//div[@class="navigator-user-account-info"]'
XPATH_LOGOUT_NEW = '//li[normalize-space(.)="退出登录"]'
SEL_EMAIL = 'input[placeholder="请输入邮箱"]'
SEL_PASSWORD = 'input[placeholder="密码"]'
SEL_LOGIN = "button.account-center-action-button"
SEL_BG = "img.captcha-verify-image"
SEL_DRAG = "div.captcha-slider-btn"
SLIDER_TRIES = 7


def login(account: str, password: str, token: str, *, relogin: bool = True, page: Optional[Page] = None):
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=20000)
    sleep(1)
    if HOME_MARK in (page.url or "") and relogin and xpath_visible(page, XPATH_ACCOUNT_NEW, timeout=3):
        page.locator(f"xpath={XPATH_ACCOUNT_NEW}").first.click(timeout=5000)
        page.locator(f"xpath={XPATH_LOGOUT_NEW}").first.click(timeout=5000)
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20000)
    elif HOME_MARK in (page.url or "") and not relogin:
        return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
    fill_checked(page.locator(SEL_EMAIL).first, account, limit=3)
    fill_checked(page.locator(SEL_PASSWORD).first, password, limit=3)
    page.locator(SEL_LOGIN).first.click(timeout=10000)
    for _ in range(SLIDER_TRIES):
        if not visible(page, SEL_BG, timeout=1):
            break
        captcha.require_yunma_token(token)
        image = __import__("base64").b64encode(page.locator(SEL_BG).first.screenshot(type="png")).decode("ascii")
        response = captcha.yunma_post(captcha.dy_slider_payload(image, token))
        calls[0] += 1
        px = captcha.dy_recognized_px(response)
        box = page.locator(SEL_DRAG).first.bounding_box()
        if box:
            x1 = box["x"] + box["width"] / 2
            y1 = box["y"] + box["height"] / 2
            mouse_drag(page, x1, y1, x1 + px, y1)
        sleep(1)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def oceanengine_collection_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    relogin: bool = True,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("OCEANENGINE_COLLECTION_EMAIL", "")
    password = password if password is not None else os.environ.get("OCEANENGINE_COLLECTION_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if not account or not password:
        raise ValueError("缺少巨量引擎合集登录邮箱或密码")

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, relogin=relogin, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
