# 速卖通

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `aliexpress_login_pw.py`

## 影刀来源

- Playwright port of 速卖通登录 activity_aliexpress/aliexpress_login.py.

## 环境变量

- `ALIEXPRESS_ACCOUNT`
- `ALIEXPRESS_EMAIL_CODE`
- `ALIEXPRESS_LANG`
- `ALIEXPRESS_PASSWORD`

Do not put accounts, passwords, or tokens in this folder.
