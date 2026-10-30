"""Playwright port of 影刀「拼多多推广平台登录」 process51.py.

Home URL is https://mms.pinduoduo.com/home/. Logout uses the janus API.
SMS/captcha is left as a manual gate: the source raises and marks a TODO.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import (
    NeedsHumanError,
    OnError,
    SellerLoginResult,
    close_result,
    fill_checked,
    finish,
    goto_with_retry,
    open_page,
    sleep,
    xpath_visible,
)

HOME_URL = "https://mms.pinduoduo.com/home/"
LOGOUT_URL = "https://mms.pinduoduo.com/janus/api/logout"
XPATH_USER = '(//*[@class="user-name-text"])[last()]'
XPATH_SHOP = '(//*[@class="user-name-text"])[1]'
XPATH_ACCOUNT_TAB = '//*[text()="账号登录"]'
XPATH_USER_INPUT = '//*[@id="usernameId"]'
XPATH_PASSWORD = '//*[@id="passwordId"]'
XPATH_LOGIN = '//*[text()="登录"]'
FAIL = "登录失败，请先手动通过验证。"
ALREADY = "不退出已登录账户，登录流程结束。"


def _require(account: str, password: str) -> None:
    if not isinstance(account, str) or not account:
        raise ValueError("请检查登录账号密码是否为字符串类型, 且不为空")
    if not isinstance(password, str) or not password:
        raise ValueError("请检查登录账号密码是否为字符串类型, 且不为空")


def login(account: str, password: str, *, relogin: bool = False, page: Optional[Page] = None):
    shots: list = []
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, HOME_URL, attempts=1, timeout_ms=120000)
    if xpath_visible(page, XPATH_USER, timeout=5):
        if not relogin:
            return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
        page.goto(LOGOUT_URL, wait_until="domcontentloaded", timeout=20000)
        sleep(2)
    page.goto(HOME_URL, wait_until="domcontentloaded", timeout=20000)
    page.locator(f"xpath={XPATH_ACCOUNT_TAB}").first.click(timeout=10000)
    sleep(1)
    fill_checked(page.locator(f"xpath={XPATH_USER_INPUT}").first, account, limit=3)
    fill_checked(page.locator(f"xpath={XPATH_PASSWORD}").first, password, limit=3)
    page.locator(f"xpath={XPATH_LOGIN}").first.click(timeout=5000)
    sleep(1)
    if xpath_visible(page, XPATH_SHOP, timeout=10):
        return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
    raise NeedsHumanError(FAIL)


def pdd_promote_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    relogin: bool = False,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("PDD_PROMOTE_ACCOUNT", "")
    password = password if password is not None else os.environ.get("PDD_PROMOTE_PASSWORD", "")
    _require(account, password)

    def _run(page=None, **_ignored):
        return login(account, password, relogin=relogin, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = pdd_promote_login()
    print({"ok": result.ok, "error": result.error})
    close_result(result)


if __name__ == "__main__":
    main()
