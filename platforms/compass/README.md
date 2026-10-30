# 电商罗盘

## 模块简介

这个目录有两个罗盘登录，滑块都是抖音云码类型 `"20225"`（`dy_slider_payload` / `dy_slider_distance`）：

- `compass_login`：电商罗盘，`https://compass.jinritemai.com/login`。店铺页标记 `compass.jinritemai.com/shop`。已登录文案「当前账号已经登录，不必再重新登录」。
- `compass_strategy_login`：罗盘策略，`https://compassbrand.jinritemai.com/login`。舱页标记 `compassbrand.jinritemai.com/cabin`。影刀 `activity_7bca6d/process59.py`。

策略登录复用罗盘登录里的表单选择器和 `_slider`，自己的选择器是角标 `span.user-info` 和返回条 `div.index_backbar__3dcm0`。

组织列表 xpath：`//div[text()='请选择组织']/following-sibling::div//div[@class='index_introName__2tsRs']`。class 带哈希，改版后会失效。

## 目录与文件说明

- `__init__.py`：包标记。
- `compass_login_pw.py`：公开函数 `compass_login`、`login`、`main`。私有函数 `_slider`、`_pick_shop`。
- `compass_strategy_login_pw.py`：公开函数 `compass_strategy_login`、`login`、`main`。滑块函数从罗盘模块 import，文件顶部的 `import captcha` 在本文件函数体里没有再使用。
- `helpers.py`：`open_page`、`finish`、`SellerLoginResult`。
- `captcha.py`：抖音滑块请求体。`_slider` 实际 import 的是这份。

## 实现逻辑

### `compass_login`

环境变量 `COMPASS_ACCOUNT`、`COMPASS_PASSWORD`、`YUNMA_TOKEN`、`COMPASS_SHOP`。`relogin` 默认 `False`。`wait_time` 只在内部 `login` 里，默认 3 秒，公开函数没有把它暴露成参数。

1. 打开登录 URL。地址里没有 `compass.jinritemai.com/shop` 时再打开一次。
2. `div.index_name__xx5yj`（商家入口）可见则等待后点击。
3. `relogin=True`：最多 8 次点页头用户名，再点下拉第一项。`relogin=False` 且用户名已可见：直接返回。
4. 没有邮箱 tab 时点 `div.login-switcher--cell`（点击位置偏移 3,3）。若「发送验证码」还在，改点邮箱 tab，最多 5 次。
5. 填 `input[placeholder="请输入邮箱"].ace-input` 和密码，勾选 `input.ecom-checkbox-input`，点登录按钮。
6. 最多 5 次等滑块图 `img.captcha-verify-image`，悬停拖动钮后 `_slider`。
7. `_pick_shop`：有 `shop_name` 时按组织卡片第一行文字精确匹配；为空则点第一张卡片。

### `compass_strategy_login`

环境变量 `COMPASS_STRATEGY_ACCOUNT`、`COMPASS_STRATEGY_PASSWORD`、`YUNMA_TOKEN`、`COMPASS_STRATEGY_SHOP`。

1. 地址为空、`about:blank`，或不含 cabin 标记时，打开策略登录 URL，最多 4 次。
2. `relogin=True` 时点角标或下拉里的第一项。`relogin=False` 且角标可见则直接返回。
3. 点 `div.index_backbar__3dcm0`，再点商家入口，切到邮箱（逻辑与罗盘相同，含「发送验证码」循环）。
4. 填表、登录、滑块，再按 `XPATH_SHOPS` 选组织。`shop_name` 为空时点第一项。

## 依赖与环境

- Playwright `>=1.40`，Pillow。
- 环境变量见上。可选 `SELLER_HTTP_PROXY`。有头模式。
- 策略模块依赖罗盘模块里的选择器和 `_slider`，请整目录拷贝。

## 调用方法

```python
from platforms.compass.compass_login_pw import compass_login
from platforms.compass.compass_strategy_login_pw import compass_strategy_login
from platforms.compass.helpers import close_result

shop = compass_login(shop_name=None, relogin=False)  # None 时读 COMPASS_SHOP
print(shop.ok, shop.error, shop.yunma_calls)
close_result(shop)

strategy = compass_strategy_login(relogin=False)
close_result(strategy)
```

返回 `SellerLoginResult`。缺账号抛 `ValueError`。滑块出现时 `require_yunma_token`。

## 注意事项

- `index_introName__2tsRs`、`index_name__xx5yj`、`index_backbar__3dcm0` 都是带哈希的 class。
- 店铺名为空时会点列表第一项，不是“跳过选择”。
- 已登录且 `relogin=False` 时不会退出，直接成功返回。
- 滑块类型与抖店相同，选择器是罗盘页上的 `captcha-verify-image`，不要和抖店 iframe 选择器混用。
- 不要提交账号和 token。

## 测试

`tests/test_remaining_logins_pw.py` 核对两条登录 URL、滑块图选择器、策略返回条 class。缺 `COMPASS_ACCOUNT` 或 `COMPASS_STRATEGY_ACCOUNT` 时期望 `ValueError`。

```bash
pytest tests/test_remaining_logins_pw.py::test_login_urls tests/test_remaining_logins_pw.py::test_selectors_and_flags tests/test_remaining_logins_pw.py::test_missing_credentials -q
```
