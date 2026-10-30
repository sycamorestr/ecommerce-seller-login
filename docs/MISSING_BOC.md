# 中国银行登录

在影刀「登录扩展操作」`activity_7bca6d` 与随附源码中，**没有**名为「中国银行登录」的市场指令或流程，因此本仓库**无法移植登录流**（没有登录 URL、账号框、密码框或提交步骤可以照搬）。

仅有验证码辅助，已收成纯函数，不单独做登录模块：

| 源文件 | 本仓库 | 识别 |
| --- | --- | --- |
| `activity_jfbym/bank_captcha.py` | `captcha_helpers.bank_slider_payload` / `bank_slider_distance` | 云码 `type=22222`，拖距 `(distance + offset) / speed` |
| `activity_jfbym/orangebank_slider_captcha.py` | `captcha_helpers.orangebank_drag_px` / `orangebank_yd_body` | 影刀接口码 `jfbym_22222`（桔子银行滑块，不是中国银行登录） |

若要补中国银行登录，需要提供对应的影刀流程或指令源码后再移植。不要用别的银行登录地址顶替。
