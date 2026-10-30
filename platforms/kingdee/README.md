# 金蝶云星空

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

## Files

- `helpers.py`
- `captcha.py`
- `kingdee_login_pw.py`

## 影刀来源

- Playwright port of 影刀「登录金蝶云星空」 activity_jindie/login.py.

## 环境变量

- `KINGDEE_ACCOUNT`
- `KINGDEE_PASSWORD`
- `KINGDEE_PLATFORM`
- `YUNMA_TOKEN`

Do not put accounts, passwords, or tokens in this folder.
