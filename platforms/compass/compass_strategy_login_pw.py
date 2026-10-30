"""Playwright port of 影刀「电商罗盘策略登陆」 activity_7bca6d/process59.py."""
from __future__ import annotations

import os
from typing import List, Optional

from playwright.sync_api import Page

from . import captcha
from .compass_login_pw import (
    SEL_ACCOUNT,
    SEL_AGREE,
    SEL_BG,
    SEL_DRAG,
    SEL_EMAIL_TAB,
    SEL_LOGIN,
    SEL_MERCHANT,
    SEL_PASSWORD,
    SEL_SEND,
    SEL_SWITCH,
    XPATH_SHOPS,
    _slider,
)
from .helpers import (
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

LOGIN_URL = "https://compassbrand.jinritemai.com/login"
CABIN_MARK = "compassbrand.jinritemai.com/cabin"
SEL_CORNER = "span.user-info, span[class*='user']"
SEL_BACK = "div.index_backbar__3dcm0"
XPATH_DROPDOWN = '//div[contains(@class, "dropdown-container")]'


def login(
    account: str,
    password: str,
    token: str,
    *,
    shop_name: str = "",
    relogin: bool = False,
    page: Optional[Page] = None,
):
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    if page.url in ("", "about:blank") or CABIN_MARK not in (page.url or ""):
        goto_with_retry(page, LOGIN_URL, attempts=4, timeout_ms=20000)
    sleep(3)
    if relogin:
        if visible(page, SEL_CORNER, timeout=1):
            page.locator(SEL_CORNER).first.click(timeout=5000)
            page.locator("li.ecom-dropdown-menu-item").first.click(timeout=5000)
        if xpath_visible(page, XPATH_DROPDOWN, timeout=5):
            page.locator(f"xpath={XPATH_DROPDOWN}").first.click(timeout=5000)
            page.locator("li.ecom-dropdown-menu-item").first.click(timeout=5000)
    elif visible(page, SEL_CORNER, timeout=1):
        return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
    if visible(page, SEL_BACK, timeout=1):
        page.locator(SEL_BACK).first.click(timeout=5000)
    sleep(2)
    if visible(page, SEL_MERCHANT, timeout=1):
        page.locator(SEL_MERCHANT).first.click(timeout=5000)
    sleep(2)
    if not visible(page, SEL_EMAIL_TAB, timeout=1) and visible(page, SEL_SWITCH, timeout=1):
        page.locator(SEL_SWITCH).first.click(timeout=5000, position={"x": 3, "y": 3})
    for _ in range(5):
        if not visible(page, SEL_SEND, timeout=1):
            break
        page.locator(SEL_EMAIL_TAB).first.click(timeout=5000)
    fill_checked(page.locator(SEL_ACCOUNT).first, account, limit=3)
    fill_checked(page.locator(SEL_PASSWORD).first, password, limit=3)
    if visible(page, SEL_AGREE, timeout=1):
        page.locator(SEL_AGREE).first.click(timeout=3000)
    page.locator(SEL_LOGIN).first.click(timeout=10000)
    sleep(2)
    for _ in range(5):
        if visible(page, SEL_BG, timeout=1):
            _slider(page, token, calls)
            break
        sleep(1)
    if page.locator(f"xpath={XPATH_SHOPS}").count():
        shops = page.locator(f"xpath={XPATH_SHOPS}")
        if shop_name:
            for index in range(shops.count()):
                text = (shops.nth(index).inner_text(timeout=1000) or "").split("\n")[0]
                if text == shop_name:
                    shops.nth(index).click(timeout=5000)
                    break
        elif shops.count():
            shops.first.click(timeout=5000)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def compass_strategy_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    shop_name: Optional[str] = None,
    relogin: bool = False,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("COMPASS_STRATEGY_ACCOUNT", "")
    password = password if password is not None else os.environ.get("COMPASS_STRATEGY_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if shop_name is None:
        shop_name = os.environ.get("COMPASS_STRATEGY_SHOP", "")
    if not account or not password:
        raise ValueError("缺少电商罗盘策略账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, shop_name=shop_name or "", relogin=relogin, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = compass_strategy_login()
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
