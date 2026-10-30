"""Playwright port of 影刀「兴业银行登录」 activity_e05c2690/personalbank_load.py.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import BankSpec, bank_login, OnError, SellerLoginResult

SOURCE = "activity_e05c2690/personalbank_load.py"
TITLE = '兴业银行'
ENV_PREFIX = 'CIB'
DEFAULT_LOAD_TYPE = 'default'
HIDDEN = False
LOGIN_URLS = {
    'default': 'https://personalbank.cib.com.cn/pers/main/loginV7',
}
CAPTCHA_TYPES = ()
INPUT_FAIL = '账号入失败，请手动登录'
UKEY_MESSAGE = '兴业银行个人网上银行未检测到安全控件!请根据网页提示安装控件'

SPEC = BankSpec(
    slug='personalbank',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css="input[placeholder='请输入自定义登录名']",
    password_css="input[placeholder='请输入网银登录密码']",
    login_css='a.login-btn',
    captcha_image_css='',
    captcha_input_css='',
    ukey_css='',
    ukey_message='兴业银行个人网上银行未检测到安全控件!请根据网页提示安装控件',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def personalbank_login(
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

