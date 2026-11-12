"""影刀应用 cookie 的 7 条指令，Playwright 同步 API。

网页对象是 Playwright Page。没有 Page、且 mode 为 chrome/edge 时，经 platforms.web_get 的 CDP 连接取 cookie jar。
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

from playwright.sync_api import Page

from .helpers import SellerLoginError

DOMAIN_RE = re.compile(r"(?:://)(?:www\.)?([a-zA-Z0-9\-\.]+)(?=/)")

_LOCAL_STORAGE_JS = """() => {
    let local_storage = {};
    for (let i = 0; i < localStorage.length; i++) {
        let key = localStorage.key(i);
        local_storage[key] = localStorage.getItem(key);
    }
    if (Object.keys(local_storage).length == 0) {
        return null;
    }
    return local_storage;
}"""

_SET_LOCAL_JS = """(pair) => {
    localStorage.removeItem(pair.key);
    localStorage.setItem(pair.key, pair.value);
}"""

_APPOINT = {"appoint_cookie", "appoint", "specified"}
_ALL = {"all", "all_cookie", "remove_all"}


def extract_domain_from_url(url: str) -> Optional[str]:
    matched = DOMAIN_RE.search(url or "")
    return matched.group(1) if matched else None


def _parse_expiration(raw) -> Optional[int]:
    if isinstance(raw, (int, float)):
        return int(raw)
    text = str(raw).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = None
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        for fmt in ("%m/%d/%Y, %H:%M:%S", "%m/%d/%Y %H:%M:%S"):
            try:
                dt = datetime.strptime(str(raw).strip(), fmt)
                break
            except ValueError:
                dt = None
    if dt is None:
        return None
    if dt.tzinfo is None or dt.utcoffset() is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def normalize_cookie(cookie: dict) -> dict:
    """expirationDate（数字或字符串）→ unix expires，并写 sessionCookie。"""
    item = dict(cookie)
    expiration_date = item.get("expirationDate")
    if expiration_date in (None, "") and item.get("expires") not in (None, ""):
        expiration_date = item.get("expires")
    item["expires"] = None
    if expiration_date:
        if isinstance(expiration_date, (int, float)) and expiration_date < 0:
            item["expires"] = None
        elif isinstance(expiration_date, (int, float)):
            item["expires"] = int(expiration_date)
        else:
            item["expires"] = _parse_expiration(expiration_date)
    item["sessionCookie"] = not bool(item["expires"])
    item.pop("expirationDate", None)
    return item


def cookie_expires(cookie: dict) -> Optional[int]:
    return normalize_cookie(cookie).get("expires")


def require_page(page: Optional[Page]) -> Page:
    if page is None:
        raise SellerLoginError("Cookie 操作需要已打开的 Playwright 页面")
    return page


def _context(page: Optional[Page], mode: str = "cef", cdp_url: Optional[str] = None):
    if page is not None:
        return page.context
    from platforms.web_get.web_get_pw import _cdp_url, _check_mode, connect

    _check_mode(mode or "cef")
    browser = connect(_cdp_url(cdp_url))
    if not browser.contexts:
        raise SellerLoginError("没有已打开的浏览器上下文")
    return browser.contexts[0]


def _blank(value) -> bool:
    return value is None or value == ""


def _host_matches(cookie_domain: str, host: str) -> bool:
    domain = (cookie_domain or "").lower().lstrip(".")
    host = (host or "").lower().rstrip(".")
    if not domain or not host:
        return False
    return host == domain or host.endswith("." + domain)


def _path_matches(cookie_path: str, url_path: str) -> bool:
    cookie_path = cookie_path or "/"
    url_path = url_path or "/"
    if cookie_path == "/":
        return True
    if not url_path.startswith(cookie_path):
        return False
    if len(url_path) == len(cookie_path) or cookie_path.endswith("/"):
        return True
    return url_path[len(cookie_path)] == "/"


def _cookie_matches_url(cookie: dict, url: str) -> bool:
    parsed = urlparse(url or "")
    if not parsed.hostname:
        return False
    if not _host_matches(cookie.get("domain") or "", parsed.hostname):
        return False
    if not _path_matches(cookie.get("path") or "/", parsed.path or "/"):
        return False
    if cookie.get("secure") and parsed.scheme != "https":
        return False
    return True


def _is_session(cookie: dict) -> bool:
    if cookie.get("session") is True:
        return True
    expires = cookie.get("expires", cookie.get("expirationDate"))
    return expires in (None, "") or (isinstance(expires, (int, float)) and expires < 0)


def _partition_value(cookie: dict):
    if "partitionKey" in cookie:
        return cookie.get("partitionKey")
    return cookie.get("partition_key")


def _partition_matches(cookie: dict, partition_key: str) -> bool:
    current = _partition_value(cookie)
    if isinstance(current, dict):
        current = current.get("topLevelSite")
    return current == partition_key


def _to_shadowbot(cookie: dict) -> dict:
    expires = cookie.get("expires", -1)
    item = {
        "name": cookie.get("name", ""),
        "value": cookie.get("value", ""),
        "domain": cookie.get("domain", ""),
        "path": cookie.get("path", "/"),
        "httpOnly": bool(cookie.get("httpOnly", False)),
        "secure": bool(cookie.get("secure", False)),
        "expirationDate": None if expires in (None, "") or (isinstance(expires, (int, float)) and expires < 0) else expires,
    }
    if cookie.get("sameSite"):
        item["sameSite"] = cookie["sameSite"]
    part = _partition_value(cookie)
    if part is not None:
        item["partitionKey"] = part
    return item


def _filter_cookies(
    cookies: list,
    *,
    url: Optional[str] = None,
    name: Optional[str] = None,
    domain: Optional[str] = None,
    path: Optional[str] = None,
    secure=None,
    session=None,
    partition_key: Optional[str] = None,
) -> list:
    selected = []
    for cookie in cookies:
        if not _blank(url) and not _cookie_matches_url(cookie, url):
            continue
        if not _blank(name) and cookie.get("name") != name:
            continue
        if not _blank(domain):
            cookie_domain = (cookie.get("domain") or "").lstrip(".")
            wanted = domain.lstrip(".")
            if cookie_domain != wanted and not cookie_domain.endswith("." + wanted):
                continue
        if not _blank(path) and (cookie.get("path") or "/") != path:
            continue
        if secure is not None and bool(cookie.get("secure")) is not bool(secure):
            continue
        if session is not None and _is_session(cookie) is not bool(session):
            continue
        if not _blank(partition_key) and not _partition_matches(cookie, partition_key):
            continue
        selected.append(cookie)
    return selected


def _read_cookies(context) -> list:
    return list(context.cookies())


def get_cookies(
    url: Optional[str] = None,
    mode: str = "cef",
    *,
    page: Optional[Page] = None,
    name: Optional[str] = None,
    domain: Optional[str] = None,
    path: Optional[str] = None,
    secure=None,
    session=None,
    partition_key: Optional[str] = None,
    cdp_url: Optional[str] = None,
) -> list:
    """xbot.web.get_cookies。url 为空则不做 URL 筛选（保存 Cookie 在页面无地址时如此调用）。"""
    context = _context(page, mode, cdp_url)
    raw = _filter_cookies(
        _read_cookies(context),
        url=url,
        name=name,
        domain=domain,
        path=path,
        secure=secure,
        session=session,
        partition_key=partition_key,
    )
    return [_to_shadowbot(item) for item in raw]


def get_cookies_v2(
    mode: str = "cef",
    *,
    page: Optional[Page] = None,
    name: Optional[str] = None,
    url: Optional[str] = None,
    domain: Optional[str] = None,
    path: Optional[str] = None,
    partition_key: Optional[str] = None,
    secure=None,
    session=None,
    cdp_url: Optional[str] = None,
) -> list:
    """xbot.web.get_cookies_v2。空字符串筛选条件忽略。secure/session 为 None 时不过滤。"""
    return get_cookies(
        url,
        mode,
        page=page,
        name=name,
        domain=domain,
        path=path,
        secure=secure,
        session=session,
        partition_key=partition_key,
        cdp_url=cdp_url,
    )


def get_cookie(
    url: Optional[str] = None,
    mode: str = "cef",
    *,
    page: Optional[Page] = None,
    name: Optional[str] = None,
    cdp_url: Optional[str] = None,
) -> dict:
    """xbot.web.get_cookie。没有命中时返回空 dict。"""
    found = get_cookies(url, mode, page=page, name=name, cdp_url=cdp_url)
    return found[0] if found else {}


def set_cookie(
    url: Optional[str] = None,
    mode: str = "cef",
    *,
    page: Optional[Page] = None,
    name: Optional[str] = None,
    value: Optional[str] = None,
    sessionCookie: bool = True,
    expires: float = 100,
    domain: Optional[str] = None,
    path: Optional[str] = None,
    httpOnly: bool = False,
    secure: bool = False,
    sameSite: Optional[str] = None,
    cdp_url: Optional[str] = None,
) -> None:
    """xbot.web.set_cookie。sessionCookie 为 True 时不写过期时间。False 时 expires 是从现在起的秒数，默认 100。"""
    if _blank(url):
        raise SellerLoginError("设置 Cookie 需要 url")
    context = _context(page, mode, cdp_url)
    item = {
        "name": "" if name is None else str(name),
        "value": "" if value is None else str(value),
        "url": url,
        "httpOnly": bool(httpOnly),
        "secure": bool(secure),
    }
    if not _blank(domain):
        item["domain"] = domain
    if not _blank(path):
        item["path"] = path
    if sameSite:
        item["sameSite"] = sameSite
    if not sessionCookie:
        item["expires"] = time.time() + float(100 if expires is None else expires)
    context.add_cookies([item])


def remove_cookie(
    url: Optional[str] = None,
    name: Optional[str] = None,
    mode: str = "cef",
    *,
    page: Optional[Page] = None,
    remove_type: str = "appoint_cookie",
    cdp_url: Optional[str] = None,
) -> None:
    """移除指定名称（appoint_cookie）或全部（all / all_cookie）。url 为空时按 context 里全部 cookie。"""
    context = _context(page, mode, cdp_url)
    current = _read_cookies(context)
    if remove_type in _ALL:
        if _blank(url):
            context.clear_cookies()
            return
        keep = [item for item in current if not _cookie_matches_url(item, url)]
    elif remove_type in _APPOINT:
        if name == "":
            return
        def _drop(item: dict) -> bool:
            if item.get("name") != name:
                return False
            if _blank(url):
                return True
            return _cookie_matches_url(item, url)
        keep = [item for item in current if not _drop(item)]
    else:
        raise SellerLoginError(f"remove_type {remove_type!r} 不是 appoint_cookie 或 all")
    context.clear_cookies()
    restored = []
    for item in keep:
        restored.append({key: item[key] for key in item if key in {
            "name", "value", "domain", "path", "expires", "httpOnly", "secure", "sameSite", "url",
        } and item[key] not in (None, "")})
    if restored:
        context.add_cookies(restored)


def visual_get_cookies(**args) -> list:
    """url_type=auto 用网页对象地址；manual 用 url。filter_secure/filter_session 为假则不过滤。"""
    page = args.get("browser") or args.get("page")
    url_type = args.get("url_type", "auto")
    url = args.get("url") if url_type == "manual" else None
    secure = args.get("secure") if args.get("filter_secure") else None
    session = args.get("session") if args.get("filter_session") else None
    return get_cookies(
        url,
        args.get("web_type", "cef"),
        page=page,
        name=args.get("name"),
        domain=args.get("domain"),
        path=args.get("path"),
        secure=secure,
        session=session,
        partition_key=args.get("partition_key"),
        cdp_url=args.get("cdp_url"),
    )


def visual_get_cookies_v2(**args) -> list:
    page = args.get("browser") or args.get("page")
    secure = args.get("secure") if args.get("filter_secure") else None
    session = args.get("session") if args.get("filter_session") else None
    return get_cookies_v2(
        args.get("web_type", "cef"),
        page=page,
        name=args.get("name"),
        url=args.get("url"),
        domain=args.get("domain"),
        path=args.get("path"),
        partition_key=args.get("partition_key"),
        secure=secure,
        session=session,
        cdp_url=args.get("cdp_url"),
    )


def visual_get_cookie(**args) -> dict:
    page = args.get("browser") or args.get("page")
    url_type = args.get("url_type", "auto")
    if url_type == "auto":
        url = page.url if page is not None else None
    else:
        url = args.get("url")
    return get_cookie(
        url,
        args.get("web_type", "cef"),
        page=page,
        name=args.get("name"),
        cdp_url=args.get("cdp_url"),
    )


def visual_set_cookie(**args) -> None:
    page = args.get("browser") or args.get("page")
    url_type = args.get("url_type", "auto")
    url = page.url if url_type == "auto" and page is not None else args.get("url")
    return set_cookie(
        url,
        args.get("web_type", "cef"),
        page=page,
        name=args.get("name"),
        value=args.get("value"),
        sessionCookie=args.get("sessionCookie", True),
        expires=args.get("expires", 100),
        domain=args.get("domain"),
        path=args.get("path"),
        httpOnly=bool(args.get("httpOnly", False)),
        secure=bool(args.get("secure", False)),
        sameSite=args.get("sameSite"),
        cdp_url=args.get("cdp_url"),
    )


def visual_remove_cookie(**args) -> None:
    page = args.get("browser") or args.get("page")
    url_type = args.get("url_type", "auto")
    url = args.get("url") if url_type == "manual" else None
    return remove_cookie(
        url,
        args.get("name"),
        args.get("web_type", "cef"),
        page=page,
        remove_type=args.get("remove_type", "appoint_cookie"),
        cdp_url=args.get("cdp_url"),
    )


def save_login_info(web_page: Page, save_path: str = "", url=None, partition_key=None) -> str:
    """cookie_login._core.save_login_info。传入的 url 会被页面地址覆盖，与源码一致。"""
    _ = url
    url = web_page.url
    if not url:
        cookies = visual_get_cookies(
            url_type="auto",
            browser=web_page,
            web_type=None,
            url=None,
            name=None,
            domain=None,
            path=None,
            filter_secure=False,
            secure=False,
            filter_session=False,
            session=False,
        )
    else:
        cookies = visual_get_cookies(
            url_type="manual",
            browser=web_page,
            web_type="chrome",
            url=url,
            name=None,
            domain=None,
            path=None,
            filter_secure=False,
            secure=False,
            filter_session=False,
            session=False,
        )
    if partition_key:
        try:
            if not url:
                extra = visual_get_cookies(
                    url_type="auto", browser=web_page, url=None, partition_key=partition_key,
                    filter_secure=False, filter_session=False,
                )
            else:
                extra = visual_get_cookies(
                    url_type="manual", browser=web_page, web_type="chrome", url=url,
                    partition_key=partition_key, filter_secure=False, filter_session=False,
                )
            cookies.extend(extra)
        except TypeError:
            pass
    normalized = [normalize_cookie(cookie) for cookie in cookies]
    local_storage = web_page.evaluate(_LOCAL_STORAGE_JS) or {}
    text = json.dumps(
        {"url": url, "cookies": normalized, "local_storage": local_storage},
        ensure_ascii=False,
        indent=4,
    )
    if save_path:
        with open(save_path, "w", encoding="utf-8") as handle:
            handle.write(text)
    return text


def login(web_page: Page, cookie_file_path: str, *, add_local_storage: bool = False) -> None:
    with open(cookie_file_path, "r", encoding="utf-8") as handle:
        login_info = json.load(handle)
    url = login_info.get("url", "")
    cookies = login_info.get("cookies", [])
    local_storage = login_info.get("local_storage", {}) or {}
    origin = web_page.evaluate("() => window.origin")
    if origin not in url:
        web_page.goto(url, wait_until="load", timeout=20000)
    logout(web_page)
    allowed = {"name", "value", "domain", "path", "expires", "sessionCookie", "httpOnly", "secure", "sameSite"}
    for cookie in cookies:
        if cookie.get("name", "") == "":
            continue
        try:
            fields = {key: cookie[key] for key in cookie if key in allowed}
            set_cookie(url or web_page.url, page=web_page, **fields)
        except Exception:
            pass
    if add_local_storage:
        for key, value in local_storage.items():
            try:
                stored = value if isinstance(value, str) else ("" if value is None else str(value))
                web_page.evaluate(_SET_LOCAL_JS, {"key": str(key), "value": stored})
            except Exception:
                pass
    try:
        web_page.goto(url, wait_until="load", timeout=20000)
    except Exception:
        pass


def logout(web_page: Page, del_local_storage: bool = False) -> None:
    cookies = visual_get_cookies(
        url_type="auto",
        browser=web_page,
        web_type=None,
        url=None,
        name=None,
        domain=None,
        path=None,
        filter_secure=False,
        secure=False,
        filter_session=False,
        session=False,
    )
    for cookie in cookies:
        if cookie.get("name", "") == "":
            continue
        remove_cookie(web_page.url, cookie["name"], page=web_page, remove_type="appoint_cookie")
    if del_local_storage:
        web_page.evaluate("() => localStorage.clear()")


def save_cookies(page: Optional[Page], save_path: str = "", partition_key: str = "", url: str = "") -> str:
    """指令「保存Cookie」。partition_key 非空时再按分区取一次并追加。"""
    return save_login_info(require_page(page), save_path, url=url, partition_key=partition_key or None)


def load_cookies(page: Optional[Page], cookie_file_path: str, *, add_local_storage: bool = False) -> None:
    """指令「Cookie登录」。"""
    if not cookie_file_path:
        raise SellerLoginError("Cookie文件路径为空")
    login(require_page(page), cookie_file_path, add_local_storage=add_local_storage)


def logout_cookies(page: Optional[Page], *, del_local_storage: bool = False) -> None:
    """指令「Cookie退出登录」。"""
    logout(require_page(page), del_local_storage=del_local_storage)
