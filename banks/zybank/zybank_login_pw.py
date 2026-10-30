"""Playwright port of 影刀「中原银行登录」 activity_e05c2690/zybank_load.py.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import BankSpec, bank_login, OnError, SellerLoginResult

SOURCE = "activity_e05c2690/zybank_load.py"
TITLE = '中原银行'
ENV_PREFIX = 'ZYBANK'
DEFAULT_LOAD_TYPE = 'default'
HIDDEN = False
LOGIN_URLS = {
    'default': 'https://pibs.zyebank.com/pweb/prelogin.do?_locale=zh_CN&LoginType=R&source=mh',
}
CAPTCHA_TYPES = ('10103',)
INPUT_FAIL = '输入失败，请手动登录'
UKEY_MESSAGE = '当前环境需要安装银行控件，安装完控件之后请重启浏览器'

SPEC = BankSpec(
    slug='zybank',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css='input.login_input_public',
    password_css='input#powerpass1',
    login_css='input#submitButton',
    captcha_image_css='img#form2_tokenImg',
    captcha_input_css='input.loginyzm_input_public',
    ukey_css='',
    ukey_message='当前环境需要安装银行控件，安装完控件之后请重启浏览器',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def zybank_login(
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

