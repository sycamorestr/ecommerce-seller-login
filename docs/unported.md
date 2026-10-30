# 未做成网页登录的块

这些块没有可照搬的网页登录地址，或只是验证码 / 子流程。没有为它们另造 URL。

## 桌面客户端

| 指令 | 原因 | 模块 |
| --- | --- | --- |
| 登录旺店通 `activity_7bca6d/process39.py` | 只有 `win32.element`。验证码 `captcha_type=3` / `ttshitu_3_predict` | `wangdiantong_login_pw.DesktopOnlyLogin` |
| 紫鸟登录 `super_browser/process1.py` | Win32 / UIA 客户端，标题「紫鸟浏览器专业版」 | `ziniao_login_pw.ziniao_login` |

## 验证码辅助，不是登录页

| 源 | 本仓库 |
| --- | --- |
| 美团开店宝滑块 `process65` | `captcha_helpers.meituan_slider_distance`，轨迹切片 `[25:]`。`time_ease` 在缺失的 `resources.trace_api` 里，没有自造曲线 |
| 沃尔玛长按 `module1` | `captcha_helpers.WALMART_HOLD_SECONDS = 7` |
| 桔子 / 平安滑块公式 | `captcha_helpers.orangebank_drag_px`、`orangebank_gap_offset` |
| 银行数英 `10103`、金蝶 `10110` | `captcha_helpers.alphanum_payload` |
| 短信 / 邮件收取 `activity_47680f64` | 不代收。页面要验证码时把码放进环境变量，否则 `NeedsHumanError` |

## 没有登录地址

| 块 | 原因 |
| --- | --- |
| 京东数坊 | `process41` 跳转表里是空字符串，京准通不跳转 |
| 滑块拖动 `process11`、`process3` | 调用方传入元素，没有登录页 |
| `activity_966451c9/process37.py` | 售后时间选择测试，不是「店铺切换(ID)(新）」 |
| `activity_7bca6d` 里的中国银行 | 该扩展没有中国银行登录流。网银登录在 `activity_e05c2690/bankofchina_load.py`，见 `docs/banks.md` |
| 金蝶 | 源码要求页面已经打开，不提供 URL。模块在检测到 `#user` 后才填写，见 `docs/erp_tax.md` |
| 亚马逊 | 源码不写死 sellercentral 地址，只处理当前已打开的 signin/mfa 页 |

隐藏子流程（`process22` 等）不是独立登录指令。其中已被登录模块调用的 `process48` / `process49` / `process2` / `process17` / `process36` 已经接到对应模块。
