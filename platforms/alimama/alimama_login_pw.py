"""Playwright port of 影刀「阿里妈妈数智登录」 activity_7bca6d/process42.py."""
from __future__ import annotations

import os
from typing import List, Optional

from playwright.sync_api import Page

from .helpers import (
    NeedsHumanError,
    OnError,
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

LOGIN_URL = "https://www.alimama.com/index.htm"
XPATH_LOGIN_NOW = '//div[normalize-space(text())="立即登录"]'
XPATH_FRAME = '//iframe[contains(@src, "login.taobao.com")]'
XPATH_LOGOUT = '//*[@id="app"]//*[text()="退出"]'
XPATH_HEADER_LOGOUT = '//*[@id="header-info"]//*[text()="退出"]'
SEL_USER = "#fm-login-id"
SEL_PASSWORD = "#fm-login-password"
XPATH_SUBMIT = '//button[text()="登录"]'
SEL_SMS = "#J_GetCode"
SEL_NC = "iframe#baxia-dialog-content"
SMS_MESSAGE = "需要进行短信验证！"


def login(
    account: str,
    password: str,
    *,
    relogin: bool = False,
    page: Optional[Page] = None,
):
    shots: List[str] = []
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=120000)
    sleep(3)
    if xpath_visible(page, XPATH_LOGOUT, timeout=3):
        if not relogin:
            return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
        page.locator(f"xpath={XPATH_LOGOUT}").first.click(timeout=20000)
        sleep(3)
        page.reload(wait_until="domcontentloaded", timeout=120000)
    if xpath_visible(page, XPATH_LOGIN_NOW, timeout=5):
        page.locator(f"xpath={XPATH_LOGIN_NOW}").first.click(timeout=5000)
        sleep(2)
    frame = page.locator(f"xpath={XPATH_FRAME}").first
    frame.wait_for(state="attached", timeout=20000)
    src = frame.get_attribute("src") or ""
    if src:
        page.goto(src, wait_until="domcontentloaded", timeout=120000)
    fill_checked(page.locator(SEL_USER).first, account, limit=3)
    sleep(1)
    if xpath_visible(page, XPATH_HEADER_LOGOUT, timeout=5):
        return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
    fill_checked(page.locator(SEL_PASSWORD).first, password, limit=3)
    sleep(1)
    page.locator(f"xpath={XPATH_SUBMIT}").first.click(timeout=5000)
    sleep(3)
    if visible(page, SEL_NC, timeout=3):
        box = page.locator(SEL_NC).first.bounding_box()
        if box:
            x1 = box["x"]
            y1 = box["y"] + box["height"] / 2
            mouse_drag(page, x1, y1, x1 + 10 + 320, y1 - 20)
        try:
            page.locator(f"xpath={XPATH_SUBMIT}").first.click(timeout=5000)
        except Exception:
            pass
    if visible(page, SEL_SMS, timeout=2):
        page.locator(SEL_SMS).first.click(timeout=5000)
        raise NeedsHumanError(SMS_MESSAGE)
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def alimama_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    relogin: bool = False,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("ALIMAMA_ACCOUNT", "")
    password = password if password is not None else os.environ.get("ALIMAMA_PASSWORD", "")
    if not account or not password:
        raise ValueError("账户或密码为空，请检查~")

    def _run(page=None, **_ignored):
        return login(account, password, relogin=relogin, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = alimama_login()
    print({"ok": result.ok, "error": result.error})
    close_result(result)


if __name__ == "__main__":
    main()
