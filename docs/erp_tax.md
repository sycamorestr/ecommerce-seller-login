# ERP / 税务 / 其他

| 指令 | 源文件 | 模块 | 状态 |
| --- | --- | --- | --- |
| 巨量引擎登录（合集） | `activity_52aea4a0/process1.py` | `platforms/oceanengine/oceanengine_collection_login_pw.py` | ported，不是已有巨量模块的别名。地址同样是 `https://business.oceanengine.com/login?appKey=51`，但退出登录用 `navigator-user-account-info`，滑块最多 7 次。`activity_7bca6d` 的巨量三变体仍在 `oceanengine_*_login_pw.py` |
| 生意参谋登录Plus | `activity_26766b38/process45.py` | `platforms/sycm/` | ported。`https://sycm.taobao.com/custom/login.htm`，首页 `https://sycm.taobao.com/portal/home.htm` |
| 聚水潭登录 | `activity_jvshuitan/login.py` | `platforms/jushuitan/` | ported。`https://www.erp321.com/login.aspx` |
| 阿里妈妈-平台登录 | `activity_d91a274e/process6.py` | `platforms/alimama/alimama_platform_login_pw.py` | ported，区别于数智登录 `alimama_login_pw.py`。平台首页只有源码字典里的六个 |

环境变量：`OCEANENGINE_COLLECTION_EMAIL` / `OCEANENGINE_COLLECTION_PASSWORD`，`SYCM_ACCOUNT` / `SYCM_PASSWORD`，`JUSHUITAN_ACCOUNT` / `JUSHUITAN_PASSWORD`，`ALIMAMA_PLATFORM` / `ALIMAMA_PLATFORM_ACCOUNT` / `ALIMAMA_PLATFORM_PASSWORD`。
