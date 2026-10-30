# 金蝶云星空

## 模块简介

这个目录移植影刀「登录金蝶云星空」`activity_jindie/login.py`。

`LOGIN_URL` 是空字符串。源码要求登录页已经打开：页面上没有 `#user` 时抛 `SellerLoginError("账号输入框不存在，请检查是否打开登录页面")`。本函数不会自己导航到金蝶网址。

验证码是云码数英类型 `10110`（`alphanum_payload`，不附加「需要区分大小写」）。图片 `#img_VelidationCode`，输入框 `#velidationCode`。

常量 `LOGIN_FAIL`（「登录失败，登录按钮在规定时间没有消失」）写在模块里。当前 `login` 点击 `#btnLogin` 后没有等待按钮消失，也没有抛出这句。

## 目录与文件说明

- `__init__.py`：包标记。
- `kingdee_login_pw.py`：公开函数 `kingdee_login`、`login`。没有 `main`。
- `helpers.py`：`open_page`、`fill_checked`、`finish`、`NeedsHumanError`。
- `captcha.py`：`yunma_post`、`alphanum_payload`。类型常量 `YUNMA_TYPE_KINGDEE_ALPHANUM = "10110"`。

## 实现逻辑

`kingdee_login` 读取 `KINGDEE_ACCOUNT`、`KINGDEE_PASSWORD`、`YUNMA_TOKEN`、`KINGDEE_PLATFORM`。`login_now` 默认 `True`。缺账号或密码抛 `ValueError`。

1. 未传 `page` 时仍会启动有头浏览器，停在空白页。空白页没有 `#user`，于是抛「账号输入框不存在」。实际使用时应传入已经打开金蝶登录页的 `page`。
2. `platform` 非空时，点 `#datacenter_ct span.toolTip`，再点 `//ul/li[contains(., 平台名)]`。
3. 填 `#user`（最多 3 次校验），按 Tab，填 `#password`。
4. 验证码图可见：没有 token 则 `NeedsHumanError("数英验证码")`。否则截图 POST 类型 `10110`，把返回字符串填入 `#velidationCode`。`yunma_calls` 加 1。
5. 点 `#btnLogin`。
6. 若出现 `//span[.="该帐号已登录在线，确认让对方下线,"]`（源码逗号保留）：`login_now=True` 点「确认」，否则点「取消」。

## 依赖与环境

- Playwright `>=1.40`，Pillow（验证码截图）。
- `KINGDEE_ACCOUNT`、`KINGDEE_PASSWORD`、`YUNMA_TOKEN`、可选 `KINGDEE_PLATFORM`、`SELLER_HTTP_PROXY`。
- 拷贝整个 `platforms/kingdee/`。调用方自己准备已打开的登录页。

## 调用方法

```python
from playwright.sync_api import sync_playwright
from platforms.kingdee.kingdee_login_pw import kingdee_login
from platforms.kingdee.helpers import close_result

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    # 先由调用方打开金蝶登录页，本函数的 LOGIN_URL 是空字符串
    page.goto("在这里填写你自己的金蝶登录地址")
    result = kingdee_login(page=page, platform=None, login_now=True)
    print(result.ok, result.error, result.yunma_calls)
    browser.close()
```

`platform=None` 时读 `KINGDEE_PLATFORM`。返回 `SellerLoginResult`。

不要把示例里的地址换成仓库里没有的“官方默认 URL”。源码没有提供。

## 注意事项

- 不传 `page` 会开空白页并立刻因缺少 `#user` 失败。
- 已在线提示的 xpath 以源码为准，句末有逗号。
- 类型是 `10110`，不是银行常用的 `10103`。
- `LOGIN_FAIL` 当前不会被抛出。
- 不要把账号、数据中心名称、token 写进仓库。

## 测试

`tests/test_login_ext_pw.py` 断言 `LOGIN_URL == ""`、`CAPTCHA_TYPE == "10110"`、`SEL_USER == "#user"`。`test_captcha_payloads` 断言 `10110` 请求体没有 `extra`。缺 `KINGDEE_ACCOUNT` 时期望 `ValueError`。

```bash
pytest tests/test_login_ext_pw.py::test_collection_logins tests/test_login_ext_pw.py::test_captcha_payloads tests/test_login_ext_pw.py::test_tax_and_crossborder_guards -q
```
