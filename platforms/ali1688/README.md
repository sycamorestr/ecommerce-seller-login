# 1688

## 模块简介

这个目录移植影刀 1688 登录，模块名是 `login_1688_pw.py`，公开函数 `login_1688`。

`LOGIN_URL` 是一段很长的淘宝登录跳转，查询串里带 `from=1688web`，最终落到 1688。完整字符串以 `platforms/ali1688/login_1688_pw.py` 为准，这里不截断抄写，避免和源码差一个百分号。

没有云码。NC 条 `#nc_1_n1z` 按 `span.nc-lang-cnt` 的宽度拖到轨道右端。切不到登录页抛「切换至登录页面失败」。登录按钮点完仍在则抛「登录失败，请手动登录」。

## 目录与文件说明

- `__init__.py`：包标记。
- `login_1688_pw.py`：公开函数 `login_1688`、`login`、`main`。私有函数 `_nc`。常量 `XPATH_OTHER`、`XPATH_PASSWORD_TAB`、`XPATH_USER`、`XPATH_PASSWORD`、`XPATH_LOGIN`、`XPATH_ERROR`、`SEL_NC`、`SEL_NC_ERROR`。
- `helpers.py`：`open_page`、`mouse_drag`、`finish`、`SellerLoginError`、`CredentialsRejected`。
- 没有 `captcha.py`。

## 实现逻辑

环境变量 `LOGIN1688_ACCOUNT`、`LOGIN1688_PASSWORD`。`retries` 默认 3，`main()` 读 `LOGIN1688_RETRIES`。缺账号或密码抛 `ValueError`。

1. 最多 5 次打开 `LOGIN_URL`。当前 URL 与常量完全一致才算打开成功。否则若地址里也不包含这段 URL，抛 `SWITCH_FAIL`。
2. 「快速进入」按钮可见时，点「使用其他账号登录」。
3. 点「密码登录」。填 placeholder「账号名/邮箱/手机号」和「请输入登录密码」，各最多 3 次校验。
4. 最多 `retries` 次：`div.errloading` 可见则点击；`span.nc-lang-cnt` 可见则 `_nc` 拖动；否则跳出。
5. 点「登录」。`div.login-error-msg` 有文字则 `CredentialsRejected`（用页面原文，空则「登录失败」）。登录按钮仍可见则 `SellerLoginError(LOGIN_FAIL)`。

## 依赖与环境

- Playwright `>=1.40`。不需要云码，也不需要 Pillow 做识别。
- `LOGIN1688_ACCOUNT`、`LOGIN1688_PASSWORD`、可选 `LOGIN1688_RETRIES`、`SELLER_HTTP_PROXY`。
- 拷贝整个 `platforms/ali1688/`。有头模式。

## 调用方法

```python
from platforms.ali1688.login_1688_pw import login_1688, LOGIN_URL
from platforms.ali1688.helpers import close_result

assert "from=1688web" in LOGIN_URL
result = login_1688(retries=3)
print(result.ok, result.error)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)
```

返回 `SellerLoginResult`。`page=` 可传入已有页面。

## 注意事项

- 登录地址是多层百分号编码的跳转。改其中一个 `%` 就会打不开 1688。
- NC 拖动距离等于文案条的宽度，不是云码返回值。
- 「帐户 / 账号」字样以源码 xpath 为准：这里是「使用其他账号登录」。
- 不要把账号密码写进仓库。

## 测试

`tests/test_remaining_logins_pw.py` 的 `test_login_urls` 断言 `LOGIN_URL` 含 `from=1688web`。缺 `LOGIN1688_ACCOUNT` 时期望 `ValueError`。

```bash
pytest tests/test_remaining_logins_pw.py::test_login_urls tests/test_remaining_logins_pw.py::test_missing_credentials -q
```
