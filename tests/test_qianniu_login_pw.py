"""Unit tests for the Playwright ShadowBot-faithful port (no live network)."""
import json
from unittest import mock
import pytest
import platforms.qianniu.qianniu_login_pw as q


def test_yunma_recg_payload(monkeypatch):
    class FakeResp:
        def read(self):
            return json.dumps(
                {"msg": "识别成功", "data": {"data": "120"}}
            ).encode()

        def getresponse(self):
            return self

    class FakeConn:
        def __init__(self, *a, **k):
            self.body = None
            self.path = None

        def request(self, method, path, body=None, headers=None):
            self.path = path
            self.body = json.loads(body)

        def getresponse(self):
            return FakeResp()

        def close(self):
            pass

    fake = FakeConn()
    monkeypatch.setattr(q.http.client, "HTTPConnection", lambda *a, **k: fake)
    out = q.yunma_recg("tok", "abc")
    assert out["msg"] == "识别成功"
    assert fake.path == q.YUNMA_PATH
    assert fake.body == {"image": "abc", "token": "tok", "type": 20226}


def test_join_images_height():
    from PIL import Image

    a = Image.new("RGBA", (100, 30), (1, 2, 3, 255))
    b = Image.new("RGBA", (320, 180), (4, 5, 6, 255))
    j = q.join_images(a, b)
    assert j.size == (320, 30 + 180 + 11)


def test_distance_formula():
    # mirrors ali_slider_captcha: (distance-24-10)/320 * 320
    distance = 120
    pct = (int(distance) - 24 - 10) / 320
    assert int(320 * pct) == 86


def test_missing_creds(monkeypatch):
    monkeypatch.delenv("QIANNIU_ACCOUNT", raising=False)
    monkeypatch.delenv("QIANNIU_PASSWORD", raising=False)
    with pytest.raises(ValueError):
        q.qianniu_login(account="", password="x", yunma_token="t")


def test_onerror_ignore(monkeypatch):
    monkeypatch.setattr(
        q, "login", mock.Mock(side_effect=RuntimeError("boom"))
    )
    r = q.qianniu_login(
        "a",
        "b",
        "t",
        page=mock.Mock(),
        on_error=q.OnError.IGNORE,
        print_error_log=False,
    )
    assert not r.ok and "boom" in (r.error or "")


def test_needs_human_returned(monkeypatch):
    monkeypatch.setattr(
        q, "login", mock.Mock(side_effect=q.NeedsHumanError("短信验证"))
    )
    r = q.qianniu_login("a", "b", "t", page=mock.Mock(), print_error_log=False)
    assert not r.ok and r.error == "短信验证"


def test_login_url_constant():
    assert q.LOGIN_URL == "https://loginmyseller.taobao.com/"


def test_selectors():
    assert q.SEL_USERNAME == "#fm-login-id"
    assert q.SEL_NC_SLIDE == "#nc_1_n1z"
    assert q.SEL_NC_VERIFY == "#nc_1__scale_text"
    assert q.YUNMA_TYPE_ALI_SLIDER == 20226
