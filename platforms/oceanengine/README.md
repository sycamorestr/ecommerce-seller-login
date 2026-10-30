# 巨量引擎

## 模块简介

这个目录有四条巨量登录，彼此不是别名：

| 函数 | 影刀来源 | 登录 URL |
| --- | --- | --- |
| `oceanengine_login` | `activity_7bca6d` 巨量登录 | `https://business.oceanengine.com/login` |
| `oceanengine_email_login` | 巨量引擎邮箱登录 | `https://business.oceanengine.com/login?appKey=51` |
| `oceanengine_zongheng_login` | 巨量纵横 | 与邮箱登录同一 URL |
| `oceanengine_collection_login` | `activity_52aea4a0/process1.py` 合集 | 同一 `appKey=51` URL，自己处理滑块 |

前三个在提交登录后调用 `platforms.doudian.doudian_login_pw` 的 `verify_platform`（邮箱登录还有 `verify_email`）。合集登录不 import 抖店，滑块在本文件里用云码类型 `"20225"`，最多 `SLIDER_TRIES = 7` 次。

拷贝本目录时请同时拷贝 `platforms/doudian/`（含它的 `captcha.py` 和 `helpers.py`）。合集若单独使用，仍依赖本目录的 `captcha.py` 和 `helpers.py`。

## 目录与文件说明

- `__init__.py`：包标记。
- `oceanengine_login_pw.py`：公开函数 `oceanengine_login`、`login`、`main`。私有函数 `_logout`、`_already`。已登录文案常量 `ALREADY = "已登录，不执行重新登录"`。
- `oceanengine_email_login_pw.py`：公开函数 `oceanengine_email_login`、`login`、`main`。`_old_workbench` 在出现「请选择工作台版本」时点旧版。已登录文案「不退出已登录的账户，登录流程结束。」
- `oceanengine_zongheng_login_pw.py`：公开函数 `oceanengine_zongheng_login`、`login`、`main`。从邮箱模块引用 `XPATH_OLD`、`XPATH_VERSION`。滑块和邮箱验证仍走抖店的 `verify_platform`。
- `oceanengine_collection_login_pw.py`：公开函数 `oceanengine_collection_login`、`login`。没有 `main`。退出 xpath 是 `//div[@class="navigator-user-account-info"]` 和 `//li[normalize-space(.)="退出登录"]`。
- `helpers.py`：本目录的 `finish` / `SellerLoginResult`。抖店验证用的是抖店目录自己的 helpers。
- `captcha.py`：合集滑块用 `dy_slider_payload`、`dy_recognized_px`。前三个入口在调用前用 `require_yunma_token`，真正识别发生在抖店模块。

## 实现逻辑

### `oceanengine_login`

环境变量 `OCEANENGINE_ACCOUNT`、`OCEANENGINE_PASSWORD`、`YUNMA_TOKEN`。`relogin` 默认 `False`；`main()` 在 `OCEANENGINE_RELOGIN` 为 `1` / `true` / `yes` 时设为真。`retries` 默认 5（`OCEANENGINE_RETRIES`）。

1. 打开不带 `appKey` 的登录 URL，最多 4 次。
2. 页头有「首页」：`relogin` 为假则返回；为真则点头像再点「退出账号」。
3. 点「邮箱登录」，填写 `input[name="email"]` 和密码，勾选协议，点 `button.account-center-action-button`。
4. `detect_human_text` 命中短信等标记则 `NeedsHumanError`。
5. `verify_platform`（抖店）处理滑块 `"20225"` 和点选。点选需要 `click_recognizer`，否则人工。

调用前就会 `require_yunma_token`，所以没有 token 时在打开页面前就失败。

### `oceanengine_email_login`

环境变量 `OCEANENGINE_EMAIL`、`OCEANENGINE_EMAIL_PASSWORD`、`OCEANENGINE_EMAIL_CODE`、`YUNMA_TOKEN`。`retries` 默认 10。`relogin` 默认 `False`。

打开带 `appKey=51` 的 URL。已登录且不重登则返回。否则点邮箱 tab，填邮箱和密码，勾选协议，点「登录」，必要时切旧版工作台，再 `verify_email` / `verify_platform`。邮箱验证码来自参数或 `OCEANENGINE_EMAIL_CODE`，本模块不拉信。

### `oceanengine_zongheng_login`

环境变量 `OCEANENGINE_ZH_ACCOUNT`、`OCEANENGINE_ZH_PASSWORD`、`YUNMA_TOKEN`。`retries` 默认 5。选择器是 `div.account-center-switch-button.email`、`input[placeholder="请输入邮箱"].ace-input`、`input[placeholder="密码"].ace-input`。登录后同样 `verify_platform`。

### `oceanengine_collection_login`

环境变量 `OCEANENGINE_COLLECTION_EMAIL`、`OCEANENGINE_COLLECTION_PASSWORD`、`YUNMA_TOKEN`。`relogin` 默认 `True`。

URL 含 `appKey=51`。已在 `https://business.oceanengine.com/` 且 `relogin` 为真时，点账户信息再点「退出登录」。然后填邮箱密码并登录。滑块图 `img.captcha-verify-image`、拖动 `div.captcha-slider-btn`，云码 `"20225"`，最多 7 次。不调用抖店点选。

## 依赖与环境

- Playwright `>=1.40`，Pillow。
- 上面列出的环境变量，外加可选 `SELLER_HTTP_PROXY`。
- 前三个函数依赖 `platforms.doudian.doudian_login_pw.verify_platform`。邮箱登录还依赖 `verify_email`。
- 四个入口都是有头 Chromium。
- 废弃的根目录 `oceanengine_*_login_pw.py` 只做重新导出。

## 调用方法

```python
from platforms.oceanengine.oceanengine_login_pw import oceanengine_login
from platforms.oceanengine.oceanengine_email_login_pw import oceanengine_email_login
from platforms.oceanengine.oceanengine_zongheng_login_pw import oceanengine_zongheng_login
from platforms.oceanengine.oceanengine_collection_login_pw import oceanengine_collection_login
from platforms.oceanengine.helpers import close_result

result = oceanengine_login(relogin=False, retries=5)
print(result.ok, result.error, result.yunma_calls)
close_result(result)

mail = oceanengine_email_login(retries=10, email_code=None)  # None 时读 OCEANENGINE_EMAIL_CODE
close_result(mail)

zh = oceanengine_zongheng_login(retries=5)
close_result(zh)

collection = oceanengine_collection_login(relogin=True)
close_result(collection)
```

返回 `SellerLoginResult`。缺账号或密码抛 `ValueError`。缺云码 token 时，前三个在 `require_yunma_token` 抛错；合集在滑块出现时才检查。

`click_recognizer` 只对前三个的抖店点选生效，签名与抖店相同：传入图片 base64，返回 `"x,y|x,y"`。

## 注意事项

- `oceanengine_login` 的 URL 没有 `appKey=51`。另外三个有。不要把合集登录当成 `oceanengine_login` 的别名。
- 合集的退出按钮文案是「退出登录」，工作台登录的退出文案是「退出账号」，选择器不同。
- 点选没有内置图鉴 HTTP。
- 邮箱验证码需要调用方事先放到环境变量或参数里。
- 工作台版本卡片、`ace-input` placeholder 改版后会点不到。
- 不要提交账号和 token。

## 测试

`tests/test_remaining_logins_pw.py` 的 `test_login_urls` 断言三条工作台 URL（不含合集），`test_missing_credentials` 对 `oceanengine_login`、邮箱、纵横期望 `ValueError`。

`tests/test_login_ext_pw.py` 的 `test_collection_logins` 断言合集 URL、`SLIDER_TRIES == 7`，并确认它不是 `activity_7bca6d/process47.py`。缺合集账号时期望 `ValueError`。

```bash
pytest tests/test_remaining_logins_pw.py::test_login_urls tests/test_remaining_logins_pw.py::test_missing_credentials tests/test_login_ext_pw.py::test_collection_logins -q
```
