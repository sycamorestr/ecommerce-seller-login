# 电商卖家登录

影刀登录流程的 Playwright 移植。每个产品一个目录，目录里带上它自己的 `helpers.py`（以及需要云码时的 `captcha.py`），拷走该目录即可放到别的项目里用。

## 目录规则

```
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
| 国内电商 | `platforms/qianniu` `jingmai` `pdd` `doudian` `alipay` `oceanengine` `youzan` `jd` `jzt` `taobao` `compass` `aikucun` `alimama` `ali1688` `tmall` |
| 抖店多店 / 切店 | 与单店同在 `platforms/doudian/` |
| 银行 | `banks/pingan` `boc` `ccb` `icbc` `cmb` `bocom` 等，见 [`docs/banks.md`](docs/banks.md) |
| 跨境 | `platforms/temu` `aliexpress` |
| ERP / 税务 | `platforms/jushuitan` `sycm`；阿里妈妈平台登录在 `platforms/alimama/`；巨量合集登录在 `platforms/oceanengine/` |
| Cookie | `platforms/cookie/` |
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

`pytest` 不打开登录页，也不读取真实凭据。实机千牛入口是 `scripts/run_live_login_pw.py`。

银行环境变量是各目录 README 里的 `<ENV_PREFIX>_ACCOUNT` / `<ENV_PREFIX>_PASSWORD`，可选 `<ENV_PREFIX>_LOAD_TYPE`。云码统一是 `YUNMA_TOKEN`。

## 安全

不要把账号、密码、Token、手机号写进仓库。`.env`、`shots/`、`cookies/`、`captcha_cache/` 已被忽略。短信、扫码、人脸、UKey 停在该目录 `helpers.NeedsHumanError`。
