# 爱库存

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `captcha.py`
- `aikucun_login_pw.py`

## 影刀来源

- Playwright port of 影刀「爱库存登录」 activity_7bca6d/process33.py.

## 环境变量

- `AIKUCUN_ACCOUNT`
- `AIKUCUN_PASSWORD`
- `AIKUCUN_RETRIES`

Do not put accounts, passwords, or tokens in this folder.
