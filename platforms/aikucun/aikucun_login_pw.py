"""Playwright port of 影刀「爱库存登录」 activity_7bca6d/process33.py.

Slider is activity_4f0f15d7.slider_captcha with offset -4 and move_speed fast.
Distance uses the OpenCV match only when opencv is installed; the offset
formula is always free_slider_drag_distance.
"""
from __future__ import annotations

import os
from typing import List, Optional

from playwright.sync_api import Page

from . import captcha
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
)

LOGIN_URL = "https://merc.aikucun.com/login.html"
SEL_USER = 'input.el-input__inner[placeholder="输入用户名"]'
SEL_PASSWORD = 'input.el-input__inner[placeholder="输入密码"]'
SEL_LOGIN = "button.merchant_login_btn"
SEL_SLIDER = "#dx_captcha_basic_slider_2"
SEL_REFRESH = "#dx_captcha_basic_btn-refresh_4"
SEL_BAD_PASSWORD = "p.el-form-item__error"
BAD_PASSWORD = "账号密码错误"
FAIL = "次未通过，登录失败"


def login(account: str, password: str, *, retries: int = 5, page: Optional[Page] = None):
    shots: List[str] = []
    page, owned = open_page(page, headless=False)
    for _ in range(int(retries) or 5):
        goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=30000)
        fill_checked(page.locator(SEL_USER).first, account, limit=3)
        fill_checked(page.locator(SEL_PASSWORD).first, password, limit=3)
        page.locator(SEL_LOGIN).first.click(timeout=20000)
        for _inner in range(20):
            if not visible(page, SEL_LOGIN, timeout=1):
                return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
            if visible(page, SEL_REFRESH, timeout=1):
                page.locator(SEL_REFRESH).first.click(timeout=3000)
            if visible(page, SEL_SLIDER, timeout=1) and visible(page, "canvas", timeout=0.5):
                try:
                    match_x = captcha.canny_match_x(
                        page.locator("canvas").first.screenshot(type="png"),
                        page.locator(SEL_SLIDER).first.screenshot(type="png"),
                    )
                except Exception:
                    match_x = None
                piece = page.locator(SEL_SLIDER).first
                box = piece.bounding_box()
                if match_x is not None and box:
                    distance = captcha.free_slider_drag_distance(
                        match_x, captcha.AIKUCUN_FREE_SLIDER_OFFSET
                    )
                    x1 = box["x"] + box["width"] / 2
                    y1 = box["y"] + box["height"] / 2
                    mouse_drag(page, x1, y1, x1 + distance, y1)
            sleep(2)
        if visible(page, SEL_BAD_PASSWORD, timeout=0.5):
            raise CredentialsRejected(BAD_PASSWORD)
    raise SellerLoginError(f"验证码{retries}{FAIL}")


def aikucun_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    retries: int = 5,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("AIKUCUN_ACCOUNT", "")
    password = password if password is not None else os.environ.get("AIKUCUN_PASSWORD", "")
    if not account or not password:
        raise ValueError("缺少爱库存账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, retries=retries, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = aikucun_login(retries=int(os.environ.get("AIKUCUN_RETRIES", "5")))
    print({"ok": result.ok, "error": result.error})
    close_result(result)


if __name__ == "__main__":
    main()
