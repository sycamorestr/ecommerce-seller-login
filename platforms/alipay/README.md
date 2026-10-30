# 支付宝

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `captcha.py`
- `alipay_login_pw.py`

## 影刀来源

- Playwright port of 影刀「支付宝登录」.

## 环境变量

- `ALIPAY_ACCOUNT`
- `ALIPAY_PASSWORD`
- `ALIPAY_RETRIES`
- `YUNMA_TOKEN`

Do not put accounts, passwords, or tokens in this folder.
