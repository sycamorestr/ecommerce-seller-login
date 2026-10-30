"""
Playwright port of 影刀市场指令「千牛登录」
(xbot_extensions.activity_7bca6d.qn_login + activity_jfbym.ali_slider_captcha).

Behavior mirrors 影刀市场指令「千牛登录」(qn_login + ali_slider_captcha).
Reverse notes: docs/qianniu_login_reverse_notes.md
Selenium sibling: qianniu_login.py (imported below as _se).

Do NOT invent alternate login URLs / captcha types. Mirror the ShadowBot steps.
Unavoidable vs Selenium: page.mouse down/move/up instead of CDP Input.dispatchMouseEvent;
Playwright FrameLocator instead of switch_to.frame (bounding_box already in top viewport CSS px).
"""
from __future__ import annotations

import base64
import http.client
import json
import os
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from PIL import Image
from playwright.sync_api import (
    Browser,
    BrowserContext,
    FrameLocator,
    Page,
    Playwright,
    sync_playwright,
)

# Re-export / reuse pure helpers from the Selenium port (identical API).
import qianniu_login as _se

# ---- constants from ShadowBot sources (same as Selenium port) ----
LOGIN_URL = _se.LOGIN_URL
YUNMA_HOST = _se.YUNMA_HOST
YUNMA_PATH = _se.YUNMA_PATH
YUNMA_TYPE_ALI_SLIDER = _se.YUNMA_TYPE_ALI_SLIDER

IFRAME_CSS = _se.IFRAME_CSS
BAXIA_IFRAME_CSS = _se.BAXIA_IFRAME_CSS
SEL_USERNAME = _se.SEL_USERNAME
SEL_PASSWORD = _se.SEL_PASSWORD
SEL_LOGIN_BTN = _se.SEL_LOGIN_BTN
SEL_DRAG_LABEL = _se.SEL_DRAG_LABEL
SEL_REFRESH = _se.SEL_REFRESH
SEL_DRAG_ELE = _se.SEL_DRAG_ELE
SEL_NC_VERIFY = _se.SEL_NC_VERIFY
SEL_NC_SLIDE = _se.SEL_NC_SLIDE
SEL_LOGIN_ERROR = _se.SEL_LOGIN_ERROR
SEL_ERRLOADING = _se.SEL_ERRLOADING

HERE = Path(__file__).resolve().parent
SHOT_DIR = HERE / "shots"
CACHE_DIR = HERE / "captcha_cache"

_LAST_OWNED: dict = {}

# Pure helpers — identical to Selenium port / ShadowBot sources
yunma_recg = _se.yunma_recg
encode_image = _se.encode_image
decode_image = _se.decode_image
join_images = _se.join_images

OnError = _se.OnError
QianniuLoginError = _se.QianniuLoginError
NeedsHumanError = _se.NeedsHumanError
CredentialsRejected = _se.CredentialsRejected


@dataclass
class QianniuLoginResult:
    ok: bool
    web_page: Optional[Page] = None
    error: Optional[str] = None
    yunma_calls: int = 0
    shots: List[str] = field(default_factory=list)
    # Keep browser/context/playwright alive when we own them (NeedsHuman leave-open)
    _browser: Optional[Browser] = field(default=None, repr=False)
    _context: Optional[BrowserContext] = field(default=None, repr=False)
    _playwright: Optional[Playwright] = field(default=None, repr=False)


def sleep(seconds: float) -> None:
    time.sleep(seconds)


# ---------------------------------------------------------------- browser launch
def create_browser(
    playwright: Playwright,
    headless: bool = False,
) -> Tuple[Browser, BrowserContext, Page]:
    """Launch Chromium with box egress proxy (same as box-chrome / Selenium port)."""
    browser = playwright.chromium.launch(
        headless=headless,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ],
        proxy={"server": "http://127.0.0.1:8791"},
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        ignore_https_errors=True,
    )
    context.add_init_script(
        "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
    )
    page = context.new_page()
    return browser, context, page


def login_frame(page: Page) -> FrameLocator:
    return page.frame_locator(IFRAME_CSS)


def baxia_frame(page: Page) -> FrameLocator:
    """Nested: top → #alibaba-login-box → #baxia-dialog-content."""
    return login_frame(page).frame_locator(BAXIA_IFRAME_CSS)


def _locator_displayed(fl: FrameLocator, css: str, timeout_ms: float = 1500) -> bool:
    try:
        loc = fl.locator(css).first
        loc.wait_for(state="visible", timeout=timeout_ms)
        return True
    except Exception:
        return False


def is_displayed(page: Page, css: str, timeout: float = 1.5, *, in_baxia: bool = False) -> bool:
    fl = baxia_frame(page) if in_baxia else login_frame(page)
    return _locator_displayed(fl, css, timeout_ms=timeout * 1000)


def nc_visible(page: Page) -> bool:
    """True when NC slide is shown — classic nocaptcha or baxia iframe."""
    fl = login_frame(page)
    if _locator_displayed(fl, SEL_NC_SLIDE, timeout_ms=600):
        return True
    for box in ("#nocaptcha-password", "#nocaptcha", ".nc-container.tb-login", ".nc-container"):
        if _locator_displayed(fl, box, timeout_ms=400):
            if _locator_displayed(fl, SEL_NC_VERIFY, timeout_ms=400) or _locator_displayed(
                fl, SEL_NC_SLIDE, timeout_ms=400
            ):
                return True
    # baxia nested
    bf = baxia_frame(page)
    if _locator_displayed(bf, SEL_NC_SLIDE, timeout_ms=1000) or _locator_displayed(
        bf, SEL_NC_VERIFY, timeout_ms=1000
    ):
        return True
    return False


def element_text_value(page: Page, locator) -> str:
    try:
        v = locator.input_value(timeout=1000)
        if v is not None:
            return v.strip()
    except Exception:
        pass
    try:
        return (locator.inner_text(timeout=1000) or "").strip()
    except Exception:
        return ""


def input_text(page: Page, locator, text: str) -> None:
    """Mirror qn_login username/password input + verify loop (i>3 -> raise)."""
    locator.click(timeout=10000)
    sleep(0.2)
    locator.fill("")
    locator.fill(text)
    got = element_text_value(page, locator)
    i = 1
    while got != text:
        # simulative=False path: JS set value + events
        locator.evaluate(
            """(el, value) => {
                el.focus();
                el.value = value;
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
            }""",
            text,
        )
        got = element_text_value(page, locator)
        i += 1
        if i > 3:
            raise QianniuLoginError("输入失败，请手动登录")


def shot(page: Page, name: str, shots: List[str]) -> None:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SHOT_DIR / f"{int(time.time())}_{name}.png"
    try:
        page.screenshot(path=str(path), full_page=False)
        shots.append(str(path))
    except Exception:
        pass


def mouse_drag(
    page: Page,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    overshoot: bool = False,
    speed: str = "middle",
) -> None:
    """Port of win32 / CDP drag via Playwright page.mouse (top-viewport CSS px).

    Geometry same as qn_login / Selenium CDP: start at (x1,y1), end at (x2,y2).
    When overshoot=True, mirrors ali_slider_captcha.drag overshoot pattern.
    """
    page.mouse.move(x1, y1)
    sleep(0.15)
    page.mouse.down()
    sleep(0.12)
    if overshoot:
        right_offset = random.randint(-5, 5)
        left_offset = random.randint(-5, 5)
        pause = 0.05 if speed == "fast" else 0.08
        page.mouse.move(x2 + right_offset, y2, steps=16)
        sleep(pause)
        page.mouse.move(x2 - left_offset, y2, steps=8)
        sleep(pause)
        page.mouse.move(x2, y2, steps=4)
        sleep(0.05)
    else:
        # ease-out cubic steps (mirrors Selenium cdp_drag)
        steps = 32
        for i in range(1, steps + 1):
            t = i / steps
            e = 1 - (1 - t) ** 3
            x = x1 + (x2 - x1) * e + random.uniform(-0.5, 0.5)
            y = y1 + (y2 - y1) * e + random.uniform(-0.4, 0.4)
            page.mouse.move(x, y)
            sleep(0.014 + (0.01 if t > 0.7 else 0))
        for _ in range(3):
            page.mouse.move(
                x2 + random.uniform(-1, 1),
                y2 + random.uniform(-0.5, 0.5),
            )
            sleep(0.02)
        page.mouse.move(x2, y2)
    page.mouse.up()


def collect_data_images(page: Page) -> List[str]:
    """DOM scrape of data:image / canvas — same fallback as Selenium NetworkImageMonitor."""
    fl = login_frame(page)
    try:
        # Run inside login iframe document
        urls = fl.locator("body").evaluate(
            """() => {
                const out = [];
                for (const img of document.querySelectorAll('img')) {
                  const s = img.getAttribute('src') || '';
                  if (s.startsWith('data:image')) out.push(s);
                }
                for (const c of document.querySelectorAll('canvas')) {
                  try { out.push(c.toDataURL('image/png')); } catch (e) {}
                }
                return out;
            }"""
        )
        return list(urls or [])
    except Exception:
        return []


def handle_verification(
    page: Page,
    token: str,
    retry_count: int,
    offset: int = -30,
    monitor_time: float = 3,
    speed: str = "middle",
    yunma_calls: Optional[List[int]] = None,
) -> None:
    """Port of activity_jfbym.ali_slider_captcha.handle_verification as used by qn_login."""
    if not retry_count:
        retry_count = 5
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fl = login_frame(page)

    for i in range(int(retry_count)):
        print(f"[ali_slider] 第 {i+1} 识别验证码")
        if not _locator_displayed(fl, SEL_DRAG_LABEL, timeout_ms=2000) and not _locator_displayed(
            fl, SEL_DRAG_ELE, timeout_ms=1000
        ):
            break

        try:
            refresh = fl.locator(SEL_REFRESH).first
            refresh.click(force=True, timeout=5000)
        except Exception as e:
            print(f"[ali_slider] refresh click failed: {e}")
        sleep(monitor_time)
        res_list = collect_data_images(page)

        tip_images_base64: List[str] = []
        background_image_base64 = None
        try:
            for image_base64 in res_list:
                if image_base64.startswith("https://"):
                    continue
                raw = image_base64.split(",", 1)[-1]
                img = decode_image(raw)
                width, height = img.size
                if height == 180:
                    background_image_base64 = image_base64
                if height == 30:
                    tip_images_base64.append(image_base64)
        except Exception:
            continue

        if not (tip_images_base64 or background_image_base64):
            # 默认当作成功通过
            break

        distance = None
        captcha_flag = False
        for index, tip_b64 in enumerate(tip_images_base64):
            tip_image = decode_image(tip_b64.split(",", 1)[-1])
            if not background_image_base64:
                continue
            background_image = decode_image(background_image_base64.split(",", 1)[-1])
            captcha_image = join_images(tip_image, background_image)
            path = CACHE_DIR / f"ali_image_captcha{i}{index}.png"
            captcha_image.save(path)
            captcha_image_base64 = encode_image(captcha_image)

            if not token:
                raise QianniuLoginError("云码 token 为空，无法识别滑块（影刀 ym 引擎）")
            result = yunma_recg(token, captcha_image_base64)
            if yunma_calls is not None:
                yunma_calls[0] += 1
            if result.get("msg") != "识别成功":
                print("识别失败, 请重试, 本次不计费", result.get("msg"))
                continue
            distance = result.get("data", {}).get("data")
            captcha_flag = True
            break

        if not captcha_flag:
            continue

        print(f"[ali_slider] Distance: {distance}")
        drag_distance_pct = (int(distance) - 24 - 10) / 320
        background_ele_width = 320
        _ = offset  # unused in source distance math
        distance_px = int(background_ele_width * drag_distance_pct)
        print(f"[ali_slider] distance_px: {distance_px}")

        drag_el = fl.locator(SEL_DRAG_ELE).first
        box = drag_el.bounding_box(timeout=5000)
        if not box:
            continue
        cx = box["x"] + box["width"] / 2 + random.randint(-5, 5)
        cy = box["y"] + box["height"] / 2 + random.randint(-5, 5)
        mouse_drag(
            page,
            cx,
            cy,
            cx + distance_px,
            cy,
            overshoot=True,
            speed=speed,
        )
        sleep(3)
        if not _locator_displayed(fl, SEL_DRAG_ELE, timeout_ms=2000):
            break


def click_errloading(page: Page) -> bool:
    """Port of web_page.find_by_xpath('//div[@class=\"errloading\"]').click()."""
    fl = login_frame(page)
    try:
        el = fl.locator('div.errloading').first
        if el.is_visible(timeout=2000):
            el.click(timeout=2000)
            print("[nc] clicked errloading in login iframe")
            return True
    except Exception:
        pass
    bf = baxia_frame(page)
    try:
        el = bf.locator('div.errloading').first
        if el.is_visible(timeout=1500):
            el.click(timeout=1500)
            print("[nc] clicked errloading in baxia iframe")
            return True
    except Exception:
        pass
    # text fallback
    for text in (
        "验证失败, 点击框体重试",
        "验证失败，点击框体重试",
    ):
        try:
            el = fl.get_by_text(text, exact=False).first
            if el.is_visible(timeout=800):
                el.click(timeout=800)
                print("[nc] clicked 验证失败 text fallback")
                return True
        except Exception:
            continue
    return False


def do_nc_mouse_drag(page: Page) -> None:
    """Measure qn_slide / qn_login_verify in top-viewport CSS px, page.mouse drag.

    Geometry mirrors qn_login: center of slide + verify_width.
    Playwright locator.bounding_box() already returns main-frame viewport coords
    even through nested FrameLocators — so no manual iframe offset math needed.
    """
    sleep(3)
    fl = login_frame(page)
    # Prefer baxia nested if present
    target: FrameLocator = fl
    try:
        bf = baxia_frame(page)
        if _locator_displayed(bf, SEL_NC_SLIDE, timeout_ms=2000):
            target = bf
    except Exception:
        pass

    slide = target.locator(SEL_NC_SLIDE).first
    verify = target.locator(SEL_NC_VERIFY).first
    slide.wait_for(state="visible", timeout=5000)
    verify.wait_for(state="visible", timeout=5000)
    sr = slide.bounding_box()
    vr = verify.bounding_box()
    if not sr or not vr:
        raise QianniuLoginError("NC slide/verify bounding box missing")

    verify_w = vr["width"]
    try:
        track = target.locator("#nc_1_n1t").first
        tr = track.bounding_box(timeout=1000)
        if tr and tr["width"] > 0:
            verify_w = min(verify_w, tr["width"])
    except Exception:
        tr = None

    x1 = sr["x"] + sr["width"] / 2
    y1 = sr["y"] + sr["height"] / 2
    x2 = x1 + verify_w
    print(
        f"[nc] mouse_drag ({x1:.1f},{y1:.1f}) -> ({x2:.1f},{y1:.1f}) "
        f"verify_w={verify_w:.1f} slide_w={sr['width']:.1f} "
        f"track_w={(tr or {}).get('width')}"
    )
    mouse_drag(page, x1, y1, x2, y1, overshoot=False, speed="middle")
    sleep(1.2)


def detect_human_gate(page: Page) -> Optional[str]:
    """Stop on SMS / phone / face gates (task requirement; not in qn_login)."""
    markers = [
        "你正在使用手机短信验证身份",
        "手机短信验证",
        "短信验证",
        "点击获取验证码",
        "其他验证方式",
        "验证码已发送",
        "请输入验证码",
        "校验码",
        "人脸验证",
        "手机验证",
        "获取验证码",
    ]
    texts: List[str] = []

    def _collect_from(get_text) -> None:
        try:
            texts.append(get_text() or "")
        except Exception:
            pass

    _collect_from(lambda: page.locator("body").inner_text(timeout=2000))
    _collect_from(lambda: page.content())
    fl = login_frame(page)
    _collect_from(lambda: fl.locator("body").inner_text(timeout=2000))
    # nested frames inside login
    try:
        n = page.locator(IFRAME_CSS).content_frame
        # also try baxia
        _collect_from(lambda: baxia_frame(page).locator("body").inner_text(timeout=1500))
    except Exception:
        pass
    # any nested iframe text via evaluate on login iframe
    try:
        nested = fl.locator("body").evaluate(
            """() => {
                const parts = [];
                for (const ifr of document.querySelectorAll('iframe')) {
                  try {
                    const doc = ifr.contentDocument;
                    if (doc && doc.body) parts.push(doc.body.innerText || '');
                  } catch (e) {}
                }
                return parts.join('\\n');
            }"""
        )
        if nested:
            texts.append(nested)
    except Exception:
        pass

    blob = "\n".join(texts)
    for m in markers:
        if m in blob:
            return m
    if "安全验证" in blob and ("校验码" in blob or "验证码" in blob):
        return "安全验证"
    if "身份验证" in blob and ("校验码" in blob or "验证码" in blob or "手机" in blob):
        return "身份验证"
    return None


# ---------------------------------------------------------------- main flow = qn_login.login
def login(
    mode: str,
    username: str,
    password: str,
    token: str,
    retry_count: int,
    page: Optional[Page] = None,
) -> Tuple[Page, int, List[str], Optional[Browser], Optional[BrowserContext], Optional[Playwright]]:
    """Faithful port of qn_login.login(mode, username, password, token, retry_count).

    Returns (page, yunma_calls, shots, browser, context, playwright).
    browser/context/playwright are non-None only when this function created them.
    """
    if not retry_count:
        retry_count = 3
    shots: List[str] = []
    yunma_calls = [0]
    own_pw: Optional[Playwright] = None
    own_browser: Optional[Browser] = None
    own_context: Optional[BrowserContext] = None
    # Mutable bag so NeedsHumanError path can still recover owned browser refs
    owned: dict = {"browser": None, "context": None, "playwright": None, "page": None}
    global _LAST_OWNED
    _LAST_OWNED = owned

    if page is None:
        if mode not in ("chrome", "edge", "cef", "SunBrowser"):
            mode = "chrome"
        own_pw = sync_playwright().start()
        own_browser, own_context, page = create_browser(own_pw, headless=False)
        owned["browser"] = own_browser
        owned["context"] = own_context
        owned["playwright"] = own_pw
        owned["page"] = page
        # stash on page for wrapper recovery if login raises
        setattr(page, "_qn_owned", owned)
    else:
        owned["page"] = page
        setattr(page, "_qn_owned", owned)

    url = LOGIN_URL
    cnt = 0
    for _ in range(3):
        try:
            if cnt == 0:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            else:
                page.reload(wait_until="domcontentloaded", timeout=60000)
            break
        except Exception:
            cnt += 1
            if cnt >= 3:
                raise

    sleep(1)
    fl = login_frame(page)
    username_input = fl.locator(SEL_USERNAME).first
    username_input.wait_for(state="visible", timeout=30000)
    input_text(page, username_input, username)

    password_input = fl.locator(SEL_PASSWORD).first
    password_input.wait_for(state="visible", timeout=20000)
    password_input.click()

    # pre-password scratch captcha (qn_drag_label → ali_slider)
    try:
        if _locator_displayed(fl, SEL_DRAG_LABEL, timeout_ms=2000):
            handle_verification(
                page, token, retry_count, offset=-30, yunma_calls=yunma_calls
            )
    except NeedsHumanError:
        raise
    except Exception as e:
        # qn_login: bare except pass
        print(f"[qn_login] pre-password captcha ignored: {e}")

    fl = login_frame(page)
    password_input = fl.locator(SEL_PASSWORD).first
    # xbot_visual.decrypt(password) — plaintext from env; no-op
    input_text(page, password_input, password)

    for _outer in range(6):
        for _count in range(0, int(retry_count)):
            if nc_visible(page):
                try:
                    do_nc_mouse_drag(page)
                except Exception as e:
                    print(f"[nc] drag failed: {e}")
            else:
                if click_errloading(page):
                    sleep(1)
                    continue
                break

        fl = login_frame(page)
        login_btn = fl.locator(SEL_LOGIN_BTN).first
        login_btn.wait_for(state="attached", timeout=10000)
        try:
            login_btn.evaluate(
                """el => {
                    el.classList.remove('fm-button-disabled');
                    el.removeAttribute('disabled');
                    el.click();
                }"""
            )
        except Exception:
            login_btn.click(force=True)

        human = detect_human_gate(page)
        if human:
            shot(page, "human_gate", shots)
            raise NeedsHumanError(human)

        # soft probe — original swallows "登录失败"
        try:
            fl.locator(SEL_LOGIN_BTN).first.wait_for(state="attached", timeout=5000)
            print("[qn_login] login button still present after click (soft)")
        except Exception:
            pass

        human = detect_human_gate(page)
        if human:
            shot(page, "human_gate", shots)
            raise NeedsHumanError(human)

        if _locator_displayed(fl, SEL_LOGIN_ERROR, timeout_ms=1000):
            msg = (fl.locator(SEL_LOGIN_ERROR).first.inner_text(timeout=1000) or "").strip()
            if msg:
                raise CredentialsRejected(msg)

        if click_errloading(page):
            sleep(1)
            continue
        if nc_visible(page):
            continue
        break

    # login_error_xpath check from qn_login
    try:
        fl = login_frame(page)
        if _locator_displayed(fl, SEL_LOGIN_ERROR, timeout_ms=2000):
            msg = fl.locator(SEL_LOGIN_ERROR).first.inner_text(timeout=1000)
            raise CredentialsRejected(msg)
    except CredentialsRejected:
        raise
    except Exception:
        pass

    human = detect_human_gate(page)
    if human:
        shot(page, "human_gate", shots)
        raise NeedsHumanError(human)

    sleep(2)
    # Re-check gate after settle — SMS UI often replaces the password form.
    human = detect_human_gate(page)
    if human:
        shot(page, "human_gate", shots)
        raise NeedsHumanError(human)

    url_now = page.url or ""
    if "loginmyseller.taobao.com" in url_now and "/home" not in url_now:
        # Still on login host: password form left, SMS, or soft fail.
        try:
            fl = login_frame(page)
            if _locator_displayed(fl, SEL_LOGIN_BTN, timeout_ms=2000):
                shot(page, "still_login", shots)
                raise QianniuLoginError("登录失败")
        except QianniuLoginError:
            raise
        except Exception:
            pass
        # No password button but not navigated away — treat as human gate / incomplete.
        shot(page, "still_on_login", shots)
        raise NeedsHumanError("仍停在登录页，可能需短信/其他验证")

    shot(page, "after_login", shots)
    return page, yunma_calls[0], shots, owned["browser"], owned["context"], owned["playwright"]


def qianniu_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    mode: str = "chrome",
    retries: int = 5,
    on_error: OnError = OnError.TERMINATE,
    page: Optional[Page] = None,
    print_error_log: bool = True,
    **_ignored: Any,
) -> QianniuLoginResult:
    """Public entry matching market-command inputs (账号/密码/云码Token/重试次数/网页类型)."""
    account = account or os.environ.get("QIANNIU_ACCOUNT", "")
    password = password or os.environ.get("QIANNIU_PASSWORD", "")
    yunma_token = yunma_token or os.environ.get("YUNMA_TOKEN", "")
    if not account or not password:
        raise ValueError("缺少账号或密码")

    last_err: Optional[str] = None
    web: Optional[Page] = page
    calls = 0
    shots: List[str] = []
    own_browser = own_context = own_pw = None
    try:
        web, calls, shots, own_browser, own_context, own_pw = login(
            mode=mode,
            username=account,
            password=password,
            token=yunma_token,
            retry_count=retries,
            page=page,
        )
        sleep(2)
        return QianniuLoginResult(
            ok=True,
            web_page=web,
            yunma_calls=calls,
            shots=shots,
            _browser=own_browser,
            _context=own_context,
            _playwright=own_pw,
        )
    except NeedsHumanError as e:
        last_err = str(e)
        if print_error_log:
            print(f"[NeedsHuman] {e}")
        bag = getattr(web, "_qn_owned", None) if web is not None else None
        if not bag:
            bag = _LAST_OWNED or None
        if bag:
            own_browser = bag.get("browser")
            own_context = bag.get("context")
            own_pw = bag.get("playwright")
            if web is None:
                web = bag.get("page")
        return QianniuLoginResult(
            ok=False,
            web_page=web,
            error=last_err,
            yunma_calls=calls,
            shots=shots,
            _browser=own_browser,
            _context=own_context,
            _playwright=own_pw,
        )
    except Exception as e:
        last_err = str(e)
        if print_error_log:
            print(f"[qn_login error] {e}")
        if on_error == OnError.TERMINATE:
            raise QianniuLoginError(last_err) from e
        return QianniuLoginResult(
            ok=False,
            web_page=web,
            error=last_err,
            yunma_calls=calls,
            shots=shots,
            _browser=own_browser,
            _context=own_context,
            _playwright=own_pw,
        )


def close_result(r: QianniuLoginResult) -> None:
    """Close browser/context we own (call after NeedsHuman leave-open window)."""
    try:
        if r._context:
            r._context.close()
    except Exception:
        pass
    try:
        if r._browser:
            r._browser.close()
    except Exception:
        pass
    try:
        if r._playwright:
            r._playwright.stop()
    except Exception:
        pass


def main() -> None:
    r = qianniu_login(retries=int(os.environ.get("QIANNIU_RETRIES", "5")))
    print(
        "RESULT",
        {"ok": r.ok, "error": r.error, "yunma_calls": r.yunma_calls, "shots": r.shots},
    )
    if r.web_page and r.ok:
        print("URL", r.web_page.url)
    if r.web_page and not r.ok:
        # leave open briefly on NeedsHuman then close cleanly
        if r.error:
            sleep(5)
        close_result(r)


if __name__ == "__main__":
    main()
