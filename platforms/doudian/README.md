# 抖店

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `captcha.py`
- `doudian_login_pw.py`
- `doudian_multi_login_pw.py`
- `doudian_switch_shop_pw.py`

## 影刀来源

- Playwright port of 影刀「抖店登录」 process4.py.
- Playwright port of 影刀「抖店多店铺登录」 activity_966451c9/process1.py.
- Playwright port of 抖店店铺切换.

## 环境变量

- `DOUDIAN_ACCOUNT`
- `DOUDIAN_EMAIL`
- `DOUDIAN_EMAIL_AUTH`
- `DOUDIAN_EMAIL_CODE`
- `DOUDIAN_PASSWORD`
- `DOUDIAN_SHOP`
- `DOUDIAN_SHOP_ID`
- `YUNMA_TOKEN`

Do not put accounts, passwords, or tokens in this folder.
