# 支付宝

## 模块简介

这个目录移植影刀「支付宝登录」。登录页是 `https://auth.alipay.com/login/index.htm`。

验证码有三条，按页面上实际出现的元素走：

- 拼图滑块：`img#puzzle_backimg` 和缺口 `#puzzle_slot`。距离用本机 OpenCV（Canny 150/152，`TM_CCOEFF_NORMED`）计算，不走云码。
- 点选：`div.jshield-captcha-click-container.click`。影刀侧是冰拓类型 `1311`，主机没有写死在代码里。未传入 `click_recognizer` 时抛 `NeedsHumanError("点选验证码")`。
- 四图旋转：云码类型 `276502`（`zfb_four_click_payload`）。

手机验证页 `https://authsa127.alipay.com/login/checkSecurity.htm` 抛 `NeedsHumanError("请先填写手机验证码登录")`。

## 目录与文件说明

- `__init__.py`：包标记。
- `alipay_login_pw.py`：公开函数 `alipay_login`、`login`、`handle_captcha`、`main`。私有函数 `_solve_slider`、`_cv_distance`、`_solve_four`、`_png`、`_count`。
- `helpers.py`：`open_page`、`finish`、`SellerLoginResult`、`NeedsHumanError`、`CredentialsRejected`。
- `captcha.py`：四图点击请求体、旋转角度解析 `rotate_deg_from_style` / `rotate_click_plan`、冰拓请求体 `bingtop_click_body`（登录流程不直接 POST 冰拓）、点选坐标 `parse_click_positions`。

## 实现逻辑

`alipay_login` 读取 `ALIPAY_ACCOUNT`、`ALIPAY_PASSWORD`、`YUNMA_TOKEN`。`retries` 默认 10，`main()` 读 `ALIPAY_RETRIES`。缺账号或密码抛 `ValueError`。`retry_count` 不是整数时，`login` 抛 `SellerLoginError`。

1. 当前 URL 不含登录地址时，打开 `LOGIN_URL`，最多 3 次。
2. 若 `//li[@data-status="show_login"]` 可见，点它切到账号登录。
3. 填写 `//input[@id="J-input-user"]` 和 `//input[@id="password_rsainput"]`，点击 `//input[@id="J-login-simulate-btn"]`。`fill_checked` 最多试 3 次。
4. `handle_captcha` 循环最多 `retries * 4` 次：
   - 反馈层 `jshield-feedback-wrapper` 出现时，关反馈并点刷新图。
   - 拼图背景可见：`_solve_slider(page, None)`，内部 `_cv_distance`。没有 `cv2` 时抛「支付宝滑块需要 opencv-python 计算缺口，或人工处理」。
   - 点选容器可见：调用 `click_recognizer(png_base64)`，返回值按 `x,y|x,y` 解析后点击。次数用尽抛「支付宝验证码处理失败」。
   - 四个 `image-item clickpuzzle`：`_solve_four` 把图发给云码 `276502`，按返回角度点击并确认。
   - 都没有则结束循环。
5. URL 含 `checkSecurity.htm`：人工短信。
6. `#J-errorBox` 里有文字：`CredentialsRejected`，前缀「登录失败, 错误元素: 」。

## 依赖与环境

- Playwright `>=1.40`，Pillow。拼图滑块额外需要 `opencv-python` 和 `numpy`，`requirements.txt` 没有强制列出它们。
- 环境变量：`ALIPAY_ACCOUNT`、`ALIPAY_PASSWORD`、`YUNMA_TOKEN`、可选 `ALIPAY_RETRIES`、可选 `SELLER_HTTP_PROXY`。
- 四图点击才消耗云码。点选不在本模块里请求冰拓。
- 拷贝整个 `platforms/alipay/`。入口固定有头。

## 调用方法

```python
from platforms.alipay.alipay_login_pw import alipay_login
from platforms.alipay.helpers import close_result, OnError

def recognize(image_b64: str) -> str:
    # 返回 "x,y|x,y"。没有识别服务就不要传，点选会变成 NeedsHumanError
    raise NotImplementedError

result = alipay_login(retries=10, click_recognizer=None, on_error=OnError.TERMINATE)
print(result.ok, result.error, result.yunma_calls)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)
```

返回 `SellerLoginResult`（`ok`、`web_page`、`error`、`yunma_calls`、`shots`）。短信和点选得到 `ok=False`。传入 `page=` 时复用该页，由调用方关闭。

## 注意事项

- 拼图选择器 `#puzzle_backimg`、`#puzzle_slot`、`.dv_handler.baseslider` 和四图 class `clickpuzzle` 都较脆。
- 无 OpenCV 时，一出现拼图滑块就失败，不会退回云码。
- 冰拓类型 `1311` 只留在 `captcha.py` 的请求体函数里，`handle_captcha` 不向冰拓发 HTTP。
- 手机验证不会读短信。
- 不要把账号、密码、云码 token 写进仓库。`headless` 在 `login` 里固定为 `False`。

## 测试

现有三个测试文件都没有 import `platforms.alipay`。跑全量 `pytest` 时本目录没有专门用例。改选择器或云码类型后，需要自己补测试或做有头实机。

```bash
pytest -q
```
