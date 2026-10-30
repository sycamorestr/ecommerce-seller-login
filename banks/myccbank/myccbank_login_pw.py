"""Playwright port of 影刀「绵阳市商业银行登录」 activity_e05c2690/myccbank_load.py.

源指令在 prototype.block.json 里是 hidden，仍按源码移植。
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import BankSpec, bank_login, OnError, SellerLoginResult

SOURCE = "activity_e05c2690/myccbank_load.py"
TITLE = '绵阳市商业银行'
ENV_PREFIX = 'MYCCBANK'
DEFAULT_LOAD_TYPE = '个人网上银行'
HIDDEN = True
LOGIN_URLS = {
    '个人网上银行': 'https://pweb.mycc-bank.com/pweb/vx_zh_CN/index.html#/loginapp/UserLogin',
    '企业网上银行': 'https://eweb.mycc-bank.com/eweb/vx_zh_CN/index.html#/loginapp/UserLogin',
}
CAPTCHA_TYPES = ('66',)
INPUT_FAIL = '输入失败，请手动登录'
UKEY_MESSAGE = '当前浏览器可能安装签名控件'

SPEC = BankSpec(
    slug='myccbank',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css="input[placeholder='请输入您的手机号/证件号/卡号/用户名']",
    password_css='input#SIPBox',
    login_css='',
    captcha_image_css='',
    captcha_input_css="input[placeholder='请输入指定的验证码']",
    ukey_css='',
    ukey_message='当前浏览器可能安装签名控件',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def myccbank_login(
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

