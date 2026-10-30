"""Playwright port of 影刀「中国银行登录」 activity_e05c2690/bankofchina_load.py.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import BankSpec, bank_login, OnError, SellerLoginResult

SOURCE = "activity_e05c2690/bankofchina_load.py"
TITLE = '中国银行'
ENV_PREFIX = 'BOC'
DEFAULT_LOAD_TYPE = 'default'
HIDDEN = False
LOGIN_URLS = {
    'default': 'https://netc1.igtb.bankofchina.com/#/login-page?redirect=%2Findex',
}
CAPTCHA_TYPES = ('22222', '10103')
INPUT_FAIL = '输入失败，请手动登录'

SPEC = BankSpec(
    slug='bankofchina',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css='input.bfe-input__inner',
    password_css='input#secpwd',
    login_css='button.bfe-button--primary',
    captcha_image_css='img#dx_captcha_basic_slider-img-normal_2',
    captcha_input_css='',
    ukey_css='',
    ukey_message='当前浏览器可能未安装签名控件',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def bankofchina_login(
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

