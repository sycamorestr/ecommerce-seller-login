"""Playwright port of 影刀「平安银行登录」 activity_e05c2690/orangebank_load.py.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from banks._common import BankSpec, bank_login
from seller_common import OnError, SellerLoginResult

SOURCE = "activity_e05c2690/orangebank_load.py"
TITLE = '平安银行'
ENV_PREFIX = 'ORANGEBANK'
DEFAULT_LOAD_TYPE = 'default'
HIDDEN = False
LOGIN_URLS = {
    'default': 'https://auth.orangebank.com.cn/cimp-ccs-pc/#/p/ebank-login',
}
CAPTCHA_TYPES = ('22222',)
INPUT_FAIL = '输入失败，请手动登录'

SPEC = BankSpec(
    slug='orangebank',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css="input.pax-input[placeholder='企业网银/数字财资/橙E网用户名']",
    password_css='',
    login_css='button.main-btn-enterprise',
    captcha_image_css='',
    captcha_input_css="input.pax-input[placeholder='请输入图形验证码']",
    ukey_css='',
    ukey_message='当前浏览器可能未安装签名控件',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def orangebank_login(
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

