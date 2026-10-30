"""Playwright port of 影刀「亚马逊-店铺登录」 amazon_ext_op/process1.py.

process1 only calls _amazon_api.login → _amazon_core_beta.login. That function
does not open a seller URL. It returns immediately unless the current URL
contains signin or mfa. Missing OTP autofill and the aa-challenge iframe are
NeedsHumanError, matching the source exceptions.
"""
from __future__ import annotations

from typing import Optional

from playwright.sync_api import Page

from seller_common import NeedsHumanError, OnError, SellerLoginResult, finish, open_page

SOURCE = "amazon_ext_op/process1.py"
LOGIN_BTN = '//input[@id="signInSubmit"]'
AUTH_SELECT = '//*[@id="guide-component"]'
CAPTCHA_IFRAME = '//*[@id="aa-challenge-whole-page-iframe"]'
HOME = '//*[@id="partner-switcher"] | //*[@id="dropdown-account-switcher-container"] '
OTP_MISSING = "二次验证验证码没有自动填充，请先进行配置"
CAPTCHA_SEEN = "出现了数英验证码"
TIMEOUT = "登录超时"


def _is_login_page(url: str) -> bool:
    return ("signin" in url) or ("mfa" in url) or ("ap/signin" in url)


def login(*, page: Optional[Page] = None):
    shots: list = []
    page, owned = open_page(page, headless=False)
    url = page.url or ""
    if not _is_login_page(url):
        return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
    if page.locator(f"xpath={AUTH_SELECT}").count():
        raise NeedsHumanError(OTP_MISSING)
    if page.locator(f"xpath={CAPTCHA_IFRAME}").count():
        raise NeedsHumanError(CAPTCHA_SEEN)
    button = page.locator(f"xpath={LOGIN_BTN}")
    if button.count():
        button.first.click(timeout=5000)
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def amazon_login(
    *,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    def _run(page=None, **_ignored):
        return login(page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
