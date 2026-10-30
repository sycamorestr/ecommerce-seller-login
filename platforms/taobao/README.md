# 淘宝

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `captcha.py`
- `taobao_login_pw.py`
- `taobao_mini_login_pw.py`

## 影刀来源

- Playwright port of 影刀「淘宝登录」 activity_7bca6d/process7.py.
- Playwright port of 影刀「淘宝mini登录」 activity_7bca6d/taobao_mini.py.

## 环境变量

- `TAOBAO_ACCOUNT`
- `TAOBAO_MINI_ACCOUNT`
- `TAOBAO_MINI_PASSWORD`
- `TAOBAO_MINI_RETRIES`
- `TAOBAO_PASSWORD`
- `YUNMA_TOKEN`

Do not put accounts, passwords, or tokens in this folder.
