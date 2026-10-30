# Temu

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `temu_ads_login_pw.py`
- `temu_login_pw.py`
- `temu_switch_store_pw.py`

## 影刀来源

- Playwright port of Temu-广告平台-登录 activity_temu_shop/advertisement_login.py.
- Temu-切换店铺 and Temu-广告平台-切换店铺.
- Playwright port of Temu-账号登录 activity_temu_shop/login.py.

## 环境变量

- `TEMU_ACCOUNT`
- `TEMU_ADS_ACCOUNT`
- `TEMU_ADS_PASSWORD`
- `TEMU_ADS_STORE`
- `TEMU_PASSWORD`
- `TEMU_STORE`

Do not put accounts, passwords, or tokens in this folder.
