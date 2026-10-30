# 拼多多

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `captcha.py`
- `pdd_login_pw.py`
- `pdd_mms_legacy_login_pw.py`
- `pdd_promote_login_pw.py`

## 影刀来源

- Playwright port of 影刀「拼多多登录」 activity_7bca6d/process21.py.
- Playwright port of 影刀「拼多多商家后台登录（待下架）」 process43.py.
- Playwright port of 影刀「拼多多推广平台登录」 process51.py.

## 环境变量

- `PDD_ACCOUNT`
- `PDD_LEGACY_ACCOUNT`
- `PDD_LEGACY_PASSWORD`
- `PDD_PASSWORD`
- `PDD_PROMOTE_ACCOUNT`
- `PDD_PROMOTE_PASSWORD`
- `PDD_RETRIES`
- `YUNMA_TOKEN`

Do not put accounts, passwords, or tokens in this folder.
