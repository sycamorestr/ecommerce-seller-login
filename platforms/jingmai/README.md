# 京麦

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `captcha.py`
- `jingmai_login_pw.py`

## 影刀来源

- Playwright port of 影刀「京麦登录」 activity_7bca6d/process56.py.

## 环境变量

- `JINGMAI_ACCOUNT`
- `JINGMAI_PASSWORD`
- `JINGMAI_RETRIES`
- `YUNMA_TOKEN`

Do not put accounts, passwords, or tokens in this folder.
