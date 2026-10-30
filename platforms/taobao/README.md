# 淘宝

## 模块简介

这个目录有两个淘宝登录：

- `taobao_login`：`https://login.taobao.com/member/login.jhtml`。影刀淘宝登录。账号填完要和输入框读回值一致，否则抛「当前输入框内容和实际账号不相等，请重新运行该指令」。
- `taobao_mini_login`：迷你登录框，地址带 `style=minisimple`，回跳 `https://myseller.taobao.com/home.htm#/index`。填失败文案是「输入失败，请手动登录」。

两者的拼图都走云码阿里滑块类型 `20226`，距离 `(识别值 - 24 - 10) / 320 * 320`，拖动 `div.button`。NC 条 `#nc_1_n1z` 按轨道宽度拖到底，不请求云码。短信按钮 `#J_GetCode` 在完整登录里抛 `NeedsHumanError("登录需要短信验证，请手动完成短信验证登录")`。

源码里曾经出现的默认账号没有抄进本仓库。

## 目录与文件说明

- `__init__.py`：包标记。
- `taobao_login_pw.py`：公开函数 `taobao_login`、`login`、`main`。私有函数 `_fill_exact`、`_nc`、`_puzzle`。
- `taobao_mini_login_pw.py`：公开函数 `taobao_mini_login`、`login`、`main`。私有函数 `_exact`、`_nc`、`_puzzle`。`retries` 默认 3。
- `helpers.py`：`open_page`、`finish`、`mouse_drag`。
- `captcha.py`：`ali_slider_payload`（类型 `20226`）。本入口不调用文件里的其他识别函数。

## 实现逻辑

### `taobao_login`

环境变量 `TAOBAO_ACCOUNT`、`TAOBAO_PASSWORD`、`YUNMA_TOKEN`。账号或密码不是字符串时抛 `ValueError`（类型错误文案）。空字符串仍会进入页面流程；公开函数在两者都空时先抛缺账号的 `ValueError`。

1. 打开登录 URL。
2. 「使用其他帐户登录」「密码登录」可见则点击（「帐户」用源码里的字形）。
3. `_fill_exact` 填 `#fm-login-id`。
4. `#captcha-question` 可见则云码 `20226` 并拖动。
5. 点击密码框。`div.nc_scale` 可见则拖 NC。
6. 同样方式填 `#fm-login-password`，勾选协议（可见才点），点 `button.password-login`。
7. 最多 3 轮：NC 或拼图再处理并重新点登录；`.login-error-msg` 有文字则 `CredentialsRejected`；`#J_GetCode` 则短信人工。登录按钮消失视为成功。3 轮后按钮还在则「登录失败，请手动登录」。

### `taobao_mini_login`

环境变量 `TAOBAO_MINI_ACCOUNT`、`TAOBAO_MINI_PASSWORD`、`YUNMA_TOKEN`，重试 `TAOBAO_MINI_RETRIES`（默认 3）。

打开迷你 URL。`_exact` 填 `#fm-login-id`，读回不一致抛「输入失败，请手动登录」。点击密码框后，若 `#captcha-question` 可见则尝试云码拼图，异常被吃掉。再填密码。`span.nc-lang-cnt` 可见则拖 NC。点击 `button.password-login, button.fm-submit`。登录后 NC 再拖一次；拼图仍在则按 `retries`（默认 3）重试，单次异常同样被吃掉。函数不检查短信按钮。

## 依赖与环境

- Playwright `>=1.40`，Pillow。
- 环境变量见上。可选 `SELLER_HTTP_PROXY`。两个入口都是有头。
- 拷贝整个 `platforms/taobao/`。

## 调用方法

```python
from platforms.taobao.taobao_login_pw import taobao_login
from platforms.taobao.taobao_mini_login_pw import taobao_mini_login
from platforms.taobao.helpers import close_result

full = taobao_login()
print(full.ok, full.error, full.yunma_calls)
close_result(full)

mini = taobao_mini_login(retries=3)
close_result(mini)
```

返回 `SellerLoginResult`。短信得到 `ok=False`。`page=` 可传入已有页面。

## 注意事项

- 完整登录要求输入框读回值与账号完全一致，输入法或自动填充干扰会导致 `INPUT_FAIL`。
- 拼图距离公式和千牛相同，但截图只截 `#captcha-question`，不拼接提示图和背景图。
- NC 是整段拖动。`span.nc-lang-cnt` 用来判断轨道还在。
- 迷你登录和完整登录的环境变量前缀不同，不要混用。
- 不要把账号、密码、token 写进仓库。

## 测试

`tests/test_remaining_logins_pw.py` 核对两条 URL（迷你地址含 `style=minisimple` 和 `myseller.taobao.com`）、短信文案、`#J_GetCode`、迷你账号框 `#fm-login-id`。缺账号时期望 `ValueError`。阿里滑块类型 `20226` 在 `test_payloads_and_distances` 里通过京麦 `captcha.py` 断言。

```bash
pytest tests/test_remaining_logins_pw.py::test_login_urls tests/test_remaining_logins_pw.py::test_selectors_and_flags tests/test_remaining_logins_pw.py::test_missing_credentials -q
```
