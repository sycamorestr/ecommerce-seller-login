"""Playwright port of 影刀「登录旺店通」 activity_7bca6d/process39.py.

The source drives a Windows desktop client (win32 input/click). It has no
login URL, so this module does not open a browser page.
"""
from __future__ import annotations

from seller_common import SellerLoginError

CAPTCHA_TYPE = "3"
CAPTCHA_CODE = "ttshitu_3_predict"
REASON = (
    "登录旺店通是 Windows 客户端流程（win32.element），源码没有网页登录地址，"
    "不能改写成 Playwright 打开页面。验证码参数仍是 captcha_type=3 / ttshitu_3_predict。"
)


class DesktopOnlyLogin(SellerLoginError):
    """Raised when a ShadowBot block is a desktop client, not a web login."""


def wangdiantong_login(*_args, **_kwargs) -> None:
    raise DesktopOnlyLogin(REASON)
