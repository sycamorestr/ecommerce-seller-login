# 影刀「千牛登录」逆向说明

本仓库对应实现：

- `qianniu_login_pw.py` — Playwright 主流程（`page.mouse` 拖拽，`FrameLocator`）
- `qianniu_login.py` — Selenium 同级实现；Playwright 复用其中的纯函数与常量
- 登录地址、选择器、云码 type 以下文为准，不要另造

## 包位置（原始机器）

市场扩展 **登录扩展操作** (`activity_7bca6d` v24.1.13 / 依赖声明 `activity_7bca6d==26.10.12`)：

```
/home/box/.config/Shadowbot/users/1005876321989500928/apps/1079d79d-ce8f-4d00-91ee-cfcc69ad9adb/
  xbot_extensions/activity_7bca6d/          # 登录扩展操作
    qn_login.py                             # ★ 市场指令「千牛登录」代码实现
    process62.py                            # 同名可视化旧流程（未挂到该指令 block）
    selectorsV2.xml                         # qn_* 选择器
    prototype.block.json                    # block: function=...qn_login
  xbot_extensions/activity_jfbym/           # 云码/验证码扩展
    ali_slider_captcha.py                   # handle_verification / recg type=20226
  xbot_robot/                               # 用户应用「千牛登录」
```

本仓库不附带影刀扩展源码副本；行为以本文与 `qianniu_login.py` / `qianniu_login_pw.py` 为准。

未找到加密阻碍：`qn_login.py` 与 `ali_slider_captcha.py` 均为明文 Python。`.dev/*.flow.json.enc` 是可视化源的加密稿，但已编译出同名 `.py`（`process62.py` 等），且市场指令 block 指向 **Code 模块 `qn_login`**，不以 `process62` 为准。

## 市场指令入参（prototype.block.json）

| 影刀字段 | 含义 | 默认 |
| --- | --- | --- |
| mode | 网页类型 chrome/edge/cef/SunBrowser | chrome |
| engine | 识别引擎 xbot / ym | — |
| username | 账号 | — |
| password | 密码（影刀内可加密，运行时 decrypt） | — |
| retry_count | 验证码重试次数 | 5 |
| token | 云码 Token（engine=ym） | — |
| 输出 web_page | 浏览器对象 | — |

用户应用里实际配置：Chrome + 云码引擎 + 自定义 Token + retries=5。

## `qn_login.login` 步骤 → Python

| # | 影刀 `qn_login.py` | 本仓库 `qianniu_login.py` |
| --- | --- | --- |
| 1 | `url = "https://loginmyseller.taobao.com/"` | `LOGIN_URL` 相同 |
| 2 | `web.create` / `reload` 最多 3 次，`load_timeout=60` | `driver.get` / `refresh` ×3 |
| 3 | `manual_motion_on()` | 拖拽时用 ActionChains / xdotool 模拟 |
| 4 | `find("qn_uername_input").input`，校验 value，失败重试≤3 | iframe `#alibaba-login-box` 内 `#fm-login-id` |
| 5 | `qn_password_input.click()` | `#fm-login-password`.click() |
| 6 | 若 `qn_drag_label` 可见 → `ali_slider_captcha.handle_verification(..., offset=-30)` | `handle_verification` 同序移植 |
| 7 | `decrypt(password)` 后 input，校验≤3 | 明文密码直接 input（环境变量） |
| 8 | 循环：若 `qn_login_verify` 可见，按 `qn_slide` 中心拖 `verify_width` | `xdotool_drag` 同几何 |
| 9 | 否则点 `//div[@class="errloading"]` 或 break | 相同 xpath |
| 10 | `qn_login.click()`；`manual_motion_off` | `button.password-login` click |
| 11 | 5s 内仍能找到登录按钮 → `登录失败`；`errloading` 则外圈重试 | 同逻辑 |
| 12 | `login-error-msg` 可见 → `ValueError(text)` | `CredentialsRejected` |

选择器叶子（`selectorsV2.xml`）：

- 账号：`#fm-login-id`（iframe `#alibaba-login-box`）
- 密码：`#fm-login-password`
- 登录：`button.fm-button...password-login`
- 拼图题：`canvas#captcha-question`（`qn_drag_label`）
- 刷新：`i.icon-refresh...scratch`（`qn_refresh`）
- 拖块：`.scratch-captcha-slider .button`（`qn_drag_ele`）
- NC 条：`#nc_1__scale_text` / `#nc_1_n1z`

## 云码（`ali_slider_captcha`）

- `POST http://api.jfbym.com/api/YmServer/customApi`
- body: `{ image: <joined tip+bg base64>, token, type: 20226 }`
- tip 图高 30、底图高 180；`join_images` 上下拼接 +11px 间距
- 成功：`msg == "识别成功"`，距离 `data.data`
- 拖距：`(distance - 24 - 10) / 320 * background_width`（默认 width=320）
- 拖拽：按下 → 过冲 → 回拉 → 松手（`drag()`）

影刀用 `start_monitor_network` 抓 data URL；Python 侧用刷新后 DOM/`canvas.toDataURL` 等价采集（同为 data:image）。

## 刻意未采用的内容

- `process62.py` 可视化「千牛登录」：用 1688 滑块选择器 + `process11`，**不是**市场指令 block 绑定的实现。
- 旧版自研脚本里的 `login.taobao.com`、云码 type 20110/20111/30100 等，与本指令无关。

## 运行环境备注（本机）

Selenium 直连时 `iframe#alibaba-login-box`（havanalogin.taobao.com）会 403；需走 box 出口代理 `127.0.0.1:8791`（与 `/usr/local/bin/box-chrome` 一致）。这不属于影刀指令逻辑，但是本沙箱跑通的前置条件。

## Baxia 嵌套 iframe（与 selectorsV2 路径一致）

当前千牛页在填密后把 NC 滑块放进：

`iframe#alibaba-login-box` → `iframe#baxia-dialog-content`（punish captcha）

其中可见 `#nc_1_n1z` / `#nc_1__scale_text`（文案「向右滑动验证」）。外层 `#nocaptcha-password` 为 `display:none`，故必须切入 baxia iframe 才能拖——这与 `selectorsV2.xml` 里 `qn_login_verify` / `qn_slide` 经过 `baxia-dialog-content` 的路径一致。

## NC 拖拽在本机的落地

影刀用 `win32.mouse_*` 屏幕坐标拖 `qn_slide`。本沙箱：

- Selenium `ActionChains` → 经常「验证失败」
- `xdotool` 屏幕坐标 → 嵌套 iframe 时易偏
- **CDP `Input.dispatchMouseEvent`**（顶层 viewport CSS 像素 = login iframe 偏移 + baxia iframe 偏移 + 元素框）可通过；拖距仍为「滑块中心 + verify 宽度」，与 `qn_login.py` 一致

短信门文案示例（实测）：`你正在使用手机短信验证身份` / `点击获取验证码` / `其他验证方式` → `NeedsHumanError`，浏览器保持打开。

## 本轮修正（对齐 qn_login 行为）

1. **登录按钮「登录失败」**：原版 `try: find(qn_login); raise 登录失败; except: pass` 会吞掉异常。Python 端口改为 soft probe，不再在此处硬失败；真正失败看 `login-error-msg` 或最终仍停在密码登录表单。
2. **`div.errloading`**：拖拽失败后的黄条「验证失败, 点击框体重试」即 `class="errloading"`（selectorsV2 里 `nc_1_refresh1`）。原版在 NC 不可见时点它刷新；端口用 `click_errloading()` 在 login / baxia iframe 内查找并点击。
3. **NC 选择器**：逗号 CSS `#nc_1__scale_text, .slidetounlock, #nc_1_n1t` 会先命中父级 `#nc_1_n1t`，拖距偶发异常。改为精确 `#nc_1_n1z` / `#nc_1__scale_text`（与 selectorsV2 叶子一致）。
4. **拖拽落地**：本沙箱用 CDP `Input.dispatchMouseEvent`（顶层 viewport CSS px = login iframe 偏移 + baxia 偏移 + 元素框），几何仍是「滑块中心 + verify 宽度」。

## 实测（Asia/Shanghai）

- 账号子账号形式登录 → NC（baxia）CDP 拖过 → **短信门**。
- UI 原文：`你正在使用手机短信验证身份` / `手机号码：166******45` / `校验码：` / `点击获取验证码` / `确定` / `其他验证方式`。
- `NeedsHumanError`；浏览器保持打开（`shots/browser_keep.flag`、`shots/live_human.png`）。
- 单元测试：`test_qianniu_login.py` 6 passed。
