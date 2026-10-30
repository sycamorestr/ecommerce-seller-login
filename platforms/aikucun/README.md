# 爱库存

## 模块简介

这个目录移植影刀爱库存登录。地址 `https://merc.aikucun.com/login.html`。

滑块不用云码。把滑块图和 canvas 截图交给 `captcha.canny_match_x`（OpenCV Canny 150/152，`TM_CCOEFF_NORMED`）。拖动距离是 `free_slider_drag_distance(match_x, -4)`，偏移常量 `AIKUCUN_FREE_SLIDER_OFFSET = -4`。没有 `cv2` 时匹配抛错，被内层 `except` 接住，`match_x` 变成 `None`，这一轮不拖动。

密码错误文案「账号密码错误」。重试耗尽抛 `SellerLoginError`，文案是 `验证码{retries}次未通过，登录失败`。

## 目录与文件说明

- `__init__.py`：包标记。
- `aikucun_login_pw.py`：公开函数 `aikucun_login`、`login`、`main`。选择器常量 `SEL_USER`、`SEL_PASSWORD`、`SEL_LOGIN`、`SEL_SLIDER`、`SEL_REFRESH`。
- `helpers.py`：`open_page`、`mouse_drag`、`finish`、`CredentialsRejected`。
- `captcha.py`：`canny_match_x`、`free_slider_drag_distance`、`AIKUCUN_FREE_SLIDER_OFFSET`。文件里还有云码函数，本登录不调用。

## 实现逻辑

`aikucun_login` 读取 `AIKUCUN_ACCOUNT`、`AIKUCUN_PASSWORD`。`retries` 默认 5，`main()` 读 `AIKUCUN_RETRIES`。缺账号或密码抛 `ValueError`。

每一轮：

1. 打开登录 URL（超时 30 秒，1 次）。
2. 填 `input.el-input__inner[placeholder="输入用户名"]` 和「输入密码」，点 `button.merchant_login_btn`。
3. 内层最多 20 次：登录按钮消失则成功返回。刷新钮 `#dx_captcha_basic_btn-refresh_4` 可见则点击。滑块 `#dx_captcha_basic_slider_2` 和 `canvas` 都可见时做缺口匹配并拖动。
4. 内层结束仍看到 `p.el-form-item__error` 则 `CredentialsRejected("账号密码错误")`。

外层轮数用尽抛验证码失败。

## 依赖与环境

- Playwright `>=1.40`，Pillow。缺口匹配需要 `opencv-python` 和 `numpy`，未写入 `requirements.txt`。
- `AIKUCUN_ACCOUNT`、`AIKUCUN_PASSWORD`、可选 `AIKUCUN_RETRIES`、`SELLER_HTTP_PROXY`。
- 不使用 `YUNMA_TOKEN`。
- 拷贝整个 `platforms/aikucun/`。有头模式。

## 调用方法

```python
from platforms.aikucun.aikucun_login_pw import aikucun_login
from platforms.aikucun.helpers import close_result

result = aikucun_login(retries=5)
print(result.ok, result.error)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)
```

返回 `SellerLoginResult`。`yunma_calls` 保持 0。

## 注意事项

- 滑块 id `#dx_captcha_basic_slider_2` 和刷新 `#dx_captcha_basic_btn-refresh_4` 带数字后缀，页面改 id 后匹配不到。
- 没装 OpenCV 时每轮都不拖，最后以验证码失败结束。
- Windows 上 `free_slider_drag_distance(..., windows=True)` 会再除一次 ppi。登录调用没有传 `windows=True`。
- 不要把账号密码写进仓库。

## 测试

`tests/test_remaining_logins_pw.py` 核对登录 URL 和 `button.merchant_login_btn`。缺账号时期望 `ValueError`。`test_payloads_and_distances` 断言偏移 `-4` 时距离 `40 + (-4) = 36`。

```bash
pytest tests/test_remaining_logins_pw.py::test_login_urls tests/test_remaining_logins_pw.py::test_selectors_and_flags tests/test_remaining_logins_pw.py::test_missing_credentials tests/test_remaining_logins_pw.py::test_payloads_and_distances -q
```
