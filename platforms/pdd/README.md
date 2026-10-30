# 拼多多商家后台

## 模块简介

这个目录放拼多多商家后台的三个登录：

| 函数 | 影刀来源 | 说明 |
| --- | --- | --- |
| `pdd_login` | 商家后台账号登录 | 打开 `https://mms.pinduoduo.com/login/`，处理滑块和空间点选 |
| `pdd_promote_login` | `process51.py` 推广平台登录 | 从首页 `https://mms.pinduoduo.com/home/` 进入，验证码留给人工 |
| `pdd_mms_legacy_login` | `process43.py` 待下架 | `DEPRECATED = True`，点选类型记为图鉴 `19` |

滑块是云码 `22222`。空间点选是云码类型 `"9999"`（`cs_temu_payload`），提示文字来自 `span.picture-text__default`。

## 目录与文件说明

- `__init__.py`：包标记。
- `pdd_login_pw.py`：当前商家后台登录。公开函数 `pdd_login`、`login`、`main`。私有函数 `_click_account_tab`、`_solve_slider`、`_solve_space`、`_captcha_rounds`。
- `pdd_promote_login_pw.py`：推广平台登录。公开函数 `pdd_promote_login`、`login`、`main`。`_require` 检查账号密码是非空字符串。常量 `HOME_URL`、`LOGOUT_URL`、`FAIL`、`ALREADY`。
- `pdd_mms_legacy_login_pw.py`：待下架登录。公开函数 `pdd_mms_legacy_login`、`login`、`main`。从推广模块复用首页、退出地址和表单 xpath，自己处理点选。
- `helpers.py`：浏览器、`finish`、`SellerLoginResult`、`NeedsHumanError`。
- `captcha.py`：`std_slider_payload`、`cs_temu_payload`、`legacy_click_point`、图鉴类型 `19` 常量。登录只调用自己用到的那几个。

## 实现逻辑

### 商家后台 `pdd_login`

1. 读取 `PDD_ACCOUNT`、`PDD_PASSWORD`、`YUNMA_TOKEN`。账号或密码去空白后为空，抛 `ValueError`，文案是「拼多多账号、密码均不能为空」。`main()` 读 `PDD_RETRIES`（默认 5）。
2. 打开 `https://mms.pinduoduo.com/login/`，最多 3 次。
3. 登录前先跑一轮验证码。除 `SellerLoginError` 外的异常被打印后忽略。刷新图 `//div[@class="captcha-refresh"]/img` 可见则点击。
4. `#usernameId` 不可见时点「账号登录」：优先 `div.Common_item__3diIn:text-is("账号登录")`，否则 xpath `//div[@class="tab-operate"]/div/div[2]`。
5. 账号 `fill_checked` 最多 10 次。密码填两次。账号 tab 仍可见会再点一次。然后点 `button[data-testid="beast-core-button"]`。
6. 登录后再跑一轮验证码。滑块背景 `#slide-captcha-dialog img.slider-img-bg` 走 `22222` 并拖 `#slide-button`。`img#captchaClickImg` 走类型 `"9999"`，提示文字来自 `span.picture-text__default`。
7. `div.info-danger-container` 有文字时，`CredentialsRejected` 使用页面原文。URL 仍含 `login` 则 `NeedsHumanError`，文案「当前拼多多账号未成功登录，可能原因是需要手机验证。」

### 推广平台 `pdd_promote_login`

1. 账号来自 `PDD_PROMOTE_ACCOUNT` / `PDD_PROMOTE_PASSWORD`。`_require` 要求非空字符串。
2. 打开 `HOME_URL`。若 `user-name-text` 已可见且 `relogin=False`，直接返回（文案常量 `ALREADY`）。`relogin=True` 时先访问 `https://mms.pinduoduo.com/janus/api/logout`。
3. 再回首页，点「账号登录」，填 `#usernameId` / `#passwordId`，点「登录」。
4. 店铺名节点可见则成功。否则抛 `NeedsHumanError`，文案「登录失败，请先手动通过验证。」源码把短信和验证码标成 TODO，这里不自动打码。

### 待下架 `pdd_mms_legacy_login`

流程与推广平台相同，环境变量是 `PDD_LEGACY_ACCOUNT` / `PDD_LEGACY_PASSWORD`。出现点选时：传入 `click_recognizer`（返回 `x,y`）则用 `captcha.legacy_click_point` 点击；没有识别函数则 `NeedsHumanError("点选验证码")`。图鉴类型常量是 `"19"` / `ttshitu_19_predict`，源码没有图鉴账号和 HTTP 主机，所以模块本身不请求图鉴。

## 依赖与环境

- Playwright `>=1.40`。点选和滑块截图需要 Pillow。
- `PDD_ACCOUNT`、`PDD_PASSWORD`、`PDD_RETRIES`、`YUNMA_TOKEN` 给 `pdd_login`。
- `PDD_PROMOTE_ACCOUNT`、`PDD_PROMOTE_PASSWORD` 给推广登录。
- `PDD_LEGACY_ACCOUNT`、`PDD_LEGACY_PASSWORD` 给待下架登录。
- 可选 `SELLER_HTTP_PROXY`。三个入口都是 `headless=False`。
- 拷贝整个 `platforms/pdd/`。待下架模块 import 推广模块里的常量和 `_require`。

## 调用方法

```python
from platforms.pdd.pdd_login_pw import pdd_login
from platforms.pdd.pdd_promote_login_pw import pdd_promote_login
from platforms.pdd.pdd_mms_legacy_login_pw import pdd_mms_legacy_login
from platforms.pdd.helpers import close_result, OnError

result = pdd_login(retries=5)
print(result.ok, result.error, result.yunma_calls)
close_result(result)

promote = pdd_promote_login(relogin=False, on_error=OnError.TERMINATE)
close_result(promote)

legacy = pdd_mms_legacy_login(click_recognizer=None)
close_result(legacy)
```

返回 `SellerLoginResult`：`ok`、`web_page`、`error`、`yunma_calls`、`shots`。`NeedsHumanError` 得到 `ok=False`。缺账号在 `finish` 之前抛 `ValueError`。

已有页面：

```python
result = pdd_login(page=page, on_error=OnError.IGNORE)
```

## 注意事项

- 账号登录 tab 的 class `Common_item__3diIn` 是拼多多前端哈希，改版后会失效，代码里有 xpath 回退。
- `pdd_login` 的滑块和点选都要 `YUNMA_TOKEN`。推广登录和待下架登录不调用云码。
- 待下架模块 `DEPRECATED = True`，仍可调用，选择器与推广登录共用。
- 手机验证不会自动收短信。
- 不要把账号、密码、token 写进本目录。

## 测试

`tests/test_remaining_logins_pw.py` 导入推广登录和待下架登录，断言 `HOME_URL`、`LOGOUT_URL`、`DEPRECATED`、`process43`，并在清空环境变量后期望 `ValueError`。

`pdd_login_pw.py`（`https://mms.pinduoduo.com/login/` 这一支）没有被测试文件 import。图鉴类型 `19` 在 `test_payloads_and_distances` 里通过 `platforms.jingmai.captcha` 断言，与本目录 `captcha.py` 的常量相同。

```bash
pytest tests/test_remaining_logins_pw.py::test_login_urls tests/test_remaining_logins_pw.py::test_selectors_and_flags tests/test_remaining_logins_pw.py::test_missing_credentials tests/test_remaining_logins_pw.py::test_payloads_and_distances -q
```
