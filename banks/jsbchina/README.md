# 江苏银行

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

签名控件或 UKey 提示为 `helpers.NeedsHumanError`。个人/企业地址在登录模块的 `LOGIN_URLS`。

## Files

- `helpers.py`
- `captcha.py`
- `jsbchina_login_pw.py`

## 影刀来源

- Playwright port of 影刀「江苏银行登录」 activity_e05c2690/jsbchina_load.py.

Do not put accounts, passwords, or tokens in this folder.
