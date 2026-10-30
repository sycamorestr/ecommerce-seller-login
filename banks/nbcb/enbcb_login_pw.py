"""Playwright port of 影刀「宁波银行登录」 activity_e05c2690/enbcb_load.py.

源指令在 prototype.block.json 里是 hidden，仍按源码移植。
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from .helpers import BankSpec, bank_login, OnError, SellerLoginResult

SOURCE = "activity_e05c2690/enbcb_load.py"
TITLE = '宁波银行'
ENV_PREFIX = 'NBCB'
DEFAULT_LOAD_TYPE = '个人网上银行'
HIDDEN = True
LOGIN_URLS = {
    '个人网上银行': 'https://e.nbcb.com.cn/#/main',
    '企业网上银行': 'https://cb.nbcb.com.cn/microbase/microhome/index.html?v=1730441864266#/browserQueryLogin',
}
CAPTCHA_TYPES = ('22222',)
INPUT_FAIL = '输入失败，请手动登录'
UKEY_MESSAGE = '当前浏览器可能未安装签名控件'

SPEC = BankSpec(
    slug='enbcb',
    title=TITLE,
    source=SOURCE,
    urls=LOGIN_URLS,
    env_prefix=ENV_PREFIX,
    default_load_type=DEFAULT_LOAD_TYPE,
    captcha_types=CAPTCHA_TYPES,
    username_css="input[name='userName']",
    password_css='input.newpwdcontrol',
    login_css='a.login-btn',
    captcha_image_css='',
    captcha_input_css='',
    ukey_css='a.wina',
    ukey_message='当前浏览器可能未安装签名控件',
    input_fail=INPUT_FAIL,
    hidden=HIDDEN,
)


def enbcb_login(
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

