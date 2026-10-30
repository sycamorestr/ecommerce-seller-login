# 生意参谋

## 模块简介

这个目录移植影刀「生意参谋登录Plus」`activity_26766b38/process45.py`。

登录页 `https://sycm.taobao.com/custom/login.htm`。首页 `https://sycm.taobao.com/portal/home.htm`。当前 URL 已经包含首页地址时，`login` 直接返回，不再填表。

没有云码。短信按钮 `//button[@id="J_GetCode"]` 可见时抛 `NeedsHumanError("短信验证")`。

## 目录与文件说明

- `__init__.py`：包标记。
- `sycm_login_pw.py`：公开函数 `sycm_login`、`login`。没有 `main`。
- `helpers.py`：`open_page`、`fill_checked`、`finish`、`NeedsHumanError`。
- 没有 `captcha.py`。

## 实现逻辑

`sycm_login` 读取 `SYCM_ACCOUNT`、`SYCM_PASSWORD`。缺一抛 `ValueError`。

1. 有头打开页面。URL 含 `HOME_URL` 则返回。
2. 否则打开登录页，超时 20 秒，1 次。
3. `#fm-login-id` 可见时，`fill_checked` 填账号和 `#fm-login-password`（各最多 3 次），点 `button.password-login`。
4. 短信按钮可见则人工。
5. `finish` 返回 `SellerLoginResult`。账号框不可见时不会点击登录，函数仍可能 `ok=True`。

## 依赖与环境

- Playwright `>=1.40`。无云码。
- `SYCM_ACCOUNT`、`SYCM_PASSWORD`，可选 `SELLER_HTTP_PROXY`。
- 拷贝整个 `platforms/sycm/`。有头模式。

## 调用方法

```python
from platforms.sycm.sycm_login_pw import sycm_login, LOGIN_URL, HOME_URL
from platforms.sycm.helpers import close_result

print(LOGIN_URL)
print(HOME_URL)
result = sycm_login()
print(result.ok, result.error)
close_result(result)
```

`page=` 可传入已经停在生意参谋首页的页面，此时不会重新登录。

## 注意事项

- 已经在首页时不会退出再登。
- 短信不自动填。
- 登录框选择器与淘宝密码登录相同（`#fm-login-id`），但 URL 是生意参谋自己的。
- 不要把账号密码写进仓库。

## 测试

`tests/test_login_ext_pw.py` 的 `test_collection_logins` 核对 `LOGIN_URL` 和 `HOME_URL`。缺 `SYCM_ACCOUNT` 时期望 `ValueError`。

```bash
pytest tests/test_login_ext_pw.py::test_collection_logins tests/test_login_ext_pw.py::test_tax_and_crossborder_guards -q
```
