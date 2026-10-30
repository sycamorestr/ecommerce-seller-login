"""Playwright port of 影刀「京东登录-京准通」 process40.py plus process41.

京东数坊 is present in the source map with an empty URL and is not navigated.
"""
from __future__ import annotations

import os
from typing import List, Optional

from playwright.sync_api import Page

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

LOGIN_URL = "https://jzt.jd.com/gw/index"
HOME_B = "https://b.jd.com/"
XPATH_LAUNCH = "//button[contains(string(),'立即投放')]"
XPATH_LOGOUT = '//a[contains(text(),"退出登录")]'
XPATH_OPEN_LOGIN = '//*[text()=" 登录 "]'
SEL_FORM = "div.login-form"
SEL_ACCOUNT = 'input[placeholder="账号名/手机号/邮箱"], input#loginname'
SEL_PASSWORD = "input#nloginpwd, input[type='password']"
SEL_SUBMIT = "#loginsubmit, button.login-btn"
SEL_BG = "div.JDJRV-bigimg img, img.JDJRV-bigimg"
SEL_DRAG = "div.JDJRV-slide-btn"
SEL_MISMATCH = "div.msg-error"
XPATH_SMS = '//*[text()="使用 手机短信验证码"]'
SMS_MESSAGE = "需要进行短信验证码，请手动通过！"
FAIL = "登录失败，请联系运维人员进行维护。"

# process41.url_map — 京东数坊 is intentionally empty in the source.
PLATFORM_URLS = {
    "京挑客": "https://jzt.jd.com/jtk/#/index",
    "京准通": "https://jzt.jd.com/home/#/index",
    "京准通-账户中心": "https://jzt.jd.com/account/#/financial",
    "商智-品牌版": "https://ppzh.jd.com/brand/homePage/index.html",
    "商智-商家版": "https://sz.jd.com",
    "京东快车": "https://jzt.jd.com/jdkc/survey.html#/survey",
    "京东联盟": "https://union.jd.com",
    "推荐广告": "https://jzt.jd.com/touch_point/index.html#/survey",
    "互动广告": "https://jzt.jd.com/jdzw/#/index",
    "京东数坊": "",
    "站外广告": "https://jyt.jd.com/jyt/#/accountHome",
    "站外广告-账户中心": "https://jzt.jd.com/zt/#/index",
    "智能投放": "https://jzt.jd.com/jst/#/index",
}


def platform_url(name: str) -> str:
    return PLATFORM_URLS.get(name, "")


def _slider(page: Page, token: str, calls: List[int]) -> None:
    captcha.require_yunma_token(token)
    background = page.locator(SEL_BG).first
    drag = page.locator(SEL_DRAG).first
    image = __import__("base64").b64encode(background.screenshot(type="png")).decode("ascii")
    response = captcha.yunma_post(captcha.std_slider_payload(image, token))
    calls[0] += 1
    distance = captcha.std_slider_distance(response.get("data") or {}, offset=0, speed=1)
    box = drag.bounding_box()
    if not box:
        return
    x1 = box["x"] + box["width"] / 2
    y1 = box["y"] + box["height"] / 2
    mouse_drag(page, x1, y1, x1 + distance, y1)


def login(
    account: str,
    password: str,
    token: str,
    *,
    platform: str = "",
    relogin: bool = True,
    page: Optional[Page] = None,
):
    shots: List[str] = []
    calls = [0]
    page, owned = open_page(page, headless=False)
    goto_with_retry(page, LOGIN_URL, attempts=4, timeout_ms=120000)
    sleep(3)
    logged_in = xpath_visible(page, XPATH_LAUNCH, timeout=5)
    if logged_in and relogin:
        for _ in range(5):
            if not xpath_visible(page, XPATH_LOGOUT, timeout=1):
                break
            try:
                page.locator(f"xpath={XPATH_LOGOUT}").first.click(timeout=5000)
                sleep(1)
            except Exception:
                pass
    elif logged_in and not relogin:
        return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]
    for _ in range(10):
        if visible(page, SEL_FORM, timeout=1) or visible(page, SEL_ACCOUNT, timeout=0.5):
            break
        if xpath_visible(page, XPATH_OPEN_LOGIN, timeout=1):
            page.locator(f"xpath={XPATH_OPEN_LOGIN}").first.click(timeout=5000)
            sleep(3)
    fill_checked(page.locator(SEL_ACCOUNT).first, account, limit=3)
    fill_checked(page.locator(SEL_PASSWORD).first, password, limit=3)
    page.locator(SEL_SUBMIT).first.click(timeout=20000)
    sleep(2)
    for _ in range(5):
        if not visible(page, SEL_BG, timeout=1):
            break
        _slider(page, token, calls)
        sleep(1)
    if (page.url or "") == HOME_B:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20000)
    if visible(page, SEL_MISMATCH, timeout=1):
        text = (page.locator(SEL_MISMATCH).first.inner_text(timeout=1000) or "").strip()
        raise CredentialsRejected(text or "账号名与密码不匹配，请重新输入")
    if xpath_visible(page, XPATH_SMS, timeout=5):
        raise NeedsHumanError(SMS_MESSAGE)
    if not xpath_visible(page, XPATH_LAUNCH, timeout=5):
        raise SellerLoginError(FAIL)
    target = platform_url(platform)
    if target:
        page.goto(target, wait_until="domcontentloaded", timeout=120000)
    return page, calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def jzt_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    platform: Optional[str] = None,
    relogin: bool = True,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    account = account if account is not None else os.environ.get("JZT_ACCOUNT", "")
    password = password if password is not None else os.environ.get("JZT_PASSWORD", "")
    yunma_token = yunma_token if yunma_token is not None else os.environ.get("YUNMA_TOKEN", "")
    if platform is None:
        platform = os.environ.get("JZT_PLATFORM", "")
    if not account or not password:
        raise ValueError("缺少京准通账号或密码")

    def _run(page=None, **_ignored):
        return login(account, password, yunma_token, platform=platform or "", relogin=relogin, page=page)

    return finish(_run, on_error=on_error, print_error_log=print_error_log, page=page)


def main() -> None:
    result = jzt_login()
    print({"ok": result.ok, "error": result.error, "yunma_calls": result.yunma_calls})
    close_result(result)


if __name__ == "__main__":
    main()
