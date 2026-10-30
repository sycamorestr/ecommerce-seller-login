# 紫鸟浏览器

## 模块简介

这个目录对应影刀「紫鸟登录」`super_browser/process1.py`。源码驱动 Windows 客户端「紫鸟浏览器专业版」，版本常量是 `V5` 和 `V6`，使用 win32 / UIA。源码没有网页登录地址。

`ziniao_login` 在任何参数下都抛出本目录 `helpers.DesktopOnlyLogin`，原因字符串是 `REASON`。这里没有 Playwright 打开页面的实现，以免编造一个不存在的网址。

## 目录与文件说明

- `__init__.py`：包标记。
- `ziniao_login_pw.py`：公开函数 `ziniao_login(*args, **kwargs)`。常量 `SOURCE`、`CLIENT_TITLE`、`VERSIONS`、`REASON`。没有 `main`。
- `helpers.py`：含 `DesktopOnlyLogin`（`SellerLoginError` 的子类）以及通用浏览器工具。本入口不调用 `open_page`。
- 没有 `captcha.py`。

## 实现逻辑

1. 调用 `ziniao_login`。
2. 函数立刻 `raise DesktopOnlyLogin(REASON)`。
3. 不启动浏览器，不读账号环境变量，不返回 `SellerLoginResult`。

`REASON` 全文：紫鸟登录驱动 Windows 客户端（win32 / UIA），源码没有网页登录地址。版本为 V5 或 V6。

## 依赖与环境

- 导入模块需要安装 Playwright（`helpers.py` 在导入时引用它），但本函数不会启动浏览器。
- 没有账号、密码、云码环境变量。
- 拷贝本目录只能得到这个明确的异常，不能在 Linux 上完成紫鸟登录。

## 调用方法

```python
from platforms.ziniao.ziniao_login_pw import ziniao_login
from platforms.ziniao.helpers import DesktopOnlyLogin

try:
    ziniao_login()
except DesktopOnlyLogin as exc:
    print(exc)
```

## 注意事项

- 不要给这个函数补一个网页 URL。影刀原文没有。
- 客户端标题是「紫鸟浏览器专业版」。版本只记录 `V5`、`V6`。
- 不要把紫鸟账号写进本目录。

## 测试

`tests/test_login_ext_pw.py` 的 `test_collection_logins` 期望 `ziniao_login()` 抛 `DesktopOnlyLogin`，并断言 `CLIENT_TITLE == "紫鸟浏览器专业版"`。异常类必须从 `platforms.ziniao.helpers` 导入，和测试一致。

```bash
pytest tests/test_login_ext_pw.py::test_collection_logins -q
```
