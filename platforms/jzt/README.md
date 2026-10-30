# 京准通

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `captcha.py`
- `jzt_login_pw.py`

## 影刀来源

- Playwright port of 影刀「京东登录-京准通」 process40.py plus process41.

## 环境变量

- `JZT_ACCOUNT`
- `JZT_PASSWORD`
- `JZT_PLATFORM`
- `YUNMA_TOKEN`

Do not put accounts, passwords, or tokens in this folder.
