# 电商卖家登录

把影刀（ShadowBot）里的卖家登录、切店和网银登录移植成 Playwright。登录地址、选择器和验证码类型跟源流程一致。账号、密码、云码 Token 只从环境变量读取，不写进源码。

完整指令矩阵：[`docs/CATALOG.md`](docs/CATALOG.md)。

## 分类

| 类别 | 说明 | 文档 |
| --- | --- | --- |
| 国内电商登录 | 千牛、京麦、拼多多、抖店单店、支付宝、巨量、有赞、京东、京准通、淘宝、罗盘、爱库存、阿里妈妈数智、1688、天猫超市 | [`docs/ecommerce.md`](docs/ecommerce.md) |
| 抖店多店铺 / 切店 | 多店铺登录、按名称切换、按店铺 ID 切换 | [`docs/doudian_ops.md`](docs/doudian_ops.md) |
| 银行网银登录 | `activity_e05c2690` 的 `*_load.py`，含中国银行 | [`docs/banks.md`](docs/banks.md) |
| 跨境 | 亚马逊、Temu、速卖通。紫鸟是桌面客户端 | [`docs/crossborder.md`](docs/crossborder.md) |
| ERP / 税务 / 其他 | 聚水潭、金蝶、电子税局、生意参谋、阿里妈妈平台、巨量合集 | [`docs/erp_tax.md`](docs/erp_tax.md) |
| Cookie / 验证码 | Cookie 保存与写入；云码 / 图鉴载荷在 `captcha_helpers.py` | [`docs/CATALOG.md`](docs/CATALOG.md) |
| 未做成网页登录 | 桌面客户端、没有 URL 的块、验证码辅助 | [`docs/unported.md`](docs/unported.md) |

## 安装与测试

需要 Python 3.10+。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
pytest
```

`pytest` 不打开登录页，也不需要真实凭据。实机登录才需要 Chromium。

```bash
python -m qianniu_login_pw
python -m banks.bankofchina_login_pw
```

银行模块的入口函数是 `banks.<slug>_login_pw.<slug>_login()`。环境变量名是 `<ENV_PREFIX>_ACCOUNT` / `<ENV_PREFIX>_PASSWORD`，可选 `<ENV_PREFIX>_LOAD_TYPE`（`个人网上银行` 或 `企业网上银行`）。云码统一用 `YUNMA_TOKEN`。

## 安全

- 不要把账号、密码、Token、手机号写进仓库。
- `.env`、`shots/`、`cookies/`、`captcha_cache/` 已被 `.gitignore` 忽略。
- `vendor/shadowbot/` 是影刀源码副本，凭据已清空。
- 短信、扫码、人脸、UKey / 签名控件停在 `NeedsHumanError`。
- 只有 Windows 客户端、没有网页地址的流程抛出 `DesktopOnlyLogin`（旺店通、紫鸟）。

仅用于操作者自己的卖家账号和网银。
