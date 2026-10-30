"""Playwright port of 影刀「电商罗盘登录」 activity_7bca6d/process15.py.

Slider is dy_slider_captcha type 20225, offset 0, retry 5.
"""
from __future__ import annotations

import os
from typing import List, Optional

from playwright.sync_api import Page

import captcha_helpers as captcha
from seller_common import (
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

LOGIN_URL = "https://compass.jinritemai.com/login"
SHOP_MARK = "compass.jinritemai.com/shop"
XPATH_LOADING = '//span[contains(@class, "dot-spin")]'
XPATH_USER = '//div[@id="compass-shop-header"]//div[contains(@class, "userName")]'
SEL_MERCHANT = "div.index_name__xx5yj"
SEL_EMAIL_TAB = "div.account-center-switch-button.email"
SEL_SWITCH = "div.login-switcher--cell"
SEL_SEND = "div.account-center-code-captcha"
SEL_ACCOUNT = 'input[placeholder="请输入邮箱"].ace-input'
SEL_PASSWORD = 'input[placeholder="密码"].ace-input'
SEL_AGREE = "input.ecom-checkbox-input"
SEL_LOGIN = "button.account-center-action-button"
SEL_BG = "img.captcha-verify-image"
SEL_DRAG = "div.captcha-slider-btn"
XPATH_SHOPS = "//div[text()='请选择组织']/following-sibling::div//div[@class='index_introName__2tsRs']"
ALREADY = "当前账号已经登录，不必再重新登录"


def _slider(page: Page, token: str, calls: List[int]) -> None:
    captcha.require_yunma_token(token)
    background = page.locator(SEL_BG).first
    drag = page.locator(SEL_DRAG).first
    png = background.screenshot(type="png")
    image = __import__("base64").b64encode(png).decode("ascii")
    response = captcha.yunma_post(captcha.dy_slider_payload(image, token))
    calls[0] += 1
    px = captcha.dy_recognized_px(response)
    box = background.bounding_box() or {"width": 1}
    scale = box["width"] / max(background.evaluate("el => el.naturalWidth || el.width || 1"), 1)
    distance = captcha.dy_slider_distance(px, scale, 0)
    drag_box = drag.bounding_box()
    if not drag_box:
        return
    x1 = drag_box["x"] + drag_box["width"] / 2
    y1 = drag_box["y"] + drag_box["height"] / 2
    mouse_drag(page, x1, y1, x1 + distance, y1)


def _pick_shop(page: Page, shop_name: str) -> None:
    shops = page.locator(f"xpath={XPATH_SHOPS}")
    count = shops.count()
    if count == 0:
        return
    if not shop_name:
        shops.first.click(timeout=5000)
        return
    for index in range(count):
        text = (shops.nth(index).inner_text(timeout=1000) or "").split("\n")[0]
        if text == shop_name:
            shops.nth(index).click(timeout=5000)
            return


def login(
    account: str,
    password: str,
    token: str,
    *,
    shop_name: str = "",
    relogin: bool = False,
    wait_time: int = 3,
    page: Optional[Page] = None,
):
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=20000)
    if SHOP_MARK not in (page.url or ""):
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20000)
    if visible(page, SEL_MERCHANT, timeout=2):
        sleep(wait_time)
        page.locator(SEL_MERCHANT).first.click(timeout=5000)
        sleep(1)
    if relogin:
        for _ in range(8):
            sleep(1)
            if not xpath_visible(page, XPATH_USER, timeout=2):
                break
            page.locator(f"xpath={XPATH_USER}").first.click(timeout=5000)
            page.locator("li.ecom-dropdown-menu-item").first.click(timeout=5000)
    elif xpath_visible(page, XPATH_USER, timeout=2):
        return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
    sleep(wait_time)
    if visible(page, SEL_MERCHANT, timeout=1):
        page.locator(SEL_MERCHANT).first.click(timeout=5000)
    sleep(wait_time)
    for _ in range(5):
        if visible(page, SEL_EMAIL_TAB, timeout=1):
            break
        if visible(page, SEL_SWITCH, timeout=1):
            page.locator(SEL_SWITCH).first.click(timeout=5000, position={"x": 3, "y": 3})
    for _ in range(5):
        if not visible(page, SEL_SEND, timeout=1):
            break
        page.locator(SEL_EMAIL_TAB).first.click(timeout=5000)
    if xpath_visible(page, XPATH_LOADING, timeout=1):
        try:
            page.locator(f"xpath={XPATH_LOADING}").first.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass
    fill_checked(page.locator(SEL_ACCOUNT).first, str(account), limit=3)
    fill_checked(page.locator(SEL_PASSWORD).first, str(password), limit=3)
    if visible(page, SEL_AGREE, timeout=1):
        page.locator(SEL_AGREE).first.click(timeout=3000)
    page.locator(SEL_LOGIN).first.click(timeout=10000)
    sleep(wait_time)
    for _ in range(5):
        if not visible(page, SEL_BG, timeout=1):
            sleep(1)
            continue
        page.locator(SEL_DRAG).first.hover(timeout=5000)
        _slider(page, token, calls)
        break
    _pick_shop(page, shop_name)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def compass_login(
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
    account = account if account is not None else os.environ.get("COMPASS_ACCOUNT", "")
    password = password if password is not None else os.environ.get("COMPASS_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if shop_name is None:
        shop_name = os.environ.get("COMPASS_SHOP", "")
    if not account or not password:
        raise ValueError("缺少电商罗盘账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, shop_name=shop_name or "", relogin=relogin, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = compass_login()
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
