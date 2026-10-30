"""Offline checks for 登陆拓展合集 ports. No browser, no secrets."""
import importlib
from pathlib import Path

import pytest

import platforms.aliexpress.aliexpress_login_pw as ali
import platforms.alimama.alimama_platform_login_pw as mama
import platforms.amazon.amazon_login_pw as amazon
import platforms.jd.captcha as captcha
import platforms.doudian.doudian_multi_login_pw as multi
import platforms.doudian.doudian_switch_shop_pw as switch
import platforms.jushuitan.jushuitan_login_pw as jst
import platforms.kingdee.kingdee_login_pw as kingdee
import platforms.oceanengine.oceanengine_collection_login_pw as oe
import platforms.oceanengine.oceanengine_email_login_pw as oe_mail
import platforms.sycm.sycm_login_pw as sycm
import platforms.tax_invoice.tax_invoice_login_pw as tax
import platforms.temu.temu_ads_login_pw as temu_ads
import platforms.temu.temu_login_pw as temu
import platforms.temu.temu_switch_store_pw as temu_sw
import platforms.ziniao.ziniao_login_pw as ziniao
from platforms.tax_invoice.helpers import NeedsHumanError
from platforms.ziniao.helpers import DesktopOnlyLogin


def test_bank_urls_and_missing_creds(monkeypatch):
    modules = []
    for folder in sorted(p for p in Path("banks").iterdir() if p.is_dir()):
        for py in sorted(folder.glob("*_login_pw.py")):
            modules.append(importlib.import_module(f"banks.{folder.name}.{py.stem}"))
    assert len(modules) >= 26
    monkeypatch.delenv("YUNMA_TOKEN", raising=False)
    for mod in modules:
        urls = getattr(mod, "LOGIN_URLS", None) or {"default": mod.LOGIN_URL}
        for url in urls.values():
            assert url.startswith("https://"), mod.__name__
        prefix = mod.ENV_PREFIX
        monkeypatch.delenv(f"{prefix}_ACCOUNT", raising=False)
        monkeypatch.delenv(f"{prefix}_PASSWORD", raising=False)
        fn = getattr(mod, f"{mod.SPEC.slug}_login")
        with pytest.raises(ValueError):
            fn()


def test_captcha_payloads():
    body = captcha.alphanum_payload("img", "tok", "10103", case_sensitive=True)
    assert body["type"] == "10103"
    assert body["extra"] == "需要区分大小写"
    king = captcha.alphanum_payload("img", "tok", captcha.YUNMA_TYPE_KINGDEE_ALPHANUM)
    assert king["type"] == "10110"
    assert "extra" not in king
    assert captcha.TTSHITU_CDRCBANK_TYPE == "4"
    assert captcha.TTSHITU_MYCCBANK_TYPE == "66"
    assert captcha.orangebank_gap_offset(10, 40) == 30


def test_doudian_ops_constants():
    assert multi.LOGIN_URL == "https://fxg.jinritemai.com/login/common"
    assert switch.MULTI_SHOP_URL == "https://fxg.jinritemai.com/ffa/multiShop"
    assert "process17" in switch.NEW_NAME_SOURCE
    assert "process36" in switch.NEW_ID_SOURCE
    assert "process37" in switch.PROCESS37_NOTE
    assert "headerShopName" in switch.XPATH_HEADER_SHOP
    assert switch.XPATH_SHOP_ID == '//div[@label="店铺ID"]'


def test_collection_logins(monkeypatch):
    assert oe.LOGIN_URL == "https://business.oceanengine.com/login?appKey=51"
    assert oe.SLIDER_TRIES == 7
    assert oe.LOGIN_URL != "https://business.oceanengine.com/login"
    assert oe.SOURCE != "activity_7bca6d/process47.py"
    assert oe_mail.LOGIN_URL == oe.LOGIN_URL
    monkeypatch.delenv("OCEANENGINE_COLLECTION_EMAIL", raising=False)
    monkeypatch.delenv("OCEANENGINE_COLLECTION_PASSWORD", raising=False)
    with pytest.raises(ValueError):
        oe.oceanengine_collection_login()
    with pytest.raises(DesktopOnlyLogin):
        ziniao.ziniao_login()
    assert ziniao.CLIENT_TITLE == "紫鸟浏览器专业版"
    assert sycm.LOGIN_URL == "https://sycm.taobao.com/custom/login.htm"
    assert sycm.HOME_URL == "https://sycm.taobao.com/portal/home.htm"
    assert jst.LOGIN_URL == "https://www.erp321.com/login.aspx"
    assert "fm-login-id" in jst.XPATH_ACCOUNT or "邮箱" in jst.XPATH_ACCOUNT
    assert kingdee.LOGIN_URL == ""
    assert kingdee.CAPTCHA_TYPE == "10110"
    assert kingdee.SEL_USER == "#user"
    assert mama.PLATFORM_URLS["直通车"] == "https://subway.simba.taobao.com/index.jsp"
    assert mama.PLATFORM_URLS["商家中心"].startswith("https://ad.alimama.com/")
    assert amazon.LOGIN_BTN == '//input[@id="signInSubmit"]'
    assert amazon._is_login_page("https://www.amazon.com/ap/signin")
    assert not amazon._is_login_page("https://sellercentral.amazon.com/home")
    assert temu.LOGIN_URL == "https://seller.kuajingmaihuo.com/login"
    assert temu_ads.LOGIN_URL == "https://ads.temu.com/login.html"
    assert "半托管" in temu_sw.XPATH_ADS_STORES
    assert ali.login_url("zh_CN").startswith("https://login.aliexpress.com/user/seller/login?bizSegment=CSP")
    assert ali.extract_email_code("一次性验证码是 123456") == "123456"
    assert ali.BAD_PASSWORD.startswith("您的帐户名或密码不正确")
    assert tax.API_BASE_URL == "https://openapi.njmbxx.com"
    body = tax.tax_login_body("ns", "user", "pw", "998877")
    assert body["sms_code"] == "998877"
    assert "password" in body and body["password"] == "pw"


def test_tax_and_crossborder_guards(monkeypatch):
    for key in (
        "TAX_APP_ID",
        "TAX_APP_SECRET",
        "TAX_ACCOUNT",
        "TAX_PASSWORD",
        "TAX_NSRSBH",
        "SYCM_ACCOUNT",
        "SYCM_PASSWORD",
        "JUSHUITAN_ACCOUNT",
        "JUSHUITAN_PASSWORD",
        "KINGDEE_ACCOUNT",
        "KINGDEE_PASSWORD",
        "ALIMAMA_PLATFORM_ACCOUNT",
        "ALIMAMA_PLATFORM_PASSWORD",
        "TEMU_ACCOUNT",
        "TEMU_PASSWORD",
        "TEMU_ADS_ACCOUNT",
        "TEMU_ADS_PASSWORD",
        "ALIEXPRESS_ACCOUNT",
        "ALIEXPRESS_PASSWORD",
    ):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValueError):
        tax.tax_invoice_login()
    monkeypatch.setenv("TAX_APP_ID", "app")
    monkeypatch.setenv("TAX_APP_SECRET", "sec")
    monkeypatch.setenv("TAX_ACCOUNT", "acct")
    monkeypatch.setenv("TAX_PASSWORD", "pw")
    monkeypatch.setenv("TAX_NSRSBH", "ns")
    with pytest.raises(NeedsHumanError):
        tax.tax_invoice_login(sms_required=True, is_qr_code=True)
    with pytest.raises(ValueError):
        sycm.sycm_login()
    with pytest.raises(ValueError):
        jst.jushuitan_login()
    with pytest.raises(ValueError):
        kingdee.kingdee_login()
    with pytest.raises(ValueError):
        mama.alimama_platform_login()
    with pytest.raises(ValueError):
        temu.temu_login()
    with pytest.raises(ValueError):
        temu_ads.temu_ads_login()
    with pytest.raises(ValueError):
        ali.aliexpress_login()
    with pytest.raises(ValueError):
        temu_sw.switch_seller("")
