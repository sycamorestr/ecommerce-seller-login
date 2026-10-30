"""Playwright port of 影刀「交通银行登录-客户号登录」 activity_e05c2690/pbank_load_custom.py.

Same corporate URL as pbank_load 企业网上银行. Fields are 客户号 and 用户编号.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import BankSpec, bank_login, OnError, SellerLoginResult

TITLE = "交通银行客户号"
SOURCE = "activity_e05c2690/pbank_load_custom.py"
HIDDEN = False
LOGIN_URL = "https://ebank.bankcomm.cn/NEBS/CLG/CNLGAAA01?loginType=1"
CUSTOMER_CSS = "input[placeholder='请输入客户号']"
USER_CSS = "input[placeholder='请输入用户编号/别名']"
PASSWORD_CSS = "input#safeLogonPwd1"
ENV_PREFIX = "BOCOM_CUSTOM"

SPEC = BankSpec(
    slug="jiaotong_custom",
    title="交通银行客户号",
    source=SOURCE,
    urls={"default": LOGIN_URL},
    env_prefix=ENV_PREFIX,
    username_css=CUSTOMER_CSS,
    password_css=PASSWORD_CSS,
    ukey_message="当前浏览器可能未安装签名控件",
    captcha_types=("22222",),
)


def jiaotong_custom_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    user_num: Optional[str] = None,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    """``account`` is 客户号 (custome_num). ``user_num`` is 用户编号."""
    _ = user_num if user_num is not None else os.environ.get("BOCOM_CUSTOM_USER", "")
    return bank_login(
        SPEC, account, password, yunma_token,
        on_error=on_error, page=page, print_error_log=print_error_log,
    )
