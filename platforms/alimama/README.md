# 阿里妈妈

## 模块简介

这个目录有两个不同的登录，不要混用：

- `alimama_login`：阿里妈妈数智，`https://www.alimama.com/index.htm`。环境变量 `ALIMAMA_ACCOUNT`、`ALIMAMA_PASSWORD`。短信按钮 `#J_GetCode` 出现时先点击，再抛 `NeedsHumanError("需要进行短信验证！")`。
- `alimama_platform_login`：影刀「阿里妈妈_平台登录」`activity_d91a274e/process6.py`。按平台名打开六个广告后台之一，再填淘宝登录框。环境变量 `ALIMAMA_PLATFORM_ACCOUNT`、`ALIMAMA_PLATFORM_PASSWORD`、`ALIMAMA_PLATFORM`。

平台登录支持的名称和地址写在 `PLATFORM_URLS`：

- 引力魔方 `https://tuijian.taobao.com/indexbp.html`
- 直通车 `https://subway.simba.taobao.com/index.jsp`
- 万象台 `https://adbrain.taobao.com/indexbp.html`
- 超级钻展 `https://zuanshi.taobao.com/index_poquan.jsp`
- 品销宝 `https://branding.taobao.com/index.action`
- 商家中心 `https://ad.alimama.com/portal/v2/report/promotionDataPage.htm`

其他名称抛 `SellerLoginError`，文案以「当前版本指令仅支持以下六个平台」开头。账号或密码为空抛「账户或密码为空，请检查~」。

两个入口都不调用云码。NC 滑块是按元素宽度拖动。

## 目录与文件说明

- `__init__.py`：包标记。
- `alimama_login_pw.py`：数智。公开函数 `alimama_login`、`login`、`main`。`relogin` 默认 `False`。
- `alimama_platform_login_pw.py`：六平台。公开函数 `alimama_platform_login`、`login`。没有 `main`。`DRAG_RELEASE_X = 50`。
- `helpers.py`：`open_page`、`mouse_drag`、`finish`、`NeedsHumanError`。
- 没有 `captcha.py`。

## 实现逻辑

### 数智 `alimama_login`

1. 打开首页，超时 120 秒。
2. `//*[@id="app"]//*[text()="退出"]` 可见：`relogin=False` 直接返回；为真则点退出并 reload。
3. 「立即登录」可见则点击。
4. 等到 `iframe` 的 src 含 `login.taobao.com`，然后 `goto` 这个 src（离开阿里妈妈首页，进入淘宝登录页）。
5. 填 `#fm-login-id`。若 `#header-info` 里已有「退出」，返回。
6. 填 `#fm-login-password`，点「登录」。
7. `iframe#baxia-dialog-content` 可见时，从滑块中心拖到 `x + 10 + 320`、`y - 20`，再点一次登录。
8. `#J_GetCode` 可见：点击后抛短信人工错误。

### 平台 `alimama_platform_login`

1. `platform` 必须是上面六个键之一。
2. 打开对应 URL。
3. `#fm-login-id` 可见时填账号密码。`#nc_1_n1z` 可见则从滑块中心拖到 `x + 滑块宽度 + 50`。
4. 点 `button.fm-submit, button.password-login`。
5. 账号框不可见时函数仍返回 `ok=True`（没有再检查是否已经处于登录态）。

## 依赖与环境

- Playwright `>=1.40`。不需要 `YUNMA_TOKEN`。
- 环境变量见模块简介。可选 `SELLER_HTTP_PROXY`。有头模式。
- 拷贝整个 `platforms/alimama/`。两个入口共用 `helpers.py`。

## 调用方法

```python
from platforms.alimama.alimama_login_pw import alimama_login
from platforms.alimama.alimama_platform_login_pw import alimama_platform_login
from platforms.alimama.helpers import close_result

shu = alimama_login(relogin=False)
print(shu.ok, shu.error)
close_result(shu)

ad = alimama_platform_login(platform="直通车")
print(ad.ok, ad.web_page.url if ad.web_page else None)
close_result(ad)
```

`platform=None` 时读 `ALIMAMA_PLATFORM`。返回 `SellerLoginResult`。

## 注意事项

- 数智登录会把页面导航到淘宝 iframe 的 src，后续选择器在顶层文档，不在阿里妈妈首页里。
- NC 拖动是固定像素（数智 `+330` 再上移 20；平台是滑块宽度再加 50），不识别缺口。
- 平台名必须和字典键完全一致，例如「直通车」而不是「淘宝直通车」。
- 短信只在数智流程里处理，平台流程没有 `#J_GetCode` 分支。
- 不要把账号密码写进仓库。

## 测试

`tests/test_remaining_logins_pw.py` 核对数智 URL `https://www.alimama.com/index.htm` 和短信文案，缺 `ALIMAMA_ACCOUNT` 时期望 `ValueError`。

`tests/test_login_ext_pw.py` 的 `test_collection_logins` 核对直通车和商家中心 URL。`test_tax_and_crossborder_guards` 在平台名为空时期望 `ValueError`。

```bash
pytest tests/test_remaining_logins_pw.py::test_login_urls tests/test_remaining_logins_pw.py::test_missing_credentials tests/test_login_ext_pw.py::test_collection_logins tests/test_login_ext_pw.py::test_tax_and_crossborder_guards -q
```
