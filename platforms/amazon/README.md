# 亚马逊卖家

## 模块简介

这个目录移植影刀「亚马逊-店铺登录」`amazon_ext_op/process1.py`。

`amazon_login` 不打开卖家后台 URL，也没有账号、密码参数。它只检查当前页面：地址里不含 `signin`、`mfa`、`ap/signin` 时立刻返回成功。调用方需要先把页面打开到亚马逊登录或二次验证。

二次验证选择 `#guide-component` 出现时抛 `NeedsHumanError("二次验证验证码没有自动填充，请先进行配置")`。验证码 iframe `#aa-challenge-whole-page-iframe` 出现时抛 `NeedsHumanError("出现了数英验证码")`。

常量 `HOME`（`#partner-switcher`）和 `TIMEOUT`（「登录超时」）写在模块里，`login` 没有使用它们。

## 目录与文件说明

- `__init__.py`：包标记。
- `amazon_login_pw.py`：公开函数 `amazon_login`、`login`。内部函数 `_is_login_page`。没有 `main`。
- `helpers.py`：`open_page`、`finish`、`NeedsHumanError`、`SellerLoginResult`。
- 没有 `captcha.py`。

## 实现逻辑

1. `amazon_login` 没有账号参数，直接 `finish(login)`。
2. 未传 `page` 时 `open_page` 会打开一张空白有头页。空白页的 URL 不是登录页，函数马上返回 `ok=True`。
3. 传入的 `page.url` 含 `signin`、`mfa` 或 `ap/signin` 时：
   - `#guide-component` 有节点：二次验证人工。
   - `#aa-challenge-whole-page-iframe` 有节点：数英验证码人工。
   - `#signInSubmit` 有节点：点击一次。
4. 然后返回页面。没有轮询，也没有使用「登录超时」这句文案。

## 依赖与环境

- Playwright `>=1.40`。
- 不读取账号环境变量。可选 `SELLER_HTTP_PROXY`（仅当本函数自己启动浏览器时）。
- 拷贝整个 `platforms/amazon/`。有头模式。

## 调用方法

```python
from playwright.sync_api import sync_playwright
from platforms.amazon.amazon_login_pw import amazon_login
from platforms.amazon.helpers import close_result, OnError

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://sellercentral.amazon.com/")  # 由调用方打开，本函数不内置这个地址
    result = amazon_login(page=page, on_error=OnError.TERMINATE)
    print(result.ok, result.error, page.url)
    browser.close()
```

不传 `page` 时：

```python
from platforms.amazon.amazon_login_pw import amazon_login
from platforms.amazon.helpers import close_result

result = amazon_login()
print(result.ok, result.web_page.url if result.web_page else None)
close_result(result)
```

返回 `SellerLoginResult`。二次验证和数英验证码得到 `ok=False`。

## 注意事项

- 本函数不负责输入亚马逊账号。源码就是只点 `signInSubmit` 并拦截两种人工验证。
- 空白页会得到 `ok=True`，这不表示已经登录卖家中心。
- `HOME`、`TIMEOUT` 目前没有被 `login` 读取。
- 不要把账号、二次验证码写进仓库。

## 测试

`tests/test_login_ext_pw.py` 的 `test_collection_logins` 断言登录按钮 xpath，以及 `_is_login_page` 对含 `ap/signin` 的地址为真、对不含这些片段的卖家首页为假。

```bash
pytest tests/test_login_ext_pw.py::test_collection_logins -q
```
