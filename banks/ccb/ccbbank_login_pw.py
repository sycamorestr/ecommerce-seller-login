"""Playwright port of 影刀「中国建设银行登录」 activity_e05c2690/ccbbank_load.py.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import BankSpec, bank_login, OnError, SellerLoginResult

SOURCE = "activity_e05c2690/ccbbank_load.py"
TITLE = '中国建设银行'
ENV_PREFIX = 'CCB'
DEFAULT_LOAD_TYPE = 'default'
HIDDEN = False
LOGIN_URLS = {
    'default': 'https://ebanking1.ccb.com.cn/CCBIS/V6/common/loginNew.jsp',
}
CAPTCHA_TYPES = ('10103',)
INPUT_FAIL = '输入失败，请手动登录'

SPEC = BankSpec(
    slug='ccbbank',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css='input#USERID',
    password_css='input.wrap_input_search',
    login_css='input#loginButton',
    captcha_image_css='img#fujiama',
    captcha_input_css='',
    ukey_css='',
    ukey_message='当前浏览器可能未安装签名控件',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def ccbbank_login(
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

