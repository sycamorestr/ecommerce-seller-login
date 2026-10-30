"""Playwright port of 影刀「巨量纵横登录」 activity_7bca6d/process12.py."""
from __future__ import annotations

import os
from typing import Callable, List, Optional

from playwright.sync_api import Page

import captcha_helpers as captcha
from doudian_login_pw import verify_platform
from oceanengine_email_login_pw import XPATH_OLD, XPATH_VERSION
from seller_common import (
    OnError,
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
SEL_SWITCH = "div.account-center-switch-button.email"
SEL_ACCOUNT = 'input[placeholder="请输入邮箱"].ace-input'
SEL_PASSWORD = 'input[placeholder="密码"].ace-input'
SEL_AGREE = "div.account-center-agreement-check"
SEL_LOGIN = "button.account-center-action-button"


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
    retries: int = 5,
    page: Optional[Page] = None,
    click_recognizer: Optional[Callable[[str], str]] = None,
):
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=20000)
    sleep(2)
    _old_workbench(page)
    if visible(page, SEL_SWITCH, timeout=2):
        try:
            page.locator(SEL_SWITCH).first.click(timeout=5000)
            sleep(1)
        except Exception:
            pass
    fill_checked(page.locator(SEL_ACCOUNT).first, str(account), limit=3)
    sleep(1)
    fill_checked(page.locator(SEL_PASSWORD).first, str(password), limit=3)
    sleep(1)
    page.locator(SEL_AGREE).first.click(timeout=20000)
    sleep(0.3)
    page.locator(SEL_LOGIN).first.click(timeout=20000)
    sleep(1)
    _old_workbench(page)
    verify_platform(page, token, retries, calls, click_recognizer)
    _old_workbench(page)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def oceanengine_zongheng_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    retries: int = 5,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
    click_recognizer: Optional[Callable[[str], str]] = None,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("OCEANENGINE_ZH_ACCOUNT", "")
    password = password if password is not None else os.environ.get("OCEANENGINE_ZH_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if not account or not password:
        raise ValueError("缺少巨量纵横账号或密码")
    captcha.require_yunma_token(yunma_token)

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, retries=retries, page=page, click_recognizer=click_recognizer)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = oceanengine_zongheng_login()
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
