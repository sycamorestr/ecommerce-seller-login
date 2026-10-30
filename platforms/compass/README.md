# 电商罗盘

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `captcha.py`
- `compass_login_pw.py`
- `compass_strategy_login_pw.py`

## 影刀来源

- Playwright port of 影刀「电商罗盘策略登陆」 activity_7bca6d/process59.py.
- Playwright port of 影刀「电商罗盘登录」 activity_7bca6d/process15.py.

## 环境变量

- `COMPASS_ACCOUNT`
- `COMPASS_PASSWORD`
- `COMPASS_SHOP`
- `COMPASS_STRATEGY_ACCOUNT`
- `COMPASS_STRATEGY_PASSWORD`
- `COMPASS_STRATEGY_SHOP`
- `YUNMA_TOKEN`

Do not put accounts, passwords, or tokens in this folder.
