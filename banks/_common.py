"""Shared runner for activity_e05c2690 bank logins.

Each bank module keeps the source URLs, selector names, and captcha types.
Password controls and UKey prompts stop at NeedsHumanError. Alphanumeric
captchas use Yunma type 10103 unless the bank names another type.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from playwright.sync_api import Page

import captcha_helpers as captcha
from seller_common import (
    CredentialsRejected,
    NeedsHumanError,
    OnError,
    SellerLoginResult,
    finish,
    goto_with_retry,
    open_page,
    sleep,
    visible,
    xpath_visible,
)


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
