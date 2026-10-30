# 电子税局

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `tax_invoice_login_pw.py`

## 影刀来源

- 电子税局登录 activity_invoice/tax_invoice_auth_login.py.

## 环境变量

- `TAX_ACCOUNT`
- `TAX_APP_ID`
- `TAX_APP_SECRET`
- `TAX_NSRSBH`
- `TAX_PASSWORD`
- `TAX_SMS_CODE`

Do not put accounts, passwords, or tokens in this folder.
