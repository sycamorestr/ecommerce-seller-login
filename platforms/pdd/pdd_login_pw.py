"""Playwright port of 影刀「拼多多登录」 activity_7bca6d/process21.py.

URL is https://mms.pinduoduo.com/login/. Captchas are std_slider_captcha
(type 22222) and cs_temu_captcha (type "9999"), in that order, both before
and after the password submit. A URL that still contains "login" is treated
as the source's phone-verification failure.
"""
from __future__ import annotations

import base64
import os
from typing import List, Optional, Tuple

from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from . import captcha
from .helpers import (
    CredentialsRejected,
    NeedsHumanError,
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
    xpath_visible,
)

LOGIN_URL = "https://mms.pinduoduo.com/login/"
EMPTY_CREDENTIALS = "拼多多账号、密码均不能为空"
PHONE_GATE = "当前拼多多账号未成功登录，可能原因是需要手机验证。"

SEL_ACCOUNT_TAB = 'div.tab-operate div.Common_item__3diIn:text-is("账号登录")'
SEL_USERNAME = "#usernameId"
SEL_PASSWORD = "#passwordId"
SEL_LOGIN = 'div.password-section button[data-testid="beast-core-button"]'
SEL_SLIDER_BG = "#slide-captcha-dialog img.slider-img-bg"
SEL_DRAG = "#slide-button"
SEL_SPACE_BG = "img#captchaClickImg"
SEL_SPACE_TEXT = "span.picture-text__default"
SEL_FAIL = "div.info-danger-container"
XPATH_TAB_FALLBACK = '//div[@class="tab-operate"]/div/div[2]'
XPATH_REFRESH = '//div[@class="captcha-refresh"]/img'


def _png_b64(locator) -> str:
    return base64.b64encode(locator.screenshot(type="png")).decode("ascii")


def _solve_slider(page: Page, token: str, calls: List[int]) -> None:
    captcha.require_yunma_token(token)
    image = _png_b64(page.locator(SEL_SLIDER_BG).first)
    response = captcha.yunma_post(captcha.std_slider_payload(image, token))
    calls[0] += 1
    distance = captcha.std_slider_distance(response.get("data") or {}, offset=0, speed=1)
    box = page.locator(SEL_DRAG).first.bounding_box()
    if not box:
        return
    x1 = box["x"] + box["width"] / 2
    y1 = box["y"] + box["height"] / 2
    mouse_drag(page, x1, y1, x1 + distance, y1)


def _solve_space(page: Page, token: str, calls: List[int]) -> None:
    captcha.require_yunma_token(token)
    extra = ""
    if visible(page, SEL_SPACE_TEXT, timeout=1):
        try:
            extra = (page.locator(SEL_SPACE_TEXT).first.inner_text(timeout=1000) or "").strip()
        except Exception:
            extra = ""
    image = _png_b64(page.locator(SEL_SPACE_BG).first)
    response = captcha.yunma_post(captcha.cs_temu_payload(image, token, extra))
    calls[0] += 1
    positions = captcha.cs_temu_positions(response)
    box = page.locator(SEL_SPACE_BG).first.bounding_box()
    if not box:
        return
    for x, y in captcha.click_points_from_origin(box["x"], box["y"], positions):
        page.mouse.click(x, y)
        sleep(0.2)


def _captcha_rounds(page: Page, token: str, retries: int, calls: List[int]) -> None:
    for _ in range(int(retries)):
        if not visible(page, SEL_SLIDER_BG, timeout=1.2):
            break
        try:
            _solve_slider(page, token, calls)
        except Exception as exc:
            print(f"[pdd] slider ignored: {exc}")
        sleep(2)
    if visible(page, SEL_SLIDER_BG, timeout=1):
        raise SellerLoginError("拼多多登录失败")

    for _ in range(int(retries)):
        if not visible(page, SEL_SPACE_BG, timeout=1.2):
            break
        _solve_space(page, token, calls)
        sleep(2)
    # process21 re-checks the slider background after the space-captcha loop.
    if visible(page, SEL_SLIDER_BG, timeout=1):
        raise SellerLoginError("拼多多登录失败")


def _click_account_tab(page: Page) -> None:
    if visible(page, SEL_ACCOUNT_TAB, timeout=2):
        page.locator(SEL_ACCOUNT_TAB).first.click(timeout=5000)
        return
    if xpath_visible(page, XPATH_TAB_FALLBACK, timeout=2):
        page.locator(f"xpath={XPATH_TAB_FALLBACK}").first.click(timeout=5000)


def login(
    account: str,
    password: str,
    token: str,
    retry_count: int,
    page: Optional[Page] = None,
) -> Tuple[Page, int, List[str], Optional[Browser], Optional[BrowserContext], Optional[Playwright]]:
    if not account.strip() or not password.strip():
        raise ValueError(EMPTY_CREDENTIALS)
    if not retry_count:
        retry_count = 5
    calls = [0]
    shots: List[str] = []
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=3, timeout_ms=60000)
    sleep(2)

    try:
        _captcha_rounds(page, token, retry_count, calls)
    except SellerLoginError:
        raise
    except Exception as exc:
        print(f"[pdd] pre-login captcha ignored: {exc}")

    if xpath_visible(page, XPATH_REFRESH, timeout=1):
        try:
            page.locator(f"xpath={XPATH_REFRESH}").first.click(timeout=3000)
        except Exception:
            pass

    if not visible(page, SEL_USERNAME, timeout=2):
        _click_account_tab(page)
    fill_checked(page.locator(SEL_USERNAME).first, account, limit=10)
    fill_checked(page.locator(SEL_PASSWORD).first, password.strip(), limit=3)
    sleep(2)
    fill_checked(page.locator(SEL_PASSWORD).first, password.strip(), limit=3)
    if visible(page, SEL_ACCOUNT_TAB, timeout=1):
        page.locator(SEL_ACCOUNT_TAB).first.click(timeout=5000)
    if visible(page, SEL_LOGIN, timeout=3):
        page.locator(SEL_LOGIN).first.click(timeout=10000)
        sleep(3)

    try:
        _captcha_rounds(page, token, retry_count, calls)
    except SellerLoginError:
        raise
    except Exception as exc:
        print(f"[pdd] post-login captcha ignored: {exc}")

    if visible(page, SEL_FAIL, timeout=1.5):
        try:
            reason = (page.locator(SEL_FAIL).first.inner_text(timeout=1000) or "").strip()
        except Exception:
            reason = ""
        if reason:
            raise CredentialsRejected(reason)

    url = page.url or ""
    if "login" in url:
        raise NeedsHumanError(PHONE_GATE)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def pdd_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    retries: int = 5,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("PDD_ACCOUNT", "")
    password = password if password is not None else os.environ.get("PDD_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if not (account or "").strip() or not (password or "").strip():
        raise ValueError(EMPTY_CREDENTIALS)

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, retries, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = pdd_login(retries=int(os.environ.get("PDD_RETRIES", "5")))
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
