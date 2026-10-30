# 电商平台登录

卖家平台登录自动化。Playwright 模块按影刀「登录扩展操作」原流程移植：登录地址、选择器、验证码类型与源码一致，不另造入口或验证码类型。

已移植的登录：

| 平台 | 模块 | 影刀来源 | 登录地址 |
| --- | --- | --- | --- |
| 千牛 | `qianniu_login_pw.py` | `qn_login` + `ali_slider_captcha` | `https://loginmyseller.taobao.com/` |
| 京麦 | `jingmai_login_pw.py` | `process56.py` + `std_slider_captcha` | `https://passport.shop.jd.com/login/index.action/jdm?...` |
| 拼多多 | `pdd_login_pw.py` | `process21.py` + `std_slider_captcha` + `cs_temu_captcha` | `https://mms.pinduoduo.com/login/` |
| 抖店 | `doudian_login_pw.py` | `process4.py`、`process48/45/44`、`process49` | `https://fxg.jinritemai.com/login/common` |
| 支付宝 | `alipay_login_pw.py` | `process20.py` → `zfb_login.py` | `https://auth.alipay.com/login/index.htm` |
| 巨量 | `oceanengine_login_pw.py` | `process1.py` + `process48` | `https://business.oceanengine.com/login` |
| 巨量引擎邮箱 | `oceanengine_email_login_pw.py` | `process47.py` + `process48` + `process49` | `https://business.oceanengine.com/login?appKey=51` |
| 巨量纵横 | `oceanengine_zongheng_login_pw.py` | `process12.py` + `process48` | `https://business.oceanengine.com/login?appKey=51` |
| 有赞 | `youzan_login_pw.py` | `process5.py` + `std_slider_captcha` | `https://account.youzan.com/login` |
| 京东 | `jd_login_pw.py` | `process6.py` | `https://passport.jd.com/new/login.aspx` |
| 京准通 | `jzt_login_pw.py` | `process40.py` + `process41.py` | `https://jzt.jd.com/gw/index` |
| 淘宝 | `taobao_login_pw.py` | `process7.py` + `ali_slider_captcha` | `https://login.taobao.com/member/login.jhtml` |
| 淘宝 mini | `taobao_mini_login_pw.py` | `taobao_mini.py` | `https://login.taobao.com/member/login.jhtml?style=minisimple&...` |
| 电商罗盘 | `compass_login_pw.py` | `process15.py` + `dy_slider_captcha` | `https://compass.jinritemai.com/login` |
| 电商罗盘策略 | `compass_strategy_login_pw.py` | `process59.py` + `dy_slider_captcha` | `https://compassbrand.jinritemai.com/login` |
| 爱库存 | `aikucun_login_pw.py` | `process33.py` + `slider_captcha` offset `-4` | `https://merc.aikucun.com/login.html` |
| 阿里妈妈数智 | `alimama_login_pw.py` | `process42.py` | `https://www.alimama.com/index.htm` |
| 拼多多推广 | `pdd_promote_login_pw.py` | `process51.py` | `https://mms.pinduoduo.com/home/` |
| 拼多多商家后台（待下架） | `pdd_mms_legacy_login_pw.py` | `process43.py` + 点选 type `19` | `https://mms.pinduoduo.com/home/` |
| 1688 | `login_1688_pw.py` | `login_1688.py` | 淘宝登录页 `from=1688web` |
| 天猫超市 | `tmall_supermarket_login_pw.py` | `login_tmall_supermarket.py` | `https://web.txcs.tmall.com/login?...` |
| Cookie | `cookie_login_pw.py` | `cookie_login/process1–3` + `_core.py` | 使用当前页面，不另开登录站 |

中国银行：**没有登录指令，无法移植登录流。** 说明见 `docs/MISSING_BOC.md`。`bank_captcha` / `orangebank_slider_captcha` 只放在 `captcha_helpers.py`。

登录旺店通是 Windows 客户端，没有网页地址，见 `docs/UNPORTED_BLOCKS.md`。京准通跳转表里的「京东数坊」在源码中是空 URL，不会跳转。拼多多商家后台（待下架）模块带 `DEPRECATED = True`。

千牛的云码请求、拼图和选择器常量仍在 Selenium 同级模块 `qianniu_login.py`，Playwright 通过 `import qianniu_login as _se` 复用。其余平台共用 `captcha_helpers.py` 与 `seller_common.py`。

影刀原文（已去掉账号、密码、Token）在 `vendor/shadowbot/`。

## 目录

| 路径 | 作用 |
| --- | --- |
| `qianniu_login_pw.py` | 千牛 Playwright 登录 |
| `qianniu_login.py` | 千牛 Selenium 同级实现，以及被 Playwright 复用的纯函数 |
| `jingmai_login_pw.py` | 京麦登录 |
| `pdd_login_pw.py` | 拼多多登录 |
| `doudian_login_pw.py` | 抖店登录 |
| `alipay_login_pw.py` | 支付宝登录 |
| `captcha_helpers.py` | 云码载荷、拖距、点选坐标、支付宝旋转、银行滑块公式 |
| `seller_common.py` | 浏览器、`NeedsHumanError`、结果对象 |
| `tests/` | 单元测试（不访问登录页，不需要真实凭据） |
| `run_live_login_pw.py` | 千牛实机登录入口 |
| `run_sms_get_code.py` | 千牛停在短信门时点击「点击获取验证码」 |
| `docs/MISSING_BOC.md` | 中国银行登录缺失说明 |
| `docs/UNPORTED_BLOCKS.md` | 没有网页登录地址、或只有子流程的影刀块 |
| `cookie_login_pw.py` | 保存 / 写入 / 清除 Cookie 与 localStorage |
| `vendor/shadowbot/` | 影刀源码副本（账号、密码、Token 已清空） |

## 安装

需要 Python 3.10+。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

单元测试只依赖 Python 包，不必安装 Chromium。实机登录需要 Chromium，并且与源脚本一样走本机出口代理 `http://127.0.0.1:8791`（直连时登录 iframe 会 403）。脚本在未设置 `DISPLAY` 时默认 `:2`。

## 环境变量

账号、密码、云码 Token 只从环境变量读取。不要写进源码，不要提交到 git。

| 变量 | 含义 |
| --- | --- |
| `QIANNIU_ACCOUNT` / `QIANNIU_PASSWORD` | 千牛账号、密码 |
| `JINGMAI_ACCOUNT` / `JINGMAI_PASSWORD` | 京麦账号、密码 |
| `PDD_ACCOUNT` / `PDD_PASSWORD` | 拼多多账号、密码 |
| `DOUDIAN_ACCOUNT` / `DOUDIAN_PASSWORD` | 抖店邮箱登录账号、密码 |
| `DOUDIAN_EMAIL` / `DOUDIAN_EMAIL_AUTH` | 抖店邮箱验证用的邮箱与授权码（页面出现「发送验证码」且没有验证码时需要） |
| `DOUDIAN_EMAIL_CODE` | 可选。已经拿到的邮箱验证码；不提供则停在邮箱门（`NeedsHumanError`） |
| `ALIPAY_ACCOUNT` / `ALIPAY_PASSWORD` | 支付宝账号、密码 |
| `OCEANENGINE_ACCOUNT` / `OCEANENGINE_PASSWORD` | 巨量登录。`OCEANENGINE_RELOGIN=1` 时先退出 |
| `OCEANENGINE_EMAIL` / `OCEANENGINE_EMAIL_PASSWORD` / `OCEANENGINE_EMAIL_CODE` | 巨量引擎邮箱登录。没有验证码时停在邮箱门 |
| `OCEANENGINE_ZH_ACCOUNT` / `OCEANENGINE_ZH_PASSWORD` | 巨量纵横 |
| `YOUZAN_ACCOUNT` / `YOUZAN_PASSWORD` | 有赞 |
| `JD_ACCOUNT` / `JD_PASSWORD` | 京东。可选 `JD_LOGIN_URL`，默认同源码 |
| `JZT_ACCOUNT` / `JZT_PASSWORD` / `JZT_PLATFORM` | 京准通。`JZT_PLATFORM` 取 process41 的平台名；京东数坊不跳转 |
| `TAOBAO_ACCOUNT` / `TAOBAO_PASSWORD` | 淘宝 |
| `TAOBAO_MINI_ACCOUNT` / `TAOBAO_MINI_PASSWORD` | 淘宝 mini |
| `COMPASS_ACCOUNT` / `COMPASS_PASSWORD` / `COMPASS_SHOP` | 电商罗盘。店铺名可空，空则点第一条 |
| `COMPASS_STRATEGY_ACCOUNT` / `COMPASS_STRATEGY_PASSWORD` / `COMPASS_STRATEGY_SHOP` | 电商罗盘策略 |
| `AIKUCUN_ACCOUNT` / `AIKUCUN_PASSWORD` | 爱库存 |
| `ALIMAMA_ACCOUNT` / `ALIMAMA_PASSWORD` | 阿里妈妈数智 |
| `PDD_PROMOTE_ACCOUNT` / `PDD_PROMOTE_PASSWORD` | 拼多多推广 |
| `PDD_LEGACY_ACCOUNT` / `PDD_LEGACY_PASSWORD` | 拼多多商家后台（待下架） |
| `LOGIN1688_ACCOUNT` / `LOGIN1688_PASSWORD` | 1688 |
| `TMALL_SUPERMARKET_ACCOUNT` / `TMALL_SUPERMARKET_PASSWORD` / `TMALL_SUPERMARKET_SHOP` | 天猫超市 |
| `YUNMA_TOKEN` | 云码 Token。千牛/淘宝滑块 `type=20226`；京麦/拼多多/有赞/京准通单图滑块与 `bank_captcha` 为 `22222`；拼多多空间点选 `"9999"`；抖店/罗盘滑块 `"20225"`；支付宝四图旋转 `276502`；京东点选 `30330`；京东点选 plus `30009` direction `bottom`；京东轨迹 `100015` |
| `QIANNIU_RETRIES` / `JINGMAI_RETRIES` / `PDD_RETRIES` / `ALIPAY_RETRIES` | 可选，各模块 `main()` 的重试次数 |
| `SELLER_HTTP_PROXY` | 可选。京麦/拼多多/抖店/支付宝默认不走代理；千牛仍使用源脚本里的 `127.0.0.1:8791` |

```bash
cp .env.example .env
# 编辑 .env 后载入（.env 已被 git 忽略）
set -a && source .env && set +a
```

截图、验证码缓存、Cookie / 浏览器存储里可能含登录态，同样不要提交。`.gitignore` 已忽略 `.env`、`shots/`、`cookies/`、`captcha_cache/`。

## 测试

在仓库根目录：

```bash
pytest
```

覆盖这些不联网的检查：千牛云码 `type=20226` 与拖距公式；京麦/拼多多/抖店/支付宝的登录 URL；云码 `22222` / `"9999"` / `"20225"` / `276502` 的请求体；拼多多点选坐标；抖店点选 `captcha_type=27`；支付宝旋转点击次数与冰拓 `1311`；桔子银行拖距公式；缺凭据、`OnError.IGNORE`、短信或二维码 `NeedsHumanError`。中国银行只断言说明文档，不存在登录模块。

## 实机运行

```bash
python run_live_login_pw.py
```

- 退出码 `0`：登录成功，并关闭本次拉起的浏览器
- 退出码 `10`：未成功（常见是短信 / 人脸等人机验证）。脚本会截图到 `shots/`，浏览器保持约 120 秒再关闭
- 退出码 `2`：未设置 `QIANNIU_ACCOUNT`、`QIANNIU_PASSWORD` 或 `YUNMA_TOKEN`
- 退出码 `1`：其他失败

已在短信门、需要点「点击获取验证码」并等待人工填写时：

```bash
python run_sms_get_code.py
```

也可以直接跑模块入口（凭据同样只读环境变量）：

```bash
python -m qianniu_login_pw
```

在代码里调用：

```python
import qianniu_login_pw as q

result = q.qianniu_login()  # 读取 QIANNIU_ACCOUNT / QIANNIU_PASSWORD / YUNMA_TOKEN
# result.ok、result.error、result.web_page、result.yunma_calls
q.close_result(result)
```

## 各平台行为

短信、扫码、人脸等停在 `NeedsHumanError`，不继续代填。账号或密码被页面拒绝时为 `CredentialsRejected`。

### 京麦

`process56`：打开京麦登录页，若二维码在则点「账号密码」图标，填写 `0706` 账号框和密码框，点「立即登录」。滑块调用 `std_slider_captcha`（云码 type `22222`，`offset=0`，`speed=1`）。源流程里的图鉴账号/密码没有传入验证码调用，这里同样不另接图鉴接口。密码错误文案为「账户密码错误」。仍停在登录域时会打开 `https://shop.jd.com/jdm/home`。

```bash
python -m jingmai_login_pw
```

### 拼多多

`process21`：`https://mms.pinduoduo.com/login/`。先处理单图滑块（type `22222`），再处理空间点选（`cs_temu_captcha`，type `"9999"`，`extra` 为提示文字）。然后点「账号登录」，填写 `#usernameId` / `#passwordId`，再点登录，并再跑一轮同样的验证码。账号或密码为空时报「拼多多账号、密码均不能为空」。结束后 URL 仍含 `login` 时，按源码视为可能要手机验证（`NeedsHumanError`）。

```bash
python -m pdd_login_pw
```

### 抖店

`process4` 打开 `https://fxg.jinritemai.com/login/common`，切到邮箱登录，填写邮箱和密码，勾选协议后点登录。`process48`：iframe 里的滑块走 `dy_slider_captcha` type `"20225"`（拖距 `识别像素 * (CSS宽/图片宽) + offset`）；`#verify-bar-code` 点选对应 `process44` 的 `captcha_type=27` / `ttshitu_27_predict`。该调用在影刀里走 `web_service.captcha`，源码没有单独的 HTTP 地址，因此默认把点选交给人工（`NeedsHumanError`）。若要自动点，传入 `click_recognizer(image_b64) -> "x,y|x,y"`。邮箱验证码正则与 `process49` 相同（先 6 位再 4 位）。本仓库不代收邮件；把验证码放在 `DOUDIAN_EMAIL_CODE`，或在页面上人工完成。

```bash
python -m doudian_login_pw
```

### 支付宝

`zfb_login`：`https://auth.alipay.com/login/index.htm`，点 `li[data-status=show_login]`，填写 `#J-input-user` 与 `#password_rsainput`，点 `#J-login-simulate-btn`。验证码顺序与源码一致：拼图滑块（本地 CV，需要可选依赖 `opencv-python`）、冰拓点选 type `1311`（同样没有在源码里写死客户端域名，默认 `NeedsHumanError`）、四图旋转 `zfb_four_click_captcha` type `276502`（按 `rotate()` 方向决定补点次数）。落到 `https://authsa127.alipay.com/login/checkSecurity.htm` 时停止，提示先填写手机验证码。

```bash
python -m alipay_login_pw
```

### 中国银行

没有登录流。不要把桔子银行滑块当成中国银行登录。详见 `docs/MISSING_BOC.md`。

## 千牛行为

- 登录页固定为 `https://loginmyseller.taobao.com/`
- 账号、密码在 `iframe#alibaba-login-box` 内填写（`#fm-login-id` / `#fm-login-password`）
- 拼图滑块走云码 `http://api.jfbym.com/api/YmServer/customApi`，`type=20226`；拖距为 `(distance - 24 - 10) / 320 * 320`
- NC 滑块在登录 iframe 或嵌套的 `iframe#baxia-dialog-content` 里，用 Playwright `page.mouse` 按滑块中心加验证条宽度拖动
- 账号或密码被页面拒绝时抛 `CredentialsRejected`
- 短信、手机、人脸等验证停止自动化，返回 `NeedsHumanError`，并留下页面供人工处理

仅用于操作者自己的卖家账号。
