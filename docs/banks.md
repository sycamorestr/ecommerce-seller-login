# 银行网银登录

来源是影刀应用「登陆拓展合集」里的 `activity_e05c2690`。每家银行一个目录 `banks/<银行>/`，登录入口和 `helpers.py`、`captcha.py` 放在一起。

个人版和企业版 URL 都在该目录登录模块的 `LOGIN_URLS` 里。源码没有的地址不会补。签名控件 / UKey 文案命中时抛该目录的 `NeedsHumanError`。数英验证码走云码 `type=10103`（目录内 `captcha.alphanum_payload`）。滑块仍是 `22222`。成都农商验证码是图鉴 `captcha_type=4` / `ttshitu_4_predict`。绵阳商业银行是 `66` / `ttshitu_66_predict`。

环境变量：`<ENV_PREFIX>_ACCOUNT`、`<ENV_PREFIX>_PASSWORD`，可选 `<ENV_PREFIX>_LOAD_TYPE`。招商银行证书密码是 `CMB_CERT_PASSWORD`。交通银行客户号登录另见 `banks/bocom/jiaotong_custom_login_pw.py`（`BOCOM_CUSTOM_ACCOUNT` 是客户号）。

| 银行 | 源文件 | 模块 | 可见性 | 登录地址 |
| --- | --- | --- | --- | --- |
| 北京银行 | `activity_e05c2690/bankofbeijing_load.py` | `banks/bob/` | public | https://ibank.bankofbeijing.com.cn/login?redirect=%2F ; https://cbank.bankofbeijing.com.cn/login?version=query |
| 中国银行 | `activity_e05c2690/bankofchina_load.py` | `banks/boc/` | public | https://netc1.igtb.bankofchina.com/#/login-page?redirect=%2Findex |
| 中国建设银行 | `activity_e05c2690/ccbbank_load.py` | `banks/ccb/` | public | https://ebanking1.ccb.com.cn/CCBIS/V6/common/loginNew.jsp |
| 成都农商银行 | `activity_e05c2690/cdrcbank_load.py` | `banks/cdrcbank/` | hidden | https://ebank.cdrcbank.com/perbank/ ; https://ebank.cdrcbank.com/corporbank/index.jsp |
| 光大银行 | `activity_e05c2690/cebbank_load.py` | `banks/ceb/` | public | https://e.cebbank.com/per/prePerlogin.do?_locale=zh_CN ; https://e.cebbank.com/cebent/prelogin.do?_locale=zh_CN |
| 浦发银行 | `activity_e05c2690/ebankhent_load.py` | `banks/spdb/` | public | https://ebankhent.spdb.com.cn/msent-web-login/qryLogin.do |
| 中信银行 | `activity_e05c2690/ecitic_load.py` | `banks/ecitic/` | public | https://i.bank.ecitic.com/perbank6/signIn.do ; https://corp.bank.ecitic.com/cotb/login.html |
| 宁波银行 | `activity_e05c2690/enbcb_load.py` | `banks/nbcb/` | hidden | https://e.nbcb.com.cn/#/main ; https://cb.nbcb.com.cn/microbase/microhome/index.html?v=1730441864266#/browserQueryLogin |
| 广东华兴银行 | `activity_e05c2690/ghibank_load.py` | `banks/ghibank/` | public | https://www.ghibank.com.cn/eweb/#/index |
| 东亚银行 | `activity_e05c2690/hkbea_load.py` | `banks/hkbea/` | public | https://ebank.hkbea.com.cn/Perbank/#/login |
| 杭州银行 | `activity_e05c2690/hyzx_load.py` | `banks/hzbank/` | public | https://hyzx.hzbank.com.cn/hykx/logon.jsp |
| 工商银行 | `activity_e05c2690/icbcbank_load.py` | `banks/icbc/` | public | https://mybank.icbc.com.cn/icbc/newperbank/perbank3/frame/frame_index.jsp ; https://corporbank-simp.icbc.com.cn/frame/web/ebc/index.html |
| 交通银行客户号 | `activity_e05c2690/pbank_load_custom.py` | `banks/bocom/jiaotong_custom_login_pw.py` | public | https://ebank.bankcomm.cn/NEBS/CLG/CNLGAAA01?loginType=1 |
| 交通银行 | `activity_e05c2690/pbank_load.py` | `banks/bocom/jiaotong_login_pw.py` | public | https://pbank.bankcomm.cn/personbank/system/index.html#/login ; https://ebank.bankcomm.cn/NEBS/CLG/CNLGAAA01?loginType=1 |
| 江苏银行 | `activity_e05c2690/jsbchina_load.py` | `banks/jsbchina/` | public | https://ebank.jsbchina.cn/newperbank/ ; https://cbank.jsbchina.cn/corporbank/ |
| 绵阳市商业银行 | `activity_e05c2690/myccbank_load.py` | `banks/myccbank/` | hidden | https://pweb.mycc-bank.com/pweb/vx_zh_CN/index.html#/loginapp/UserLogin ; https://eweb.mycc-bank.com/eweb/vx_zh_CN/index.html#/loginapp/UserLogin |
| 南京银行 | `activity_e05c2690/njcbbank_load.py` | `banks/njcb/` | public | https://ebank.njcb.com.cn/perbank/login.jsp ; https://ebank.njcb.com.cn/corporbank/public/login.jsp |
| 民生银行 | `activity_e05c2690/nper_load.py` | `banks/cmbc/` | public | https://nper.cmbc.com.cn/pweb/static/login.html# |
| 平安银行 | `activity_e05c2690/orangebank_load.py` | `banks/pingan/` | public | https://auth.orangebank.com.cn/cimp-ccs-pc/#/p/ebank-login |
| 中国邮政储蓄银行 | `activity_e05c2690/pbank_psbc_load.py` | `banks/psbc/` | public | https://pbank.psbc.com/perbank/ |
| 浙商银行 | `activity_e05c2690/perbank_czbank_load.py` | `banks/czbank/` | public | https://perbank.czbank.com/PERBANK/logon.jsp ; https://corbank.czbank.com/CORPORBANK/logon.jsp |
| 兴业银行 | `activity_e05c2690/personalbank_load.py` | `banks/cib/` | public | https://personalbank.cib.com.cn/pers/main/loginV7 |
| 上海银行 | `activity_e05c2690/shanghaibank_load.py` | `banks/shanghaibank/` | public | https://ebanks.bankofshanghai.com/pweb/prelogin.do?LoginType=R&_locale=zh_CN ; https://ibank.bosc.cn:6074/eib/?#/login |
| 苏州银行 | `activity_e05c2690/suzhoubank_load.py` | `banks/suzhoubank/` | public | https://ebank.suzhoubank.com/perplat/ ; https://ebank.suzhoubank.com/corporplatBank/#/login |
| 温州银行 | `activity_e05c2690/wzbank_load.py` | `banks/wzbank/` | public | https://ebankp.wzbank.cn/ebank/static/index.html#/home |
| 招商银行 | `activity_e05c2690/zsbank_load.py` | `banks/cmb/` | public | https://u.ebank.cmbchina.com/CmbBank_FB/UI/Login/FBPOPLogin.aspx |
| 中原银行 | `activity_e05c2690/zybank_load.py` | `banks/zybank/` | public | https://pibs.zyebank.com/pweb/prelogin.do?_locale=zh_CN&LoginType=R&source=mh |

`activity_7bca6d` 里仍然没有中国银行登录指令。网银登录以本页的 `bankofchina_load.py` 为准。桔子银行滑块公式仍在 `captcha_helpers.orangebank_drag_px`，那不是中国银行登录。
