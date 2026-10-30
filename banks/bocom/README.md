# 交通银行

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

签名控件或 UKey 提示为 `helpers.NeedsHumanError`。个人/企业地址在登录模块的 `LOGIN_URLS`。

## Files

- `helpers.py`
- `captcha.py`
- `jiaotong_custom_login_pw.py`
- `jiaotong_login_pw.py`

## 影刀来源

- Playwright port of 影刀「交通银行登录」 activity_e05c2690/pbank_load.py.
- Playwright port of 影刀「交通银行登录-客户号登录」 activity_e05c2690/pbank_load_custom.py.

## 环境变量

- `BOCOM_CUSTOM_USER`

Do not put accounts, passwords, or tokens in this folder.
