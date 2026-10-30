"""Playwright port of 影刀「天猫超市登录」 activity_7bca6d/login_tmall_supermarket.py.

Supplier matching rules are copied. A visible NC slider is a human gate,
matching the source wait for 人工验证.
"""
from __future__ import annotations

import os
import re
from typing import List, Optional, Sequence
from urllib.parse import urlparse

from playwright.sync_api import Page

from seller_common import (
    NeedsHumanError,
    OnError,
    SellerLoginError,
    SellerLoginResult,
    close_result,
    fill_checked,
    finish,
    goto_with_retry,
    open_page,
    sleep,
)

LOGIN_URL = "https://web.txcs.tmall.com/login?from=https%3A%2F%2Fweb.txcs.tmall.com%2F"
LOGIN_FRAME = 'iframe#alibaba-login-box'
PROXY_MARK = "https://web.txcs.tmall.com/pages/ascm/basic_login_proxy?"
SEL_USER = "#fm-login-id"
SEL_PASSWORD = "#fm-login-password"
SEL_SUBMIT = "button.password-login"
SEL_NC = "#nc_1_n1z"
SEL_ERROR = ".login-error-msg"
SEL_SUPPLIER = "li.menu-item"
SEL_ENTER = "button.login-button"
SEL_CURRENT = "span.current-supplier-name"


def supplier_name(label: str) -> str:
    return re.split(r"\s+--\s+", label.strip(), maxsplit=1)[0]


def match_supplier(labels: Sequence[str], requested: str) -> int:
    matches = [index for index, label in enumerate(labels) if label == requested]
    if not matches:
        raise ValueError("未找到精确匹配的二级供应商，请填写完整店铺名或完整选项文本。")
    if len(matches) != 1:
        raise ValueError("完整店铺名对应多个业务身份，请填写含业务类型后缀的完整选项文本。")
    return matches[0]


def verify_supplier(actual: str, requested: str) -> None:
    if not actual or actual.strip() != supplier_name(requested):
        raise SellerLoginError("后台当前店铺与指定店铺不一致，停止后续操作。请确认二级供应商身份已绑定。")


def verify_identity(active: str, requested: str) -> None:
    suffix = re.split(r"\s+--\s+", requested, maxsplit=1)
    expected = suffix[0] + ("-" + suffix[1] if len(suffix) == 2 else "")
    if not active or re.sub(r"^\d+-", "", active.strip()) != expected:
        raise SellerLoginError("后台当前业务身份与指定的完整二级供应商名称不一致，停止后续操作。")


def _backend(url: str) -> bool:
    parsed = urlparse(url or "")
    return (
        parsed.scheme == "https"
        and parsed.hostname == "web.txcs.tmall.com"
        and parsed.path not in ("/login", "/logout", "/pages/ascm/basic_login_proxy")
    )


def login(account: str, password: str, *, shop_name: str = "", page: Optional[Page] = None):
    if not isinstance(account, str) or not account.strip():
        raise ValueError("登录账号必须填写非空文本。")
    if not isinstance(password, str) or not password.strip():
        raise ValueError("登录密码必须填写非空文本。")
    if not isinstance(shop_name, str):
        raise ValueError("店铺名须为文本；留空时默认选择第一条可见店铺。")
    shots: List[str] = []
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=1, timeout_ms=60000)
    frame = page.frame_locator(LOGIN_FRAME)
    user = frame.locator(SEL_USER).first
    user.wait_for(state="visible", timeout=60000)
    fill_checked(user, account.strip(), limit=3)
    fill_checked(frame.locator(SEL_PASSWORD).first, password, limit=3)
    frame.locator(SEL_SUBMIT).first.click(timeout=10000)
    sleep(1)
    if frame.locator(SEL_NC).count() and frame.locator(SEL_NC).first.is_visible():
        raise NeedsHumanError("天猫超市登录需要人工完成页面验证")
    if frame.locator(SEL_ERROR).count():
        text = (frame.locator(SEL_ERROR).first.inner_text(timeout=1000) or "").strip()
        if text:
            raise SellerLoginError("账号登录失败，请检查账号、密码或页面验证提示。")
    if shop_name:
        labels = []
        options = page.locator(SEL_SUPPLIER)
        for index in range(options.count()):
            labels.append((options.nth(index).inner_text(timeout=1000) or "").strip())
        if labels:
            chosen = match_supplier(labels, shop_name)
            options.nth(chosen).click(timeout=5000)
    return page, 0, shots, owned["browser"], owned["context"], owned["playwright"]


def tmall_supermarket_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    *,
    shop_name: Optional[str] = None,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("TMALL_SUPERMARKET_ACCOUNT", "")
    password = password if password is not None else os.environ.get("TMALL_SUPERMARKET_PASSWORD", "")
    if shop_name is None:
        shop_name = os.environ.get("TMALL_SUPERMARKET_SHOP", "")
    if not isinstance(account, str) or not account.strip():
        raise ValueError("登录账号必须填写非空文本。")
    if not isinstance(password, str) or not password.strip():
        raise ValueError("登录密码必须填写非空文本。")
    if not isinstance(shop_name, str):
        raise ValueError("店铺名须为文本；留空时默认选择第一条可见店铺。")

    def _run(page=None, **_ignored):
        return login(account, password, shop_name=shop_name or "", page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = tmall_supermarket_login()
    print({"ok": result.ok, "error": result.error})
    close_result(result)


if __name__ == "__main__":
    main()
