"""Playwright port of 影刀「中信银行登录」 activity_e05c2690/ecitic_load.py.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from banks._common import BankSpec, bank_login
from seller_common import OnError, SellerLoginResult

SOURCE = "activity_e05c2690/ecitic_load.py"
TITLE = '中信银行'
ENV_PREFIX = 'ECITIC'
DEFAULT_LOAD_TYPE = '个人网上银行'
HIDDEN = False
LOGIN_URLS = {
    '个人网上银行': 'https://i.bank.ecitic.com/perbank6/signIn.do',
    '企业网上银行': 'https://corp.bank.ecitic.com/cotb/login.html',
}
CAPTCHA_TYPES = ('10103', '22222')
INPUT_FAIL = '输入失败，请手动登录'
UKEY_MESSAGE = '当前浏览器可能未安装签名控件'

SPEC = BankSpec(
    slug='ecitic',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css='input.el-input__inner',
    password_css='input#ocxEdit',
    login_css='button.loginbutton',
    captcha_image_css='',
    captcha_input_css="input[name='verifyCode']",
    ukey_css='a.linkbtn',
    ukey_message='当前浏览器可能未安装签名控件',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def ecitic_login(
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

