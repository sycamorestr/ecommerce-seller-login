"""Playwright port of 影刀「抖店多店铺登录」 activity_966451c9/process1.py.

Login URL is https://fxg.jinritemai.com/login/common. After the single-store
email login, a non-empty shop name follows process17 (店铺切换（新）).
"""
from __future__ import annotations

import os
from typing import Optional

from playwright.sync_api import Page

from doudian_login_pw import doudian_login
from doudian_switch_shop_pw import doudian_switch_shop
from seller_common import OnError, SellerLoginResult

LOGIN_URL = "https://fxg.jinritemai.com/login/common"
SOURCE = "activity_966451c9/process1.py"
CAPTCHA_HUMAN = "验证码识别失败，需人工确认！"


def doudian_multi_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    shop_name: Optional[str] = None,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
) -> SellerLoginResult:
    if shop_name is None:
        shop_name = os.environ.get("DOUDIAN_SHOP", "")
    result = doudian_login(
        account,
        password,
        yunma_token,
        on_error=on_error,
        page=page,
        print_error_log=print_error_log,
    )
    if not result.ok or not shop_name:
        return result
    return doudian_switch_shop(
        shop_name=shop_name,
        on_error=on_error,
        page=result.web_page,
        print_error_log=print_error_log,
    )
