# 电商卖家登录

影刀登录流程的 Playwright 移植。每个产品一个目录，目录里带上它自己的 `helpers.py`（以及需要云码时的 `captcha.py`），拷走该目录即可放到别的项目里用。

## 千牛新版入口

最新版千牛登录位于 [`qianniu/`](qianniu/README.md)：通过 `config.json` 指定已有浏览器的调试地址，在新标签页登录并沿用 Cookie；程序结束后保留浏览器。代码分为入口、登录步骤和验证码处理三个文件，便于阅读和调试。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item qianniu\config.example.json qianniu\config.json
# 填写 config.json 中的 cdp_url、account、password 后运行
.\.venv\Scripts\python.exe qianniu\main.py
```

复制配置模板只需做一次。所有平台共用根目录的 `.venv`。Cursor 打开仓库后可按 F5 选择“千牛登录（连接已有浏览器）”。完整说明和函数调用示例见 [千牛文档](qianniu/README.md)。原 `platforms/qianniu/` 接口继续保留，以下目录说明主要针对原有平台模块。

## 目录规则

```
qianniu/               # 新版千牛：main.py、login.py、captcha.py 与配置模板
platforms/<product>/     # 同一产品的登录、切店入口放在一起
  *_login_pw.py          # 入口：*_login() 和 main()
  helpers.py             # 这个目录用到的浏览器、异常、结果对象
  captcha.py             # 仅当该登录调用云码或图鉴
  README.md              # 该登录的文件、流程、调用示例和测试
banks/<bank>/            # 每家银行单独一个目录，结构同上
vendor/shadowbot/        # 已脱敏的影刀原文，不参与运行
docs/CATALOG.md          # 指令 → 目录 → 状态
scripts/                 # 千牛实机入口
```

巨量引擎的滑块和邮箱验证调用 `platforms/doudian/`（process48 / process49）。拷贝 `platforms/oceanengine/` 时请一并拷贝 `platforms/doudian/`。其余目录不依赖别的产品目录。

仓库根上的 `banks/orangebank_login_pw.py` 这类旧路径只是重新导出。新代码请从 `platforms.*` 或 `banks.<银行目录>.*` 导入。

## 分类

| 类别 | 位置 |
| --- | --- |
| 国内电商 | 新版千牛见 `qianniu/`；原模块位于 `platforms/qianniu` `jingmai` `pdd` `doudian` `alipay` `oceanengine` `youzan` `jd` `jzt` `taobao` `compass` `aikucun` `alimama` `ali1688` `tmall` |
| 抖店多店 / 切店 | 与单店同在 `platforms/doudian/` |
| 银行 | `banks/pingan` `boc` `ccb` `icbc` `cmb` `bocom` 等，见 [`docs/banks.md`](docs/banks.md) |
| 跨境 | `platforms/temu` `aliexpress` |
| ERP / 税务 | `platforms/jushuitan` `sycm`；阿里妈妈平台登录在 `platforms/alimama/`；巨量合集登录在 `platforms/oceanengine/` |
| Cookie | `platforms/cookie/` |
| 获取已打开的网页 | `platforms/web_get/` |
| 未做成网页登录 | [`docs/unported.md`](docs/unported.md) |

完整矩阵：[`docs/CATALOG.md`](docs/CATALOG.md)。每个 `platforms/<product>/README.md` 和 `banks/<bank>/README.md` 按该目录里的函数写了调用方式和注意点，矩阵只做索引。

## 运行与测试

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
pytest
python -m platforms.qianniu.qianniu_login_pw
```

`pytest` 同时检查原有模块和新版千牛，不打开登录页，也不读取真实凭据。新版千牛入口是 `qianniu/main.py`；`scripts/run_live_login_pw.py` 仅用于原有千牛接口。

银行环境变量是各目录 README 里的 `<ENV_PREFIX>_ACCOUNT` / `<ENV_PREFIX>_PASSWORD`，可选 `<ENV_PREFIX>_LOAD_TYPE`。云码统一是 `YUNMA_TOKEN`。

## 安全

不要把账号、密码、Token、手机号写进仓库。`.env`、`shots/`、`cookies/`、`captcha_cache/` 已被忽略。短信、扫码、人脸、UKey 停在该目录 `helpers.NeedsHumanError`。
