# ERP / 税务 / 其他

| 指令 | 源文件 | 模块 | 状态 |
| --- | --- | --- | --- |
| 巨量引擎登录（合集） | `activity_52aea4a0/process1.py` | `oceanengine_collection_login_pw.py` | ported，不是已有巨量模块的别名。地址同样是 `https://business.oceanengine.com/login?appKey=51`，但退出登录用 `navigator-user-account-info`，滑块最多 7 次。`activity_7bca6d` 的巨量三变体仍在 `oceanengine_*_login_pw.py` |
| 生意参谋登录Plus | `activity_26766b38/process45.py` | `sycm_login_pw.py` | ported。`https://sycm.taobao.com/custom/login.htm`，首页 `https://sycm.taobao.com/portal/home.htm` |
| 电子税局登录 | `activity_invoice/tax_invoice_auth_login.py` | `tax_invoice_login_pw.py` | ported 为 API，不是浏览器。`APIBaseUrl.BASE_URL` = `https://openapi.njmbxx.com`。接口消息含「验证码」或要求扫脸时为 `NeedsHumanError`。本模块不请求该接口 |
| 聚水潭登录 | `activity_jvshuitan/login.py` | `jushuitan_login_pw.py` | ported。`https://www.erp321.com/login.aspx` |
| 阿里妈妈-平台登录 | `activity_d91a274e/process6.py` | `alimama_platform_login_pw.py` | ported，区别于数智登录 `alimama_login_pw.py`。平台首页只有源码字典里的六个 |
| 登录金蝶云星空 | `activity_jindie/login.py` | `kingdee_login_pw.py` | ported。源码不导航，页面上必须已经有 `#user`。验证码 type `10110` |
| 登录旺店通 | `activity_7bca6d/process39.py` | `wangdiantong_login_pw.py` | desktop-only |

环境变量：`OCEANENGINE_COLLECTION_EMAIL` / `OCEANENGINE_COLLECTION_PASSWORD`，`SYCM_ACCOUNT` / `SYCM_PASSWORD`，`TAX_APP_ID` / `TAX_APP_SECRET` / `TAX_ACCOUNT` / `TAX_PASSWORD` / `TAX_NSRSBH` / `TAX_SMS_CODE`，`JUSHUITAN_ACCOUNT` / `JUSHUITAN_PASSWORD`，`ALIMAMA_PLATFORM` / `ALIMAMA_PLATFORM_ACCOUNT` / `ALIMAMA_PLATFORM_PASSWORD`，`KINGDEE_ACCOUNT` / `KINGDEE_PASSWORD` / `KINGDEE_PLATFORM`。
