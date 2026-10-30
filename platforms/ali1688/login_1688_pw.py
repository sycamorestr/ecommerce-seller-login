"""Playwright port of 影刀「1688登录」 activity_7bca6d/login_1688.py.

NC slider is a full-width drag of 1688_login_verify. No default account is stored.
"""
from __future__ import annotations

import os
from typing import List, Optional

from playwright.sync_api import Page

from .helpers import (
    CredentialsRejected,
    OnError,
    SellerLoginError,
    SellerLoginResult,
    close_result,
    fill_checked,
    finish,
    goto_with_retry,
    mouse_drag,
    open_page,
    sleep,
    visible,
    xpath_visible,
)

LOGIN_URL = (
    "https://login.taobao.com/?redirect_url=https%3A%2F%2Flogin.1688.com%2Fmember%2Fjump.htm"
    "%3Ftarget%3Dhttps%253A%252F%252Flogin.1688.com%252Fmember%252FmarketSigninJump.htm"
    "%253FDone%253Dhttps%25253A%25252F%25252Fmember.1688.com%25252Fmember%25252Foperations"
    "%25252Fmember_operations_jump_engine.htm%25253Ftracelog%25253Dlogin%252526operSceneId"
    "%25253Dafter_pass_from_taobao_new%252526defaultTarget%25253Dhttps%2525253A%2525252F"
    "%2525252Fwork.1688.com%2525252F%2525253Ftracelog%2525253Dlogin_target_is_blank_1688"
    "&style=tao_custom&from=1688web"
)
XPATH_OTHER = '//div[.="使用其他账号登录"]'
XPATH_PASSWORD_TAB = '//a[.="密码登录"]'
XPATH_USER = '//input[@placeholder="账号名/邮箱/手机号"]'
XPATH_PASSWORD = '//input[@placeholder="请输入登录密码"]'
XPATH_LOGIN = '//button[.="登录"]'
XPATH_ERROR = '//div[@class="login-error-msg"]'
SEL_NC = "#nc_1_n1z"
SEL_NC_LABEL = "span.nc-lang-cnt"
SEL_NC_ERROR = "div.errloading"
SWITCH_FAIL = "切换至登录页面失败"
LOGIN_FAIL = "登录失败，请手动登录"


def _nc(page: Page) -> None:
    slider = page.locator(SEL_NC).first
    label = page.locator(SEL_NC_LABEL).first
    box = slider.bounding_box()
    bar = label.bounding_box()
    if not box or not bar:
        return
    x1 = box["x"] + box["width"] / 2
    y1 = box["y"] + box["height"] / 2
    mouse_drag(page, x1, y1, x1 + bar["width"], y1)


def login(account: str, password: str, *, retries: int = 3, page: Optional[Page] = None):
    shots: List[str] = []
    page, owned = open_page(page, headless=False)
    ok = False
    for _ in range(5):
        goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=20000)
        if page.url == LOGIN_URL:
            ok = True
            break
        sleep(1)
    if not ok and LOGIN_URL not in (page.url or ""):
        raise SellerLoginError(SWITCH_FAIL)
    if xpath_visible(page, '//button[.="快速进入"]', timeout=1):
        page.locator(f"xpath={XPATH_OTHER}").first.click(timeout=5000)
    page.locator(f"xpath={XPATH_PASSWORD_TAB}").first.click(timeout=10000)
    fill_checked(page.locator(f"xpath={XPATH_USER}").first, account, limit=3)
    password_box = page.locator(f"xpath={XPATH_PASSWORD}").first
    password_box.click(timeout=5000)
    fill_checked(password_box, password, limit=3)
    for _ in range(int(retries) or 3):
        if visible(page, SEL_NC_ERROR, timeout=0.5):
            page.locator(SEL_NC_ERROR).first.click(timeout=3000)
        if visible(page, SEL_NC_LABEL, timeout=0.8):
            _nc(page)
        else:
            break
    page.locator(f"xpath={XPATH_LOGIN}").first.click(timeout=10000)
    sleep(1)
    if xpath_visible(page, XPATH_ERROR, timeout=1):
        text = (page.locator(f"xpath={XPATH_ERROR}").first.inner_text(timeout=1000) or "").strip()
        raise CredentialsRejected(text or "登录失败")
    if xpath_visible(page, XPATH_LOGIN, timeout=2):
        raise SellerLoginError(LOGIN_FAIL)
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def login_1688(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    retries: int = 3,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("LOGIN1688_ACCOUNT", "")
    password = password if password is not None else os.environ.get("LOGIN1688_PASSWORD", "")
    if not account or not password:
        raise ValueError("缺少1688账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, retries=retries, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = login_1688(retries=int(os.environ.get("LOGIN1688_RETRIES", "3")))
    print({"ok": result.ok, "error": result.error})
    close_result(result)


if __name__ == "__main__":
    main()
