"""Playwright port of 速卖通登录 activity_aliexpress/aliexpress_login.py.

Email fetch is not bundled. A visible 验证 button without ALIEXPRESS_EMAIL_CODE
raises NeedsHumanError. Wrong password text matches the source exception.
"""
from __future__ import annotations

import os
import re
from typing import Optional

from playwright.sync_api import Page

from seller_common import (
    CredentialsRejected,
    NeedsHumanError,
    OnError,
    SellerLoginResult,
    finish,
    goto_with_retry,
    open_page,
    xpath_visible,
)

SOURCE = "activity_aliexpress/aliexpress_login.py"
LOGIN_URL_TEMPLATE = "https://login.aliexpress.com/user/seller/login?bizSegment=CSP&_lang={lang}"
XPATH_SUBMIT = '//form/button[normalize-space(.)="Sign In" or normalize-space(.)="登录"]'
XPATH_USER = '//form//input[@id="loginName"]'
XPATH_PASSWORD = '//form//input[@type="password"]'
XPATH_FAIL = '//form/section[normalize-space(.)="您的帐户名或密码不正确。"]'
XPATH_VERIFY = '//button[normalize-space(.)="验证"]'
BAD_PASSWORD = "您的帐户名或密码不正确，程序终止，请重新输入账号和密码"
EMAIL_CODE_RE = re.compile(r"(?:一次性验证码是|Verification code:|【[^】]*】.*?一次性验证码是)\s*(\d{6})")


def login_url(language: str = "zh_CN") -> str:
    return LOGIN_URL_TEMPLATE.format(lang=language)


def extract_email_code(html: str) -> str:
    matched = EMAIL_CODE_RE.search(html or "")
    return matched.group(1) if matched else ""


def login(
    account: str,
    password: str,
    *,
    language: str = "zh_CN",
    email_code: str = "",
    page: Optional[Page] = None,
):
    shots: list = []
    page, owned = open_page(page, headless=False)
    url = login_url(language)
    if page.url != url:
        goto_with_retry(page, url, attempts=1, timeout_ms=20000)
    page.locator(f"xpath={XPATH_SUBMIT}").first.wait_for(state="visible", timeout=20000)
    page.locator(f"xpath={XPATH_USER}").first.fill(account)
    page.locator(f"xpath={XPATH_PASSWORD}").first.fill(password)
    page.locator(f"xpath={XPATH_SUBMIT}").first.click(timeout=10000)
    if xpath_visible(page, XPATH_FAIL, timeout=1):
        raise CredentialsRejected(BAD_PASSWORD)
    if xpath_visible(page, XPATH_VERIFY, timeout=2):
        code = email_code or extract_email_code(email_code)
        if not code:
            raise NeedsHumanError("邮箱验证")
        frame = page.frame_locator("iframe")
        frame.locator("input").first.fill(code)
        frame.locator(f"xpath={XPATH_VERIFY}").first.click(timeout=5000)
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def aliexpress_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    language: Optional[str] = None,
    email_code: Optional[str] = None,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("ALIEXPRESS_ACCOUNT", "")
    password = password if password is not None else os.environ.get("ALIEXPRESS_PASSWORD", "")
    if language is None:
        language = os.environ.get("ALIEXPRESS_LANG", "zh_CN")
    if email_code is None:
        email_code = os.environ.get("ALIEXPRESS_EMAIL_CODE", "")
    if not account or not password:
        raise ValueError("缺少速卖通账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, language=language or "zh_CN", email_code=email_code or "", page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
