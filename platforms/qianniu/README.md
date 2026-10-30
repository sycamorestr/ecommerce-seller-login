# 千牛

## 模块简介

这个目录移植影刀市场指令「千牛登录」：`activity_7bca6d` 的 `qn_login`，加上 `activity_jfbym` 的阿里滑块 `ali_slider_captcha`。

登录页固定为 `https://loginmyseller.taobao.com/`。滑块识别走云码类型 `20226`（主机 `api.jfbym.com`，路径 `/api/YmServer/customApi`）。短信、身份校验和其他人工闸门返回失败结果，不在这里自动填验证码。

日常入口用 Playwright：`qianniu_login_pw.py`。同目录的 `qianniu_login.py` 是 Selenium 版本，HTTP 识别函数也放在那里，Playwright 入口通过 `from . import qianniu_login as _se` 复用 `yunma_recg`。

## 目录与文件说明

- `__init__.py`：空文件，使 `platforms.qianniu` 可以作为包导入。
- `qianniu_login_pw.py`：Playwright 入口。公开函数是 `qianniu_login`、`login`、`close_result`、`main`，以及滑块辅助 `handle_verification`、`do_nc_mouse_drag`、`detect_human_gate`、`create_browser`。`login` 负责打开页面、填表、滑块和 NC 条；`qianniu_login` 读取环境变量并收成 `QianniuLoginResult`。
- `qianniu_login.py`：Selenium 版同一流程。公开函数包括 `qianniu_login`（参数是 `driver` 而不是 `page`）、`yunma_recg`、`join_images`、`encode_image`、`decode_image`。拖动在这版里可以走 `xdotool`（默认 `DISPLAY`，缺省 `:2`）或 CDP。
- `helpers.py`：一份通用内核（`SellerLoginResult`、`open_page`、`finish` 等）。千牛两个入口都没有 import 它。Playwright 入口自己定义 `QianniuLoginResult` 和 `OnError`，并写死代理 `http://127.0.0.1:8791`。
- 本目录没有 `captcha.py`。云码请求写在 `qianniu_login.yunma_recg`。

## 实现逻辑

`qianniu_login` 先取账号、密码、token（参数优先，否则读环境变量）。缺账号或密码直接抛 `ValueError`。然后调用 `login`。

1. 未传入 `page` 时启动有头 Chromium。`mode` 只接受 `chrome`、`edge`、`cef`、`SunBrowser`，其他值改成 `chrome`。Playwright 版实际都是 Chromium，并带固定代理 `http://127.0.0.1:8791`。
2. 打开 `LOGIN_URL`，失败则 reload，最多 3 次。
3. 进入 `iframe#alibaba-login-box`，填写 `#fm-login-id`。
4. 若出现滑块题干（`canvas#captcha-question` 等），先跑 `handle_verification`。这一步里的异常除 `NeedsHumanError` 外会被吃掉，与影刀一致。
5. 再填写 `#fm-login-password`。
6. 外层最多 6 轮。每轮里若 NC 条可见（`#nc_1_n1z`），用鼠标拖过整条；若出现 `div.errloading` 则点击后重试。
7. 去掉登录按钮的 disabled，点击 `button.password-login`。
8. `detect_human_gate` 看到短信、身份验证等文案时抛 `NeedsHumanError`。`div.login-error-msg` 有文字时抛 `CredentialsRejected`，文字用页面上的原文。
9. 仍停在 `loginmyseller.taobao.com` 且地址里没有 `/home`：登录按钮还在则抛「登录失败」；按钮没了则抛「仍停在登录页，可能需短信/其他验证」。

滑块：监听图片，把提示图和背景图上下拼接后 POST 类型 `20226`。距离像素是 `(识别值 - 24 - 10) / 320 * 320`。调用时传入的 `offset=-30` 在这段距离计算里没有使用。拖动带轻微过冲。

`qianniu_login` 捕获 `NeedsHumanError` 后返回 `ok=False`，浏览器句柄留在结果里。其他异常在 `OnError.TERMINATE` 时抛 `QianniuLoginError`。

## 依赖与环境

- Python 3.10 及以上。Playwright `>=1.40`，Selenium `>=4.15`，Pillow `>=10`。
- 环境变量：`QIANNIU_ACCOUNT`、`QIANNIU_PASSWORD`、`YUNMA_TOKEN`。`main()` 还会读 `QIANNIU_RETRIES`（默认 5）。Selenium 拖动读 `DISPLAY`（默认 `:2`）。
- 代理写死为 `http://127.0.0.1:8791`，不受 `SELLER_HTTP_PROXY` 控制。机器上没有这个代理时，页面打不开。
- 拷贝本目录即可运行千牛登录，不必再拷其他平台。`helpers.py` 可以不参与运行。
- 仓库根上的 `qianniu_login_pw.py` 只是重新导出，请改用 `python -m platforms.qianniu.qianniu_login_pw`。

实机脚本 `scripts/run_live_login_pw.py` 会设置 `DISPLAY` 默认 `:2`，缺三个环境变量时退出码 2。

## 调用方法

```python
from platforms.qianniu.qianniu_login_pw import qianniu_login, close_result

# 从 QIANNIU_ACCOUNT / QIANNIU_PASSWORD / YUNMA_TOKEN 读取，不要把值写进代码
result = qianniu_login(retries=5)
print(result.ok, result.error, result.yunma_calls)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)
```

传入已有页面时，`close_result` 只关闭结果对象上挂着的浏览器；你自己创建的 `page` 若没有写进 `_browser`，需要自己关。

```python
from playwright.sync_api import sync_playwright
from platforms.qianniu.qianniu_login_pw import qianniu_login

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False, proxy={"server": "http://127.0.0.1:8791"})
    page = browser.new_page()
    result = qianniu_login(page=page)
    browser.close()
```

Selenium 入口签名是 `qianniu_login(..., driver=None)`，返回 `QianniuLoginResult`（字段与 Playwright 版同类，浏览器对象不同）。

`QianniuLoginResult` 字段：`ok`、`web_page`、`error`、`yunma_calls`、`shots`。截图落在本目录 `shots/`。

## 注意事项

- 登录框在 `iframe#alibaba-login-box` 里，滑块弹层再套 `iframe#baxia-dialog-content`。选择器写在顶层页面上会找不到元素。
- 云码 token 为空时，滑块步骤抛「云码 token 为空，无法识别滑块（影刀 ym 引擎）」。不要把 token 写进仓库。
- Playwright 与 Selenium 都强制代理 `127.0.0.1:8791`。无头参数在 `create_browser` 里默认 `False`，`login` 也传 `headless=False`。
- NC 条是整段拖动，不走云码。`div.errloading` 要点一次再重试。
- 短信和身份验证返回 `ok=False`。页面留着，方便人工处理后再 `close_result`。
- `captcha_cache/` 和 `shots/` 会被生成，不要提交。

## 测试

`tests/test_qianniu_login_pw.py` 覆盖云码请求体类型 `20226`、拼图高度、距离公式、缺账号、`OnError.IGNORE`、`NeedsHumanError` 返回值、登录 URL，以及 Playwright 选择器与 Selenium 常量一致。不打开淘宝页面。

```bash
pytest tests/test_qianniu_login_pw.py -q
```
