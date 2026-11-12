import json

import pytest
from playwright.sync_api import sync_playwright

from platforms.cookie.cookie_login_pw import (
    get_cookie,
    get_cookies,
    get_cookies_v2,
    normalize_cookie,
    remove_cookie,
    save_login_info,
    set_cookie,
    visual_get_cookies_v2,
    visual_remove_cookie,
    visual_set_cookie,
)


def test_expiration_strings():
    unix = normalize_cookie({"name": "a", "expirationDate": "2026-08-07T03:38:19.517Z"})
    assert unix["expires"] == int(__import__("datetime").datetime(2026, 8, 7, 3, 38, 19, tzinfo=__import__("datetime").timezone.utc).timestamp())
    assert unix["sessionCookie"] is False
    us = normalize_cookie({"name": "a", "expirationDate": "10/5/2026, 05:41:39"})
    assert us["expires"]
    assert "expirationDate" not in us


def test_cookie_instructions_roundtrip(tmp_path):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("data:text/html,<title>cookie</title><script>localStorage.setItem('k','v')</script>")
        set_cookie(
            "https://shop.example.com/home",
            page=page,
            name="sid",
            value="1",
            sessionCookie=False,
            expires=3600,
            secure=False,
        )
        set_cookie(
            "https://shop.example.com/home",
            page=page,
            name="sec",
            value="2",
            sessionCookie=True,
            secure=True,
        )
        named = get_cookies("https://shop.example.com/home", page=page, name="sid")
        assert [item["name"] for item in named] == ["sid"]
        assert named[0]["expirationDate"]
        sessions = get_cookies_v2(page=page, url="https://shop.example.com/", session=True)
        assert [item["name"] for item in sessions] == ["sec"]
        persistent = visual_get_cookies_v2(
            page=page, url="https://shop.example.com/", filter_session=True, session=False,
        )
        assert [item["name"] for item in persistent] == ["sid"]
        one = get_cookie("https://shop.example.com/home", page=page, name="sid")
        assert one["value"] == "1"
        assert get_cookie("https://shop.example.com/home", page=page, name="missing") == {}
        assert get_cookies_v2(page=page, partition_key="https://taobao.com") == []
        by_domain = get_cookies_v2(page=page, domain=".example.com", name="sid")
        assert len(by_domain) == 1
        visual_set_cookie(
            url_type="manual",
            page=page,
            url="https://shop.example.com/other",
            name="extra",
            value="3",
            sessionCookie=True,
            httpOnly=False,
            secure=False,
        )
        assert get_cookie("https://shop.example.com/other", page=page, name="extra")["value"] == "3"
        remove_cookie("https://shop.example.com/home", "sid", page=page, remove_type="appoint_cookie")
        assert get_cookie("https://shop.example.com/home", page=page, name="sid") == {}
        assert get_cookie("https://shop.example.com/home", page=page, name="sec")["name"] == "sec"
        visual_remove_cookie(url_type="manual", page=page, url="https://shop.example.com/", remove_type="all", name=None)
        assert get_cookies_v2(page=page, url="https://shop.example.com/") == []
        page.goto("https://example.com/")
        set_cookie("https://example.com/", page=page, name="keep", value="9", sessionCookie=False, expires=60)
        path = tmp_path / "login.json"
        text = save_login_info(page, str(path), url="ignored", partition_key="")
        saved = json.loads(text)
        assert saved["url"].startswith("https://example.com/")
        assert saved["cookies"][0]["name"] == "keep"
        assert "expirationDate" not in saved["cookies"][0]
        assert "expires" in saved["cookies"][0]
        assert "sessionCookie" in saved["cookies"][0]
        browser.close()
