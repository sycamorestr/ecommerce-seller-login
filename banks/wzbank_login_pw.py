"""Playwright port of 影刀「温州银行登录」 activity_e05c2690/wzbank_load.py.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from banks._common import BankSpec, bank_login
from seller_common import OnError, SellerLoginResult

SOURCE = "activity_e05c2690/wzbank_load.py"
TITLE = '温州银行'
ENV_PREFIX = 'WZBANK'
DEFAULT_LOAD_TYPE = '个人网上银行'
HIDDEN = False
LOGIN_URLS = {
    '个人网上银行': 'https://ebankp.wzbank.cn/ebank/static/index.html#/home',
}
CAPTCHA_TYPES = ()
INPUT_FAIL = '输入失败，请手动登录'
UKEY_MESSAGE = '温州银行-个人版密码控件检测'

SPEC = BankSpec(
    slug='wzbank',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css="input[placeholder='请输入手机号']",
    password_css='input.ocx_style',
    login_css='',
    captcha_image_css='',
    captcha_input_css='',
    ukey_css='',
    ukey_message='温州银行-个人版密码控件检测',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def wzbank_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    load_type: Optional[str] = None,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    if load_type is None:
        load_type = os.environ.get(ENV_PREFIX + "_LOAD_TYPE", "") or None
    return bank_login(
        SPEC, account, password, yunma_token,
        load_type=load_type, on_error=on_error, page=page, print_error_log=print_error_log,
    )

