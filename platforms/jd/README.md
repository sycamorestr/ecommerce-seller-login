# 京东

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `captcha.py`
- `jd_login_pw.py`

## 影刀来源

- Playwright port of 影刀「京东登录」 activity_7bca6d/process6.py.

## 环境变量

- `JD_ACCOUNT`
- `JD_LOGIN_URL`
- `JD_PASSWORD`
- `JD_RETRIES`
- `YUNMA_TOKEN`

Do not put accounts, passwords, or tokens in this folder.
