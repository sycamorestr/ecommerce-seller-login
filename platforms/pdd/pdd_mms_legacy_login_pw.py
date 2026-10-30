"""Playwright port of 影刀「拼多多商家后台登录（待下架）」 process43.py.

Deprecated in ShadowBot (hidden block) and still ported. Same home URL as
process51, plus 点选1个坐标 (图鉴 captcha_type 19 / ttshitu_19_predict).
The source passes empty 图鉴账号/密码 and has no HTTP host, so a visible
点选验证码 stops at NeedsHumanError unless ``click_recognizer`` returns ``x,y``.
"""
from __future__ import annotations

import os
from typing import Callable, Optional

from playwright.sync_api import Page

from . import captcha
from .pdd_promote_login_pw import (
    FAIL,
    HOME_URL,
    LOGOUT_URL,
    XPATH_ACCOUNT_TAB,
    XPATH_LOGIN,
    XPATH_PASSWORD,
    XPATH_SHOP,
    XPATH_USER,
    XPATH_USER_INPUT,
    _require,
)
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

DEPRECATED = True
SHADOWBOT_PROCESS = "process43"
SEL_HINT = "span.picture-text__default"
XPATH_BG = '//img[contains(@class,"picture") or contains(@src,"captcha")]'


def login(
    account: str,
    password: str,
    *,
    relogin: bool = False,
    page: Optional[Page] = None,
    click_recognizer: Optional[Callable[[str], str]] = None,
):
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
    if xpath_visible(page, f'//{SEL_HINT}', timeout=0.2) or page.locator(SEL_HINT).count():
        hint = page.locator(SEL_HINT).first
        try:
            hint.wait_for(state="visible", timeout=3000)
        except Exception:
            hint = None
        if hint is not None:
            if click_recognizer is None:
                raise NeedsHumanError("点选验证码")
            image = __import__("base64").b64encode(hint.screenshot(type="png")).decode("ascii")
            raw = click_recognizer(image)
            positions = captcha.parse_click_positions(raw)
            if not positions:
                raise NeedsHumanError("点选验证码")
            box = hint.bounding_box() or {"x": 0, "y": 0}
            x, y = captcha.legacy_click_point(
                positions[0][0], positions[0][1], box["x"], box["y"], box["x"], box["y"], 1
            )
            page.mouse.click(x, y)
    if xpath_visible(page, XPATH_SHOP, timeout=5):
        return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
    raise NeedsHumanError(FAIL)


def pdd_mms_legacy_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    relogin: bool = False,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
    click_recognizer: Optional[Callable[[str], str]] = None,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("PDD_LEGACY_ACCOUNT", "")
    password = password if password is not None else os.environ.get("PDD_LEGACY_PASSWORD", "")
    _require(account, password)

    def _run(page=None, **_ignored):
        return login(account, password, relogin=relogin, page=page, click_recognizer=click_recognizer)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = pdd_mms_legacy_login()
    print({"ok": result.ok, "error": result.error, "deprecated": DEPRECATED})
    close_result(result)


if __name__ == "__main__":
    main()
