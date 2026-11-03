"""验证码处理：普通拖动滑块，以及需要云码识别的图片滑块。"""
import base64
import http.client
import json
import random
from io import BytesIO
from pathlib import Path
from time import sleep

from PIL import Image
from playwright.sync_api import Error as PlaywrightError, FrameLocator, Page, TimeoutError as PlaywrightTimeout

YUNMA_HOST = "api.jfbym.com"
YUNMA_PATH = "/api/YmServer/customApi"
YUNMA_TYPE_ALI_SLIDER = 20226
IFRAME_CSS = "iframe#alibaba-login-box"
BAXIA_IFRAME_CSS = "iframe#baxia-dialog-content"
SEL_DRAG_LABEL = "canvas#captcha-question, .scratch-captcha-question-header, .drag-captcha-question"
SEL_REFRESH = "i.icon-refresh.refresh.scratch, i.icon-refresh.scratch, i.refresh.scratch"
SEL_DRAG_ELE = ".scratch-captcha-slider .button, #nocaptcha .scratch-captcha-slider .button"
SEL_NC_VERIFY = "#nc_1__scale_text"
SEL_NC_SLIDE = "#nc_1_n1z"


CACHE_DIR = Path(__file__).resolve().parent / "output" / "captcha_cache"


class QianniuLoginError(Exception):
    """登录流程已知的失败原因。"""


class NeedsHumanError(QianniuLoginError):
    """当前步骤需要人工验证。"""


def yunma_recg(token: str, base64_im: str) -> dict:
    """把验证码图片发给云码，返回识别结果。"""
    conn = http.client.HTTPConnection(YUNMA_HOST, timeout=60)
    data = {"image": base64_im, "token": token, "type": YUNMA_TYPE_ALI_SLIDER}
    try:
        conn.request("POST", YUNMA_PATH, body=json.dumps(data), headers={"Content-Type": "application/json"})
        return json.loads(conn.getresponse().read())
    finally:
        conn.close()


def encode_image(image: Image.Image) -> str:
    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def decode_image(base64_string: str) -> Image.Image:
    base64_string += "=" * (-len(base64_string) % 4)
    img = Image.open(BytesIO(base64.b64decode(base64_string)))
    return img.convert("RGBA")


def join_images(image1: Image.Image, image2: Image.Image) -> Image.Image:
    """按云码的图片格式，把提示图放在背景图上方，中间留 11 像素。"""
    w1, h1 = image1.size
    w2, h2 = image2.size
    new_image = Image.new("RGB", (max(w1, w2), h1 + h2 + 11), (255, 255, 255))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (0, h1 + 11))
    return new_image


def login_frame(page: Page) -> FrameLocator:
    return page.frame_locator(IFRAME_CSS)


def baxia_frame(page: Page) -> FrameLocator:
    """登录 iframe 内还有一层验证 iframe。"""
    return login_frame(page).frame_locator(BAXIA_IFRAME_CSS)


def is_visible(frame: FrameLocator, selector: str, timeout_ms: int = 1500) -> bool:
    """可选验证码未出现时返回 False；其他错误正常抛出。"""
    try:
        frame.locator(selector).first.wait_for(state="visible", timeout=timeout_ms)
        return True
    except PlaywrightTimeout:
        return False


def mouse_drag(
    page: Page,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    overshoot: bool = False,
) -> None:
    """从起点拖到终点；图片滑块到终点后会轻微回调。"""
    page.mouse.move(x1, y1)
    sleep(0.15)
    page.mouse.down()
    sleep(0.12)
    if overshoot:
        right_offset = random.randint(-5, 5)
        left_offset = random.randint(-5, 5)
        page.mouse.move(x2 + right_offset, y2, steps=16)
        sleep(0.08)
        page.mouse.move(x2 - left_offset, y2, steps=8)
        sleep(0.08)
        page.mouse.move(x2, y2, steps=4)
        sleep(0.05)
    else:
        # 普通滑块先快后慢，保留原来的拖动轨迹。
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


def collect_data_images(page: Page) -> list[str]:
    """从登录 iframe 读取内嵌图片和画布中的验证码。"""
    return login_frame(page).locator("body").evaluate(
        """() => {
            const images = [];
            for (const img of document.querySelectorAll('img')) {
                if (img.src.startsWith('data:image')) images.push(img.src);
            }
            for (const canvas of document.querySelectorAll('canvas')) {
                // 含跨域内容的画布不允许导出，跳过这类画布。
                try { images.push(canvas.toDataURL('image/png')); }
                catch (error) { if (error.name !== 'SecurityError') throw error; }
            }
            return images;
        }"""
    )


def handle_verification(page: Page, token: str, retry_count: int) -> None:
    """读取图片 → 云码识别 → 拖动滑块；未通过则提示人工验证。"""
    if not token:
        raise NeedsHumanError("检测到图片滑块，请在浏览器手动验证，或在配置文件填写云码 Token。")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    frame = login_frame(page)

    for attempt in range(retry_count):
        if not is_visible(frame, SEL_DRAG_LABEL, timeout_ms=2000) and not is_visible(
            frame, SEL_DRAG_ELE, timeout_ms=1000
        ):
            return
        print(f"图片滑块：第 {attempt + 1} 次识别")
        refresh = frame.locator(SEL_REFRESH).first
        if refresh.is_visible():
            refresh.click(force=True, timeout=5000)
        sleep(3)

        # 这个验证码的提示图高 30 像素，背景图高 180 像素。
        tips = []
        background = None
        for data_url in collect_data_images(page):
            img = decode_image(data_url.split(",", 1)[1])
            if img.height == 30:
                tips.append(img)
            elif img.height == 180:
                background = img
        if background is None or not tips:
            continue

        for index, tip in enumerate(tips):
            captcha_image = join_images(tip, background)
            captcha_image.save(CACHE_DIR / f"captcha_{attempt}_{index}.png")
            result = yunma_recg(token, encode_image(captcha_image))
            if result.get("msg") != "识别成功":
                print("图片识别失败：", result.get("msg"))
                continue
            # 识别坐标减去原验证码的两个偏移量，得到拖动距离。
            distance = int(result["data"]["data"]) - 24 - 10
            box = frame.locator(SEL_DRAG_ELE).first.bounding_box(timeout=5000)
            if box is None:
                raise NeedsHumanError("图片滑块位置已变化，请在浏览器中手动验证。")
            x = box["x"] + box["width"] / 2 + random.randint(-5, 5)
            y = box["y"] + box["height"] / 2 + random.randint(-5, 5)
            mouse_drag(page, x, y, x + distance, y, overshoot=True)
            break
        sleep(3)
        if not is_visible(frame, SEL_DRAG_ELE, timeout_ms=2000):
            return
    raise NeedsHumanError("图片滑块未通过，请在浏览器中手动验证。")


def do_nc_mouse_drag(page: Page) -> None:
    """普通滑块：获取坐标，再向右拖动一个验证条的宽度。"""
    sleep(3)
    frame = baxia_frame(page)
    if not is_visible(frame, SEL_NC_SLIDE, timeout_ms=2000):
        frame = login_frame(page)
    slide = frame.locator(SEL_NC_SLIDE).first
    verify = frame.locator(SEL_NC_VERIFY).first
    slide.wait_for(state="visible", timeout=5000)
    verify.wait_for(state="visible", timeout=5000)
    sr = slide.bounding_box()
    vr = verify.bounding_box()
    if not sr or not vr:
        raise NeedsHumanError("无法获取普通滑块的位置，请在浏览器中手动验证。")

    verify_w = vr["width"]
    track = frame.locator("#nc_1_n1t").first
    if track.is_visible():
        tr = track.bounding_box(timeout=1000)
        if tr and tr["width"] > 0:
            verify_w = min(verify_w, tr["width"])

    # bounding_box 已经是整个页面的坐标，不需要加 iframe 偏移。
    x1 = sr["x"] + sr["width"] / 2
    y1 = sr["y"] + sr["height"] / 2
    x2 = x1 + verify_w
    mouse_drag(page, x1, y1, x2, y1)
    sleep(1.2)


def nc_visible(page: Page) -> bool:
    """普通滑块可能在登录框，也可能在内层验证框。"""
    return any(
        is_visible(frame, selector, timeout_ms=500)
        for frame in (login_frame(page), baxia_frame(page))
        for selector in (SEL_NC_SLIDE, SEL_NC_VERIFY)
    )


def click_errloading(page: Page) -> bool:
    """验证码提示重试时，点击对应提示。"""
    frame = login_frame(page)
    targets = [
        frame.locator("div.errloading").first,
        baxia_frame(page).locator("div.errloading").first,
        frame.get_by_text("验证失败, 点击框体重试", exact=False).first,
        frame.get_by_text("验证失败，点击框体重试", exact=False).first,
    ]
    for target in targets:
        try:
            if target.is_visible():
                target.click(timeout=2000)
                return True
        except PlaywrightError:
            continue  # 页面切换时，验证框可能已经关闭。
    return False
