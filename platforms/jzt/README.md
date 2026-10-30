# 京准通

## 模块简介

这个目录移植影刀「京东登录-京准通」。先登录 `https://jzt.jd.com/gw/index`，成功后再按平台名打开对应后台。滑块是云码 `22222`，拖动 `div.JDJRV-slide-btn`。

短信 xpath `//*[text()="使用 手机短信验证码"]` 出现时抛 `NeedsHumanError("需要进行短信验证码，请手动通过！")`。登录后仍看不到「立即投放」则抛「登录失败，请联系运维人员进行维护。」

## 目录与文件说明

- `__init__.py`：包标记。
- `jzt_login_pw.py`：公开函数 `jzt_login`、`login`、`platform_url`、`main`。私有函数 `_slider`。常量 `PLATFORM_URLS`、`HOME_B`、`SMS_MESSAGE`、`FAIL`。
- `helpers.py`：`open_page`、`finish`、`SellerLoginResult`。
- `captcha.py`：本入口用标准滑块请求体和 `std_slider_distance`（偏移 0，速度 1）。

`PLATFORM_URLS` 的键：京挑客、京准通、京准通-账户中心、商智-品牌版、商智-商家版、京东快车、京东联盟、推荐广告、互动广告、站外广告、站外广告-账户中心、智能投放。具体 URL 以 `jzt_login_pw.py` 里的字典为准。

## 实现逻辑

`jzt_login` 读取 `JZT_ACCOUNT`、`JZT_PASSWORD`、`YUNMA_TOKEN`、`JZT_PLATFORM`。`relogin` 默认 `True`。缺账号或密码抛 `ValueError`。

1. 打开 `LOGIN_URL`，超时 120 秒，最多 4 次，再等 3 秒。
2. 「立即投放」可见表示已登录。`relogin=True` 时最多 5 次点「退出登录」。`relogin=False` 时直接返回。
3. 最多 10 次：登录表单或账号框出现就停；否则点文本「 登录 」（两侧有空格，与源码 xpath 一致）。
4. 填账号（`placeholder="账号名/手机号/邮箱"` 或 `#loginname`）和密码（`#nloginpwd`），点 `#loginsubmit` 或 `button.login-btn`。
5. 最多 5 次拖标准滑块。
6. 若落到 `https://b.jd.com/`，再打开京准通首页。
7. `div.msg-error` 有文字则 `CredentialsRejected`。短信入口可见则人工。没有「立即投放」则 `SellerLoginError(FAIL)`。
8. `platform_url(platform)` 非空才 `goto` 该地址。空字符串或未知名称都不跳转。

## 依赖与环境

- Playwright `>=1.40`，Pillow。
- `JZT_ACCOUNT`、`JZT_PASSWORD`、`YUNMA_TOKEN`、可选 `JZT_PLATFORM`、`SELLER_HTTP_PROXY`。
- 拷贝整个 `platforms/jzt/`。有头模式。

## 调用方法

```python
from platforms.jzt.jzt_login_pw import jzt_login, platform_url
from platforms.jzt.helpers import close_result

print(platform_url("京东快车"))

result = jzt_login(platform="京准通", relogin=True)
print(result.ok, result.error, result.yunma_calls)
if result.web_page is not None:
    print(result.web_page.url)
close_result(result)
```

`platform=None` 时读 `JZT_PLATFORM`。返回 `SellerLoginResult`。

## 注意事项

- 「 登录 」xpath 含首尾空格，改成 `text()="登录"` 会和源码不一致。
- 未知平台名不跳转。
- 短信不自动填。滑块要 `YUNMA_TOKEN`。
- 不要把账号和 token 写进仓库。

## 测试

`tests/test_remaining_logins_pw.py` 的 `test_jzt_platform_map` 断言京东快车 URL、商智商家版为 `https://sz.jd.com`。`test_login_urls` 核对网关地址。缺账号时期望 `ValueError`。

```bash
pytest tests/test_remaining_logins_pw.py::test_jzt_platform_map tests/test_remaining_logins_pw.py::test_login_urls -q
```
