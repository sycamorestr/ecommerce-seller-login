"""Playwright port of 影刀「聚水潭登录」 activity_jvshuitan/login.py."""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from seller_common import OnError, SellerLoginResult, fill_checked, finish, goto_with_retry, open_page, xpath_visible

LOGIN_URL = "https://www.erp321.com/login.aspx"
SOURCE = "activity_jvshuitan/login.py"
XPATH_SWITCH = '//img[@alt="切换密码"]'
XPATH_ACCOUNT = '//input[@placeholder="邮箱地址/手机号码"]'
XPATH_PASSWORD = '//input[@placeholder="请输入密码"]'
XPATH_AGREE = '//span[@class="ant-checkbox"]/input'
XPATH_LOGIN = '//button[.="立即登录"]'
XPATH_WELCOME = '//div[@role="tab" and .="聚水潭欢迎您"]'


def login(account: str, password: str, *, page: Optional[Page] = None):
    shots: list = []
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=60000)
    if xpath_visible(page, XPATH_SWITCH, timeout=2):
        page.locator(f"xpath={XPATH_SWITCH}").first.click(timeout=5000)
    fill_checked(page.locator(f"xpath={XPATH_ACCOUNT}").first, account, limit=3)
    fill_checked(page.locator(f"xpath={XPATH_PASSWORD}").first, password, limit=3)
    agree = page.locator(f"xpath={XPATH_AGREE}").first
    try:
        agree.check(timeout=3000)
    except Exception:
        agree.click(timeout=3000)
    page.locator(f"xpath={XPATH_LOGIN}").first.click(timeout=10000)
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def jushuitan_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("JUSHUITAN_ACCOUNT", "")
    password = password if password is not None else os.environ.get("JUSHUITAN_PASSWORD", "")
    if not account or not password:
        raise ValueError("缺少聚水潭账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
