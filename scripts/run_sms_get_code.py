"""Re-run PW login to SMS gate, click 点击获取验证码, leave browser open."""
import os
import sys
import time
import traceback
from pathlib import Path

os.environ.setdefault("DISPLAY", ":2")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import platforms.qianniu.qianniu_login_pw as q

SHOT = ROOT / "shots"
SHOT.mkdir(parents=True, exist_ok=True)

REQUIRED = ("QIANNIU_ACCOUNT", "QIANNIU_PASSWORD", "YUNMA_TOKEN")
missing = [name for name in REQUIRED if not os.environ.get(name)]
if missing:
    print("缺少环境变量: " + ", ".join(missing), file=sys.stderr)
    print("请设置 QIANNIU_ACCOUNT / QIANNIU_PASSWORD / YUNMA_TOKEN，不要把凭据写进仓库。", file=sys.stderr)
    sys.exit(2)

account = os.environ["QIANNIU_ACCOUNT"]
password = os.environ["QIANNIU_PASSWORD"]
token = os.environ["YUNMA_TOKEN"]
print("START sms-get-code account_len=", len(account), flush=True)

r = q.qianniu_login(
    account=account,
    password=password,
    yunma_token=token,
    retries=5,
    print_error_log=True,
)
print("RESULT ok=", r.ok, "error=", (r.error or "")[:300], flush=True)
page = r.web_page
if page is None:
    print("NO_PAGE", flush=True)
    sys.exit(2)


def try_click_get_code(p):
    # Prefer exact link text; try main page and login iframe / nested.
    selectors = [
        "text=点击获取验证码",
        "a:has-text('点击获取验证码')",
        "span:has-text('点击获取验证码')",
        "button:has-text('点击获取验证码')",
        "text=获取验证码",
    ]
    # top page
    for sel in selectors:
        loc = p.locator(sel).first
        try:
            if loc.count() and loc.is_visible(timeout=1500):
                loc.click(timeout=5000)
                print("CLICKED via", sel, "on top page", flush=True)
                return True
        except Exception as e:
            print("try top", sel, type(e).__name__, flush=True)
    # login iframe
    try:
        fl = p.frame_locator("iframe#alibaba-login-box")
        for sel in selectors:
            loc = fl.locator(sel).first
            try:
                if loc.count() and loc.is_visible(timeout=1500):
                    loc.click(timeout=5000)
                    print("CLICKED via", sel, "in login iframe", flush=True)
                    return True
            except Exception as e:
                print("try iframe", sel, type(e).__name__, flush=True)
    except Exception as e:
        print("login iframe fail", e, flush=True)
    # all frames
    for fr in p.frames:
        for sel in selectors:
            try:
                loc = fr.locator(sel).first
                if loc.count() and loc.is_visible(timeout=800):
                    loc.click(timeout=5000)
                    print("CLICKED via", sel, "in frame", fr.url[:80], flush=True)
                    return True
            except Exception:
                pass
    return False


try:
    page.screenshot(path=str(SHOT / "pw_sms_before_click.png"), full_page=True)
    print("URL", page.url, flush=True)
    ok = try_click_get_code(page)
    time.sleep(2)
    page.screenshot(path=str(SHOT / "pw_sms_after_click.png"), full_page=True)
    if not ok:
        print("CLICK_FAILED", flush=True)
        try:
            print("BODY:\n", page.locator("body").inner_text(timeout=3000)[:2000], flush=True)
        except Exception:
            traceback.print_exc()
        (SHOT / "browser_keep.flag").write_text("pw_sms_nofind")
        time.sleep(600)
        q.close_result(r)
        sys.exit(3)
    print("CLICK_OK", flush=True)
    try:
        print("BODY_AFTER:\n", page.locator("body").inner_text(timeout=3000)[:2000], flush=True)
    except Exception:
        pass
    (SHOT / "browser_keep.flag").write_text("pw_sms_waiting_code")
    (SHOT / "pw_sms_page.url").write_text(page.url or "")
    print("WAITING_FOR_CODE park 900s", flush=True)
    time.sleep(900)
finally:
    try:
        q.close_result(r)
    except Exception:
        pass
