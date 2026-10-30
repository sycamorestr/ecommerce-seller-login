"""Playwright port of 影刀「阿里妈妈_平台登录」 activity_d91a274e/process6.py.

Distinct from alimama_login_pw.py (数智, www.alimama.com). This one opens a
named ad-platform homepage, then fills the login iframe and drags the NC bar
to the track's right edge plus 50px, as the source drag_to does.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import (
    OnError,
    SellerLoginError,
    SellerLoginResult,
    fill_checked,
    finish,
    goto_with_retry,
    mouse_drag,
    open_page,
    visible,
)

SOURCE = "activity_d91a274e/process6.py"
PLATFORM_URLS = {
    "引力魔方": "https://tuijian.taobao.com/indexbp.html",
    "直通车": "https://subway.simba.taobao.com/index.jsp",
    "万象台": "https://adbrain.taobao.com/indexbp.html",
    "超级钻展": "https://zuanshi.taobao.com/index_poquan.jsp",
    "品销宝": "https://branding.taobao.com/index.action",
    "商家中心": "https://ad.alimama.com/portal/v2/report/promotionDataPage.htm",
}
UNSUPPORTED = "当前版本指令仅支持以下六个平台的汇总数据获取【直通车，万象台，商家中心，引力魔方，超级钻展，品销宝】请输入正确的平台名称~"
EMPTY = "账户或密码为空，请检查~"
SEL_USER = "#fm-login-id"
SEL_PASSWORD = "#fm-login-password"
SEL_LOGIN = "button.fm-submit, button.password-login"
SEL_SLIDER = "#nc_1_n1z"
DRAG_RELEASE_X = 50


def login(account: str, password: str, platform: str, *, page: Optional[Page] = None):
    if platform not in PLATFORM_URLS:
        raise SellerLoginError(UNSUPPORTED)
    shots: list = []
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, PLATFORM_URLS[platform], attempts=1, timeout_ms=60000)
    if visible(page, SEL_USER, timeout=8):
        fill_checked(page.locator(SEL_USER).first, account, limit=3)
        fill_checked(page.locator(SEL_PASSWORD).first, password, limit=3)
        if visible(page, SEL_SLIDER, timeout=2):
            box = page.locator(SEL_SLIDER).first.bounding_box()
            if box:
                x1 = box["x"] + box["width"] / 2
                y1 = box["y"] + box["height"] / 2
                mouse_drag(page, x1, y1, x1 + box["width"] + DRAG_RELEASE_X, y1)
        page.locator(SEL_LOGIN).first.click(timeout=10000)
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def alimama_platform_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    platform: Optional[str] = None,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("ALIMAMA_PLATFORM_ACCOUNT", "")
    password = password if password is not None else os.environ.get("ALIMAMA_PLATFORM_PASSWORD", "")
    if platform is None:
        platform = os.environ.get("ALIMAMA_PLATFORM", "")
    if not account or not password:
        raise ValueError(EMPTY)
    if not platform:
        raise ValueError(UNSUPPORTED)

    def _run(page=None, **_ignored):
        return login(account, password, platform, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
