# 京麦

## 模块简介

这个目录移植影刀「京麦登录」。登录地址是京麦商家后台的 passport：

`https://passport.shop.jd.com/login/index.action/jdm?ReturnUrl=https%3A%2F%2Fshop.jd.com%2FvcIndex.action`

成功后的首页标记是 `https://shop.jd.com/jdm/home`。滑块使用云码标准滑块类型 `22222`（`captcha.std_slider_payload` / `std_slider_distance`，偏移 0，速度 1）。

## 目录与文件说明

- `__init__.py`：包标记。
- `jingmai_login_pw.py`：入口。公开函数 `jingmai_login`、`login`、`main`，以及 `captcha_png_b64`、`captcha_input_equals`。私有函数 `_drag_std_slider`、`_error_text` 负责滑块和错误文案。
- `helpers.py`：本目录的浏览器、异常和 `SellerLoginResult`。`open_page` 默认有头。只有 `SELLER_HTTP_PROXY` 非空才加代理。
- `captcha.py`：云码 POST 和各类请求体。京麦登录用到标准滑块。文件里还有京东点选、美团距离等函数，本入口不调用。

## 实现逻辑

`jingmai_login` 读取 `JINGMAI_ACCOUNT`、`JINGMAI_PASSWORD`、`YUNMA_TOKEN`。缺账号或密码抛 `ValueError`。`main()` 把 `JINGMAI_RETRIES` 传给 `retries`（默认 5）。

`login` 的步骤：

1. 未传 `page` 时 `open_page(..., headless=False)`。`goto_with_retry` 打开登录 URL（最多 3 次），然后尝试 reload。
2. 二维码图 `div.jm-login-qrcode img[alt="二维码"]` 可见时，点击 `div.scan-login img.icon`。点击失败会被忽略。
3. 账号框最多尝试 5 次。读回值与账号不一致，到第 5 次抛 `CredentialsRejected("账号输入框填写失败")`。账号框始终不出现、二维码还在，则 `NeedsHumanError("二维码")`。
4. 密码框可见才填 `placeholder="请输入登录密码"`。登录按钮可见才点 `button.password__submit`。然后等 5 秒。
5. `detect_human_text` 命中短信等标记则 `NeedsHumanError`。
6. 滑块图可见时，按 `retries` 截背景、POST 类型 `22222`、拖 `div.jdjrv-slide-btn`。单次失败会点刷新。结束后滑块仍在则抛 `SellerLoginError("登录失败")`。滑块一开始就没有，且 URL 已经离开登录地址，则直接成功返回。
7. `#loginname_error` 或 `div.password__error` 有文字时抛 `CredentialsRejected("账户密码错误")`。异常对象里用的是这句固定文案，不是页面原文。
8. 仍在 passport 地址，或 URL 里没有 `shop.jd.com/jdm/home` 时，再打开 `HOME_URL`。
9. `finish` 收成 `SellerLoginResult`。

## 依赖与环境

- Playwright `>=1.40`，Pillow（截图进云码前会用到）。Python 3.10 及以上。
- 环境变量：`JINGMAI_ACCOUNT`、`JINGMAI_PASSWORD`、`YUNMA_TOKEN`、可选 `JINGMAI_RETRIES`、可选 `SELLER_HTTP_PROXY`。
- 本目录自带 `helpers.py` 和 `captcha.py`，单独拷走即可。
- 根目录同名 `jingmai_login_pw.py` 已废弃，请 `python -m platforms.jingmai.jingmai_login_pw`。

## 调用方法

```python
from platforms.jingmai.jingmai_login_pw import jingmai_login
from platforms.jingmai.helpers import close_result, OnError

result = jingmai_login(retries=5, on_error=OnError.TERMINATE)
print(result.ok, result.error, result.yunma_calls)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)
```

`SellerLoginResult` 字段：`ok`、`web_page`、`error`、`yunma_calls`、`shots`。自建浏览器在 `_browser` / `_context` / `_playwright`。传入的 `page` 由调用方关闭。

缺账号在 `finish` 之前抛 `ValueError`。`NeedsHumanError` 返回 `ok=False`。`OnError.IGNORE` 把其他异常收成 `ok=False`。

## 注意事项

- 京麦默认是扫码。密码框选择器依赖「切到密码登录」那一次点击，页面改版后 `div.scan-login img.icon` 很容易失效。
- 滑块选择器都挂在 `#JDJRV-wrap-passwordLoginSlideValidate` 下，和京东主站的 `JDJRV` 类名不同，不要混用 `platforms/jd` 的选择器。
- 云码 token 在滑块出现时由 `require_yunma_token` 检查。不要把 token 写进仓库。
- 入口固定有头。无头时京东滑块更容易失败。
- 没有单独的短信自动填充。页面停在验证上时，按 `finish` 的异常路径返回。

## 测试

`tests/test_remaining_logins_pw.py` 的 `test_payloads_and_distances` 通过 `platforms.jingmai.captcha` 检查标准滑块、京东点选类型 `30330`、爱库存偏移等请求体。该文件没有单独断言京麦登录 URL。不打开京麦页面。

```bash
pytest tests/test_remaining_logins_pw.py::test_payloads_and_distances -q
```
