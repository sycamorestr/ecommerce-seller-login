# 聚水潭

## 模块简介

这个目录移植影刀「聚水潭登录」`activity_jvshuitan/login.py`。地址 `https://www.erp321.com/login.aspx`。

没有验证码分支。源码测试里出现过的账号没有抄进本仓库。

常量 `XPATH_WELCOME`（「聚水潭欢迎您」）写在文件里。`login` 点击「立即登录」后就返回，没有等待这个欢迎页。

## 目录与文件说明

- `__init__.py`：包标记。
- `jushuitan_login_pw.py`：公开函数 `jushuitan_login`、`login`。没有 `main`。
- `helpers.py`：`open_page`、`fill_checked`、`finish`、`SellerLoginResult`。
- 没有 `captcha.py`。

## 实现逻辑

`jushuitan_login` 读取 `JUSHUITAN_ACCOUNT`、`JUSHUITAN_PASSWORD`。缺一抛 `ValueError`。

1. 有头打开 `https://www.erp321.com/login.aspx`，超时 60 秒，只试 1 次。
2. `//img[@alt="切换密码"]` 可见则点击，切到密码登录。
3. `fill_checked` 填 placeholder「邮箱地址/手机号码」和「请输入密码」，各最多 3 次。
4. 勾选 `//span[@class="ant-checkbox"]/input`。`check` 失败则改成 `click`。
5. 点 `//button[.="立即登录"]`。
6. `finish` 返回 `SellerLoginResult`。欢迎页 xpath 不参与判断。

## 依赖与环境

- Playwright `>=1.40`。无云码。
- `JUSHUITAN_ACCOUNT`、`JUSHUITAN_PASSWORD`，可选 `SELLER_HTTP_PROXY`。
- 拷贝整个 `platforms/jushuitan/`。有头模式。

## 调用方法

```python
from platforms.jushuitan.jushuitan_login_pw import jushuitan_login
from platforms.jushuitan.helpers import close_result, OnError

result = jushuitan_login(on_error=OnError.TERMINATE)
print(result.ok, result.error)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)
```

`page=` 可传入已打开的页面。返回 `SellerLoginResult`，`yunma_calls` 为 0。

## 注意事项

- 成功返回只表示点击了登录，不表示已经看到「聚水潭欢迎您」。
- 协议勾选是 Ant Design 的 checkbox，`check` 和 `click` 都会试一次。
- 不要把账号密码写进仓库。

## 测试

`tests/test_login_ext_pw.py` 的 `test_collection_logins` 核对 `LOGIN_URL`，并断言账号 xpath 含「邮箱」。`test_tax_and_crossborder_guards` 在缺 `JUSHUITAN_ACCOUNT` 时期望 `ValueError`。

```bash
pytest tests/test_login_ext_pw.py::test_collection_logins tests/test_login_ext_pw.py::test_tax_and_crossborder_guards -q
```
