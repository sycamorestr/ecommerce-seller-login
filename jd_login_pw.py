"""Playwright port of 影刀「京东登录」 activity_7bca6d/process6.py.

Default URL https://passport.jd.com/new/login.aspx. New UI uses the free
slider (activity_4f0f15d7, offset 0) then Yunma 22222 / click-plus 30009
direction bottom / jd click 30330. Old UI uses 图鉴 type 18 when a recognizer
is passed. SMS text is exactly 「当前账号需要短信验证」.
"""
from __future__ import annotations

import os
from typing import Callable, List, Optional

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
)

LOGIN_URL = "https://passport.jd.com/new/login.aspx"
SEL_NEW = "div.login-form.login-form-l"
SEL_PASSWORD_MODE = "div.form-login-type.select-toggle"
SEL_ACCOUNT = 'input.itxt[placeholder="账号名/手机号/邮箱"]'
SEL_PASSWORD = "#nloginpwd"
SEL_SUBMIT = "#loginsubmit"
SEL_SEARCH = "input.text"
SEL_PLEASE_LOGIN = "a.link-login"
SEL_SLIDER_IMG = "img.JDJRV-bigimg, img[class*='slide']"
SEL_BG = "img.JDJRV-bigimg"
SEL_DRAG = "div.JDJRV-slide-btn, img.JDJRV-slide-btn"
SEL_CLICK_OK = "#submit-btn"
SEL_TIP = "span.tip_text"
SEL_ERROR = "div.msg-error"
SEL_SMS = "h5.tip-title"
SEL_QUICK = "div.verifyBtn"
SEL_REFRESH = "span.JDJRV-refresh"
SMS_MESSAGE = "当前账号需要短信验证"
CAPTCHA_FAIL = "由于验证码未通过导致登录失败"


def _drag_std(page: Page, token: str, calls: List[int], background_sel: str, drag_sel: str) -> None:
    captcha.require_yunma_token(token)
    background = page.locator(background_sel).first
    drag = page.locator(drag_sel).first
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


def _click_plus(page: Page, token: str, calls: List[int], recognizer: Optional[Callable[[str], str]]) -> None:
    if recognizer is None and not token:
        raise NeedsHumanError("点选验证")
    image = __import__("base64").b64encode(page.locator(SEL_CLICK_OK).locator("xpath=..").first.screenshot(type="png")).decode("ascii")
    if recognizer:
        raw = recognizer(image)
    else:
        payload = captcha.std_click_plus_payload(image, token, captcha.STD_CLICK_PLUS_DIRECTION)
        response = captcha.yunma_post(payload)
        calls[0] += 1
        if response.get("msg") != "识别成功":
            raise SellerLoginError("识别失败, 请重试")
        raw = (response.get("data") or {}).get("data") or ""
    positions = captcha.parse_click_positions(raw)
    origin = page.locator("div.JDJRV-click").first.bounding_box() or {"x": 0, "y": 0}
    for x, y in captcha.click_points_from_origin(origin["x"], origin["y"], positions):
        page.mouse.click(x, y)
    page.locator(SEL_CLICK_OK).first.click(timeout=5000)


def _jd_click(page: Page, token: str, calls: List[int]) -> None:
    captcha.require_yunma_token(token)
    target = page.locator(SEL_TIP).first
    image = __import__("base64").b64encode(target.screenshot(type="png")).decode("ascii")
    response = captcha.yunma_post(captcha.jd_click_payload(image, token))
    calls[0] += 1
    positions = captcha.cs_temu_positions(response)
    box = target.bounding_box() or {"x": 0, "y": 0}
    for x, y in captcha.click_points_from_origin(box["x"], box["y"], positions):
        page.mouse.click(x, y)


def _sms(page: Page) -> None:
    if visible(page, SEL_SMS, timeout=0.8):
        raise NeedsHumanError(SMS_MESSAGE)


def login(
    account: str,
    password: str,
    token: str,
    *,
    login_url: str = LOGIN_URL,
    retries: int = 5,
    page: Optional[Page] = None,
    click_recognizer: Optional[Callable[[str], str]] = None,
):
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    url = login_url or LOGIN_URL
    goto_with_retry(page, url, attempts=4, timeout_ms=60000)
    if visible(page, SEL_NEW, timeout=3):
        if visible(page, SEL_PASSWORD_MODE, timeout=1):
            page.locator(SEL_PASSWORD_MODE).first.click(timeout=5000)
            sleep(1)
        user = page.locator(SEL_ACCOUNT).first
        filled = False
        for index in range(1, 6):
            fill_checked(user, str(account), limit=3)
            if input_value(user) == str(account):
                filled = True
                break
            if index == 5:
                raise CredentialsRejected("账号输入框填写失败")
        if not filled:
            raise CredentialsRejected("账号输入框填写失败")
        fill_checked(page.locator(SEL_PASSWORD).first, str(password), limit=3)
        page.locator(SEL_SUBMIT).first.click(timeout=20000)
        sleep(1)
        for _ in range(int(retries) or 5):
            if visible(page, SEL_BG, timeout=1):
                try:
                    _drag_std(page, token, calls, SEL_BG, SEL_DRAG)
                except Exception:
                    if visible(page, SEL_REFRESH, timeout=0.5):
                        page.locator(SEL_REFRESH).first.click(timeout=3000)
            if visible(page, SEL_CLICK_OK, timeout=0.8):
                _click_plus(page, token, calls, click_recognizer)
            if visible(page, SEL_TIP, timeout=0.8):
                _jd_click(page, token, calls)
            if visible(page, SEL_SEARCH, timeout=1) and not visible(page, SEL_PLEASE_LOGIN, timeout=0.5):
                return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
            sleep(1)
        if visible(page, SEL_SLIDER_IMG, timeout=0.8):
            raise SellerLoginError(CAPTCHA_FAIL)
        if visible(page, SEL_ERROR, timeout=0.8):
            text = (page.locator(SEL_ERROR).first.inner_text(timeout=1000) or "").strip()
            raise CredentialsRejected(text or "账户名与密码不匹配")
        _sms(page)
        if visible(page, SEL_QUICK, timeout=0.8):
            page.locator(SEL_QUICK).first.click(timeout=5000)
        _sms(page)
        return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
    if visible(page, "div.change-login-status-btn", timeout=1):
        page.locator("div.change-login-status-btn").first.click(timeout=5000)
    if visible(page, "a.hint-binding", timeout=1):
        page.locator("a.hint-binding").first.click(timeout=5000)
    if visible(page, "a.checked", timeout=1):
        page.locator("a.checked").first.click(timeout=5000)
    old_user = page.locator("input#loginname").first
    fill_checked(old_user, str(account), limit=3)
    fill_checked(page.locator("input#nloginpwd, input[type='password']").first, str(password), limit=3)
    page.locator("a#loginsubmit").first.click(timeout=20000)
    _sms(page)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def jd_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    login_url: Optional[str] = None,
    retries: int = 5,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
    click_recognizer: Optional[Callable[[str], str]] = None,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("JD_ACCOUNT", "")
    password = password if password is not None else os.environ.get("JD_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if login_url is None:
        login_url = os.environ.get("JD_LOGIN_URL", "") or LOGIN_URL
    if not account or not password:
        raise ValueError("缺少京东账号或密码")

    def _run(page=None, **_ignored):
        return login(
            account,
            password,
            yunma_token,
            login_url=login_url,
            retries=retries,
            page=page,
            click_recognizer=click_recognizer,
        )

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = jd_login(retries=int(os.environ.get("JD_RETRIES", "5")))
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
