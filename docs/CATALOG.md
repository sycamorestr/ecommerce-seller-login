# 影刀指令目录

状态：`ported` 已有 Playwright 或 API 模块；`desktop-only` 只有 Windows 客户端；`captcha-only` 只移植了识别参数；`skipped` 没有登录实现，原因见 [`unported.md`](unported.md)。

已有根目录 `*_login_pw.py` 保持原路径，不改 import。

## 1. 国内电商登录

详见 [`ecommerce.md`](ecommerce.md)。

| 指令 | 模块 | 状态 |
| --- | --- | --- |
| 千牛登录 | `qianniu_login_pw.py` | ported |
| 京麦登录 | `jingmai_login_pw.py` | ported |
| 拼多多商家后台 | `pdd_login_pw.py` | ported |
| 抖店登录（单店） | `doudian_login_pw.py` | ported |
| 支付宝登录 | `alipay_login_pw.py` | ported |
| 巨量登录 | `oceanengine_login_pw.py` | ported |
| 巨量引擎邮箱登录 | `oceanengine_email_login_pw.py` | ported |
| 巨量纵横登录 | `oceanengine_zongheng_login_pw.py` | ported |
| 有赞登录 | `youzan_login_pw.py` | ported |
| 京东登录 | `jd_login_pw.py` | ported |
| 京东登录-京准通 | `jzt_login_pw.py` | ported |
| 淘宝登录 | `taobao_login_pw.py` | ported |
| 淘宝 mini 登录 | `taobao_mini_login_pw.py` | ported |
| 电商罗盘登录 | `compass_login_pw.py` | ported |
| 电商罗盘策略登陆 | `compass_strategy_login_pw.py` | ported |
| 爱库存登录 | `aikucun_login_pw.py` | ported |
| 阿里妈妈数智登录 | `alimama_login_pw.py` | ported |
| 拼多多推广平台登录 | `pdd_promote_login_pw.py` | ported |
| 拼多多商家后台（待下架） | `pdd_mms_legacy_login_pw.py` | ported，`DEPRECATED = True` |
| 1688 登录 | `login_1688_pw.py` | ported |
| 天猫超市登录 | `tmall_supermarket_login_pw.py` | ported |

## 2. 抖店多店铺 / 切店

详见 [`doudian_ops.md`](doudian_ops.md)。

| 指令 | 模块 | 状态 |
| --- | --- | --- |
| 抖店多店铺登录 `activity_966451c9/process1.py` | `doudian_multi_login_pw.py` | ported |
| 抖店店铺切换 `process13.py` → `process17.py` | `doudian_switch_shop_pw.py` | ported |
| 抖店店铺切换(ID) `process35.py` → `process36.py` | `doudian_switch_shop_pw.py` | ported |
| `process37.py` | — | skipped，不是切店 |

## 3. 银行网银登录

详见 [`banks.md`](banks.md)。27 个 `banks/*_login_pw.py`，全部 `ported`。hidden 的成都农商、绵阳商业银行、宁波银行也移植了。

## 4. 跨境

详见 [`crossborder.md`](crossborder.md)。

| 指令 | 模块 | 状态 |
| --- | --- | --- |
| 亚马逊-店铺登录 | `amazon_login_pw.py` | ported |
| Temu-账号登录 | `temu_login_pw.py` | ported |
| Temu-切换店铺 | `temu_switch_store_pw.py` | ported |
| Temu-广告平台-登录 | `temu_ads_login_pw.py` | ported |
| Temu-广告平台-切换店铺 | `temu_switch_store_pw.py` | ported |
| 速卖通登录 | `aliexpress_login_pw.py` | ported |
| 紫鸟登录 | `ziniao_login_pw.py` | desktop-only |

## 5. ERP / 税务 / 其他

详见 [`erp_tax.md`](erp_tax.md)。

| 指令 | 模块 | 状态 |
| --- | --- | --- |
| 巨量引擎登录（合集 `activity_52aea4a0`） | `oceanengine_collection_login_pw.py` | ported，不是别名 |
| 生意参谋登录Plus | `sycm_login_pw.py` | ported |
| 电子税局登录 | `tax_invoice_login_pw.py` | ported（HTTP API，无浏览器 URL） |
| 聚水潭登录 | `jushuitan_login_pw.py` | ported |
| 阿里妈妈-平台登录 | `alimama_platform_login_pw.py` | ported |
| 登录金蝶云星空 | `kingdee_login_pw.py` | ported（源码不提供 URL） |
| 登录旺店通 | `wangdiantong_login_pw.py` | desktop-only |

## 6. Cookie / 验证码辅助

| 指令 | 模块 | 状态 |
| --- | --- | --- |
| 保存 Cookie / Cookie 登录 / 退出 | `cookie_login_pw.py` | ported |
| 云码、图鉴、银行滑块、美团距离、沃尔玛长按 | `captcha_helpers.py` | captcha-only |

未列入上表、且没有登录 URL 的子流程见 [`unported.md`](unported.md)。
