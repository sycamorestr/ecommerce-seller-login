# 电子税局

## 模块简介

这个目录移植影刀「电子税局登录」`activity_invoice/tax_invoice_auth_login.py`。

它不是浏览器登录。接口根地址常量 `API_BASE_URL = "https://openapi.njmbxx.com"`。`tax_invoice_login` 不发 HTTP，只检查参数并返回将要提交的 body。

`is_qr_code=True` 时抛 `NeedsHumanError("扫脸认证")`。`sms_required=True` 且没有短信码时抛 `NeedsHumanError("验证码")`。

## 目录与文件说明

- `__init__.py`：包标记。
- `tax_invoice_login_pw.py`：公开函数 `tax_invoice_login`、`tax_login_body`。没有 `main`，没有 Playwright 调用。
- `helpers.py`：提供 `NeedsHumanError`。本函数不调用 `open_page` 或 `finish`。
- 没有 `captcha.py`。

## 实现逻辑

1. 参数为 `None` 时读取环境变量：`TAX_APP_ID`、`TAX_APP_SECRET`、`TAX_ACCOUNT`、`TAX_PASSWORD`、`TAX_NSRSBH`、`TAX_SMS_CODE`。
2. 缺 `app_id` 或 `secret`：`ValueError("缺少电子税局 app_id 或 secret")`。
3. 缺税局账号、密码或纳税人识别号：`ValueError("缺少电子税局账号、密码或纳税人识别号")`。
4. `is_qr_code` 为真：扫脸，抛 `NeedsHumanError`。这个异常没有包进 `SellerLoginResult`。
5. `sms_required` 为真且短信码为空：同样抛 `NeedsHumanError("验证码")`。
6. 返回字典：

```python
{
    "base_url": "https://openapi.njmbxx.com",
    "body": {"nsrsbh": "...", "username": "...", "password": "..."},
}
```

`tax_login_body` 只在 `sms_code` 非空时加入 `sms_code` 字段。密码字段名是 `password`，值来自税局密码参数，不是 `secret`。`app_id` 和 `secret` 只做非空检查，不放进 body。

## 依赖与环境

- 不需要打开浏览器。导入 `helpers.py` 时仍会加载 Playwright 类型。
- 环境变量：`TAX_APP_ID`、`TAX_APP_SECRET`、`TAX_ACCOUNT`、`TAX_PASSWORD`、`TAX_NSRSBH`、可选 `TAX_SMS_CODE`。
- 拷贝 `platforms/tax_invoice/`。没有登录 URL 可填。

## 调用方法

```python
from platforms.tax_invoice.tax_invoice_login_pw import tax_invoice_login, tax_login_body
from platforms.tax_invoice.helpers import NeedsHumanError

payload = tax_invoice_login(sms_required=False, is_qr_code=False)
print(payload["base_url"])
print(sorted(payload["body"]))

try:
    tax_invoice_login(is_qr_code=True)
except NeedsHumanError as exc:
    print(exc)
```

环境变量齐全时可以不传账号参数。返回值是 `dict`，不是 `SellerLoginResult`。

## 注意事项

- 函数不访问 `openapi.njmbxx.com`。拿到 body 之后的 HTTP 要调用方自己发，并且不要把 body 写进日志仓库。
- 扫脸和短信都是直接抛异常。
- `secret` 不进入 `body`。
- 不要把 app id、secret、纳税人识别号、短信码写进仓库。

## 测试

`tests/test_login_ext_pw.py` 断言 `API_BASE_URL`，并用 `tax_login_body("ns", "user", "pw", "998877")` 检查 `sms_code`。`test_tax_and_crossborder_guards` 覆盖缺凭证、`is_qr_code`、`sms_required`。测试里的 `"pw"` 只是占位符，不是真实密码。

```bash
pytest tests/test_login_ext_pw.py::test_collection_logins tests/test_login_ext_pw.py::test_tax_and_crossborder_guards -q
```
