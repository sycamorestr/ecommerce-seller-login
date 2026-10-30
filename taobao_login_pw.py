"""Playwright port of 影刀「淘宝登录」 activity_7bca6d/process7.py.

Puzzle slider is ali_slider_captcha type 20226. NC bar is a full-width drag.
SMS button #J_GetCode stops the flow.
"""
from __future__ import annotations

import os
from typing import List, Optional

from playwright.sync_api import Page

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
    input_value,
    mouse_drag,
    open_page,
    sleep,
    visible,
    xpath_visible,
)

LOGIN_URL = "https://login.taobao.com/member/login.jhtml"
SEL_OTHER = "a.other-account, a[href*='login']"
SEL_PASSWORD_TAB = "a.password-login-tab, a[class*='password']"
SEL_USER = "#fm-login-id"
SEL_PASSWORD = "#fm-login-password"
SEL_SUBMIT = "button.password-login"
SEL_AGREE = "input.fm-agreement-checkbox, .agreement-checkbox"
SEL_NC = "#nc_1_n1z"
SEL_NC_LABEL = "span.nc-lang-cnt"
SEL_PUZZLE = "#captcha-question"
SEL_SMS = "#J_GetCode"
SEL_ERROR = ".login-error-msg"
SMS_MESSAGE = "登录需要短信验证，请手动完成短信验证登录"
INPUT_FAIL = "当前输入框内容和实际账号不相等，请重新运行该指令"
LOGIN_FAIL = "登录失败，请手动登录"


def _fill_exact(page: Page, selector: str, text: str, message: str) -> None:
    locator = page.locator(selector).first
    for _ in range(3):
        fill_checked(locator, text, limit=3)
        if input_value(locator) == text:
            return
    raise CredentialsRejected(message)


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
    data = (response.get("data") or {}).get("data")
    distance = int(data)
    drag = page.locator("div.button").first
    box = drag.bounding_box()
    if not box:
        return
    x1 = box["x"] + box["width"] / 2
    y1 = box["y"] + box["height"] / 2
    moved = (int(distance) - 24 - 10) / 320 * 320
    mouse_drag(page, x1, y1, x1 + moved, y1)


def login(account: str, password: str, token: str, *, page: Optional[Page] = None):
    if not isinstance(account, str):
        raise ValueError("登录账号类型错误，应为字符串类型")
    if not isinstance(password, str):
        raise ValueError("登录密码类型错误，应为字符串类型")
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=60000)
    if xpath_visible(page, '//a[.="使用其他帐户登录"]', timeout=5):
        page.locator('xpath=//a[.="使用其他帐户登录"]').first.click(timeout=5000)
    if xpath_visible(page, '//a[.="密码登录"]', timeout=2):
        page.locator('xpath=//a[.="密码登录"]').first.click(timeout=5000)
    _fill_exact(page, SEL_USER, account, INPUT_FAIL)
    if visible(page, SEL_PUZZLE, timeout=1):
        _puzzle(page, token, calls)
    page.locator(SEL_PASSWORD).first.click(timeout=5000)
    if visible(page, "div.nc_scale", timeout=1):
        _nc(page)
    _fill_exact(page, SEL_PASSWORD, password, INPUT_FAIL)
    if visible(page, SEL_AGREE, timeout=1):
        page.locator(SEL_AGREE).first.click(timeout=3000)
    page.locator(SEL_SUBMIT).first.click(timeout=10000)
    sleep(1)
    for _ in range(3):
        if visible(page, SEL_NC, timeout=1) or visible(page, SEL_NC_LABEL, timeout=0.5):
            _nc(page)
            page.locator(SEL_SUBMIT).first.click(timeout=5000)
        if visible(page, SEL_PUZZLE, timeout=0.8):
            _puzzle(page, token, calls)
        if visible(page, SEL_ERROR, timeout=0.5):
            text = (page.locator(SEL_ERROR).first.inner_text(timeout=1000) or "").strip()
            if text:
                raise CredentialsRejected(text)
        if visible(page, SEL_SMS, timeout=0.8):
            raise NeedsHumanError(SMS_MESSAGE)
        if not visible(page, SEL_SUBMIT, timeout=0.5):
            return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
        sleep(1)
    if visible(page, SEL_SUBMIT, timeout=0.5):
        raise SellerLoginError(LOGIN_FAIL)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def taobao_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("TAOBAO_ACCOUNT", "")
    password = password if password is not None else os.environ.get("TAOBAO_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if not account or not password:
        raise ValueError("缺少淘宝账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = taobao_login()
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
