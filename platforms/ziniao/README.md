# 紫鸟

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

Windows 客户端（紫鸟浏览器专业版）。`ziniao_login()` 抛出本目录 `helpers.DesktopOnlyLogin`。

## Files

- `helpers.py`
- `ziniao_login_pw.py`

## 影刀来源

- 紫鸟登录 super_browser/process1.py drives the Windows client, not a web page.

Do not put accounts, passwords, or tokens in this folder.
