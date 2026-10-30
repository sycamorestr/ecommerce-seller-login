"""Shared Playwright browser helpers for seller-platform login ports.

The Taobao/千牛 module keeps its own proxy. These ports do not add that proxy
unless ``SELLER_HTTP_PROXY`` is set.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional, Tuple

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

_LAST_OWNED: dict = {}


class OnError(Enum):
    TERMINATE = "terminate"
    IGNORE = "ignore"


class SellerLoginError(Exception):
    pass


class NeedsHumanError(SellerLoginError):
    """SMS, face, QR, or another gate that must be finished by a person."""


class CredentialsRejected(SellerLoginError):
    pass


class DesktopOnlyLogin(SellerLoginError):
    """The ShadowBot block drives a desktop client and has no web login URL."""


@dataclass
class SellerLoginResult:
    ok: bool
    web_page: Optional[Page] = None
    error: Optional[str] = None
    yunma_calls: int = 0
    shots: List[str] = field(default_factory=list)
    _browser: Optional[Browser] = field(default=None, repr=False)
    _context: Optional[BrowserContext] = field(default=None, repr=False)
    _playwright: Optional[Playwright] = field(default=None, repr=False)


def sleep(seconds: float) -> None:
    time.sleep(seconds)


def create_browser(
    playwright: Playwright,
    headless: bool = False,
) -> Tuple[Browser, BrowserContext, Page]:
    launch_kwargs: dict = {
        "headless": headless,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ],
    }
    proxy = os.environ.get("SELLER_HTTP_PROXY", "").strip()
    if proxy:
        launch_kwargs["proxy"] = {"server": proxy}
    browser = playwright.chromium.launch(**launch_kwargs)
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        ignore_https_errors=True,
    )
    context.add_init_script(
        "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
    )
    page = context.new_page()
    return browser, context, page


def open_page(page: Optional[Page], *, headless: bool = False) -> Tuple[Page, dict]:
    owned: dict = {"browser": None, "context": None, "playwright": None, "page": page}
    global _LAST_OWNED
    if page is None:
        pw = sync_playwright().start()
        browser, context, page = create_browser(pw, headless=headless)
        owned["browser"] = browser
        owned["context"] = context
        owned["playwright"] = pw
        owned["page"] = page
    _LAST_OWNED = owned
    setattr(page, "_seller_owned", owned)
    return page, owned


def goto_with_retry(page: Page, url: str, *, attempts: int = 3, timeout_ms: int = 60000) -> None:
    last: Optional[BaseException] = None
    for i in range(attempts):
        try:
            if i == 0:
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            else:
                page.reload(wait_until="domcontentloaded", timeout=timeout_ms)
            return
        except Exception as exc:
            last = exc
            sleep(1)
    if last:
        raise last


def visible(page: Page, selector: str, timeout: float = 1.5) -> bool:
    try:
        page.locator(selector).first.wait_for(state="visible", timeout=timeout * 1000)
        return True
    except Exception:
        return False


def xpath_visible(page: Page, xpath: str, timeout: float = 1.5) -> bool:
    return visible(page, f"xpath={xpath}", timeout=timeout)


def input_value(locator) -> str:
    try:
        value = locator.input_value(timeout=1000)
        if value is not None:
            return value.strip()
    except Exception:
        pass
    try:
        return (locator.inner_text(timeout=1000) or "").strip()
    except Exception:
        return ""


def fill_checked(locator, text: str, *, limit: int = 3) -> None:
    """Fill and verify. ``limit`` is the number of extra retries after the first write."""
    locator.click(timeout=10000)
    sleep(0.2)
    locator.fill("")
    locator.fill(text)
    got = input_value(locator)
    tries = 0
    while got != text:
        if tries >= limit:
            raise SellerLoginError("输入失败，请重试指令")
        locator.evaluate(
            """(el, value) => {
                el.focus();
                el.value = value;
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
            }""",
            text,
        )
        got = input_value(locator)
        tries += 1


def mouse_drag(page: Page, x1: float, y1: float, x2: float, y2: float) -> None:
    """Ease-out drag in top-viewport CSS pixels (same shape as the 千牛 port)."""
    import random

    page.mouse.move(x1, y1)
    sleep(0.15)
    page.mouse.down()
    sleep(0.12)
    steps = 32
    for i in range(1, steps + 1):
        t = i / steps
        e = 1 - (1 - t) ** 3
        x = x1 + (x2 - x1) * e + random.uniform(-0.4, 0.4)
        y = y1 + (y2 - y1) * e + random.uniform(-0.3, 0.3)
        page.mouse.move(x, y)
        sleep(0.012)
    page.mouse.move(x2, y2)
    page.mouse.up()


def page_text(page: Page) -> str:
    try:
        return page.locator("body").inner_text(timeout=2000) or ""
    except Exception:
        return ""


HUMAN_MARKERS = (
    "你正在使用手机短信验证身份",
    "手机短信验证",
    "短信验证",
    "人脸验证",
    "手机验证",
)


def detect_human_text(blob: str) -> Optional[str]:
    for marker in HUMAN_MARKERS:
        if marker in blob:
            return marker
    return None


def recover_owned(page: Optional[Page]) -> dict:
    bag = getattr(page, "_seller_owned", None) if page is not None else None
    if not bag:
        bag = _LAST_OWNED or {}
    return bag


def finish(
    runner: Callable[..., Tuple],
    *,
    on_error: OnError,
    print_error_log: bool,
    **kwargs: Any,
) -> SellerLoginResult:
    page = kwargs.get("page")
    calls = 0
    shots: List[str] = []
    browser = context = pw = None
    try:
        page, calls, shots, browser, context, pw = runner(**kwargs)
        return SellerLoginResult(
            ok=True,
            web_page=page,
            yunma_calls=calls,
            shots=shots,
            _browser=browser,
            _context=context,
            _playwright=pw,
        )
    except NeedsHumanError as exc:
        if print_error_log:
            print(f"[NeedsHuman] {exc}")
        bag = recover_owned(page)
        return SellerLoginResult(
            ok=False,
            web_page=page or bag.get("page"),
            error=str(exc),
            yunma_calls=calls,
            shots=shots,
            _browser=bag.get("browser"),
            _context=bag.get("context"),
            _playwright=bag.get("playwright"),
        )
    except Exception as exc:
        if print_error_log:
            print(f"[seller login error] {exc}")
        if on_error == OnError.TERMINATE:
            if isinstance(exc, SellerLoginError):
                raise
            raise SellerLoginError(str(exc)) from exc
        bag = recover_owned(page)
        return SellerLoginResult(
            ok=False,
            web_page=page or bag.get("page"),
            error=str(exc),
            yunma_calls=calls,
            shots=shots,
            _browser=bag.get("browser"),
            _context=bag.get("context"),
            _playwright=bag.get("playwright"),
        )


def close_result(result: SellerLoginResult) -> None:
    try:
        if result._context:
            result._context.close()
    except Exception:
        pass
    try:
        if result._browser:
            result._browser.close()
    except Exception:
        pass
    try:
        if result._playwright:
            result._playwright.stop()
    except Exception:
        pass

from . import captcha
from typing import Dict

@dataclass(frozen=True)
class BankSpec:
    slug: str
    title: str
    source: str
    urls: Dict[str, str]
    env_prefix: str
    default_load_type: str = "default"
    captcha_types: Tuple[str, ...] = ()
    username_css: str = ""
    password_css: str = ""
    login_css: str = ""
    captcha_image_css: str = ""
    captcha_input_css: str = ""
    ukey_css: str = ""
    ukey_message: str = "当前浏览器可能未安装签名控件"
    input_fail: str = "输入失败，请手动登录"
    hidden: bool = False


def resolve_url(spec: BankSpec, load_type: Optional[str]) -> str:
    key = load_type or spec.default_load_type
    if key not in spec.urls:
        known = ", ".join(spec.urls)
        raise ValueError(f"{spec.title} 不支持登录类型 {key!r}。源码只有: {known}")
    url = spec.urls[key]
    if not url:
        raise ValueError(f"{spec.title} 的 {key} 在源码里没有登录地址")
    return url


def _creds(spec: BankSpec, account: Optional[str], password: Optional[str]) -> Tuple[str, str]:
    prefix = spec.env_prefix
    account = account if account is not None else os.environ.get(f"{prefix}_ACCOUNT", "")
    password = password if password is not None else os.environ.get(f"{prefix}_PASSWORD", "")
    if not account or not password:
        raise ValueError(f"缺少{spec.title}账号或密码")
    return account, password


def bank_login(
    spec: BankSpec,
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    load_type: Optional[str] = None,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account, password = _creds(spec, account, password)
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    url = resolve_url(spec, load_type)
    captcha_type = spec.captcha_types[0] if spec.captcha_types else ""

    def _run(page=None, **_ignored):
        shots = []
        calls = [0]
        page, owned = open_page(page, headless=False)
        goto_with_retry(page, url, attempts=1, timeout_ms=40000)
        try:
            page.reload(wait_until="domcontentloaded", timeout=40000)
        except Exception:
            pass
        sleep(1)
        if spec.ukey_css and visible(page, spec.ukey_css, timeout=1):
            raise NeedsHumanError(spec.ukey_message)
        if spec.username_css and visible(page, spec.username_css, timeout=8):
            user = page.locator(spec.username_css).first
            user.click(timeout=5000)
            for index in range(1, 4):
                user.fill(account)
                got = ""
                try:
                    got = (user.input_value(timeout=1000) or "").strip()
                except Exception:
                    got = ""
                if got == account:
                    break
                if index == 3:
                    raise CredentialsRejected(spec.input_fail)
        if spec.password_css and visible(page, spec.password_css, timeout=3):
            page.locator(spec.password_css).first.fill(password)
        if captcha_type in {"10103", "10110"} and spec.captcha_image_css and visible(page, spec.captcha_image_css, timeout=1):
            if not yunma_token:
                raise NeedsHumanError("数英验证码")
            image = __import__("base64").b64encode(
                page.locator(spec.captcha_image_css).first.screenshot(type="png")
            ).decode("ascii")
            payload = captcha.alphanum_payload(
                image,
                yunma_token,
                captcha_type,
                case_sensitive=(captcha_type == "10103"),
            )
            response = captcha.yunma_post(payload)
            calls[0] += 1
            code = ((response.get("data") or {}).get("data") or "")
            if spec.captcha_input_css and code:
                page.locator(spec.captcha_input_css).first.fill(str(code))
        elif captcha_type == "22222" and spec.captcha_image_css and visible(page, spec.captcha_image_css, timeout=1):
            captcha.require_yunma_token(yunma_token)
        if spec.login_css and visible(page, spec.login_css, timeout=3):
            page.locator(spec.login_css).first.click(timeout=10000)
        return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)
