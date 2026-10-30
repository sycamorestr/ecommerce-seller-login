"""Playwright port of 影刀「广东华兴银行登录」 activity_e05c2690/ghibank_load.py.
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import BankSpec, bank_login, OnError, SellerLoginResult

SOURCE = "activity_e05c2690/ghibank_load.py"
TITLE = '广东华兴银行'
ENV_PREFIX = 'GHIBANK'
DEFAULT_LOAD_TYPE = 'default'
HIDDEN = False
LOGIN_URLS = {
    'default': 'https://www.ghibank.com.cn/eweb/#/index',
}
CAPTCHA_TYPES = ('10103',)
INPUT_FAIL = '输入失败，请手动登录'
UKEY_MESSAGE = '当前环境为安装银行控件，请检查控件是否安装'

SPEC = BankSpec(
    slug='ghibank',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css="input[placeholder='请输入手机号码/用户名']",
    password_css="input[placeholder='请输入登录密码']",
    login_css='div.login_login',
    captcha_image_css='',
    captcha_input_css="input[placeholder='请输入验证码']",
    ukey_css='',
    ukey_message='当前环境为安装银行控件，请检查控件是否安装',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def ghibank_login(
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

