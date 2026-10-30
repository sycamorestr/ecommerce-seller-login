# 抖店

## 模块简介

这个目录放抖店单店登录、多店登录和店铺切换，对应影刀：

- 单店登录：`activity_7bca6d` 的抖店登录，以及滑块 `process48`（内部 `process45` 抖音滑块、`process44` 文字点选）和邮箱验证 `process49`。
- 多店登录：`activity_966451c9/process1.py`。先走单店登录，店铺名非空再切店。
- 按名称切换：公开块 `process13.py` 调用 `process17.py`（新）。
- 按 ID 切换：公开块 `process35.py` 调用 `process36.py`（新）。
- `process37.py` 是售后时间筛选，不是切店。常量 `PROCESS37_NOTE` 说明这一点，本目录没有它的入口。

登录 URL：`https://fxg.jinritemai.com/login/common`。多店列表：`https://fxg.jinritemai.com/ffa/multiShop`。

抖音滑块云码类型 `"20225"`。文字点选类型在影刀里是图鉴 `27`，但 HTTP 主机不在源码里（走 `web_service.captcha`）。未提供 `click_recognizer` 时，点选验证码变成 `NeedsHumanError`。

巨量引擎的 `oceanengine_login`、邮箱登录、纵横登录会 import 本目录的 `verify_platform` / `verify_email`。把 `platforms/oceanengine/` 拷走时要带上本目录。

## 目录与文件说明

- `__init__.py`：包标记。
- `doudian_login_pw.py`：单店登录。公开函数 `doudian_login`、`login`、`verify_platform`、`verify_email`、`main`。私有函数 `_solve_dy_slider`、`_solve_click`、`_frame`、`_iframe_slider`。
- `doudian_multi_login_pw.py`：只导出 `doudian_multi_login`。它调用同目录的 `doudian_login` 和 `doudian_switch_shop`。
- `doudian_switch_shop_pw.py`：公开函数 `doudian_switch_shop`、`switch_by_name`、`switch_by_id`。`_ensure` 保证页面在 `fxg.jinritemai.com`。
- `helpers.py`：`open_page`、`finish`、`SellerLoginResult`、`NeedsHumanError`、`mouse_drag`。
- `captcha.py`：`dy_slider_payload`、`dy_slider_distance`、`parse_click_positions`、`click_points_from_origin`、`extract_email_code`。

## 实现逻辑

### 单店 `doudian_login`

参数：`account`、`password`、`yunma_token`，以及 `mailbox`、`auth_code`、`email_code`、`retries`（默认 10）、`logout_existing`、`click_recognizer`、`on_error`、`page`。

环境变量：`DOUDIAN_ACCOUNT`、`DOUDIAN_PASSWORD`、`YUNMA_TOKEN`、`DOUDIAN_EMAIL`、`DOUDIAN_EMAIL_AUTH`、`DOUDIAN_EMAIL_CODE`。

1. 打开 `LOGIN_URL`，最多 3 次。
2. `logout_existing=True` 且页头 `headerShopName` 可见时，点店铺名再点「退出」，失败文案「退出已登录失败，检查是否有弹窗出现」。
3. 有返回条 `div[class*='backbar']` 就点掉。没有「邮箱登录」时先点 `login-switcher`，再点邮箱 tab。
4. 填邮箱和密码，勾选 `input.auxo-checkbox-input`，点 `button.account-center-action-button`。
5. `verify_platform`：iframe 里的滑块用类型 `"20225"` 算距离再拖；点选框出现时调用 `click_recognizer`。没有识别函数则 `NeedsHumanError`。多次失败的文案常量是「验证码识别失败，需人工确认！」（多店模块也保留了这句）。
6. 需要邮箱验证时，`verify_email` 用 `mailbox` / `auth_code` / `email_code`。缺邮箱或授权码抛「需要进行邮箱验证， 请正确填写【验证邮箱】和【授权码】后重试！」（逗号后有一个空格，与源码一致）。验证码用 `captcha.extract_email_code` 从文本里取 6 位数字；没有可用验证码则 `NeedsHumanError`。本模块不连邮箱服务器。
7. 出现「进入店铺」时点第一个。

### 多店 `doudian_multi_login`

先 `doudian_login`。`result.ok` 为假，或 `DOUDIAN_SHOP` / `shop_name` 为空，就直接返回登录结果。否则用同一 `web_page` 调用 `doudian_switch_shop(shop_name=...)`。

### 切店 `doudian_switch_shop`

同时看 `shop_id` 和 `shop_name`。`shop_id` 非空（参数或 `DOUDIAN_SHOP_ID`）走 `switch_by_id`，否则走 `switch_by_name`（`DOUDIAN_SHOP`）。

按名称：

- 页头 `//div[contains(@class, "headerShopName")]` 的文字已经等于目标名，直接返回。
- 打开 `https://fxg.jinritemai.com/ffa/multiShop`，在 `index_roleItem` 里找 `index_introName`。
- 店铺名是纯数字时当成列表下标。下标 `>=` 店铺数量抛「抖店店铺切换：您提供的索引大于店铺总数量，无法选择店铺 ~」。
- 名称对不上抛「未找到目标店铺（{name}）」。

按 ID：

- 当前页 `//div[@label="店铺ID"]` 的 `value` 已经等于目标 ID，直接返回。
- 否则在角色卡片全文里查找包含该 ID 的一项并点击。
- 找不到抛「未找到目标店铺ID（{name}）」。点完若读到的 ID 与目标不同，抛「当前店铺与目标店铺不同，请检查店铺ID」。

## 依赖与环境

- Playwright `>=1.40`。滑块截图用 Pillow。
- 环境变量见上一节。可选 `SELLER_HTTP_PROXY`。三个入口都是有头 Chromium。
- 拷贝整个 `platforms/doudian/`。不要只拷其中一个 py 文件：多店依赖单店和切店，滑块依赖 `captcha.py`。
- 巨量引擎目录反过来依赖这里的 `verify_platform` 和 `verify_email`。

## 调用方法

```python
from platforms.doudian.doudian_login_pw import doudian_login
from platforms.doudian.doudian_multi_login_pw import doudian_multi_login
from platforms.doudian.doudian_switch_shop_pw import doudian_switch_shop
from platforms.doudian.helpers import close_result, OnError

result = doudian_login(retries=10, logout_existing=False)
print(result.ok, result.error, result.yunma_calls)
close_result(result)

multi = doudian_multi_login()  # shop_name 为 None 时读取 DOUDIAN_SHOP
close_result(multi)

switched = doudian_switch_shop(shop_id=None, shop_name=None, on_error=OnError.TERMINATE)
close_result(switched)
```

`shop_name=None` 且 `shop_id=None` 时，切店函数自己读环境变量；`shop_id` 有值就按 ID。返回 `SellerLoginResult`。

点选识别函数签名是 `click_recognizer(image_base64) -> "x,y|x,y"`，传给 `doudian_login(..., click_recognizer=...)`。

## 注意事项

- 邮箱登录 tab、滑块按钮 `div.captcha-slider-btn`、店铺卡片 class（`index_roleItem`、`index_introName__...`）都会随抖店前端改版失效。
- 纯数字店铺名会被当成下标，不是店铺 ID。按 ID 请传 `shop_id` 或设置 `DOUDIAN_SHOP_ID`。
- 点选没有内置图鉴 HTTP。不传 `click_recognizer` 就会停在人工。
- 邮箱验证码不自动拉信。把验证码放在 `DOUDIAN_EMAIL_CODE`，或准备好人工处理 `NeedsHumanError`。
- `process37.py` 不要当成切店调用。
- 账号、授权码、云码 token 只放环境变量。

## 测试

`tests/test_login_ext_pw.py` 的 `test_doudian_ops_constants` 检查多店 URL、`process17` / `process36`、`process37` 说明、页头 xpath 和店铺 ID xpath。

单店登录函数没有单独的浏览器测试。缺账号用例在多店所依赖的环境上，由调用方在跑 `doudian_login()` 时触发 `ValueError`；现有测试文件没有直接调用 `doudian_login()`。

```bash
pytest tests/test_login_ext_pw.py::test_doudian_ops_constants -q
```
