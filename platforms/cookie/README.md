# Cookie

影刀应用「cookie」主流程里的 7 条指令。网页对象是 Playwright `Page`。没有页面、且浏览器类型是 `chrome` 或 `edge` 时，通过 `platforms/web_get` 的 CDP 连接已打开的浏览器。

## 文件

- `cookie_login_pw.py`：7 条指令和 `visual_*` 包装。
- `helpers.py`：`SellerLoginError` 等，本目录自带。
- `example_main_flow.py`：按应用 main 的顺序调用（获取已打开网页 → 保存 → Cookie登录 → 获取指定 Cookie）。
- `__init__.py`：包标记。

## 影刀指令 → Python

| 影刀指令 | 函数 |
| --- | --- |
| Cookie登录 `cookie_login.process2` | `login` / `load_cookies` |
| 保存Cookie `cookie_login.process1` | `save_login_info` / `save_cookies` |
| Cookie退出登录 `cookie_login.process3` | `logout` / `logout_cookies` |
| 设置Cookie `xbot_visual.web.set_cookie` | `set_cookie` / `visual_set_cookie` |
| 获取筛选所有Cookie `get_cookies_v2` | `get_cookies_v2` / `visual_get_cookies_v2` |
| 获取指定Cookie信息 `get_cookie` | `get_cookie` / `visual_get_cookie` |
| 移除Cookie `remove_cookie` | `remove_cookie` / `visual_remove_cookie` |

`get_cookies` / `visual_get_cookies` 是旧版筛选（url 可空则不做网址筛选），保存 Cookie 内部会调用它。

## 实现逻辑

- 保存：用页面当前地址覆盖传入的 `url`。有地址时按该 URL 筛选 cookie；没有地址时取页面上下文里的全部。`partition_key` 非空时再取一次并追加。`expirationDate` 数字直接当 unix 秒；字符串按 UTC 解析（含 `Z` 和 `10/5/2026, 05:41:39`）。写出 `expires`、`sessionCookie`，去掉 `expirationDate`。localStorage 为空则存 `{}`。JSON `ensure_ascii=False`、缩进 4。
- Cookie登录：`window.origin` 不在文件里的 url 中就先打开该 url。然后按名称逐个 `remove_cookie`（空名称跳过），再 `set_cookie`。`sessionCookie=True` 不写过期时间；`False` 时 `expires` 是从现在起的秒数（文件里的绝对时间戳会原样传给这个参数，与 `_core.login` 的 `**cookie` 一致）。`添加本地存储` 默认关。最后再打开 url，失败忽略。
- 退出：删除每个非空名称的 cookie。`删除本地存储` 默认关。
- 设置：`url_type=auto` 用网页对象地址，`manual` 用传入 url。默认会话 Cookie、HttpOnly 关、Secure 关、有效期 100 秒。
- 筛选：`name` / `domain` / `path` / `url` / `partition_key` 空字符串忽略。`domain` 为完全相等或子域。`path` 完全相等。`url` 按域名、路径前缀、Secure 与协议是否匹配。`filter_secure` / `filter_session` 为假时不过滤；为真时 `secure` / `session` 的 True/False 才生效。返回键含 `expirationDate`、`name`、`value`、`domain`、`path`、`httpOnly`、`secure`。
- 指定 Cookie：同一套筛选，返回第一条；没有则 `{}`。
- 移除：`appoint_cookie` 按 url + name；`all` / `all_cookie` 删掉该 url 下的 cookie，url 为空则清空 context。

## 调用方法

```python
from playwright.sync_api import sync_playwright
from platforms.cookie.cookie_login_pw import (
    get_cookie, get_cookies_v2, load_cookies, logout_cookies,
    remove_cookie, save_cookies, set_cookie,
)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_context().new_page()
    page.goto("https://example.com/")
    set_cookie("https://example.com/", page=page, name="sid", value="1", sessionCookie=False, expires=100)
    print(get_cookies_v2(page=page, name="sid"))
    print(get_cookie("https://example.com/", page=page, name="sid"))
    text = save_cookies(page, "/tmp/cookies.json")
    load_cookies(page, "/tmp/cookies.json", add_local_storage=False)
    remove_cookie("https://example.com/", "sid", page=page, remove_type="appoint_cookie")
    logout_cookies(page, del_local_storage=False)
    browser.close()
```

已打开的 Chrome：`get_cookies_v2(mode="chrome", cdp_url="http://127.0.0.1:9222", url="https://example.com/")`。

应用主流程示例：`python -m platforms.cookie.example_main_flow --cdp-url http://127.0.0.1:9222 --cookie-file /tmp/cookies.json`。

## 注意事项

- `cef` / `ie` / `firefox` / `360se` / `auto` 在没有 Page 时不支持，需已打开的 Playwright 页面，或 `chrome`/`edge` 的 CDP。
- Playwright 读出的 cookie 通常没有 `partitionKey`。传入 `partition_key` 时只保留带该字段且相等的项。
- 不要把 cookie 文件提交进仓库。
- 保存路径为空时只返回 JSON 字符串，不写文件。

## 测试

```bash
pytest tests/test_cookie_app_pw.py tests/test_remaining_logins_pw.py::test_cookie_roundtrip -q
```
