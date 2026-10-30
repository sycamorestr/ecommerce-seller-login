# 中国银行

`activity_7bca6d`（登录扩展操作）里没有中国银行登录指令。

网银登录在「登陆拓展合集」的 `activity_e05c2690/bankofchina_load.py`，模块是 `banks/bankofchina_login_pw.py`。地址：

`https://netc1.igtb.bankofchina.com/#/login-page?redirect=%2Findex`

滑块 type `22222`，企业版数英 type `10103`。说明见 [`docs/banks.md`](banks.md)。

`captcha_helpers` 里的 `bank_captcha` / `orangebank_slider_captcha` 仍只是验证码公式，不是这条登录流。
