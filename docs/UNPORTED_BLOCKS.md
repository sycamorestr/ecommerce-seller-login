# 未移植成网页登录的影刀块

这些块没有可照搬的网页登录地址，或只是被登录流程调用的子步骤。没有为它们另造 URL 或验证码类型。

## 登录旺店通（process39）

源码只调用 `win32.element`（用户名、密码、验证码窗口）。没有 `web.create` 或登录 URL。`wangdiantong_login_pw.wangdiantong_login` 会抛出 `DesktopOnlyLogin`。验证码参数保留为 `captcha_type=3` / `ttshitu_3_predict`。

## 京东数坊

`process41` 的跳转表里「京东数坊」对应空字符串。京准通登录在平台名为京东数坊时不跳转。

## 美团开店宝滑块（process65）与沃尔玛验证码（module1）

不是登录块。距离公式 `背景宽 - 滑块宽`、轨迹切片 `time_ease(...)[25:]`、长按 7 秒在 `captcha_helpers`。`time_ease` / `y_offset` 的实现在 `resources.trace_api`，导出包里没有这份源码，所以没有补一条自造的拖动曲线。

## 滑块拖动（process11、process3）

通用拖动，调用方传入元素。没有登录页。

## 短信 / 邮件收取（activity_47680f64）

`latest_email` / `get_SMS_code` 需要邮箱授权码或短信接口。登录模块不代收。页面出现验证码时，把验证码放进对应环境变量，否则 `NeedsHumanError`。

## 隐藏子流程

`process22`、`process25`–`process30`、`process32`、`process34`–`process38`、`process41` 以外的跳转辅助、`process44`–`process46`、`process48`–`process50`、`process53`–`process55`、`process57`、`process58`、`process63`、`process66`–`process71`、`process75`–`process77`、`taobao_reg` 不是独立登录指令。其中 `process48` / `process49` / `process2` / `process41` 的参数已经接到对应登录模块。

## 中国银行

仍然没有登录指令。见 `docs/MISSING_BOC.md`。
