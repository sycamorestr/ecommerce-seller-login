# 跨境

| 指令 | 源文件 | 模块 | 状态 |
| --- | --- | --- | --- |
| 亚马逊-店铺登录 | `amazon_ext_op/process1.py` → `_amazon_core_beta.login` | `platforms/amazon/` | ported。源码不打开卖家站，只在当前 URL 含 `signin` / `mfa` / `ap/signin` 时点 `//input[@id="signInSubmit"]`。二次验证未自动填、或出现 `#aa-challenge-whole-page-iframe`，为 `NeedsHumanError` |
| Temu-账号登录 | `activity_temu_shop/login.py` | `platforms/temu/temu_login_pw.py` | ported。`https://seller.kuajingmaihuo.com/login` |
| Temu-切换店铺 | `activity_temu_shop/switch_store.py` | `temu_switch_store_pw.temu_switch_store` | ported。店铺名不能为空 |
| Temu-广告平台-登录 | `activity_temu_shop/advertisement_login.py` | `platforms/temu/temu_ads_login_pw.py` | ported。`https://ads.temu.com/login.html` |
| Temu-广告平台-切换店铺 | `activity_temu_shop/advertisement_switch_store.py` | `temu_switch_store_pw.temu_ads_switch_store` | ported |
| 速卖通登录 | `activity_aliexpress/aliexpress_login.py` | `platforms/aliexpress/` | ported。`https://login.aliexpress.com/user/seller/login?bizSegment=CSP&_lang=`。邮箱验证码正则与源码相同；不代收邮件 |
| 紫鸟登录 | `super_browser/process1.py` | `platforms/ziniao/` | desktop-only。Win32 / UIA，窗口标题「紫鸟浏览器专业版」，版本 V5 / V6 |

环境变量：`TEMU_ACCOUNT` / `TEMU_PASSWORD` / `TEMU_STORE`，`TEMU_ADS_ACCOUNT` / `TEMU_ADS_PASSWORD` / `TEMU_ADS_STORE`，`ALIEXPRESS_ACCOUNT` / `ALIEXPRESS_PASSWORD` / `ALIEXPRESS_LANG` / `ALIEXPRESS_EMAIL_CODE`。
