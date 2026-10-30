"""
Port of 影刀市场指令「千牛登录」
(xbot_extensions.activity_7bca6d.qn_login + activity_jfbym.ali_slider_captcha).

Behavior mirrors 影刀市场指令「千牛登录」(qn_login + ali_slider_captcha).
Reverse notes: docs/qianniu_login_reverse_notes.md
selectorsV2.xml names: qn_uername_input, qn_password_input, qn_drag_label,
  qn_refresh, qn_drag_ele, qn_login_verify, qn_slide, qn_login

Do NOT invent alternate login URLs / captcha types. Mirror the ShadowBot steps.
"""
from __future__ import annotations

import base64
import http.client
import json
import os
import random
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Any, List, Optional, Tuple

from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ---- constants from ShadowBot sources ----
LOGIN_URL = "https://loginmyseller.taobao.com/"
# ali_slider_captcha.recg
YUNMA_HOST = "api.jfbym.com"
YUNMA_PATH = "/api/YmServer/customApi"
YUNMA_TYPE_ALI_SLIDER = 20226  # jfbym type used by handle_verification

IFRAME_CSS = "iframe#alibaba-login-box"
BAXIA_IFRAME_CSS = "iframe#baxia-dialog-content"  # nested punish/captcha iframe (selectorsV2 via baxia-dialog)
# Leaf selectors from activity_7bca6d/selectorsV2.xml (inside login iframe)
SEL_USERNAME = "#fm-login-id"
SEL_PASSWORD = "#fm-login-password"
SEL_LOGIN_BTN = "button.fm-submit.password-login, button.fm-button.password-login, button.password-login"
SEL_DRAG_LABEL = "canvas#captcha-question, .scratch-captcha-question-header, .drag-captcha-question"
SEL_REFRESH = "i.icon-refresh.refresh.scratch, i.icon-refresh.scratch, i.refresh.scratch"
SEL_DRAG_ELE = ".scratch-captcha-slider .button, #nocaptcha .scratch-captcha-slider .button"
SEL_NC_VERIFY = "#nc_1__scale_text"
SEL_NC_SLIDE = "#nc_1_n1z"
SEL_LOGIN_ERROR = "div.login-error-msg"
SEL_ERRLOADING = "div.errloading"

HERE = Path(__file__).resolve().parent
SHOT_DIR = HERE / "shots"
CACHE_DIR = HERE / "captcha_cache"


class OnError(Enum):
    TERMINATE = "terminate"
    IGNORE = "ignore"
    RETRY_STEP = "retry"


class QianniuLoginError(Exception):
    pass


class NeedsHumanError(QianniuLoginError):
    """SMS / face / phone verification — stop and leave browser open."""


class CredentialsRejected(QianniuLoginError):
    pass


@dataclass
class QianniuLoginResult:
    ok: bool
    web_page: Optional[WebDriver] = None
    error: Optional[str] = None
    yunma_calls: int = 0
    shots: List[str] = field(default_factory=list)


# ---------------------------------------------------------------- yunma (ali_slider_captcha.recg)
def yunma_recg(token: str, base64_im: str) -> dict:
    """Faithful port of ali_slider_captcha.recg (HTTP POST type=20226)."""
    conn = http.client.HTTPConnection(YUNMA_HOST, timeout=60)
    headers = {"Content-Type": "application/json"}
    data = {"image": base64_im, "token": token, "type": YUNMA_TYPE_ALI_SLIDER}
    conn.request("POST", YUNMA_PATH, body=json.dumps(data), headers=headers)
    response = conn.getresponse()
    response_data = response.read().decode("utf-8")
    conn.close()
    return json.loads(response_data)


def encode_image(image: Image.Image) -> str:
    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def decode_image(base64_string: str) -> Image.Image:
    missing = len(base64_string) % 4
    if missing:
        base64_string += "=" * (4 - missing)
    img = Image.open(BytesIO(base64.b64decode(base64_string)))
    return img.convert("RGBA")


def join_images(image1: Image.Image, image2: Image.Image) -> Image.Image:
    """Port of ali_slider_captcha.join_images."""
    w1, h1 = image1.size
    w2, h2 = image2.size
    new_image = Image.new("RGB", (max(w1, w2), h1 + h2 + 11), (255, 255, 255))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (0, h1 + 11))
    return new_image


# ---------------------------------------------------------------- browser helpers
def create_chrome(headless: bool = False) -> WebDriver:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")
    # Box egress: without this proxy, havanalogin iframe returns 403 Forbidden
    opts.add_argument("--proxy-server=http://127.0.0.1:8791")
    opts.add_argument("--proxy-bypass-list=<-loopback>;localhost;127.0.0.1;[::1]")
    opts.add_argument(
        "--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE localhost , EXCLUDE 127.0.0.1 , EXCLUDE ::1"
    )
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=opts)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"},
    )
    return driver


def sleep(seconds: float) -> None:
    time.sleep(seconds)


def switch_login_iframe(driver: WebDriver, timeout: float = 30) -> None:
    driver.switch_to.default_content()
    WebDriverWait(driver, timeout).until(
        EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, IFRAME_CSS))
    )


def switch_baxia_iframe(driver: WebDriver, timeout: float = 5) -> bool:
    """Enter nested baxia captcha iframe if present (qn_login_verify path).

    Frame stack: top → #alibaba-login-box → #baxia-dialog-content.
    """
    switch_login_iframe(driver, timeout=max(timeout, 15))
    try:
        WebDriverWait(driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, BAXIA_IFRAME_CSS))
        )
        return True
    except Exception:
        return False


def nc_visible(driver: WebDriver) -> bool:
    """True when NC slide is shown — classic nocaptcha container or baxia iframe."""
    switch_login_iframe(driver)
    # classic: slide knob visible in login iframe (password NC or #nocaptcha)
    if is_displayed(driver, SEL_NC_SLIDE, timeout=0.6):
        return True
    for box in ("#nocaptcha-password", "#nocaptcha", ".nc-container.tb-login", ".nc-container"):
        if is_displayed(driver, box, timeout=0.4):
            if is_displayed(driver, SEL_NC_VERIFY, timeout=0.4) or is_displayed(
                driver, SEL_NC_SLIDE, timeout=0.4
            ):
                return True
    # baxia nested iframe (selectorsV2 qn_login_verify / qn_slide path)
    if switch_baxia_iframe(driver, timeout=2):
        try:
            return is_displayed(driver, SEL_NC_SLIDE, timeout=1) or is_displayed(
                driver, SEL_NC_VERIFY, timeout=1
            )
        finally:
            driver.switch_to.parent_frame()
    switch_login_iframe(driver)
    return False


def find_css(driver: WebDriver, css: str, timeout: float = 15) -> WebElement:
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css))
    )


def is_displayed(driver: WebDriver, css: str, timeout: float = 1.5) -> bool:
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css))
        )
        return el.is_displayed()
    except Exception:
        return False


def element_text_value(el: WebElement) -> str:
    return (el.get_attribute("value") or el.text or "").strip()


def input_with_retry(el: WebElement, text: str, simulative_first: bool = True, max_try: int = 3) -> None:
    """Mirror qn_login username/password input + verify loop (i>3 -> raise)."""
    el.clear()
    if simulative_first:
        el.click()
        el.send_keys(text)
    else:
        el.clear()
        # non-simulative equivalent: JS set value + input events
        el.parent.execute_script(  # type: ignore[attr-defined]
            "arguments[0].value=arguments[1];"
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
            el,
            text,
        )
    got = element_text_value(el)
    i = 1
    while got != text:
        el.clear()
        driver = el.parent  # may not work; use JS
        # Selenium: use send_keys again as non-simulative fallback
        try:
            el.parent.execute_script(  # noqa
                "arguments[0].focus(); arguments[0].value='';",
                el,
            )
        except Exception:
            pass
        # Prefer JS write (simulative=False path in xbot)
        try:
            driver = el._parent  # type: ignore[attr-defined]
            driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
                el,
                text,
            )
        except Exception:
            el.send_keys(text)
        got = element_text_value(el)
        i += 1
        if i > max_try:
            raise QianniuLoginError("输入失败，请手动登录")


def input_text(driver: WebDriver, el: WebElement, text: str) -> None:
    el.click()
    sleep(0.2)
    el.clear()
    el.send_keys(text)
    got = element_text_value(el)
    i = 1
    while got != text:
        driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
            el,
            text,
        )
        got = element_text_value(el)
        i += 1
        if i > 3:
            raise QianniuLoginError("输入失败，请手动登录")


def shot(driver: WebDriver, name: str, shots: List[str]) -> None:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SHOT_DIR / f"{int(time.time())}_{name}.png"
    try:
        driver.save_screenshot(str(path))
        shots.append(str(path))
    except Exception:
        pass


def _chrome_viewport_origin(driver: WebDriver) -> Tuple[float, float]:
    """Top-left of the page viewport in screen coordinates."""
    g = driver.execute_script(
        "return {sx:window.screenX, sy:window.screenY,"
        "ow:window.outerWidth, oh:window.outerHeight,"
        "iw:window.innerWidth, ih:window.innerHeight};"
    )
    chrome_left = max(0, (g["ow"] - g["iw"]) // 2)
    chrome_top = max(0, g["oh"] - g["ih"])
    return g["sx"] + chrome_left, g["sy"] + chrome_top


def element_screen_rect_in_baxia(driver: WebDriver, el: WebElement) -> Tuple[float, float, float, float]:
    """Screen rect for an element inside login iframe → baxia iframe (qn_slide path).

    Assumes current context is already the baxia iframe.
    """
    # element relative to baxia viewport
    er = driver.execute_script(
        "const r=arguments[0].getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height};",
        el,
    )
    # pop to login iframe; locate baxia iframe box
    driver.switch_to.parent_frame()
    bax = driver.find_element(By.CSS_SELECTOR, BAXIA_IFRAME_CSS)
    br = driver.execute_script(
        "const r=arguments[0].getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height};",
        bax,
    )
    # pop to top; locate login iframe box + chrome origin
    driver.switch_to.default_content()
    login = driver.find_element(By.CSS_SELECTOR, IFRAME_CSS)
    lr = driver.execute_script(
        "const r=arguments[0].getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height};",
        login,
    )
    ox, oy = _chrome_viewport_origin(driver)
    x = ox + lr["x"] + br["x"] + er["x"]
    y = oy + lr["y"] + br["y"] + er["y"]
    # restore baxia context for caller
    switch_baxia_iframe(driver, timeout=10)
    return x, y, er["w"], er["h"]


def element_screen_center(driver: WebDriver, el: WebElement) -> Tuple[float, float, float, float]:
    """Approximate xbot get_bounding() in screen coords (single frame)."""
    rect = driver.execute_script(
        "const r=arguments[0].getBoundingClientRect();"
        "return {x:r.x,y:r.y,w:r.width,h:r.height};",
        el,
    )
    ox, oy = _chrome_viewport_origin(driver)
    return ox + rect["x"], oy + rect["y"], rect["w"], rect["h"]


def xdotool_drag(x1: float, y1: float, x2: float, y2: float, speed: str = "middle") -> None:
    """Port of win32 mouse_move + click down/up used in qn_login NC slide."""
    env = {**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":2")}
    steps = 25 if speed == "middle" else 12
    subprocess.run(
        ["xdotool", "mousemove", "--sync", str(int(x1)), str(int(y1))],
        check=False,
        env=env,
    )
    subprocess.run(["xdotool", "mousedown", "1"], check=False, env=env)
    for i in range(1, steps + 1):
        xi = x1 + (x2 - x1) * i / steps
        yi = y1 + (y2 - y1) * i / steps
        subprocess.run(
            ["xdotool", "mousemove", "--sync", str(int(xi)), str(int(yi))],
            check=False,
            env=env,
        )
        sleep(0.01)
    subprocess.run(["xdotool", "mouseup", "1"], check=False, env=env)


def cdp_drag(driver: WebDriver, x1: float, y1: float, x2: float, y2: float) -> None:
    """OS-level-ish mouse via CDP Input domain (top-viewport CSS px).

    Used for NC slide inside nested baxia iframe; ActionChains/xdotool were
    either ignored or failed anti-bot. Geometry still mirrors qn_login
    (center of qn_slide → + verify_width). Ease-out then small settle, like
    win32 middle-speed move.
    """
    driver.execute_cdp_cmd(
        "Input.dispatchMouseEvent",
        {"type": "mouseMoved", "x": x1, "y": y1, "button": "none", "buttons": 0},
    )
    sleep(0.15)
    driver.execute_cdp_cmd(
        "Input.dispatchMouseEvent",
        {
            "type": "mousePressed",
            "x": x1,
            "y": y1,
            "button": "left",
            "buttons": 1,
            "clickCount": 1,
        },
    )
    sleep(0.12)
    steps = 32
    for i in range(1, steps + 1):
        t = i / steps
        # ease-out cubic (fast start, slow end) — closer to human NC slides
        e = 1 - (1 - t) ** 3
        x = x1 + (x2 - x1) * e + random.uniform(-0.5, 0.5)
        y = y1 + (y2 - y1) * e + random.uniform(-0.4, 0.4)
        driver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            {"type": "mouseMoved", "x": x, "y": y, "button": "left", "buttons": 1},
        )
        sleep(0.014 + (0.01 if t > 0.7 else 0))
    # tiny settle jitter at end before release
    for _ in range(3):
        driver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseMoved",
                "x": x2 + random.uniform(-1, 1),
                "y": y2 + random.uniform(-0.5, 0.5),
                "button": "left",
                "buttons": 1,
            },
        )
        sleep(0.02)
    driver.execute_cdp_cmd(
        "Input.dispatchMouseEvent",
        {
            "type": "mouseReleased",
            "x": x2,
            "y": y2,
            "button": "left",
            "buttons": 0,
            "clickCount": 1,
        },
    )


def action_drag_by_offset(driver: WebDriver, el: WebElement, distance: int, speed: str = "middle") -> None:
    """Port of ali_slider_captcha.drag overshoot pattern via ActionChains."""
    actions = ActionChains(driver)
    right_offset = random.randint(-5, 5)
    left_offset = random.randint(-5, 5)
    pause = 0.05 if speed == "fast" else 0.08
    actions.click_and_hold(el)
    actions.pause(0.1)
    # overshoot right then left then settle (mirrors win32 moves)
    actions.move_by_offset(distance + right_offset, 0)
    actions.pause(pause)
    actions.move_by_offset(-right_offset - left_offset, 0)
    actions.pause(pause)
    actions.move_by_offset(left_offset, 0)
    actions.pause(0.05)
    actions.release()
    actions.perform()


# ---------------------------------------------------------------- CDP network image capture (xbot start_monitor_network)
class NetworkImageMonitor:
    """Collect data:image/* responses via CDP, approximating xbot get_responses."""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._request_ids: dict[str, str] = {}

    def start(self) -> None:
        self.driver.execute_cdp_cmd("Network.enable", {})
        self._request_ids.clear()

    def stop(self) -> None:
        try:
            self.driver.execute_cdp_cmd("Network.disable", {})
        except Exception:
            pass

    def collect_data_images(self) -> List[str]:
        """Return list of data-URL-like base64 payloads (with or without data: prefix).

        CDP does not expose historical bodies easily without binding events; as a
        faithful fallback we also scrape DOM img[src^=data:] after refresh.
        """
        images: List[str] = []
        # DOM scrape (same images the network monitor would see as data URLs)
        try:
            urls = self.driver.execute_script(
                """
                const out=[];
                for (const img of document.querySelectorAll('img')) {
                  const s=img.getAttribute('src')||'';
                  if (s.startsWith('data:image')) out.push(s);
                }
                for (const c of document.querySelectorAll('canvas')) {
                  try { out.push(c.toDataURL('image/png')); } catch(e) {}
                }
                return out;
                """
            )
            images.extend(urls or [])
        except Exception:
            pass
        return images


def handle_verification(
    driver: WebDriver,
    token: str,
    retry_count: int,
    offset: int = -30,
    monitor_time: float = 3,
    speed: str = "middle",
    yunma_calls: Optional[List[int]] = None,
) -> None:
    """Port of activity_jfbym.ali_slider_captcha.handle_verification as used by qn_login:
    handle_verification(web_page, token, refresh_ele, drag_ele, retry_count, offset=-30)
    """
    if not retry_count:
        retry_count = 5
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    captcha_flag = False
    mon = NetworkImageMonitor(driver)

    for i in range(int(retry_count)):
        print(f"[ali_slider] 第 {i+1} 识别验证码")
        switch_login_iframe(driver)
        if not is_displayed(driver, SEL_DRAG_LABEL, timeout=2) and not is_displayed(
            driver, SEL_DRAG_ELE, timeout=1
        ):
            break

        mon.start()
        try:
            refresh = find_css(driver, SEL_REFRESH, timeout=5)
            driver.execute_script("arguments[0].click();", refresh)
        except Exception as e:
            print(f"[ali_slider] refresh click failed: {e}")
        sleep(monitor_time)
        res_list = mon.collect_data_images()
        mon.stop()

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
        # From ali_slider_captcha comments:
        # drag_distance_pct = (int(distance)- 24 - 10) / 320
        drag_distance_pct = (int(distance) - 24 - 10) / 320
        background_ele_width = 320
        # qn_login passes offset=-30 but handle_verification signature has offset unused
        # in distance math in the source we read — keep formula identical.
        _ = offset
        distance_px = int(background_ele_width * drag_distance_pct)
        print(f"[ali_slider] distance_px: {distance_px}")

        switch_login_iframe(driver)
        drag_el = find_css(driver, SEL_DRAG_ELE, timeout=5)
        action_drag_by_offset(driver, drag_el, distance_px, speed=speed)
        sleep(3)
        switch_login_iframe(driver)
        if not is_displayed(driver, SEL_DRAG_ELE, timeout=2):
            break


def handle_nc_slide(driver: WebDriver, retry_count: int) -> None:
    """Port of qn_login NC slide loop (qn_login_verify / qn_slide)."""
    for _outer in range(6):
        for _count in range(0, int(retry_count)):
            switch_login_iframe(driver)
            if is_displayed(driver, SEL_NC_VERIFY, timeout=1.5):
                slide = find_css(driver, SEL_NC_SLIDE, timeout=5)
                verify = find_css(driver, SEL_NC_VERIFY, timeout=5)
                sx, sy, sw, sh = element_screen_center(driver, slide)
                _, _, verify_width, _ = element_screen_center(driver, verify)
                pos_center_x = sx + sw / 2
                pos_center_y = sy + sh / 2
                sleep(3)
                xdotool_drag(
                    pos_center_x,
                    pos_center_y,
                    pos_center_x + verify_width,
                    pos_center_y,
                    speed="middle",
                )
                sleep(1)
            else:
                # 校验是否失效 — click errloading if present
                try:
                    driver.switch_to.default_content()
                    switch_login_iframe(driver)
                    err = driver.find_element(By.XPATH, '//div[@class="errloading"]')
                    err.click()
                    sleep(1)
                except Exception:
                    break
        # after inner loop, caller clicks login; this helper only does slides
        break


def detect_human_gate(driver: WebDriver) -> Optional[str]:
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

    def _collect(ctx: str) -> None:
        try:
            texts.append(driver.find_element(By.TAG_NAME, "body").text or "")
        except Exception:
            pass

    driver.switch_to.default_content()
    _collect("top")
    # login iframe
    try:
        switch_login_iframe(driver)
        _collect("login")
        # nested frames inside login (SMS UI often replaces form here)
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        for fr in frames:
            try:
                driver.switch_to.frame(fr)
                _collect("nested")
                driver.switch_to.parent_frame()
            except Exception:
                try:
                    switch_login_iframe(driver)
                except Exception:
                    break
    except Exception:
        pass
    driver.switch_to.default_content()
    blob = "\n".join(texts)
    for m in markers:
        if m in blob:
            return m
    # avoid matching bare 「安全验证」/「身份验证」 alone on generic pages unless with 校验码
    if "安全验证" in blob and ("校验码" in blob or "验证码" in blob):
        return "安全验证"
    if "身份验证" in blob and ("校验码" in blob or "验证码" in blob or "手机" in blob):
        return "身份验证"
    return None



def click_errloading(driver: WebDriver) -> bool:
    """Port of web_page.find_by_xpath('//div[@class="errloading"]').click().

    Searches login iframe and nested baxia iframe. Returns True if clicked.
    """
    # login iframe first (classic #nocaptcha-password errloading)
    try:
        switch_login_iframe(driver)
        el = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="errloading"]'))
        )
        if el.is_displayed():
            el.click()
            print("[nc] clicked errloading in login iframe")
            return True
    except Exception:
        pass
    # baxia nested
    try:
        if switch_baxia_iframe(driver, timeout=2):
            el = WebDriverWait(driver, 1.5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="errloading"]'))
            )
            if el.is_displayed():
                el.click()
                print("[nc] clicked errloading in baxia iframe")
                return True
    except Exception:
        pass
    # text fallback: yellow 「验证失败, 点击框体重试」
    try:
        switch_login_iframe(driver)
        for xpath in (
            '//*[contains(text(),"验证失败") and contains(text(),"重试")]',
            '//*[contains(text(),"验证失败, 点击框体重试")]',
            '//*[contains(text(),"验证失败，点击框体重试")]',
        ):
            try:
                el = driver.find_element(By.XPATH, xpath)
                if el.is_displayed():
                    el.click()
                    print("[nc] clicked 验证失败 text fallback")
                    return True
            except Exception:
                continue
    except Exception:
        pass
    switch_login_iframe(driver)
    return False


def do_nc_cdp_drag(driver: WebDriver) -> None:
    """Measure qn_slide / qn_login_verify in top-viewport CSS px, CDP-drag.

    Geometry mirrors qn_login: center of slide + verify_width (win32 mouse path).
    Frame stack may be classic (login iframe) or baxia nested.
    """
    sleep(3)
    driver.switch_to.default_content()
    login_el = find_css(driver, IFRAME_CSS, timeout=10)
    lr = driver.execute_script(
        "const r=arguments[0].getBoundingClientRect();return {x:r.x,y:r.y};",
        login_el,
    )
    driver.switch_to.frame(login_el)
    br = {"x": 0.0, "y": 0.0}
    try:
        bax = find_css(driver, BAXIA_IFRAME_CSS, timeout=2)
        if bax.is_displayed():
            br = driver.execute_script(
                "const r=arguments[0].getBoundingClientRect();return {x:r.x,y:r.y};",
                bax,
            )
            driver.switch_to.frame(bax)
    except Exception:
        pass
    slide = find_css(driver, SEL_NC_SLIDE, timeout=5)
    verify = find_css(driver, SEL_NC_VERIFY, timeout=5)
    # Prefer #nc_1_n1t track width when present (qn_login uses qn_login_verify width,
    # which is #nc_1__scale_text ≈ track). Cap to track so we do not leave the iframe.
    try:
        track = driver.find_element(By.CSS_SELECTOR, "#nc_1_n1t")
        tr = driver.execute_script(
            "const r=arguments[0].getBoundingClientRect();"
            "return {x:r.x,y:r.y,w:r.width,h:r.height};",
            track,
        )
    except Exception:
        tr = None
    sr = driver.execute_script(
        "const r=arguments[0].getBoundingClientRect();"
        "return {x:r.x,y:r.y,w:r.width,h:r.height};",
        slide,
    )
    vr = driver.execute_script(
        "const r=arguments[0].getBoundingClientRect();"
        "return {x:r.x,y:r.y,w:r.width,h:r.height};",
        verify,
    )
    verify_w = vr["w"]
    if tr and tr["w"] > 0:
        # qn_login: move by verify_width from slide center; keep end inside track+margin
        verify_w = min(verify_w, tr["w"])
    x1 = lr["x"] + br["x"] + sr["x"] + sr["w"] / 2
    y1 = lr["y"] + br["y"] + sr["y"] + sr["h"] / 2
    x2 = x1 + verify_w
    print(
        f"[nc] cdp_drag ({x1:.1f},{y1:.1f}) -> ({x2:.1f},{y1:.1f}) "
        f"verify_w={verify_w:.1f} slide_w={sr['w']:.1f} track_w={(tr or {}).get('w')}"
    )
    cdp_drag(driver, x1, y1, x2, y1)
    sleep(1.2)
    switch_login_iframe(driver)


# ---------------------------------------------------------------- main flow = qn_login.login
def login(
    mode: str,
    username: str,
    password: str,
    token: str,
    retry_count: int,
    driver: Optional[WebDriver] = None,
) -> Tuple[WebDriver, int, List[str]]:
    """Faithful port of qn_login.login(mode, username, password, token, retry_count)."""
    if not retry_count:
        retry_count = 3
    shots: List[str] = []
    yunma_calls = [0]
    own_driver = driver is None
    if driver is None:
        if mode not in ("chrome", "edge", "cef", "SunBrowser"):
            mode = "chrome"
        driver = create_chrome(headless=False)

    url = LOGIN_URL
    cnt = 0
    for _ in range(3):
        try:
            if cnt == 0:
                driver.get(url)
                WebDriverWait(driver, 60).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            else:
                driver.refresh()
                WebDriverWait(driver, 60).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            break
        except Exception:
            cnt += 1
            if cnt >= 3:
                raise

    # xbot.win32.manual_motion_on() — no-op marker; we use ActionChains/xdotool when dragging
    sleep(1)
    switch_login_iframe(driver)
    username_input = find_css(driver, SEL_USERNAME, timeout=30)
    input_text(driver, username_input, username)

    # re-acquire page / iframe (qn_login does get_active repeatedly)
    switch_login_iframe(driver)
    password_input = find_css(driver, SEL_PASSWORD, timeout=20)
    password_input.click()

    # pre-password scratch captcha (qn_drag_label → ali_slider)
    try:
        if is_displayed(driver, SEL_DRAG_LABEL, timeout=2):
            handle_verification(
                driver, token, retry_count, offset=-30, yunma_calls=yunma_calls
            )
    except NeedsHumanError:
        raise
    except Exception as e:
        # qn_login: bare except pass
        print(f"[qn_login] pre-password captcha ignored: {e}")

    switch_login_iframe(driver)
    password_input = find_css(driver, SEL_PASSWORD, timeout=20)
    # xbot_visual.decrypt(password) — plaintext from env; no-op
    input_text(driver, password_input, password)

    switch_login_iframe(driver)
    for _outer in range(6):
        # Inner loop mirrors qn_login: drag NC while visible; else click errloading or break
        for _count in range(0, int(retry_count)):
            if nc_visible(driver):
                try:
                    do_nc_cdp_drag(driver)
                except Exception as e:
                    print(f"[nc] drag failed: {e}")
                    # fall through — next pass may click errloading
                    switch_login_iframe(driver)
            else:
                # 校验是否失效 — qn_login: find_by_xpath errloading timeout=2
                if click_errloading(driver):
                    sleep(1)
                    continue
                break

        switch_login_iframe(driver)
        login_btn = find_css(driver, SEL_LOGIN_BTN, timeout=10)
        try:
            driver.execute_script(
                "arguments[0].classList.remove('fm-button-disabled');"
                "arguments[0].removeAttribute('disabled');"
                "arguments[0].click();",
                login_btn,
            )
        except Exception:
            login_btn.click()

        human = detect_human_gate(driver)
        if human:
            shot(driver, "human_gate", shots)
            raise NeedsHumanError(human)

        # qn_login:
        #   try: find qn_login timeout=5; raise 登录失败
        #   except: pass   ← the raise is swallowed!
        # so we only use this as a soft probe, never hard-fail here
        try:
            switch_login_iframe(driver)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SEL_LOGIN_BTN))
            )
            # soft "登录失败" marker (swallowed in original)
            print("[qn_login] login button still present after click (soft)")
        except TimeoutException:
            pass

        human = detect_human_gate(driver)
        if human:
            shot(driver, "human_gate", shots)
            raise NeedsHumanError(human)

        if is_displayed(driver, SEL_LOGIN_ERROR, timeout=1):
            msg = find_css(driver, SEL_LOGIN_ERROR).text.strip()
            if msg:
                raise CredentialsRejected(msg)

        # qn_login: errloading → click + continue outer; else break
        if click_errloading(driver):
            sleep(1)
            continue
        # Also: if NC reappeared after login click, continue outer to drag
        if nc_visible(driver):
            continue
        break

    # login_error_xpath check from qn_login
    try:
        switch_login_iframe(driver)
        if is_displayed(driver, SEL_LOGIN_ERROR, timeout=2):
            msg = find_css(driver, SEL_LOGIN_ERROR).text
            raise CredentialsRejected(msg)
    except CredentialsRejected:
        raise
    except Exception:
        pass

    human = detect_human_gate(driver)
    if human:
        shot(driver, "human_gate", shots)
        raise NeedsHumanError(human)

    driver.switch_to.default_content()
    # ShadowBot returns active page after sleep(2); require we left pure login form
    sleep(2)
    url = driver.current_url or ""
    if "loginmyseller.taobao.com" in url and "/home" not in url:
        # still on gate page — confirm iframe login button gone
        try:
            switch_login_iframe(driver)
            if is_displayed(driver, SEL_LOGIN_BTN, timeout=2):
                shot(driver, "still_login", shots)
                raise QianniuLoginError("登录失败")
        except QianniuLoginError:
            raise
        except Exception:
            pass
        driver.switch_to.default_content()

    shot(driver, "after_login", shots)
    driver.switch_to.default_content()
    return driver, yunma_calls[0], shots


def qianniu_login(
    account: Optional[str] = None,
    password: Optional[str] = None,
    yunma_token: Optional[str] = None,
    *,
    mode: str = "chrome",
    retries: int = 5,
    on_error: OnError = OnError.TERMINATE,
    driver: Optional[WebDriver] = None,
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
    web: Optional[WebDriver] = driver
    calls = 0
    shots: List[str] = []
    try:
        web, calls, shots = login(
            mode=mode,
            username=account,
            password=password,
            token=yunma_token,
            retry_count=retries,
            driver=driver,
        )
        sleep(2)
        return QianniuLoginResult(ok=True, web_page=web, yunma_calls=calls, shots=shots)
    except NeedsHumanError as e:
        last_err = str(e)
        if print_error_log:
            print(f"[NeedsHuman] {e}")
        return QianniuLoginResult(
            ok=False, web_page=web, error=last_err, yunma_calls=calls, shots=shots
        )
    except Exception as e:
        last_err = str(e)
        if print_error_log:
            print(f"[qn_login error] {e}")
        if on_error == OnError.TERMINATE:
            raise QianniuLoginError(last_err) from e
        return QianniuLoginResult(
            ok=False, web_page=web, error=last_err, yunma_calls=calls, shots=shots
        )


def main() -> None:
    r = qianniu_login(retries=int(os.environ.get("QIANNIU_RETRIES", "5")))
    print("RESULT", {"ok": r.ok, "error": r.error, "yunma_calls": r.yunma_calls, "shots": r.shots})
    if r.web_page and r.ok:
        print("URL", r.web_page.current_url)
    # leave browser open on NeedsHuman; close on hard fail if we own it
    if r.web_page and not r.ok and not isinstance(r.error, str):
        pass


if __name__ == "__main__":
    main()
