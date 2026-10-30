"""Playwright port of 影刀「浙商银行登录」 activity_e05c2690/perbank_czbank_load.py.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import BankSpec, bank_login, OnError, SellerLoginResult

SOURCE = "activity_e05c2690/perbank_czbank_load.py"
TITLE = '浙商银行'
ENV_PREFIX = 'CZBANK'
DEFAULT_LOAD_TYPE = '个人网上银行'
HIDDEN = False
LOGIN_URLS = {
    '个人网上银行': 'https://perbank.czbank.com/PERBANK/logon.jsp',
    '企业网上银行': 'https://corbank.czbank.com/CORPORBANK/logon.jsp',
}
CAPTCHA_TYPES = ('10103',)
INPUT_FAIL = '输入失败，请手动登录'
UKEY_MESSAGE = '当前浏览器可能未安装签名控件'

SPEC = BankSpec(
    slug='perbank_czbank',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css='input#custId',
    password_css='',
    login_css='a.f-loginbtn',
    captcha_image_css='',
    captcha_input_css='',
    ukey_css='a#winA',
    ukey_message='当前浏览器可能未安装签名控件',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def perbank_czbank_login(
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

