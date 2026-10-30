"""Playwright port of 影刀「淘宝mini登录」 activity_7bca6d/taobao_mini.py.

Credentials come only from arguments or TAOBAO_MINI_* env vars. The source
defaults are not copied.
"""
from __future__ import annotations

import os
from typing import List, Optional

from playwright.sync_api import Page

from . import captcha
from .helpers import (
    CredentialsRejected,
    OnError,
    SellerLoginResult,
    close_result,
    fill_checked,
    finish,
    goto_with_retry,
    input_value,
    mouse_drag,
    open_page,
    visible,
)

LOGIN_URL = (
    "https://login.taobao.com/member/login.jhtml?style=minisimple"
    "&redirect_url=https%3A%2F%2Fmyseller.taobao.com%2Fhome.htm%23%2Findex"
)
SEL_USER = "#fm-login-id"
SEL_PASSWORD = "#fm-login-password"
SEL_LOGIN = "button.password-login, button.fm-submit"
SEL_NC = "#nc_1_n1z"
SEL_NC_LABEL = "span.nc-lang-cnt"
SEL_PUZZLE = "#captcha-question"
INPUT_FAIL = "输入失败，请手动登录"


def _exact(locator, text: str) -> None:
    for _ in range(3):
        fill_checked(locator, text, limit=3)
        if input_value(locator) == text:
            return
    raise CredentialsRejected(INPUT_FAIL)


def _nc(page: Page) -> None:
    slider = page.locator(SEL_NC).first
    label = page.locator(SEL_NC_LABEL).first
    box = slider.bounding_box()
    bar = label.bounding_box()
    if not box or not bar:
        return
    x1 = box["x"] + box["width"] / 2
    y1 = box["y"] + box["height"] / 2
    mouse_drag(page, x1, y1, x1 + bar["width"], y1)


def _puzzle(page: Page, token: str, calls: List[int]) -> None:
    captcha.require_yunma_token(token)
    image = __import__("base64").b64encode(page.locator(SEL_PUZZLE).first.screenshot(type="png")).decode("ascii")
    response = captcha.yunma_post(captcha.ali_slider_payload(image, token))
    calls[0] += 1
    distance = int((response.get("data") or {}).get("data"))
    drag = page.locator("div.button").first
    box = drag.bounding_box()
    if not box:
        return
    x1 = box["x"] + box["width"] / 2
    y1 = box["y"] + box["height"] / 2
    moved = (int(distance) - 24 - 10) / 320 * 320
    mouse_drag(page, x1, y1, x1 + moved, y1)


def login(account: str, password: str, token: str, *, retries: int = 3, page: Optional[Page] = None):
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=60000)
    _exact(page.locator(SEL_USER).first, account)
    page.locator(SEL_PASSWORD).first.click(timeout=5000)
    if visible(page, SEL_PUZZLE, timeout=1):
        try:
            _puzzle(page, token, calls)
        except Exception:
            pass
    _exact(page.locator(SEL_PASSWORD).first, password)
    if visible(page, SEL_NC_LABEL, timeout=1):
        _nc(page)
    page.locator(SEL_LOGIN).first.click(timeout=10000)
    if visible(page, SEL_NC_LABEL, timeout=1):
        _nc(page)
    if visible(page, SEL_PUZZLE, timeout=1):
        try:
            for _ in range(int(retries) or 3):
                _puzzle(page, token, calls)
                if not visible(page, SEL_PUZZLE, timeout=1):
                    break
        except Exception:
            pass
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def taobao_mini_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    retries: int = 3,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("TAOBAO_MINI_ACCOUNT", "")
    password = password if password is not None else os.environ.get("TAOBAO_MINI_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if not account or not password:
        raise ValueError("缺少淘宝 mini 账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, retries=retries, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = taobao_mini_login(retries=int(os.environ.get("TAOBAO_MINI_RETRIES", "3")))
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
