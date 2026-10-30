# 速卖通

## 模块简介

这个目录移植影刀速卖通卖家登录 `activity_aliexpress/aliexpress_login.py`。

登录地址由 `login_url(language)` 生成：

`https://login.aliexpress.com/user/seller/login?bizSegment=CSP&_lang={lang}`

默认语言 `zh_CN`，也可用环境变量 `ALIEXPRESS_LANG`。

密码错误（页面 section 文案「您的帐户名或密码不正确。」）抛 `CredentialsRejected`，固定句是「您的帐户名或密码不正确，程序终止，请重新输入账号和密码」。

出现「验证」按钮且没有 6 位邮箱验证码时，抛 `NeedsHumanError("邮箱验证")`。本模块不连接邮箱。`extract_email_code` 只从已有文本里用正则提取。

## 目录与文件说明

- `__init__.py`：包标记。
- `aliexpress_login_pw.py`：公开函数 `aliexpress_login`、`login`、`login_url`、`extract_email_code`。没有 `main`。
- `helpers.py`：`open_page`、`finish`、`NeedsHumanError`、`CredentialsRejected`。
- 没有 `captcha.py`。正则 `EMAIL_CODE_RE` 匹配「一次性验证码是」「Verification code:」或「【…】…一次性验证码是」后面的 6 位数字。

## 实现逻辑

`aliexpress_login` 读取 `ALIEXPRESS_ACCOUNT`、`ALIEXPRESS_PASSWORD`、`ALIEXPRESS_LANG`、`ALIEXPRESS_EMAIL_CODE`。缺账号或密码抛 `ValueError`。

1. 若当前 URL 不是 `login_url(language)`，打开它（超时 20 秒，1 次）。
2. 等到表单按钮「Sign In」或「登录」。
3. 填 `#loginName` 和 `input[type=password]`，点击提交。
4. 失败 section 可见：`CredentialsRejected(BAD_PASSWORD)`。
5. 「验证」按钮可见：用参数里的 `email_code`。若整段文本能被正则抽出 6 位数，则用抽出的数字。仍然为空则人工。有码时在第一个 `iframe` 里填 `input` 并点「验证」。

## 依赖与环境

- Playwright `>=1.40`。无云码。
- `ALIEXPRESS_ACCOUNT`、`ALIEXPRESS_PASSWORD`、可选 `ALIEXPRESS_LANG`、`ALIEXPRESS_EMAIL_CODE`、`SELLER_HTTP_PROXY`。
- 拷贝整个 `platforms/aliexpress/`。有头模式。

## 调用方法

```python
from platforms.aliexpress.aliexpress_login_pw import aliexpress_login, login_url, extract_email_code
from platforms.aliexpress.helpers import close_result

print(login_url("zh_CN"))
print(extract_email_code("一次性验证码是 123456"))

result = aliexpress_login(language=None, email_code=None)
# language 为 None 时读 ALIEXPRESS_LANG，默认 zh_CN
print(result.ok, result.error)
close_result(result)
```

返回 `SellerLoginResult`。邮箱验证得到 `ok=False`。

## 注意事项

- 邮箱验证码要调用方事先放到 `ALIEXPRESS_EMAIL_CODE` 或参数里。正则不会发信。
- 验证码填写假设页面上有一个 `iframe`，里面第一个 `input` 就是验证码框。结构变化会填错。
- 密码错误文案用的是「帐户」这个字，与页面 section 一致。
- 不要把账号、密码、验证码写进仓库。

## 测试

`tests/test_login_ext_pw.py` 的 `test_collection_logins` 断言 `login_url("zh_CN")` 的前缀、`extract_email_code("一次性验证码是 123456") == "123456"`，以及 `BAD_PASSWORD` 的开头。缺账号在 `test_tax_and_crossborder_guards`。

```bash
pytest tests/test_login_ext_pw.py::test_collection_logins tests/test_login_ext_pw.py::test_tax_and_crossborder_guards -q
```
