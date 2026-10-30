# Cookie 保存 / 登录 / 退出

## 模块简介

这个目录移植影刀 Cookie 指令：保存登录信息、用文件恢复登录、退出。对应源码里的保存、登录、退出三个 process。

它不打开某个电商的登录页，也不读账号密码。所有函数都要求调用方传入已经存在的 Playwright `Page`。`page is None` 时 `require_page` 抛 `SellerLoginError("Cookie 操作需要已打开的 Playwright 页面")`。

`partition_key` 参数保留，与影刀 CEF 分区对应，但函数体把它丢掉。Playwright 没有 CEF partition。

## 目录与文件说明

- `__init__.py`：包标记。
- `cookie_login_pw.py`：公开函数见下。没有 `main`，不返回 `SellerLoginResult`。
- `helpers.py`：只使用其中的 `SellerLoginError`。本文件不调用 `open_page`。
- 没有 `captcha.py`。

公开函数：

- `extract_domain_from_url(url)`：用正则 `(?:://)(?:www\.)?([a-zA-Z0-9\-\.]+)(?=/)` 取域名。匹配不到返回 `None`。
- `cookie_expires(cookie)`：优先 `expires`；否则解析 `expirationDate`（把 `/` 换成 `-` 后 `fromisoformat`）。失败返回 `None`。
- `normalize_cookie(cookie)`：写入 `expires` 和 `sessionCookie`，删掉 `expirationDate`。
- `save_login_info(page, save_path="")`：导出当前 URL、context cookies、localStorage。`save_path` 非空时写入该文件。返回 JSON 文本。
- `logout(page, del_local_storage=False)`：`clear_cookies()`。`del_local_storage=True` 时再 `localStorage.clear()`。
- `login(page, cookie_file_path, add_local_storage=False)`：读 JSON，必要时先打开其中的 URL，清空 cookie，写回，再打开 URL。
- `save_cookies(page, save_path="", partition_key="")`：`process1` 包装，忽略 `partition_key`。
- `load_cookies(page, cookie_file_path, add_local_storage=False)`：`process2`。路径空则「Cookie文件路径为空」。
- `logout_cookies(page, del_local_storage=False)`：`process3`。

## 实现逻辑

保存：

1. 读 `page.url`、`page.context.cookies()`、整份 `localStorage`。
2. 每条 cookie 走 `normalize_cookie`。
3. JSON 形如 `{"url", "cookies", "local_storage"}`，`ensure_ascii=False`，缩进 4。

恢复：

1. 读文件。若当前 `window.origin` 不在保存的 URL 里，先 `goto` 该 URL（20 秒）。
2. `logout` 清空 cookie。
3. 只保留 Playwright 认识的字段：`name`、`value`、`domain`、`path`、`expires`、`httpOnly`、`secure`、`sameSite`、`url`。空 `expires` 会删掉。没有 `url` 也没有 `domain` 时，用保存的页面 URL。无名 cookie 跳过。
4. `add_cookies`。`add_local_storage=True` 时按键写回 localStorage。
5. 再 `goto` 保存的 URL。导航失败被忽略。

退出：清空 context cookie。可选清空 localStorage。源码按名字删除；这里用 `clear_cookies` 清掉全部，包括空名字。

## 依赖与环境

- Playwright `>=1.40`。无云码，无账号环境变量。
- 调用方自己持有 `Page`。本模块的 `create_browser` 不会被这些函数调用。
- 拷贝 `platforms/cookie/`。cookie 文件路径由调用方指定，不要把导出的 JSON 提交进仓库（里面有会话）。

## 调用方法

```python
from playwright.sync_api import sync_playwright
from platforms.cookie.cookie_login_pw import save_cookies, load_cookies, logout_cookies

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com/")
    text = save_cookies(page, save_path="/tmp/session.json", partition_key="ignored")
    logout_cookies(page, del_local_storage=True)
    load_cookies(page, "/tmp/session.json", add_local_storage=True)
    browser.close()
```

`save_cookies` 返回 JSON 字符串。`load_cookies` / `logout_cookies` 返回 `None`。

域名辅助：

```python
from platforms.cookie.cookie_login_pw import extract_domain_from_url
print(extract_domain_from_url("https://www.example.com/path"))
```

## 注意事项

- 必须先有页面。不要指望 `load_cookies()` 自己启动浏览器。
- `partition_key` 不生效。
- 导出文件含 cookie 和 localStorage，等同会话密钥，不要提交。
- 恢复时若 origin 已经包含在 URL 中，不会先跳转，直接在当前页清 cookie 再写回。
- `sameSite` 取值要符合 Playwright 要求，源码里的异常值可能导致 `add_cookies` 抛错。

## 测试

`tests/test_remaining_logins_pw.py` 的 `test_cookie_roundtrip` 在临时目录做保存、规范化过期时间和加载。不访问真实店铺。

```bash
pytest tests/test_remaining_logins_pw.py::test_cookie_roundtrip -q
```
