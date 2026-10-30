# Temu

## 模块简介

这个目录移植影刀 Temu 店铺相关指令（`activity_temu_shop`）：

| 函数 | 来源 | 作用 |
| --- | --- | --- |
| `temu_login` | `login.py` | 卖家中心 `https://seller.kuajingmaihuo.com/login` |
| `temu_ads_login` | `advertisement_login.py` | 广告 `https://ads.temu.com/login.html` |
| `temu_switch_store` | `switch_store.py` | 卖家中心点「切换」 |
| `temu_ads_switch_store` | `advertisement_switch_store.py` | 广告后台按店名点选，列表排除「半托管」 |

没有验证码识别。店铺名为空时，两个切换函数抛 `ValueError`，文案含「目标店铺名称不能为空或非文本」。

## 目录与文件说明

- `__init__.py`：包标记。
- `temu_login_pw.py`：公开函数 `temu_login`、`login`。环境变量 `TEMU_ACCOUNT`、`TEMU_PASSWORD`、`TEMU_STORE`。
- `temu_ads_login_pw.py`：公开函数 `temu_ads_login`、`login`。环境变量 `TEMU_ADS_ACCOUNT`、`TEMU_ADS_PASSWORD`。常量 `NO_PERMISSION` 写在文件里，`login` 没有读取它。
- `temu_switch_store_pw.py`：公开函数 `temu_switch_store`、`temu_ads_switch_store`、`switch_seller`、`switch_ads`。
- `helpers.py`：`open_page`、`finish`、`SellerLoginResult`。
- 没有 `captcha.py`。

## 实现逻辑

### 卖家登录 `temu_login`

1. 当前 URL 不是以登录地址开头时，打开 `https://seller.kuajingmaihuo.com/login`。
2. 「手机号登录」可见则点击。
3. 填 placeholder「请输入手机号」「请输入密码」，点「登录」。
4. 「我已阅读并同意以上协议」可见则点击。「确认切换」可见则点击。
5. `target_store`（或 `TEMU_STORE`）非空时，去掉其中空白。若「切换」可见，只点击一次「切换」。函数不会在列表里按店名查找。

### 广告登录 `temu_ads_login`

1. 打开 `https://ads.temu.com/login.html`。
2. 点「登录」，再点「请选择你的登录方式」后面第二个区块里的「登录」（跨境入口 xpath `XPATH_CROSS`）。
3. 填「手机号码」「密码」，点「授权登录」。
4. 点击后 URL 仍含登录地址则抛 `SellerLoginError`，文案是「{账号} 账号登录可能失败，请检查页面是否包含弹窗」。账号会进异常字符串，请不要把真实账号打进日志仓库。

### 卖家切店 `temu_switch_store`

`store_name` 必须是非空字符串（去掉空白后仍要有内容），否则 `ValueError`。然后若页面上有「切换」就点第一次出现的那个。店名本身不参与查找。

### 广告切店 `temu_ads_switch_store`

店名为空抛 `ValueError`。环境变量是 `TEMU_ADS_STORE`。

1. 顶栏 xpath `XPATH_ADS_CURRENT` 的文字已经等于店名则返回。
2. 没有「切换」但顶栏有当前店时，点当前店；「切换」恰好一个时点「切换」。
3. 在 `XPATH_ADS_STORES` 里找文字相等的 `span`。该 xpath 排除文本为「半托管」的节点。找到就点击。找不到则安静返回，不另抛「未找到」。

## 依赖与环境

- Playwright `>=1.40`。无云码。
- `TEMU_ACCOUNT`、`TEMU_PASSWORD`、`TEMU_STORE`、`TEMU_ADS_ACCOUNT`、`TEMU_ADS_PASSWORD`、`TEMU_ADS_STORE`。可选 `SELLER_HTTP_PROXY`。
- 拷贝整个 `platforms/temu/`。四个入口都是有头。卖家登录和广告登录没有 `main`。

## 调用方法

```python
from platforms.temu.temu_login_pw import temu_login
from platforms.temu.temu_ads_login_pw import temu_ads_login
from platforms.temu.temu_switch_store_pw import temu_switch_store, temu_ads_switch_store
from platforms.temu.helpers import close_result

result = temu_login(target_store=None)  # None 时读 TEMU_STORE
print(result.ok, result.error)
close_result(result)

ads = temu_ads_login()
close_result(ads)

# 需要已打开的卖家页时传入 page
switched = temu_switch_store(store_name="店铺名", page=result.web_page)
close_result(switched)

ads_switched = temu_ads_switch_store(store_name="店铺名", page=ads.web_page)
close_result(ads_switched)
```

返回 `SellerLoginResult`。缺登录账号抛 `ValueError`。切店的空名称也是 `ValueError`，发生在 `finish` 里面的 `switch_*` 中，因此 `OnError.TERMINATE` 时会变成 `SellerLoginError`。

## 注意事项

- 卖家登录里的 `target_store` 和 `temu_switch_store` 都只点击「切换」，不按名称点具体店铺。按名称点选只在 `temu_ads_switch_store`。
- 广告店铺列表排除「半托管」。
- `NO_PERMISSION` 常量当前没有被 `temu_ads_login` 抛出。
- 登录失败异常会带上账号字符串。实机日志不要提交。
- 不要把手机号和密码写进仓库。

## 测试

`tests/test_login_ext_pw.py` 的 `test_collection_logins` 核对卖家 URL、广告 URL，以及广告店铺 xpath 含「半托管」。`test_tax_and_crossborder_guards` 检查缺账号，以及空店铺名。

```bash
pytest tests/test_login_ext_pw.py::test_collection_logins tests/test_login_ext_pw.py::test_tax_and_crossborder_guards -q
```
