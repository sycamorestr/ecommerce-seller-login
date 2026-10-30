"""Temu-切换店铺 and Temu-广告平台-切换店铺.

Seller switch: activity_temu_shop/switch_store.py (shop name must be non-empty text).
Ads switch: activity_temu_shop/advertisement_switch_store.py.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import OnError, SellerLoginResult, finish, open_page

SELLER_SOURCE = "activity_temu_shop/switch_store.py"
ADS_SOURCE = "activity_temu_shop/advertisement_switch_store.py"
XPATH_ADS_CURRENT = '//div[@id="top-bar"]//span[.="返回卖家中心"]/../../../div[last()]//div[not(div)]'
XPATH_SWITCH = "//*[text()='切换']"
XPATH_ADS_STORES = '//*[.="切换店铺"]/../div[2]/div/div/div//span[not(.="半托管")]'
EMPTY_STORE = "目标店铺名称不能为空或非文本"


def switch_seller(store_name: str, *, page: Optional[Page] = None):
    if not isinstance(store_name, str) or not store_name.strip():
        raise ValueError(EMPTY_STORE.format() if False else "目标店铺名称不能为空或非文本：{!r}".format(store_name))
    shots: list = []
    page, owned = open_page(page, headless=False)
    if page.locator(f"xpath={XPATH_SWITCH}").count():
        page.locator(f"xpath={XPATH_SWITCH}").first.click(timeout=5000)
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def switch_ads(store_name: str, *, page: Optional[Page] = None):
    if not store_name:
        raise ValueError("目标店铺名称不能为空或非文本：{!r}".format(store_name))
    shots: list = []
    page, owned = open_page(page, headless=False)
    current = page.locator(f"xpath={XPATH_ADS_CURRENT}")
    if current.count():
        text = (current.first.inner_text(timeout=2000) or "").strip()
        if text == store_name:
            return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
    if page.locator(f"xpath={XPATH_SWITCH}").count() == 0 and current.count():
        current.first.click(timeout=5000)
    elif page.locator(f"xpath={XPATH_SWITCH}").count() == 1:
        page.locator(f"xpath={XPATH_SWITCH}").first.click(timeout=5000)
    stores = page.locator(f"xpath={XPATH_ADS_STORES}")
    for i in range(stores.count()):
        if (stores.nth(i).inner_text(timeout=1000) or "").strip() == store_name:
            stores.nth(i).click(timeout=5000)
            break
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def temu_switch_store(
    store_name: Optional[str] = None,
    *,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    if store_name is None:
        store_name = os.environ.get("TEMU_STORE", "")

    def _run(page=None, **_ignored):
        return switch_seller(store_name or "", page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def temu_ads_switch_store(
    store_name: Optional[str] = None,
    *,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    if store_name is None:
        store_name = os.environ.get("TEMU_ADS_STORE", "")

    def _run(page=None, **_ignored):
        return switch_ads(store_name or "", page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
