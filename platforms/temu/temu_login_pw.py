"""Playwright port of Temu-账号登录 activity_temu_shop/login.py."""
from __future__ import annotations

import os
import re
from typing import Optional

from playwright.sync_api import Page

from .helpers import OnError, SellerLoginResult, finish, goto_with_retry, open_page, xpath_visible

LOGIN_URL = "https://seller.kuajingmaihuo.com/login"
SOURCE = "activity_temu_shop/login.py"
XPATH_PHONE_TAB = "//*[text()='手机号登录']"
XPATH_PHONE = "//input[@placeholder='请输入手机号']"
XPATH_PASSWORD = "//input[@placeholder='请输入密码']"
XPATH_LOGIN = "//span[text()='登录']"
XPATH_AGREE = '//div[text()="我已阅读并同意以上协议"]'
XPATH_SWITCH = '//span[text()="切换"]'
XPATH_CONFIRM = '//span[text()="确认切换"]'


def login(
    account: str,
    password: str,
    *,
    target_store: str = "",
    page: Optional[Page] = None,
):
    shots: list = []
    page, owned = open_page(page, headless=False)
    if not (page.url or "").startswith(LOGIN_URL):
        goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=20000)
    if xpath_visible(page, XPATH_PHONE_TAB, timeout=3):
        page.locator(f"xpath={XPATH_PHONE_TAB}").first.click(timeout=5000)
    page.locator(f"xpath={XPATH_PHONE}").first.fill(account)
    page.locator(f"xpath={XPATH_PASSWORD}").first.fill(password)
    page.locator(f"xpath={XPATH_LOGIN}").first.click(timeout=10000)
    if xpath_visible(page, XPATH_AGREE, timeout=1):
        page.locator(f"xpath={XPATH_AGREE}").first.click(timeout=3000)
    if xpath_visible(page, XPATH_CONFIRM, timeout=1):
        page.locator(f"xpath={XPATH_CONFIRM}").first.click(timeout=3000)
    if target_store:
        target_store = re.sub(r"\s+", "", target_store)
        if xpath_visible(page, XPATH_SWITCH, timeout=2):
            page.locator(f"xpath={XPATH_SWITCH}").first.click(timeout=5000)
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def temu_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    target_store: Optional[str] = None,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("TEMU_ACCOUNT", "")
    password = password if password is not None else os.environ.get("TEMU_PASSWORD", "")
    if target_store is None:
        target_store = os.environ.get("TEMU_STORE", "")
    if not account or not password:
        raise ValueError("缺少 Temu 账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, target_store=target_store or "", page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
