# 旺店通

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

Windows 客户端流程，没有网页地址。`wangdiantong_login()` 抛出本目录 `helpers.DesktopOnlyLogin`。

## Files

- `helpers.py`
- `wangdiantong_login_pw.py`

## 影刀来源

- Playwright port of 影刀「登录旺店通」 activity_7bca6d/process39.py.

Do not put accounts, passwords, or tokens in this folder.
