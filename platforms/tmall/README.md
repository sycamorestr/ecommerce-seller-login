# 天猫超市

## 模块简介

这个目录移植影刀「天猫超市登录」`activity_7bca6d/login_tmall_supermarket.py`。

登录地址 `https://web.txcs.tmall.com/login?from=https%3A%2F%2Fweb.txcs.tmall.com%2F`。表单在 `iframe#alibaba-login-box`。

NC 滑块 `#nc_1_n1z` 可见时不拖动，抛 `NeedsHumanError("天猫超市登录需要人工完成页面验证")`。

供应商按完整选项文本精确匹配。多个相同文本或零个匹配都会抛 `ValueError`。

## 目录与文件说明

- `__init__.py`：包标记。
- `tmall_supermarket_login_pw.py`：公开函数 `tmall_supermarket_login`、`login`、`main`，以及纯函数 `supplier_name`、`match_supplier`、`verify_supplier`、`verify_identity`。`_backend` 判断 URL 是否已经离开登录、退出和 `basic_login_proxy`。`login` 本身不调用 `verify_supplier`、`verify_identity`、`_backend`，也不点击 `button.login-button` 或读取 `span.current-supplier-name`。
- `helpers.py`：`open_page`、`fill_checked`、`finish`、`NeedsHumanError`。
- 没有 `captcha.py`。

## 实现逻辑

`tmall_supermarket_login` 在调用 `finish` 之前检查账号、密码、店铺名类型，避免 `ValueError` 被包成 `SellerLoginError`。

环境变量：`TMALL_SUPERMARKET_ACCOUNT`、`TMALL_SUPERMARKET_PASSWORD`、`TMALL_SUPERMARKET_SHOP`。

1. 账号或密码不是非空文本：`ValueError`（「登录账号必须填写非空文本。」或密码那句）。
2. `shop_name` 不是字符串：`ValueError("店铺名须为文本；留空时默认选择第一条可见店铺。")`。这句是源码文案。当前 `login` 在店铺名为空字符串时不会去点第一条 `li.menu-item`。
3. 有头打开登录 URL。
4. 在登录 iframe 里等 `#fm-login-id`（60 秒），填写账号（去掉首尾空白）和 `#fm-login-password`，点 `button.password-login`。
5. iframe 内 `#nc_1_n1z` 可见：人工验证。
6. `.login-error-msg` 有文字：`SellerLoginError("账号登录失败，请检查账号、密码或页面验证提示。")`。页面原文不放进异常。
7. `shop_name` 非空时，读取页面上（iframe 外）全部 `li.menu-item` 的文字。列表非空则 `match_supplier`：
   - `supplier_name` 只在「 -- 」处切开，取前半，供 `verify_supplier` 使用。`match_supplier` 比较的是整段 label 与传入店铺名是否相等。
   - 没有相等项：「未找到精确匹配的二级供应商，请填写完整店铺名或完整选项文本。」
   - 多于一项：「完整店铺名对应多个业务身份，请填写含业务类型后缀的完整选项文本。」
   - 恰好一项：点击该项。
8. 列表为空则跳过点击，仍然返回。

`verify_supplier(actual, requested)`：`actual` 必须等于 `supplier_name(requested)`，否则「后台当前店铺与指定店铺不一致…」。

`verify_identity(active, requested)`：去掉 `active` 开头的数字和横线后，要等于「店名」或「店名-业务类型」。否则「后台当前业务身份与指定的完整二级供应商名称不一致…」。

## 依赖与环境

- Playwright `>=1.40`。无云码。
- 上面三个环境变量。可选 `SELLER_HTTP_PROXY`。
- 拷贝整个 `platforms/tmall/`。有头模式。

## 调用方法

```python
from platforms.tmall.tmall_supermarket_login_pw import (
    tmall_supermarket_login,
    match_supplier,
    supplier_name,
)
from platforms.tmall.helpers import close_result

print(supplier_name("店铺 -- 经销"))
print(match_supplier(["甲 -- 经销", "乙 -- 代销"], "乙 -- 代销"))

result = tmall_supermarket_login(shop_name=None)  # None 时读 TMALL_SUPERMARKET_SHOP
print(result.ok, result.error)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)
```

返回 `SellerLoginResult`。NC 滑块得到 `ok=False`。缺账号是 `ValueError`。

## 注意事项

- 供应商匹配是整段文本相等，不是只比「 -- 」前面的店名。要选「甲 -- 经销」就传入这整段。
- 空店铺名不会自动点第一项，尽管错误文案里写了「留空时默认选择第一条可见店铺」。
- `verify_supplier` / `verify_identity` 需要调用方在登录后自己调用，登录函数不会做这一步。
- NC 不自动拖。不要改成云码滑块，源码要求人工。
- 不要把账号、密码、供应商名称样本里的真实店铺写进仓库。测试用的是「甲」「乙」。

## 测试

`tests/test_remaining_logins_pw.py` 的 `test_tmall_supplier_rules` 覆盖 `supplier_name`、精确匹配、找不到、重复项、`verify_supplier`、`verify_identity`。`test_login_urls` 要求 URL 以天猫超市登录地址开头。缺账号时期望 `ValueError`。

```bash
pytest tests/test_remaining_logins_pw.py::test_tmall_supplier_rules -q
```
