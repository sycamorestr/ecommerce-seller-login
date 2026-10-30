"""Playwright port of 影刀「登录金蝶云星空」 activity_jindie/login.py.

The source expects the login page to already be open. It does not set a URL.
Captcha is std_alphanum type 10110.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from . import captcha
from .helpers import (
    NeedsHumanError,
    OnError,
    SellerLoginError,
    SellerLoginResult,
    fill_checked,
    finish,
    open_page,
    visible,
)

SOURCE = "activity_jindie/login.py"
LOGIN_URL = ""  # source raises if #user is missing; it does not navigate
SEL_USER = "#user"
SEL_PASSWORD = "#password"
SEL_LOGIN = "#btnLogin"
SEL_CAPTCHA_IMG = "#img_VelidationCode"
SEL_CAPTCHA_INPUT = "#velidationCode"
CAPTCHA_TYPE = "10110"
MISSING_PAGE = "账号输入框不存在，请检查是否打开登录页面"
LOGIN_FAIL = "登录失败，登录按钮在规定时间没有消失"
XPATH_ALREADY = '//span[.="该帐号已登录在线，确认让对方下线,"]'


def login(
    account: str,
    password: str,
    token: str,
    *,
    platform: str = "",
    login_now: bool = True,
    page: Optional[Page] = None,
):
    shots: list = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    if not visible(page, SEL_USER, timeout=2):
        raise SellerLoginError(MISSING_PAGE)
    if platform:
        page.locator("#datacenter_ct span.toolTip").first.click(timeout=5000)
        page.locator(f"xpath=//ul/li[contains(., {platform!r})]").first.click(timeout=5000)
    fill_checked(page.locator(SEL_USER).first, account, limit=3)
    page.keyboard.press("Tab")
    fill_checked(page.locator(SEL_PASSWORD).first, password, limit=3)
    if visible(page, SEL_CAPTCHA_IMG, timeout=1):
        if not token:
            raise NeedsHumanError("数英验证码")
        image = __import__("base64").b64encode(page.locator(SEL_CAPTCHA_IMG).first.screenshot(type="png")).decode("ascii")
        response = captcha.yunma_post(captcha.alphanum_payload(image, token, CAPTCHA_TYPE))
        calls[0] += 1
        code = ((response.get("data") or {}).get("data") or "")
        if code:
            page.locator(SEL_CAPTCHA_INPUT).first.fill(str(code))
    page.locator(SEL_LOGIN).first.click(timeout=10000)
    if page.locator(f"xpath={XPATH_ALREADY}").count():
        if login_now:
            page.locator('xpath=//div[@class="kd-mouseover-el"][contains(.,"确认")]').first.click(timeout=5000)
        else:
            page.locator('xpath=//div[@class="kd-mouseover-el"][contains(.,"取消")]').first.click(timeout=5000)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def kingdee_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    platform: Optional[str] = None,
    login_now: bool = True,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("KINGDEE_ACCOUNT", "")
    password = password if password is not None else os.environ.get("KINGDEE_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if platform is None:
        platform = os.environ.get("KINGDEE_PLATFORM", "")
    if not account or not password:
        raise ValueError("缺少金蝶账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, platform=platform or "", login_now=login_now, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
