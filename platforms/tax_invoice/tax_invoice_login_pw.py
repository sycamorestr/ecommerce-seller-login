"""电子税局登录 activity_invoice/tax_invoice_auth_login.py.

No browser URL. TaxInvoiceAPI.base_url is https://openapi.njmbxx.com.
When the API message contains 验证码 the source asks a person for the SMS code.
Face QR (is_qr_code) is NeedsHumanError. This module does not call the live API.
"""
from __future__ import annotations

import os
from typing import Optional

from .helpers import NeedsHumanError

API_BASE_URL = "https://openapi.njmbxx.com"
SOURCE = "activity_invoice/tax_invoice_auth_login.py"
SMS_MARK = "验证码"


def tax_login_body(nsrsbh: str, username: str, password: str, sms_code: str = "") -> dict:
    body = {"nsrsbh": nsrsbh, "username": username, "password": password}
    if sms_code:
        body["sms_code"] = sms_code
    return body


def tax_invoice_login(
    app_id: Optional[str] = None,
    secret: Optional[str] = None,
    tax_account: Optional[str] = None,
    tax_password: Optional[str] = None,
    nsrsbh: Optional[str] = None,
    *,
    sms_required: bool = False,
    sms_code: Optional[str] = None,
    is_qr_code: bool = False,
) -> dict:
    app_id = app_id if app_id is not None else os.environ.get("TAX_APP_ID", "")
    secret = secret if secret is not None else os.environ.get("TAX_APP_SECRET", "")
    tax_account = tax_account if tax_account is not None else os.environ.get("TAX_ACCOUNT", "")
    tax_password = tax_password if tax_password is not None else os.environ.get("TAX_PASSWORD", "")
    nsrsbh = nsrsbh if nsrsbh is not None else os.environ.get("TAX_NSRSBH", "")
    if sms_code is None:
        sms_code = os.environ.get("TAX_SMS_CODE", "")
    if not app_id or not secret:
        raise ValueError("缺少电子税局 app_id 或 secret")
    if not tax_account or not tax_password or not nsrsbh:
        raise ValueError("缺少电子税局账号、密码或纳税人识别号")
    if is_qr_code:
        raise NeedsHumanError("扫脸认证")
    if sms_required and not sms_code:
        raise NeedsHumanError(SMS_MARK)
    return {
        "base_url": API_BASE_URL,
        "body": tax_login_body(nsrsbh, tax_account, tax_password, sms_code),
    }
