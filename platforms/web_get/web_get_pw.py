"""Playwright port of 影刀 xbot.web.get / get_active / get_all.

Attaches to an already-running Chrome or Edge with connect_over_cdp.
cef / ie / firefox / 360se / auto are not supported.
"""
from __future__ import annotations

import fnmatch
import os
from typing import List, Optional

from playwright.sync_api import Browser, Page, TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

CDP_ENV = "WEB_GET_CDP_URL"
SUPPORTED_MODES = ("chrome", "edge")
UNSUPPORTED_MODES = ("cef", "ie", "firefox", "360se", "auto")

_CONNECTIONS: dict = {}


class WebGetError(Exception):
    pass


class UnsupportedModeError(WebGetError):
    pass


class PageNotFoundError(WebGetError):
    pass


class PageLoadTimeoutError(WebGetError):
    pass


def _check_mode(mode: str) -> None:
    if mode in SUPPORTED_MODES:
        return
    if mode in UNSUPPORTED_MODES:
        raise UnsupportedModeError(
            f"mode {mode!r} 不支持。仅 chrome / edge，通过 CDP 连接已打开的浏览器。"
        )
    raise UnsupportedModeError(f"mode {mode!r} 不支持。仅 chrome / edge。")


def _cdp_url(cdp_url: Optional[str]) -> str:
    url = cdp_url if cdp_url is not None else os.environ.get(CDP_ENV, "")
    url = (url or "").strip()
    if not url:
        raise WebGetError(f"缺少 CDP 地址，请传入 cdp_url 或设置 {CDP_ENV}")
    return url


def connect(cdp_url: str) -> Browser:
    cached = _CONNECTIONS.get(cdp_url)
    if cached is not None:
        _pw, browser = cached
        if browser.is_connected():
            return browser
    playwright = sync_playwright().start()
    browser = playwright.chromium.connect_over_cdp(cdp_url)
    _CONNECTIONS[cdp_url] = (playwright, browser)
    return browser


def close_connection(cdp_url: Optional[str] = None) -> None:
    keys = [cdp_url] if cdp_url else list(_CONNECTIONS)
    for key in keys:
        cached = _CONNECTIONS.pop(key, None)
        if not cached:
            continue
        playwright, browser = cached
        try:
            browser.close()
        except Exception:
            pass
        try:
            playwright.stop()
        except Exception:
            pass


def match_text(text: Optional[str], pattern: Optional[str], *, use_wildcard: bool) -> bool:
    """Fuzzy is substring. use_wildcard uses fnmatch (* and ?), case-sensitive."""
    if pattern is None:
        return True
    haystack = text or ""
    if use_wildcard:
        return fnmatch.fnmatchcase(haystack, pattern)
    return pattern in haystack


def _opened_at(page: Page) -> float:
    try:
        return float(page.evaluate("() => performance.timeOrigin"))
    except Exception:
        return 0.0


def list_pages(browser: Browser) -> List[Page]:
    pages: List[tuple] = []
    for context in browser.contexts:
        for page in context.pages:
            if page.is_closed():
                continue
            pages.append((_opened_at(page), page))
    pages.sort(key=lambda item: item[0])
    return [page for _origin, page in pages]


def _matches(page: Page, title: Optional[str], url: Optional[str], *, use_wildcard: bool) -> bool:
    if title is not None:
        try:
            current_title = page.title()
        except Exception:
            current_title = ""
        if not match_text(current_title, title, use_wildcard=use_wildcard):
            return False
    if url is not None:
        if not match_text(page.url or "", url, use_wildcard=use_wildcard):
            return False
    return True


def _wait_loaded(page: Page, load_timeout: float, stop_if_timeout: bool) -> None:
    if load_timeout == 0:
        return
    timeout_ms = 0 if load_timeout < 0 else int(load_timeout * 1000)
    try:
        page.wait_for_load_state("load", timeout=timeout_ms)
    except PlaywrightTimeout:
        if stop_if_timeout:
            try:
                page.evaluate("() => window.stop()")
            except Exception:
                pass
        raise PageLoadTimeoutError("网页加载超时") from None


def _goto(page: Page, url: str, load_timeout: float, stop_if_timeout: bool) -> None:
    if load_timeout == 0:
        page.goto(url, wait_until="commit", timeout=30000)
        return
    timeout_ms = 0 if load_timeout < 0 else int(load_timeout * 1000)
    try:
        page.goto(url, wait_until="load", timeout=timeout_ms)
    except PlaywrightTimeout:
        if stop_if_timeout:
            try:
                page.evaluate("() => window.stop()")
            except Exception:
                pass
        raise PageLoadTimeoutError("网页加载超时") from None


def _open_fallback(browser: Browser, address: str, load_timeout: float, stop_if_timeout: bool) -> Page:
    context = browser.contexts[-1] if browser.contexts else browser.new_context()
    page = context.new_page()
    _goto(page, address, load_timeout, stop_if_timeout)
    return page


def _is_active(page: Page) -> bool:
    try:
        return bool(page.evaluate(
            "() => document.visibilityState === 'visible' && document.hasFocus()"
        ))
    except Exception:
        return False


def get(
    title: Optional[str] = None,
    url: Optional[str] = None,
    mode: str = "cef",
    *,
    load_timeout: float = 20,
    use_wildcard: bool = False,
    stop_if_timeout: bool = False,
    open_page: bool = False,
    page_url: Optional[str] = None,
    silent_running: bool = False,
    cdp_url: Optional[str] = None,
) -> Page:
    """xbot.web.get. Several matches: the page with the latest performance.timeOrigin."""
    _ = silent_running
    _check_mode(mode)
    if title is None and url is None:
        raise ValueError("需要 title 或 url")
    browser = connect(_cdp_url(cdp_url))
    matched = [page for page in list_pages(browser) if _matches(page, title, url, use_wildcard=use_wildcard)]
    if matched:
        page = matched[-1]
        _wait_loaded(page, load_timeout, stop_if_timeout)
        return page
    if open_page:
        address = page_url or url
        if not address:
            raise PageNotFoundError("未获取到网页")
        return _open_fallback(browser, address, load_timeout, stop_if_timeout)
    raise PageNotFoundError("未获取到网页")


def get_active(
    mode: str = "cef",
    *,
    load_timeout: float = 20,
    stop_if_timeout: bool = False,
    silent_running: bool = False,
    cdp_url: Optional[str] = None,
) -> Page:
    """xbot.web.get_active. Visible and focused tab; if several, the newest."""
    _ = silent_running
    _check_mode(mode)
    browser = connect(_cdp_url(cdp_url))
    pages = list_pages(browser)
    focused = [page for page in pages if _is_active(page)]
    if not focused:
        raise PageNotFoundError("未获取到网页")
    page = focused[-1]
    _wait_loaded(page, load_timeout, stop_if_timeout)
    return page


def get_all(
    mode: str = "cef",
    *,
    title: Optional[str] = None,
    url: Optional[str] = None,
    use_wildcard: bool = False,
    silent_running: bool = False,
    cdp_url: Optional[str] = None,
) -> List[Page]:
    """xbot.web.get_all. No title/url filter returns every open page, oldest first."""
    _ = silent_running
    _check_mode(mode)
    browser = connect(_cdp_url(cdp_url))
    return [page for page in list_pages(browser) if _matches(page, title, url, use_wildcard=use_wildcard)]


def visual_get(**args) -> Page:
    """xbot_visual.web.get. mode is url / title / activated."""
    kind = args.get("mode")
    web_type = args.get("web_type", "cef")
    load_timeout = args.get("load_timeout", 20)
    if args.get("wait_load_completed") is False:
        load_timeout = 0
    common = dict(
        mode=web_type,
        load_timeout=load_timeout,
        stop_if_timeout=args.get("stop_load_if_load_timeout") == "stopLoad",
        silent_running=bool(args.get("silent_running", False)),
        cdp_url=args.get("cdp_url"),
    )
    if kind == "activated":
        return get_active(**common)
    if kind == "title":
        return get(
            title=args.get("value"),
            use_wildcard=bool(args.get("use_wildcard", False)),
            open_page=bool(args.get("open_page", False)),
            page_url=args.get("url"),
            **common,
        )
    if kind == "url":
        return get(
            url=args.get("value"),
            use_wildcard=bool(args.get("use_wildcard", False)),
            open_page=bool(args.get("open_page", False)),
            page_url=args.get("url"),
            **common,
        )
    raise ValueError(f"mode {kind!r} 不是 url/title/activated")


def visual_get_all(**args) -> List[Page]:
    """xbot_visual.web.get_all. mode is all / url / title."""
    kind = args.get("mode", "all")
    web_type = args.get("web_type", "cef")
    common = dict(
        mode=web_type,
        use_wildcard=bool(args.get("use_wildcard", False)),
        silent_running=bool(args.get("silent_running", False)),
        cdp_url=args.get("cdp_url"),
    )
    if kind == "all":
        return get_all(**common)
    if kind == "url":
        return get_all(url=args.get("value"), **common)
    if kind == "title":
        return get_all(title=args.get("value"), **common)
    raise ValueError(f"mode {kind!r} 不是 all/url/title")
