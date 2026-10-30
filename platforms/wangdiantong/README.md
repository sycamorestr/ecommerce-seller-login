# 旺店通

## 模块简介

这个目录对应影刀「登录旺店通」。源码是 Windows 客户端流程（`win32.element`），没有网页登录地址。

`wangdiantong_login` 直接抛出本目录 `helpers.DesktopOnlyLogin`。验证码参数仍记录在常量里：`CAPTCHA_TYPE = "3"`，`CAPTCHA_CODE = "ttshitu_3_predict"`。函数不会去请求图鉴。

## 目录与文件说明

- `__init__.py`：包标记。
- `wangdiantong_login_pw.py`：公开函数 `wangdiantong_login(*args, **kwargs)`。常量 `CAPTCHA_TYPE`、`CAPTCHA_CODE`、`REASON`。没有 `main`。
- `helpers.py`：`DesktopOnlyLogin` 定义在这里。本入口不调用 `open_page`。
- 没有 `captcha.py`。图鉴类型 `3` 的请求体在其他目录的 `captcha.py`（例如 `platforms/jingmai/captcha.py` 的 `TTSHITU_WANGDIANTONG_TYPE`）里，供离线测试核对，旺店通登录不调用它。

## 实现逻辑

调用 `wangdiantong_login` 即抛 `DesktopOnlyLogin`。`REASON` 说明：登录旺店通是 Windows 客户端流程（win32.element），源码没有网页登录地址，不能改写成 Playwright 打开页面。验证码参数仍是 captcha_type=3 / ttshitu_3_predict。

不返回 `SellerLoginResult`。

## 依赖与环境

- 导入需要 Playwright 已安装（`helpers.py` 的类型引用），函数不启动浏览器。
- 没有账号环境变量，也没有 `YUNMA_TOKEN`。
- 拷贝本目录不能在 Linux 上登录旺店通客户端。

## 调用方法

```python
from platforms.wangdiantong.wangdiantong_login_pw import wangdiantong_login, CAPTCHA_TYPE
from platforms.wangdiantong.helpers import DesktopOnlyLogin

assert CAPTCHA_TYPE == "3"
try:
    wangdiantong_login()
except DesktopOnlyLogin as exc:
    print(exc)
```

## 注意事项

- 不要补一个网页登录 URL。
- 图鉴类型 `3` 只作为常量保留。
- 不要把旺店通账号写进仓库。
- 和紫鸟一样属于桌面客户端。异常类在各自目录的 `helpers.py`，不要从别的目录 import 来 `pytest.raises`。

## 测试

`tests/test_remaining_logins_pw.py` 的 `test_wangdiantong_is_desktop_only` 期望 `DesktopOnlyLogin`。`test_docs_mentions_skipped` 要求 `docs/unported.md` 提到「登录旺店通」。`test_payloads_and_distances` 断言 `TTSHITU_WANGDIANTONG_TYPE == "3"`。

```bash
pytest tests/test_remaining_logins_pw.py::test_wangdiantong_is_desktop_only -q
```
