# 巨量引擎

This folder is the copy unit. It contains the login entrypoint and the helpers it imports (`helpers.py`, and `captcha.py` when the login calls Yunma or 图鉴).

滑块和邮箱验证调用 `platforms/doudian/doudian_login_pw.py` 里的 process48/process49。单独拷贝本目录时请一并拷贝 `platforms/doudian/`。

## Files

- `helpers.py`
- `captcha.py`
- `oceanengine_collection_login_pw.py`
- `oceanengine_email_login_pw.py`
- `oceanengine_login_pw.py`
- `oceanengine_zongheng_login_pw.py`

## 影刀来源

- Playwright port of 影刀「巨量登录」 activity_7bca6d/process1.py.
- 登陆拓展合集「巨量引擎登录」 activity_52aea4a0/process1.py.
- Playwright port of 影刀「巨量纵横登录」 activity_7bca6d/process12.py.
- Playwright port of 影刀「巨量引擎邮箱登录」 activity_7bca6d/process47.py.

## 环境变量

- `OCEANENGINE_ACCOUNT`
- `OCEANENGINE_COLLECTION_EMAIL`
- `OCEANENGINE_COLLECTION_PASSWORD`
- `OCEANENGINE_EMAIL`
- `OCEANENGINE_EMAIL_CODE`
- `OCEANENGINE_EMAIL_PASSWORD`
- `OCEANENGINE_EMAIL_RETRIES`
- `OCEANENGINE_PASSWORD`
- `OCEANENGINE_RELOGIN`
- `OCEANENGINE_RETRIES`
- `OCEANENGINE_ZH_ACCOUNT`
- `OCEANENGINE_ZH_PASSWORD`
- `YUNMA_TOKEN`

Do not put accounts, passwords, or tokens in this folder.
