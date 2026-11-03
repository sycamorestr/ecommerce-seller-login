"""千牛登录步骤，在 main.py 传入的浏览器页面上执行。"""
from dataclasses import dataclass
from pathlib import Path
from time import sleep, time

from playwright.sync_api import Error as PlaywrightError, Page

from captcha import (
    NeedsHumanError,
    QianniuLoginError,
    SEL_DRAG_LABEL,
    click_errloading,
    do_nc_mouse_drag,
    handle_verification,
    is_visible,
    login_frame,
    nc_visible,
)

LOGIN_URL = "https://loginmyseller.taobao.com/"
SEL_USERNAME = "#fm-login-id"
SEL_PASSWORD = "#fm-login-password"
SEL_LOGIN_BTN = "button.fm-submit.password-login, button.fm-button.password-login, button.password-login"
SEL_LOGIN_ERROR = "div.login-error-msg"

SHOT_DIR = Path(__file__).resolve().parent / "output" / "shots"


@dataclass
class LoginResult:
    ok: bool
    error: str = ""


def save_screenshot(page: Page, name: str) -> None:
    """保存当前页面，方便对照登录结果。"""
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SHOT_DIR / f"{int(time())}_{name}.png"))


def detect_human_gate(page: Page) -> str | None:
    """检查页面及 iframe 中实际显示的验证提示。"""
    markers = ("短信验证", "获取验证码", "验证码已发送", "请输入验证码",
               "校验码", "人脸验证", "手机验证", "其他验证方式")
    for frame in page.frames:
        try:
            text = frame.locator("body").inner_text(timeout=1500)
        except PlaywrightError:
            continue  # 页面跳转时，原 iframe 可能已经销毁。
        for marker in markers:
            if marker in text:
                return marker
    return None


def check_login_feedback(page: Page) -> None:
    """短信验证和账号错误属于登录结果，交给主程序显示。"""
    human = detect_human_gate(page)
    if human:
        save_screenshot(page, "human_gate")
        raise NeedsHumanError(human)
    frame = login_frame(page)
    if is_visible(frame, SEL_LOGIN_ERROR, timeout_ms=1000):
        message = frame.locator(SEL_LOGIN_ERROR).first.inner_text().strip()
        if message:
            raise QianniuLoginError(message)


def login_steps(page: Page, account: str, password: str, token: str, retries: int) -> None:
    # 1. 打开登录页；已有登录状态时可能直接跳转到后台。
    page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
    if page.url.startswith(("https://myseller.taobao.com/", "https://loginmyseller.taobao.com/home")):
        print("已进入千牛后台，跳过账号密码输入，请确认当前店铺。")
        return
    frame = login_frame(page)
    frame.locator(SEL_USERNAME).fill(account)
    frame.locator(SEL_PASSWORD).click()

    # 2. 输入密码前，页面有时会先要求图片滑块验证。
    if is_visible(frame, SEL_DRAG_LABEL, timeout_ms=2000):
        handle_verification(page, token, retries)
    frame.locator(SEL_PASSWORD).fill(password)

    # 3. 处理普通滑块，再提交登录。
    for _ in range(6):
        for _ in range(retries):
            if nc_visible(page):
                do_nc_mouse_drag(page)
            elif click_errloading(page):
                sleep(1)
            else:
                break

        button = login_frame(page).locator(SEL_LOGIN_BTN).first
        button.wait_for(state="attached", timeout=10000)
        button.evaluate("""el => {
            el.classList.remove('fm-button-disabled');
            el.removeAttribute('disabled');
            el.click();
        }""")
        sleep(2)
        check_login_feedback(page)
        if click_errloading(page) or nc_visible(page):
            continue
        break

    # 4. 等页面跳转完成，再确认是否仍停在登录页。
    sleep(2)
    check_login_feedback(page)
    if "loginmyseller.taobao.com" in page.url and "/home" not in page.url:
        save_screenshot(page, "still_login")
        raise QianniuLoginError("仍停在登录页，请查看页面提示或手动完成验证。")
    save_screenshot(page, "after_login")


def qianniu_login(page: Page, account: str, password: str,
                  yunma_token: str = "", retries: int = 5) -> LoginResult:
    """已知登录失败返回结果；程序错误直接抛出，便于断点调试。"""
    try:
        login_steps(page, account, password, yunma_token, retries)
    except QianniuLoginError as error:
        return LoginResult(False, str(error))
    return LoginResult(True)
