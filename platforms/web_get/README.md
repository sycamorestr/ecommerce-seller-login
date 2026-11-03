# 获取已打开的网页对象

影刀 `xbot_visual.web.get` → `xbot.web.get`，以及 `get_active`、`get_all`。

## 文件

- `web_get_pw.py`：`get`、`get_active`、`get_all`、`visual_get`、`visual_get_all`、`connect`、`close_connection`、`match_text`。
- `__init__.py`：包标记。

## 逻辑

`mode` 为 `chrome` 或 `edge` 时，用 `connect_over_cdp` 接上已经开着的浏览器（地址来自参数 `cdp_url`，否则环境变量 `WEB_GET_CDP_URL`）。遍历所有 context 的 page。

- 模糊匹配（`use_wildcard=False`）：子串，区分大小写。
- 通配符（`use_wildcard=True`）：`fnmatch` 的 `*` 和 `?`，区分大小写。
- `title` 与 `url` 同时传入时都要匹配。
- 多个命中时，`get` 返回 `performance.timeOrigin` 最大的那个（最新打开）。`get_all` 按打开时间从早到晚。
- `load_timeout > 0` 等待 `load`；`0` 不等待；`< 0` 一直等到 load。超时抛 `PageLoadTimeoutError`。`stop_if_timeout=True` 时先执行 `window.stop()`。
- 没有命中且 `open_page=True`：在最后一个 context 里打开 `page_url`，没有则用 `url`。
- `get_active`：`visibilityState === 'visible'` 且 `document.hasFocus()`。多个时取最新打开的。
- `visual_get`：`mode=url|title|activated`，`value` 是匹配串，`url` 是 `open_page` 时要打开的地址，`stop_load_if_load_timeout=stopLoad` 对应 `stop_if_timeout`，`wait_load_completed=False` 时 `load_timeout=0`。
- `visual_get_all`：`mode=all|url|title`。

`cef`、`ie`、`firefox`、`360se`、`auto` 抛 `UnsupportedModeError`。默认 `mode` 仍是源码里的 `cef`。

## 调用

```python
from platforms.web_get.web_get_pw import get, get_active, get_all, visual_get, close_connection

page = get(title="店铺", mode="chrome", cdp_url="http://127.0.0.1:9222", load_timeout=20)
active = get_active(mode="chrome", cdp_url="http://127.0.0.1:9222")
pages = get_all(mode="edge", url="https://example.com/", use_wildcard=True, cdp_url="http://127.0.0.1:9222")
same = visual_get(web_type="chrome", mode="title", value="店铺", cdp_url="http://127.0.0.1:9222")
close_connection("http://127.0.0.1:9222")
```

返回 Playwright `Page`。连接会留着，用完调用 `close_connection`。

## 注意

- 浏览器需要已带远程调试端口启动。本模块不负责拉起 Chrome/Edge，也不读取用户数据目录。
- `silent_running` 按源码保留，接到已打开的浏览器上时不会改静默状态。
- 无头 Chrome 里多个标签可能都报告 `hasFocus()`，这时 `get_active` 退回最新打开的可见页。
- `chrome` 与 `edge` 都走同一个 `cdp_url`，本模块不另找浏览器可执行文件。

## 测试

```bash
pytest tests/test_web_get_pw.py -q
```
