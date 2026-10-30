"""Playwright port of 影刀「巨量引擎邮箱登录」 activity_7bca6d/process47.py.

URL is https://business.oceanengine.com/login?appKey=51. After login it runs
process48, then process49 (email code). Mail fetch is not bundled.
"""
from __future__ import annotations

import os
from typing import Callable, List, Optional

from playwright.sync_api import Page

from . import captcha
from platforms.doudian.doudian_login_pw import verify_email, verify_platform
from .helpers import (
    OnError,
    SellerLoginError,
    SellerLoginResult,
    close_result,
    fill_checked,
    finish,
    goto_with_retry,
    open_page,
    sleep,
    visible,
    xpath_visible,
)

LOGIN_URL = "https://business.oceanengine.com/login?appKey=51"
XPATH_VERSION = '//span[contains(@class, "typography")][text()="请选择工作台版本"]'
XPATH_OLD = '//div[@class="card-body"][.//span[normalize-space(.)="旧版巨量引擎工作台"]]//button'
XPATH_ACCOUNT = '//div[@id="header-user" or @id="navigator-right-account" or @class="navigator-user-button"]'
XPATH_LOGOUT = '//*[contains(text(), "退出")]'
XPATH_EMAIL_TAB = '//div[contains(@class, "account-center-switch-button")][contains(text(), "邮箱")]'
XPATH_EMAIL = '//input[contains(@placeholder , "邮箱")]'
XPATH_PASSWORD = '//input[@placeholder = "密码"]'
XPATH_AGREE = '//div[contains(@class, "account-center-agreement-check")]'
XPATH_LOGIN = '//button[text() = "登录"]'
XPATH_SHOP = '(//div[@id="header-user" or @id="navigator-right-account" or @class="navigator-user-button"]//div[contains(@class,"bp-tree-container-name")])[1]'
ALREADY = "不退出已登录的账户，登录流程结束。"


def _old_workbench(page: Page) -> None:
    if not xpath_visible(page, XPATH_VERSION, timeout=3):
        return
    page.locator(f"xpath={XPATH_OLD}").first.click(timeout=20000)
    sleep(1)


def login(
    account: str,
    password: str,
    token: str,
    *,
    relogin: bool = False,
    email_code: str = "",
    retries: int = 10,
    page: Optional[Page] = None,
    click_recognizer: Optional[Callable[[str], str]] = None,
):
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=120000)
    _old_workbench(page)
    if xpath_visible(page, XPATH_ACCOUNT, timeout=4):
        if not relogin:
            return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
        account_box = page.locator(f"xpath={XPATH_ACCOUNT}").first
        account_box.hover(timeout=20000)
        sleep(1)
        page.locator(f"xpath={XPATH_LOGOUT}").first.click(timeout=20000)
        sleep(1)
    if xpath_visible(page, XPATH_EMAIL_TAB, timeout=5):
        page.locator(f"xpath={XPATH_EMAIL_TAB}").first.click(timeout=20000)
        sleep(1)
    fill_checked(page.locator(f"xpath={XPATH_EMAIL}").first, account, limit=3)
    sleep(1)
    fill_checked(page.locator(f"xpath={XPATH_PASSWORD}").first, password, limit=3)
    sleep(1)
    agree = page.locator(f"xpath={XPATH_AGREE}").first
    agree.wait_for(state="visible", timeout=10000)
    class_name = agree.get_attribute("class") or ""
    if "checked" not in class_name.lower():
        agree.click(timeout=20000)
        sleep(1)
    page.locator(f"xpath={XPATH_LOGIN}").first.click(timeout=20000)
    sleep(2)
    _old_workbench(page)
    verify_platform(page, token, retries, calls, click_recognizer)
    verify_email(page, "", "", email_code, token, retries, calls, click_recognizer)
    if not xpath_visible(page, XPATH_SHOP, timeout=4):
        raise SellerLoginError("登录流程失败！")
    _old_workbench(page)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def oceanengine_email_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    email_code: Optional[str] = None,
    relogin: bool = False,
    retries: int = 10,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
    click_recognizer: Optional[Callable[[str], str]] = None,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("OCEANENGINE_EMAIL", "")
    password = password if password is not None else os.environ.get("OCEANENGINE_EMAIL_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if email_code is None:
        email_code = os.environ.get("OCEANENGINE_EMAIL_CODE", "")
    if not account or not password:
        raise ValueError("缺少巨量引擎邮箱或密码")
    captcha.require_yunma_token(yunma_token)

    def _run(page=None, **_ignored):
        return login(
            account,
            password,
            yunma_token,
            relogin=relogin,
            email_code=email_code or "",
            retries=retries,
            page=page,
            click_recognizer=click_recognizer,
        )

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = oceanengine_email_login(retries=int(os.environ.get("OCEANENGINE_EMAIL_RETRIES", "10")))
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
