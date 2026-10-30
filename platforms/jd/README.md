# 京东

## 模块简介

这个目录移植影刀「京东登录」。默认地址 `https://passport.jd.com/new/login.aspx`，可用参数或 `JD_LOGIN_URL` 换成别的京东登录页（只使用调用方传入的地址，模块不另造 URL）。

新版表单 `div.login-form.login-form-l` 上会处理三种验证码：

- 标准滑块 `22222`（背景 `img.JDJRV-bigimg`，拖动 `div.JDJRV-slide-btn`）。
- 点选加强：云码类型 `30009`，方向 `bottom`（`std_click_plus_payload`）。没有 `click_recognizer` 时这一支抛 `NeedsHumanError`。
- 京东点选：云码类型 `30330`（`jd_click_payload`），坐标用 `cs_temu_positions` 解析。

短信标题 `h5.tip-title` 出现时抛 `NeedsHumanError`，文案「当前账号需要短信验证」。滑块耗尽仍在则抛「由于验证码未通过导致登录失败」。

`captcha.py` 里还有京东旋转 `30330`（带 `image2`）、轨迹 `100015`、旧滑块图鉴类型 `18`。`jd_login` 当前不调用旋转、轨迹和类型 `18`。

## 目录与文件说明

- `__init__.py`：包标记。
- `jd_login_pw.py`：公开函数 `jd_login`、`login`、`main`。私有函数 `_drag_std`、`_click_plus`、`_jd_click`、`_sms`。
- `helpers.py`：`open_page`、`finish`、`input_value`、`fill_checked`。
- `captcha.py`：上面列出的请求体和距离函数。银行测试也会 import 一份内容相同的 captcha；京东目录这份是本登录实际 import 的那份。

## 实现逻辑

`jd_login` 读取 `JD_ACCOUNT`、`JD_PASSWORD`、`YUNMA_TOKEN`。`login_url` 为 `None` 时用 `JD_LOGIN_URL`，再没有则用默认 passport 地址。`retries` 默认 5，`main()` 读 `JD_RETRIES`。

1. 打开 `login_url`，最多 4 次。
2. 新版表单可见：点 `div.form-login-type.select-toggle` 切到密码。账号框 `input.itxt[placeholder="账号名/手机号/邮箱"]` 最多填 5 次，读回不一致抛 `CredentialsRejected("账号输入框填写失败")`。密码是 `#nloginpwd`。点击 `#loginsubmit`。
3. 最多 `retries` 轮：有背景图就拖标准滑块，失败则点 `span.JDJRV-refresh`；`#submit-btn` 可见走点选加强；`span.tip_text` 可见走京东点选 `30330`。搜索框 `input.text` 出现且「请登录」链接不可见，视为成功返回。
4. 仍有滑块图：`SellerLoginError(CAPTCHA_FAIL)`。`div.msg-error` 有文字则 `CredentialsRejected`。然后 `_sms`。`div.verifyBtn` 可见会点击一次再查短信。
5. 新版表单不可见时走旧版：点 `div.change-login-status-btn`、`a.hint-binding`、`a.checked`（各自可见才点），填 `input#loginname` 和 `input#nloginpwd`，点 `a#loginsubmit`，再查短信。

## 依赖与环境

- Playwright `>=1.40`，Pillow。
- `JD_ACCOUNT`、`JD_PASSWORD`、`YUNMA_TOKEN`、可选 `JD_LOGIN_URL`、`JD_RETRIES`、`SELLER_HTTP_PROXY`。
- 拷贝整个 `platforms/jd/`。有头模式。

## 调用方法

```python
from platforms.jd.jd_login_pw import jd_login
from platforms.jd.helpers import close_result, OnError

result = jd_login(retries=5, login_url=None, click_recognizer=None)
print(result.ok, result.error, result.yunma_calls)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)
```

`click_recognizer` 只服务于类型 `30009` 那一支。京东点选 `30330` 由云码返回坐标，不使用这个回调。

返回 `SellerLoginResult`。缺账号抛 `ValueError`。短信返回 `ok=False`。

## 注意事项

- 新版和旧版选择器都在。页面没有 `div.login-form.login-form-l` 时走旧版，旧版没有滑块重试循环。
- `JD_LOGIN_URL` 会原样打开。不要在代码里写死别人的登录地址。
- 类型 `18`、`100015` 和旋转 `image2` 只在 `captcha.py`，登录函数未调用。
- 短信不自动填充。
- 不要提交账号和 token。

## 测试

`tests/test_remaining_logins_pw.py` 核对 `LOGIN_URL`、`SMS_MESSAGE`、`#nloginpwd`，缺账号时期望 `ValueError`。`test_payloads_and_distances` 用京麦目录的 captcha 断言类型 `30330`、`30009` 方向 `bottom`、轨迹 `100015`、旧滑块距离公式。`tests/test_login_ext_pw.py` 的 `test_captcha_payloads` import 的是 `platforms.jd.captcha`，检查 `10103` / `10110`，那是验证码库测试，不是京东登录步骤。

```bash
pytest tests/test_remaining_logins_pw.py::test_login_urls tests/test_remaining_logins_pw.py::test_selectors_and_flags tests/test_remaining_logins_pw.py::test_missing_credentials tests/test_remaining_logins_pw.py::test_payloads_and_distances -q
```
