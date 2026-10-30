"""Playwright port of Temu-广告平台-登录 activity_temu_shop/advertisement_login.py."""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import OnError, SellerLoginError, SellerLoginResult, finish, goto_with_retry, open_page

LOGIN_URL = "https://ads.temu.com/login.html"
SOURCE = "activity_temu_shop/advertisement_login.py"
XPATH_LOGIN = '//span[text()="登录"]'
XPATH_CROSS = '//div[.="请选择你的登录方式"]/following-sibling::div[2]//span[.="登录"]'
XPATH_PHONE = '//input[@placeholder="手机号码"]'
XPATH_PASSWORD = '//input[@placeholder="密码"]'
XPATH_EMPOWER = '//button/span[.="授权登录"]'
NO_PERMISSION = "当前子账号无平台登入权限或需切换主账号签署协议"


def login(account: str, password: str, *, page: Optional[Page] = None):
    shots: list = []
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=20000)
    page.locator(f"xpath={XPATH_LOGIN}").first.click(timeout=10000)
    page.locator(f"xpath={XPATH_CROSS}").first.click(timeout=10000)
    page.locator(f"xpath={XPATH_PHONE}").first.fill(account)
    page.locator(f"xpath={XPATH_PASSWORD}").first.fill(password)
    page.locator(f"xpath={XPATH_EMPOWER}").first.click(timeout=10000)
    if LOGIN_URL in (page.url or ""):
        raise SellerLoginError(f"{account} 账号登录可能失败，请检查页面是否包含弹窗")
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def temu_ads_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("TEMU_ADS_ACCOUNT", "")
    password = password if password is not None else os.environ.get("TEMU_ADS_PASSWORD", "")
    if not account or not password:
        raise ValueError("缺少 Temu 广告平台账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
