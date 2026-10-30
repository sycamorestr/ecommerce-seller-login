"""Offline checks for the remaining ShadowBot login ports."""
import json

import pytest

import aikucun_login_pw as aikucun
import alimama_login_pw as alimama
import captcha_helpers as captcha
import compass_login_pw as compass
import compass_strategy_login_pw as strategy
import cookie_login_pw as cookies
import jd_login_pw as jd
import jzt_login_pw as jzt
import login_1688_pw as ali1688
import oceanengine_email_login_pw as oe_mail
import oceanengine_login_pw as ocean
import oceanengine_zongheng_login_pw as zongheng
import pdd_mms_legacy_login_pw as pdd_old
import pdd_promote_login_pw as pdd_ad
import taobao_login_pw as taobao
import taobao_mini_login_pw as mini
import tmall_supermarket_login_pw as tmall
import wangdiantong_login_pw as wdt
import youzan_login_pw as youzan


def test_login_urls():
    assert ocean.LOGIN_URL == "https://business.oceanengine.com/login"
    assert oe_mail.LOGIN_URL == "https://business.oceanengine.com/login?appKey=51"
    assert zongheng.LOGIN_URL == oe_mail.LOGIN_URL
    assert youzan.LOGIN_URL == "https://account.youzan.com/login"
    assert jd.LOGIN_URL == "https://passport.jd.com/new/login.aspx"
    assert jzt.LOGIN_URL == "https://jzt.jd.com/gw/index"
    assert taobao.LOGIN_URL == "https://login.taobao.com/member/login.jhtml"
    assert "style=minisimple" in mini.LOGIN_URL
    assert "myseller.taobao.com" in mini.LOGIN_URL
    assert compass.LOGIN_URL == "https://compass.jinritemai.com/login"
    assert strategy.LOGIN_URL == "https://compassbrand.jinritemai.com/login"
    assert aikucun.LOGIN_URL == "https://merc.aikucun.com/login.html"
    assert alimama.LOGIN_URL == "https://www.alimama.com/index.htm"
    assert pdd_ad.HOME_URL == "https://mms.pinduoduo.com/home/"
    assert pdd_ad.LOGOUT_URL == "https://mms.pinduoduo.com/janus/api/logout"
    assert pdd_old.HOME_URL == pdd_ad.HOME_URL
    assert "from=1688web" in ali1688.LOGIN_URL
    assert tmall.LOGIN_URL.startswith("https://web.txcs.tmall.com/login")


def test_selectors_and_flags():
    assert ocean.SEL_EMAIL.startswith("input")
    assert "请输入邮箱" in ocean.SEL_EMAIL
    assert youzan.SEL_DRAG == "#slideIconRef"
    assert jd.SMS_MESSAGE == "当前账号需要短信验证"
    assert jd.SEL_PASSWORD == "#nloginpwd"
    assert taobao.SMS_MESSAGE == "登录需要短信验证，请手动完成短信验证登录"
    assert taobao.SEL_SMS == "#J_GetCode"
    assert mini.SEL_USER == "#fm-login-id"
    assert alimama.SMS_MESSAGE == "需要进行短信验证！"
    assert pdd_old.DEPRECATED is True
    assert pdd_old.SHADOWBOT_PROCESS == "process43"
    assert compass.SEL_BG == "img.captcha-verify-image"
    assert strategy.SEL_BACK == "div.index_backbar__3dcm0"
    assert aikucun.SEL_LOGIN == "button.merchant_login_btn"
    assert "fm-login-id" in tmall.SEL_USER


def test_missing_credentials(monkeypatch):
    for key in (
        "OCEANENGINE_ACCOUNT",
        "OCEANENGINE_PASSWORD",
        "YUNMA_TOKEN",
        "OCEANENGINE_EMAIL",
        "OCEANENGINE_EMAIL_PASSWORD",
        "OCEANENGINE_ZH_ACCOUNT",
        "OCEANENGINE_ZH_PASSWORD",
        "YOUZAN_ACCOUNT",
        "YOUZAN_PASSWORD",
        "JD_ACCOUNT",
        "JD_PASSWORD",
        "JZT_ACCOUNT",
        "JZT_PASSWORD",
        "TAOBAO_ACCOUNT",
        "TAOBAO_PASSWORD",
        "TAOBAO_MINI_ACCOUNT",
        "TAOBAO_MINI_PASSWORD",
        "COMPASS_ACCOUNT",
        "COMPASS_PASSWORD",
        "COMPASS_STRATEGY_ACCOUNT",
        "COMPASS_STRATEGY_PASSWORD",
        "AIKUCUN_ACCOUNT",
        "AIKUCUN_PASSWORD",
        "ALIMAMA_ACCOUNT",
        "ALIMAMA_PASSWORD",
        "PDD_PROMOTE_ACCOUNT",
        "PDD_PROMOTE_PASSWORD",
        "PDD_LEGACY_ACCOUNT",
        "PDD_LEGACY_PASSWORD",
        "LOGIN1688_ACCOUNT",
        "LOGIN1688_PASSWORD",
        "TMALL_SUPERMARKET_ACCOUNT",
        "TMALL_SUPERMARKET_PASSWORD",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("YUNMA_TOKEN", "tok")
    with pytest.raises(ValueError):
        ocean.oceanengine_login()
    with pytest.raises(ValueError):
        oe_mail.oceanengine_email_login()
    with pytest.raises(ValueError):
        zongheng.oceanengine_zongheng_login()
    with pytest.raises(ValueError):
        youzan.youzan_login()
    with pytest.raises(ValueError):
        jd.jd_login()
    with pytest.raises(ValueError):
        jzt.jzt_login()
    with pytest.raises(ValueError):
        taobao.taobao_login()
    with pytest.raises(ValueError):
        mini.taobao_mini_login()
    with pytest.raises(ValueError):
        compass.compass_login()
    with pytest.raises(ValueError):
        strategy.compass_strategy_login()
    with pytest.raises(ValueError):
        aikucun.aikucun_login()
    with pytest.raises(ValueError):
        alimama.alimama_login()
    with pytest.raises(ValueError):
        pdd_ad.pdd_promote_login()
    with pytest.raises(ValueError):
        pdd_old.pdd_mms_legacy_login()
    with pytest.raises(ValueError):
        ali1688.login_1688()
    with pytest.raises(ValueError):
        tmall.tmall_supermarket_login()


def test_payloads_and_distances():
    assert captcha.ali_slider_payload("img", "tok")["type"] == 20226
    assert captcha.jd_click_payload("img", "tok") == {
        "image": "img",
        "token": "tok",
        "type": 30330,
    }
    rotate = captcha.jd_rotate_payload("big", "small", "tok")
    assert rotate["type"] == 30330 and rotate["image2"] == "small"
    assert captcha.jd_trace_payload("img", "tok")["type"] == 100015
    plus = captcha.std_click_plus_payload("img", "tok")
    assert plus["type"] == 30009 and plus["direction"] == "bottom"
    assert captcha.jd_legacy_slider_distance("120,88", 30, 1) == 150
    assert captcha.free_slider_drag_distance(40, captcha.AIKUCUN_FREE_SLIDER_OFFSET) == 36
    assert captcha.free_slider_drag_distance(40, 0, ppi=2, windows=True) == 40
    assert captcha.meituan_slider_distance(300, 40) == 260
    assert captcha.meituan_trace_points(list(range(30))) == list(range(25, 30))
    assert captcha.WALMART_HOLD_SECONDS == 7
    assert captcha.TTSHITU_PDD_ONE_CLICK_TYPE == "19"
    assert captcha.TTSHITU_WANGDIANTONG_TYPE == "3"
    assert captcha.legacy_click_point("10", "20", 5, 6, 1, 2, 1) == (11, 22)
    assert captcha.AIKUCUN_FREE_SLIDER_OFFSET == -4
    assert youzan.PHONE_GATE.startswith("登录失败")


def test_jzt_platform_map():
    assert jzt.platform_url("京东快车") == "https://jzt.jd.com/jdkc/survey.html#/survey"
    assert jzt.platform_url("京东数坊") == ""
    assert jzt.platform_url("商智-商家版") == "https://sz.jd.com"
    assert "京东联盟" in jzt.PLATFORM_URLS


def test_tmall_supplier_rules():
    assert tmall.supplier_name("店铺 -- 经销") == "店铺"
    assert tmall.match_supplier(["甲 -- 经销", "乙 -- 代销"], "乙 -- 代销") == 1
    with pytest.raises(ValueError):
        tmall.match_supplier(["甲"], "乙")
    with pytest.raises(ValueError):
        tmall.match_supplier(["甲 -- 经销", "甲 -- 经销"], "甲 -- 经销")
    tmall.verify_supplier("店铺", "店铺 -- 经销")
    tmall.verify_identity("12-店铺-经销", "店铺 -- 经销")
    with pytest.raises(Exception):
        tmall.verify_identity("其他", "店铺 -- 经销")


def test_cookie_roundtrip(tmp_path):
    assert cookies.extract_domain_from_url("https://www.shop.example.com/home") == "shop.example.com"
    raw = {"name": "sid", "value": "1", "expirationDate": "2026-01-02 03:04:05", "domain": ".example.com", "path": "/"}
    normalized = cookies.normalize_cookie(raw)
    assert normalized["expires"]
    assert normalized["sessionCookie"] is False
    assert "expirationDate" not in normalized
    empty = cookies.normalize_cookie({"name": "", "value": "x"})
    assert empty["sessionCookie"] is True

    class FakeContext:
        def __init__(self):
            self.jar = [{"name": "sid", "value": "1", "expires": 1, "domain": ".example.com", "path": "/"}]
            self.added = None

        def cookies(self):
            return list(self.jar)

        def clear_cookies(self):
            self.jar.clear()

        def add_cookies(self, items):
            self.added = items

    class FakePage:
        def __init__(self):
            self.context = FakeContext()
            self.url = "https://shop.example.com/home"
            self.storage = {"k": "v"}
            self.gone = []

        def evaluate(self, script, arg=None):
            if arg is not None:
                self.storage[arg["key"]] = arg["value"]
                return None
            if "clear" in script:
                self.storage.clear()
                return None
            if "origin" in script:
                return "https://shop.example.com"
            return dict(self.storage)

        def goto(self, url, **_kwargs):
            self.gone.append(url)

    page = FakePage()
    path = tmp_path / "cookies.json"
    text = cookies.save_login_info(page, str(path))
    saved = json.loads(text)
    assert saved["url"].endswith("/home")
    assert saved["local_storage"]["k"] == "v"
    cookies.login(page, str(path), add_local_storage=True)
    assert page.context.added[0]["name"] == "sid"
    cookies.logout(page, del_local_storage=True)
    assert page.storage == {}
    with pytest.raises(Exception):
        cookies.save_cookies(None)


def test_wangdiantong_is_desktop_only():
    with pytest.raises(wdt.DesktopOnlyLogin):
        wdt.wangdiantong_login()
    assert wdt.CAPTCHA_TYPE == "3"
    assert "ttshitu_3_predict" in wdt.REASON


def test_docs_mentions_skipped():
    text = open("docs/UNPORTED_BLOCKS.md", encoding="utf-8").read()
    assert "登录旺店通" in text
    assert "京东数坊" in text
    assert "trace_api" in text
