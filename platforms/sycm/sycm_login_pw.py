"""Playwright port of 影刀「生意参谋登录Plus」 activity_26766b38/process45.py."""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import (
    NeedsHumanError,
    OnError,
    SellerLoginResult,
    fill_checked,
    finish,
    goto_with_retry,
    open_page,
    visible,
    xpath_visible,
)

LOGIN_URL = "https://sycm.taobao.com/custom/login.htm"
HOME_URL = "https://sycm.taobao.com/portal/home.htm"
SOURCE = "activity_26766b38/process45.py"
SEL_USER = "#fm-login-id"
SEL_PASSWORD = "#fm-login-password"
SEL_LOGIN = "button.password-login"
XPATH_SMS = '//button[@id="J_GetCode"]'


def login(account: str, password: str, *, page: Optional[Page] = None):
    shots: list = []
    page, owned = open_page(page, headless=False)
    if HOME_URL in (page.url or ""):
        return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=20000)
    if visible(page, SEL_USER, timeout=8):
        fill_checked(page.locator(SEL_USER).first, account, limit=3)
        fill_checked(page.locator(SEL_PASSWORD).first, password, limit=3)
        page.locator(SEL_LOGIN).first.click(timeout=10000)
    if xpath_visible(page, XPATH_SMS, timeout=2):
        raise NeedsHumanError("短信验证")
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def sycm_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("SYCM_ACCOUNT", "")
    password = password if password is not None else os.environ.get("SYCM_PASSWORD", "")
    if not account or not password:
        raise ValueError("缺少生意参谋账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
