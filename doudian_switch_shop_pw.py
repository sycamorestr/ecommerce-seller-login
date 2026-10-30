"""Playwright port of 抖店店铺切换.

- process13.py (公开「抖店店铺切换」) only calls hidden process17.py.
  process17 block comments name it 抖店店铺切换（新）.
- process35.py (公开「抖店店铺切换(ID)」) only calls process36.py.
  process36 block comments name it 抖店店铺切换(ID)(新).
- process37.py is a date-filter test harness, not a shop-id switch.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from seller_common import (
    OnError,
    SellerLoginError,
    SellerLoginResult,
    finish,
    goto_with_retry,
    open_page,
    xpath_visible,
)

MULTI_SHOP_URL = "https://fxg.jinritemai.com/ffa/multiShop"
XPATH_HEADER_SHOP = '//div[contains(@class, "headerShopName")]'
XPATH_ROLE = '//div[contains(@class, "index_roleItem")]'
XPATH_SHOP_ID = '//div[@label="店铺ID"]'
NOT_FOUND = "未找到目标店铺（{name}）"
NOT_FOUND_ID = "未找到目标店铺ID（{name}）"
MISMATCH_NAME = "当前店铺与目标店铺不同，请检查店铺名"
MISMATCH_ID = "当前店铺与目标店铺不同，请检查店铺ID"
INDEX_TOO_BIG = "抖店店铺切换：您提供的索引大于店铺总数量，无法选择店铺 ~"
LEGACY_NAME_SOURCE = "activity_966451c9/process13.py"
NEW_NAME_SOURCE = "activity_966451c9/process17.py"
LEGACY_ID_SOURCE = "activity_966451c9/process35.py"
NEW_ID_SOURCE = "activity_966451c9/process36.py"
PROCESS37_NOTE = "process37.py 是售后时间选择测试，不是店铺切换(ID)(新)。"


def _ensure(page: Optional[Page]):
    page, owned = open_page(page, headless=False)
    if "fxg.jinritemai.com" not in (page.url or ""):
        goto_with_retry(page, MULTI_SHOP_URL, attempts=1, timeout_ms=60000)
    return page, owned


def switch_by_name(shop_name: str, *, page: Optional[Page] = None):
    shots: list = []
    page, owned = _ensure(page)
    if not shop_name:
        return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
    if xpath_visible(page, XPATH_HEADER_SHOP, timeout=2):
        current = (page.locator(f"xpath={XPATH_HEADER_SHOP}").first.inner_text(timeout=2000) or "").strip()
        if current == shop_name:
            return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
    page.goto(MULTI_SHOP_URL, wait_until="domcontentloaded", timeout=60000)
    roles = page.locator(f"xpath={XPATH_ROLE}")
    count = roles.count()
    if shop_name.isnumeric():
        index = int(shop_name)
        if index >= count:
            raise SellerLoginError(INDEX_TOO_BIG)
        roles.nth(index).click(timeout=10000)
    else:
        found = False
        for i in range(count):
            text = (
                roles.nth(i)
                .locator("xpath=.//div[contains(@class, 'index_introName')]")
                .first.inner_text(timeout=2000)
                or ""
            ).strip()
            if text == shop_name:
                roles.nth(i).click(timeout=10000)
                found = True
                break
        if not found:
            raise SellerLoginError(NOT_FOUND.format(name=shop_name))
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def switch_by_id(shop_id: str, *, page: Optional[Page] = None):
    shots: list = []
    page, owned = _ensure(page)
    if not shop_id:
        return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
    if xpath_visible(page, XPATH_SHOP_ID, timeout=2):
        current = page.locator(f"xpath={XPATH_SHOP_ID}").first.get_attribute("value") or ""
        if current == shop_id:
            return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]
    page.goto(MULTI_SHOP_URL, wait_until="domcontentloaded", timeout=60000)
    roles = page.locator(f"xpath={XPATH_ROLE}")
    found = False
    for i in range(roles.count()):
        blob = roles.nth(i).inner_text(timeout=2000) or ""
        if shop_id in blob:
            roles.nth(i).click(timeout=10000)
            found = True
            break
    if not found:
        raise SellerLoginError(NOT_FOUND_ID.format(name=shop_id))
    if xpath_visible(page, XPATH_SHOP_ID, timeout=8):
        current = page.locator(f"xpath={XPATH_SHOP_ID}").first.get_attribute("value") or ""
        if current and current != shop_id:
            raise SellerLoginError(MISMATCH_ID)
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def doudian_switch_shop(
    shop_name: Optional[str] = None,
    shop_id: Optional[str] = None,
    *,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    if shop_name is None:
        shop_name = os.environ.get("DOUDIAN_SHOP", "")
    if shop_id is None:
        shop_id = os.environ.get("DOUDIAN_SHOP_ID", "")
    if shop_id:
        def _run(page=None, **_ignored):
            return switch_by_id(shop_id, page=page)
    else:
        def _run(page=None, **_ignored):
            return switch_by_name(shop_name or "", page=page)
    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
