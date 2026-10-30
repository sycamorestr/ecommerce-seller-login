# 抖店多店铺 / 切店

来源 `activity_966451c9`。单店登录仍是根目录 `doudian_login_pw.py`（`activity_7bca6d/process4.py`），这里不重复。

| 指令 | 源文件 | 模块 | 状态 |
| --- | --- | --- | --- |
| 抖店多店铺登录 | `process1.py` | `doudian_multi_login_pw.py` | ported。地址 `https://fxg.jinritemai.com/login/common`，然后按店铺名走切店 |
| 抖店店铺切换 | `process13.py` | `doudian_switch_shop_pw.switch_by_name` | ported。process13 只调用 process17 |
| 抖店店铺切换（新） | `process17.py`（块标题在 JSON 里仍是「抖店店铺切换」，流程注释写「新」） | 同上 | ported。列表页 `https://fxg.jinritemai.com/ffa/multiShop`，名称在 `headerShopName` / `index_roleItem` |
| 抖店店铺切换(ID) | `process35.py` | `doudian_switch_shop_pw.switch_by_id` | ported。process35 只调用 process36 |
| 抖店店铺切换(ID)(新) | `process36.py`（JSON 标题是「子流程2」，流程注释是 ID 新版） | 同上 | ported。当前店 ID 读 `//div[@label="店铺ID"]` 的 `value` |
| process37 | `process37.py` | 无 | skipped。这是售后时间选择的测试子流程，不是切店 |

环境变量：沿用 `DOUDIAN_ACCOUNT` / `DOUDIAN_PASSWORD` / `YUNMA_TOKEN`。切店用 `DOUDIAN_SHOP` 或 `DOUDIAN_SHOP_ID`。点选验证码没有识别器时仍是 `NeedsHumanError`（源文案「验证码识别失败，需人工确认」）。
