# 阿里妈妈

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `alimama_login_pw.py`
- `alimama_platform_login_pw.py`

## 影刀来源

- Playwright port of 影刀「阿里妈妈数智登录」 activity_7bca6d/process42.py.
- Playwright port of 影刀「阿里妈妈_平台登录」 activity_d91a274e/process6.py.

## 环境变量

- `ALIMAMA_ACCOUNT`
- `ALIMAMA_PASSWORD`
- `ALIMAMA_PLATFORM`
- `ALIMAMA_PLATFORM_ACCOUNT`
- `ALIMAMA_PLATFORM_PASSWORD`

Do not put accounts, passwords, or tokens in this folder.
