# 千牛登录

连接你指定的已有浏览器环境，在新标签页执行千牛登录。沿用该环境的 Cookie，程序结束或报错后，浏览器和标签页保持打开。

## 安装与运行

需要 Python 3.10+，以及已开启远程调试的 Edge、Chrome 等 Chromium 浏览器。从仓库根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item qianniu\config.example.json qianniu\config.json
```

只有第一次需要复制配置模板，已有 `config.json` 时直接编辑它。填写配置后运行：

```powershell
.\.venv\Scripts\python.exe qianniu\main.py
```

所有平台共用仓库根目录的 `.venv`。也可以把整个 `qianniu` 文件夹复制到自己的项目中，继续使用父目录的虚拟环境。千牛模块本身只需要 Playwright 和 Pillow，无需另外下载 Chromium。

## 配置

在 `config.json` 填写下面的字段；配置文件已被 Git 忽略。

| 字段 | 用途 |
| --- | --- |
| `cdp_url` | 已打开浏览器环境的调试地址，必须填写 |
| `account` | 千牛账号 |
| `password` | 千牛密码 |
| `yunma_token` | 云码 Token，可留空 |
| `retries` | 每轮验证码最多尝试次数，正整数，默认 `5` |

例如，调试端口为 `9222` 时，`cdp_url` 填写 `http://127.0.0.1:9222`。请使用浏览器环境提供的调试地址；它不是代理地址，也不是浏览器管理工具的网页地址。普通方式打开的浏览器通常没有调试端口。连接失败时程序直接报错。

如果进入千牛时直接跳转到后台，程序会跳过账号密码输入，沿用环境中已经登录的账号，请确认店铺。此时不会自动切换成配置中的另一个账号。短信等人工验证会显示提示，可在保留的浏览器窗口中继续操作。

普通滑块通过 Playwright 模拟鼠标拖动。只有图片验证码流程且填写了 Token 时，才会调用云码。截图与验证码临时图片保存在 `output/`，不提交到 Git。

## 文件和调试

```text
qianniu/
  main.py                # 读取配置、连接浏览器、调用登录
  login.py               # 登录步骤和结果
  captcha.py             # 普通滑块和图片验证码
  config.example.json    # 空白配置模板
  tests/                 # 离线测试
```

在 Cursor 中打开仓库根目录，按 F5 选择“千牛登录（连接已有浏览器）”；也可以单独打开 `qianniu` 文件夹，选择“千牛登录（读取 config.json）”。这两种方式都使用父目录共享的 `.venv`。

阅读顺序是 `main.py → login.py → captcha.py`。在 `main.py` 的 `config = load_config()` 行设置断点，F10 执行下一行，F11 进入函数。代码错误保留原始异常和行号，便于调试。

## 在其他代码中调用

下面的调用文件放在 `qianniu` 文件夹中，复用现有配置：

```python
from playwright.sync_api import sync_playwright
from main import load_config
from login import qianniu_login

config = load_config()
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(config["cdp_url"], no_defaults=True)
    page = browser.contexts[0].new_page()
    result = qianniu_login(
        page=page,
        account=config["account"],
        password=config["password"],
        yunma_token=config["yunma_token"],
        retries=config["retries"],
    )
    if result.ok:
        print("登录流程完成，请确认店铺")
        # 在这里继续用 page 操作网页。
    else:
        print(result.error)
```

已经有 Playwright `page` 时，可直接调用 `qianniu_login()`。已知登录失败返回 `result.ok=False` 和 `result.error`；程序错误直接抛出。后续网页操作要放在 `with` 里面，退出后连接会断开。

## 测试

从仓库根目录运行全部离线测试：

```powershell
.\.venv\Scripts\python.exe -B -m pytest
```

只检查新版千牛模块时，可在本目录运行：

```powershell
..\.venv\Scripts\python.exe -B -m unittest discover -s tests -b
```

这些测试不使用真实账号，不访问千牛或云码。`main.py` 在自动流程完成时返回退出码 `0`，已知登录未完成时返回 `1`；人工验证之后不会重新判定之前的结果。

本目录由原 `platforms/qianniu/qianniu_login_pw.py` 整理而来，采用配置文件和已有浏览器连接，去掉了固定代理、环境变量回退及多余的异常包装。原接口仍保留在 `platforms/qianniu/`，方便现有调用者继续使用。
