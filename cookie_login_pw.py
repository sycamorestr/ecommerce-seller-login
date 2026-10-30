"""Playwright port of cookie_login (保存Cookie / Cookie登录 / Cookie退出登录).

``_core.py`` stores the page URL, cookies (``expirationDate`` → unix ``expires``),
and localStorage. Login clears existing cookies, writes the saved ones, then
navigates back to the saved URL.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Optional

from playwright.sync_api import Page

from seller_common import SellerLoginError

DOMAIN_RE = re.compile(r"(?:://)(?:www\.)?([a-zA-Z0-9\-\.]+)(?=/)")

_LOCAL_STORAGE_JS = """() => {
    const local_storage = {};
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        local_storage[key] = localStorage.getItem(key);
    }
    return Object.keys(local_storage).length ? local_storage : null;
}"""


def extract_domain_from_url(url: str) -> Optional[str]:
    matched = DOMAIN_RE.search(url or "")
    return matched.group(1) if matched else None


def cookie_expires(cookie: dict) -> Optional[int]:
    """ShadowBot save_login_info: parse expirationDate, else None."""
    if cookie.get("expires") not in (None, ""):
        try:
            return int(cookie["expires"])
        except (TypeError, ValueError):
            pass
    raw = cookie.get("expirationDate")
    if not raw:
        return None
    text = str(raw).replace("/", "-")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return int(dt.timestamp())


def normalize_cookie(cookie: dict) -> dict:
    item = dict(cookie)
    expires = cookie_expires(item)
    item["expires"] = expires
    item["sessionCookie"] = not bool(expires)
    item.pop("expirationDate", None)
    return item


def save_login_info(page: Page, save_path: str = "") -> str:
    url = page.url
    cookies = [normalize_cookie(item) for item in page.context.cookies()]
    local_storage = page.evaluate(_LOCAL_STORAGE_JS) or {}
    payload = {"url": url, "cookies": cookies, "local_storage": local_storage}
    text = json.dumps(payload, ensure_ascii=False, indent=4)
    if save_path:
        with open(save_path, "w", encoding="utf-8") as handle:
            handle.write(text)
    return text


def logout(page: Page, *, del_local_storage: bool = False) -> None:
    cookies = page.context.cookies()
    page.context.clear_cookies()
    # Mirror remove_cookie(name=...) by clearing the context jar. Empty names
    # were skipped in the source; clear_cookies drops every name including those.
    _ = [item for item in cookies if item.get("name")]
    if del_local_storage:
        page.evaluate("() => localStorage.clear()")


def login(page: Page, cookie_file_path: str, *, add_local_storage: bool = False) -> None:
    with open(cookie_file_path, "r", encoding="utf-8") as handle:
        login_info = json.load(handle)
    url = login_info.get("url") or ""
    cookies = login_info.get("cookies") or []
    local_storage = login_info.get("local_storage") or {}
    origin = page.evaluate("() => window.origin")
    if origin not in url:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
    logout(page)
    playwright_cookies = []
    for cookie in cookies:
        if not cookie.get("name"):
            continue
        item = {key: cookie[key] for key in cookie if key in {
            "name", "value", "domain", "path", "expires", "httpOnly", "secure", "sameSite", "url",
        }}
        if "expires" in item and item["expires"] in (None, ""):
            item.pop("expires")
        if "url" not in item and "domain" not in item and url:
            item["url"] = url
        playwright_cookies.append(item)
    if playwright_cookies:
        page.context.add_cookies(playwright_cookies)
    if add_local_storage:
        for key, value in local_storage.items():
            page.evaluate(
                "(pair) => { localStorage.removeItem(pair.key); localStorage.setItem(pair.key, pair.value); }",
                {"key": str(key), "value": "" if value is None else str(value)},
            )
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
    except Exception:
        pass


def require_page(page: Optional[Page]) -> Page:
    if page is None:
        raise SellerLoginError("Cookie 操作需要已打开的 Playwright 页面")
    return page


def save_cookies(page: Optional[Page], save_path: str = "", partition_key: str = "") -> str:
    """process1. ``partition_key`` is accepted and unused: Playwright has no CEF partition."""
    _ = partition_key
    return save_login_info(require_page(page), save_path)


def load_cookies(page: Optional[Page], cookie_file_path: str, *, add_local_storage: bool = False) -> None:
    """process2."""
    if not cookie_file_path:
        raise SellerLoginError("Cookie文件路径为空")
    login(require_page(page), cookie_file_path, add_local_storage=add_local_storage)


def logout_cookies(page: Optional[Page], *, del_local_storage: bool = False) -> None:
    """process3."""
    logout(require_page(page), del_local_storage=del_local_storage)
