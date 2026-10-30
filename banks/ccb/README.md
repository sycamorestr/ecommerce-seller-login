# 中国建设银行

## 模块简介

这个目录是中国建设银行的网银登录。它移植影刀应用「登陆拓展合集」里的 `activity_e05c2690/ccbbank_load.py`。
对外入口是 `ccbbank_login_pw.py` 里的登录函数，内部都调用本目录 `helpers.bank_login`。影刀里对应指令是公开块。
浏览器流程是同一套：打开对应网址、检查控件提示、按选择器填写、按验证码类型决定是否请求云码、点击登录。
短信、扫码、人脸、UKey 安装都不会在这里自动完成。

## 目录与文件说明

- `__init__.py`：空文件，用来把该银行标成 Python 包，这样可以从 `banks.ccb` 导入。
- `captcha.py`：云码 POST（`yunma_post`）以及数英、滑块、点选的请求体。银行登录实际用到的是 `alphanum_payload`、`yunma_post`、`require_yunma_token`。其余函数随目录拷贝，这个入口不一定调用。不要在这个文件里填写 token。
- `ccbbank_login_pw.py`：影刀网银登录的 Playwright 入口。公开函数见下文。模块级常量 `LOGIN_URLS`、`ENV_PREFIX`、`CAPTCHA_TYPES`、`SPEC` 描述这一家的网址和选择器。
- `helpers.py`：本目录自带的运行内核。公开类型有 `OnError`、`SellerLoginError`、`NeedsHumanError`、`CredentialsRejected`、`DesktopOnlyLogin`、`SellerLoginResult`、`BankSpec`。公开函数有 `open_page`、`create_browser`、`goto_with_retry`、`visible`、`fill_checked`、`mouse_drag`、`finish`、`close_result`、`resolve_url`、`bank_login`。`_creds` 是内部函数，按参数或环境变量取账号密码。`SellerLoginResult` 字段是 `ok`、`web_page`、`error`、`yunma_calls`、`shots`，自建浏览器用 `_browser`、`_context`、`_playwright` 保存。

## 实现逻辑

### 中国建设银行（`ccbbank_login`）

来源 `activity_e05c2690/ccbbank_load.py`。环境变量前缀 `CCB`。

网址：

- `default`（默认）：https://ebanking1.ccb.com.cn/CCBIS/V6/common/loginNew.jsp

选择器：

- 用户名：`input#USERID`
- 密码：`input.wrap_input_search`
- 登录按钮：`input#loginButton`
- 验证码图片：`img#fujiama`
- 验证码输入框：空，这一步跳过
- 控件/UKey 提示：空，这一步跳过

步骤：

1. `ccbbank_login` 若没传 `load_type`，读取 `CCB_LOAD_TYPE`；空字符串当成未指定，再用默认键 `default`。
2. `resolve_url` 按键取网址。键不在表里会抛 `ValueError`，并列出源码里有的键。网址是空字符串也会抛 `ValueError`，不会编造地址。
3. `_creds` 取账号密码。参数优先；参数是 `None` 时读 `CCB_ACCOUNT` 和 `CCB_PASSWORD`。任一为空抛 `ValueError`，文案是「缺少中国建设银行账号或密码」。
4. `yunma_token` 为 `None` 时读 `YUNMA_TOKEN`。
5. `open_page` 在未传入 `page` 时启动有头 Chromium，然后 `goto` 上述网址（只试 1 次，超时 40 秒），接着尝试 `reload`。
6. `ukey_css` 为空，打开页面后不会因为控件提示中断。常量里的控件文案是「当前浏览器可能未安装签名控件」，当前这条路径用不到。
7. 用户名选择器可见时点击并填写，最多 3 次。读回的值与账号不一致则抛 `CredentialsRejected`，文案是「输入失败，请手动登录」。
8. 密码选择器可见时填写密码，不回读校验。
9. 验证码图片 `img#fujiama` 可见时，用云码类型 `10103` 调用 `captcha.alphanum_payload` 和 `captcha.yunma_post`。没有 `YUNMA_TOKEN` 时抛出 `NeedsHumanError`，文案是「数英验证码」。`captcha_input_css` 为空，识别出的字符串不会写入页面。类型 `10103` 的请求体会附带「需要区分大小写」。
10. 登录按钮选择器可见时点击。
11. 用户名、密码、登录按钮三个选择器都有值，可见时会依次填写并点击。

公共收尾：`finish` 成功时 `ok=True`。`NeedsHumanError` 不向外抛，返回 `ok=False` 且 `error` 为原因。
`on_error` 默认 `OnError.TERMINATE`，其他异常包成 `SellerLoginError`。设成 `OnError.IGNORE` 时返回 `ok=False`。
缺账号或密码时，`_creds` 在进入 `finish` 之前抛出 `ValueError`。

## 依赖与环境

- Python 3.10 及以上，Playwright `>=1.40`（同步 API）。本目录不使用 Selenium。
- 登录函数固定 `open_page(..., headless=False)`，也就是有头 Chromium，视口 1280×900。
- 只有环境变量 `SELLER_HTTP_PROXY` 非空时，`create_browser` 才给浏览器加代理。不要把代理账号写进仓库。
- 云码地址写在 `captcha.py`：主机 `api.jfbym.com`，路径 `/api/YmServer/customApi`。Token 只用环境变量 `YUNMA_TOKEN`，或调用时传入 `yunma_token`。
- 本目录自带 `helpers.py` 和 `captcha.py`，拷走这一家银行时带上这两个文件即可，不必再拷其他银行。
- 仓库根上的 `banks/<旧文件名>.py` 只是重新导出，已废弃。请从 `banks.<目录>.<模块>` 导入。

环境变量（只写名字，值放在进程环境里，不要写进仓库）：

- `CCB_ACCOUNT`、`CCB_PASSWORD`：账号和密码。
- `CCB_LOAD_TYPE`：可选，对应 `LOGIN_URLS` 的键。
- `YUNMA_TOKEN`：云码 token。只有验证码分支真正发请求或调用 `require_yunma_token` 时才需要。
- `SELLER_HTTP_PROXY`：可选 HTTP 代理。

## 调用方法

```python
from banks.ccb.ccbbank_login_pw import ccbbank_login
from banks.ccb.helpers import close_result, OnError

# 账号密码来自 CCB_ACCOUNT / CCB_PASSWORD，不要写在代码里
result = ccbbank_login(on_error=OnError.TERMINATE)
print(result.ok, result.error)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)  # 只关闭本次新建的浏览器
```

传入已有页面时，本函数不会关闭它：

```python
from playwright.sync_api import sync_playwright
from banks.ccb.ccbbank_login_pw import ccbbank_login

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    result = ccbbank_login(page=page, on_error=OnError.IGNORE)
    browser.close()
```

## 注意事项

- 选择器来自影刀源码。银行页面改版后，class 和 placeholder 很容易失效，失败时先对一下本目录模块里的 CSS，不要另写一套选择器。
- 过宽的选择器（单独的 `button`、`a`、`input[type=text]`）在移植时已清空，避免点错元素。清空后对应步骤会跳过，这是当前代码的行为。
- 有头模式是写死的。无头环境下银行控件和滑块更容易失败，本模块没有 `headless=True` 的开关。
- `22222` 在这个公共流程里只检查 token，不拖滑块。需要拖动的话不在 `bank_login` 里。
- 图鉴类型 `4`（成都农商）和 `66`（绵阳商行）只记在 `SPEC` 和 `captcha.py`，登录函数不会去调用图鉴。
- 不要把账号、密码、UKey 口令、云码 token、手机号写进本目录或提交到仓库。
- 登录成功后的页面留在 `result.web_page`。Cookie 不会自动落盘；若要保存，使用 `platforms/cookie/`，并单独传入页面。

## 测试

离线测试在 `tests/test_login_ext_pw.py` 的 `test_bank_urls_and_missing_creds`。
它会导入本目录的登录模块，核对 `LOGIN_URLS` 能被 `resolve_url` 解析，并在清空对应环境变量后调用登录函数，期望得到 `ValueError`。
不打开网银页面，也不读取真实账号。

只跑银行相关测试：

```bash
pytest tests/test_login_ext_pw.py::test_bank_urls_and_missing_creds -q
```

验证码请求体（含 `10103` 区分大小写）在同文件的 `test_captcha_payloads`，它导入的是 `platforms.jd.captcha`，与各银行目录里的 `captcha.py` 内容一致。
