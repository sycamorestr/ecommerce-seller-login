"""Live Playwright run of 影刀-faithful qianniu_login_pw. Secrets via env only."""
import os
import sys
import time
import traceback
from pathlib import Path

os.environ.setdefault("DISPLAY", ":2")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import platforms.qianniu.qianniu_login_pw as q

SHOT_DIR = ROOT / "shots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)
SHOT = str(SHOT_DIR / "pw_live")

REQUIRED = ("QIANNIU_ACCOUNT", "QIANNIU_PASSWORD", "YUNMA_TOKEN")
missing = [name for name in REQUIRED if not os.environ.get(name)]
if missing:
    print("缺少环境变量: " + ", ".join(missing), file=sys.stderr)
    print("请设置 QIANNIU_ACCOUNT / QIANNIU_PASSWORD / YUNMA_TOKEN，不要把凭据写进仓库。", file=sys.stderr)
    sys.exit(2)

account = os.environ["QIANNIU_ACCOUNT"]
password = os.environ["QIANNIU_PASSWORD"]
token = os.environ["YUNMA_TOKEN"]
print("START pw login url=", q.LOGIN_URL, "account_len=", len(account), flush=True)

r = None
try:
    r = q.qianniu_login(
        account=account,
        password=password,
        yunma_token=token,
        retries=5,
        print_error_log=True,
    )
    if r.ok:
        print(
            "LOGIN_OK url=",
            r.web_page.url if r.web_page else None,
            "yunma_calls=",
            r.yunma_calls,
            "shots=",
            r.shots,
            flush=True,
        )
        if r.web_page:
            r.web_page.screenshot(path=SHOT + "_ok.png", full_page=True)
            print("SHOT", SHOT + "_ok.png", flush=True)
        q.close_result(r)
        sys.exit(0)
    else:
        print("LOGIN_NOT_OK error=", (r.error or "")[:500], flush=True)
        if r.web_page:
            try:
                r.web_page.screenshot(path=SHOT + "_human.png", full_page=True)
                print("SHOT", SHOT + "_human.png", flush=True)
                print("PAGE_URL:", r.web_page.url, flush=True)
                print("PAGE_TITLE:", r.web_page.title(), flush=True)
                body = r.web_page.locator("body").inner_text(timeout=5000)
                print("BODY_TEXT_SNIP:\n", body[:2500], flush=True)
            except Exception:
                traceback.print_exc()
            (SHOT_DIR / "browser_keep.flag").write_text("pw1")
            print("BROWSER_LEFT_OPEN=1", flush=True)
            time.sleep(120)
        q.close_result(r)
        sys.exit(10)
except Exception as e:
    print("LOGIN_FAIL:", type(e).__name__, str(e)[:800], flush=True)
    traceback.print_exc()
    if r is not None:
        try:
            if r.web_page:
                r.web_page.screenshot(path=SHOT + "_fail.png", full_page=True)
                print("SHOT", SHOT + "_fail.png", flush=True)
        except Exception:
            pass
        q.close_result(r)
    sys.exit(1)
