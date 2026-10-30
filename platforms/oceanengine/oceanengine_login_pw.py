"""Playwright port of 影刀「巨量登录」 activity_7bca6d/process1.py.

Opens https://business.oceanengine.com/login, optionally logs out when
``status`` is true, fills the email/password selectors, then runs process48.
"""
from __future__ import annotations

import os
from typing import Callable, List, Optional

from playwright.sync_api import Page

from . import captcha
from platforms.doudian.doudian_login_pw import verify_platform
from .helpers import (
    NeedsHumanError,
    OnError,
    SellerLoginResult,
    close_result,
    detect_human_text,
    fill_checked,
    finish,
    goto_with_retry,
    open_page,
    page_text,
    sleep,
    visible,
    xpath_visible,
)

LOGIN_URL = "https://business.oceanengine.com/login"
XPATH_HOME = '//div[contains(@class, "style_header")][text()="首页"]'
XPATH_AVATAR = '//div[contains(@class, "index_header-user-info")]'
XPATH_LOGOUT = '//div[contains(@class, "index_header-user-card-layout-item")]//*[text()="退出账号"]'
XPATH_EMAIL_TAB = '//div[text()="邮箱登录"]'
SEL_EMAIL = 'input[name="email"][placeholder="请输入邮箱"]'
SEL_PASSWORD = 'input[placeholder="密码"][type="password"]'
SEL_LOGIN = "button.account-center-action-button"
SEL_AGREEMENT = "div.account-center-agreement-check"
ALREADY = "已登录，不执行重新登录"


def _logout(page: Page) -> None:
    page.locator(f"xpath={XPATH_AVATAR}").first.click(timeout=20000)
    sleep(3)
    page.locator(f"xpath={XPATH_LOGOUT}").first.click(timeout=20000)
    sleep(1)


def _already(page: Page, relogin: bool) -> bool:
    if not xpath_visible(page, XPATH_HOME, timeout=2):
        return False
    if relogin:
        _logout(page)
        return False
    return True


def login(
    account: str,
    password: str,
    token: str,
    *,
    relogin: bool = False,
    retries: int = 5,
    page: Optional[Page] = None,
    click_recognizer: Optional[Callable[[str], str]] = None,
):
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=4, timeout_ms=60000)
    if _already(page, relogin):
        return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
    if not visible(page, SEL_EMAIL, timeout=5) and _already(page, relogin):
        return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
    if xpath_visible(page, XPATH_EMAIL_TAB, timeout=3):
        try:
            page.locator(f"xpath={XPATH_EMAIL_TAB}").first.click(timeout=3000)
            sleep(1)
        except Exception:
            pass
    fill_checked(page.locator(SEL_EMAIL).first, str(account), limit=3)
    sleep(1)
    fill_checked(page.locator(SEL_PASSWORD).first, str(password), limit=3)
    sleep(1)
    if visible(page, SEL_AGREEMENT, timeout=1):
        page.locator(SEL_AGREEMENT).first.click(timeout=5000)
        sleep(1)
    page.locator(SEL_LOGIN).first.click(timeout=20000)
    sleep(1)
    human = detect_human_text(page_text(page))
    if human:
        raise NeedsHumanError(human)
    verify_platform(page, token, retries, calls, click_recognizer)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def oceanengine_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    relogin: bool = False,
    retries: int = 5,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
    click_recognizer: Optional[Callable[[str], str]] = None,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("OCEANENGINE_ACCOUNT", "")
    password = password if password is not None else os.environ.get("OCEANENGINE_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if not account or not password:
        raise ValueError("缺少巨量账号或密码")
    captcha.require_yunma_token(yunma_token)

    def _run(page=None, **_ignored):
        return login(
            account,
            password,
            yunma_token,
            relogin=relogin,
            retries=retries,
            page=page,
            click_recognizer=click_recognizer,
        )

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    relogin = os.environ.get("OCEANENGINE_RELOGIN", "").lower() in {"1", "true", "yes"}
    result = oceanengine_login(relogin=relogin, retries=int(os.environ.get("OCEANENGINE_RETRIES", "5")))
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
