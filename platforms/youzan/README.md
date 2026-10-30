# 有赞

## 模块简介

这个目录移植影刀「有赞登录」。地址是 `https://account.youzan.com/login`。

滑块走云码标准类型 `22222`：`std_slider_payload`，距离 `std_slider_distance(..., offset=0, speed=1)`。拖动元素是 `#slideIconRef`。登录按钮在结束后仍可见时，抛 `NeedsHumanError`，文案是「登录失败，当前可能需要验证手机号或账号未设置密码登录」。

## 目录与文件说明

- `__init__.py`：包标记。
- `youzan_login_pw.py`：公开函数 `youzan_login`、`login`、`main`。私有函数 `_slider` 截背景、请求云码并拖动。
- `helpers.py`：`open_page`、`finish`、`mouse_drag`、`SellerLoginResult`。
- `captcha.py`：本入口用 `require_yunma_token`、`std_slider_payload`、`std_slider_distance`、`yunma_post`。

## 实现逻辑

`youzan_login` 读取 `YOUZAN_ACCOUNT`、`YOUZAN_PASSWORD`、`YUNMA_TOKEN`。缺账号或密码抛 `ValueError`。

1. 打开登录 URL，最多 4 次，然后等待 2 秒。
2. 若当前 URL 已经不是登录页，尝试点掉引导 `a.introjs-donebutton`、昵称 `div.user-nickname` 或退出 `span.exit-link`。
3. 扫码标题 `span.login-qrcode__title__right` 可见时，点密码登录图 `img.js-tab-password-login`。
4. 再点 `span.bold.js-tab-password-login` 切到密码。
5. 第一个 `input.zent-input` 填账号，`input.zent-input[placeholder="输入登录密码"]` 填密码。协议勾选框可见则勾上。
6. 点击 `button.js-login-btn`。
7. 最多 5 次：背景 `div.captcha-bg, #slideBgRef` 可见就拖滑块；异常时点 `div.captcha-refresh`。
8. 登录按钮仍可见：`NeedsHumanError(PHONE_GATE)`。

## 依赖与环境

- Playwright `>=1.40`，Pillow。
- 环境变量：`YOUZAN_ACCOUNT`、`YOUZAN_PASSWORD`、`YUNMA_TOKEN`，可选 `SELLER_HTTP_PROXY`。
- 拷贝整个 `platforms/youzan/`。有头模式写死。

## 调用方法

```python
from platforms.youzan.youzan_login_pw import youzan_login
from platforms.youzan.helpers import close_result, OnError

result = youzan_login(on_error=OnError.TERMINATE)
print(result.ok, result.error, result.yunma_calls)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)
```

也可以 `youzan_login(page=page)` 复用已打开的页面。返回 `SellerLoginResult`。

## 注意事项

- 账号框是「第一个 `input.zent-input`」，页面上多一个输入框就会填错。
- `#slideIconRef` 和 `#slideBgRef` 是有赞滑块的关键选择器，测试里锁定了 `SEL_DRAG`。
- 手机验证和未设密码登录都走同一句 `PHONE_GATE`，模块不收短信。
- 云码 token 在滑块出现时才强制要求。
- 不要把账号和 token 写进仓库。

## 测试

`tests/test_remaining_logins_pw.py`：`test_login_urls` 核对登录 URL，`test_selectors_and_flags` 核对 `#slideIconRef`，`test_missing_credentials` 期望缺账号时 `ValueError`，`test_payloads_and_distances` 断言 `PHONE_GATE` 以「登录失败」开头。

```bash
pytest tests/test_remaining_logins_pw.py::test_login_urls tests/test_remaining_logins_pw.py::test_selectors_and_flags tests/test_remaining_logins_pw.py::test_missing_credentials tests/test_remaining_logins_pw.py::test_payloads_and_distances -q
```
