# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import xbot_visual

from xbot_visual import web_service
from xbot import print, sleep, web, ai
from xbot.web import WebBrowser
from . import package
from .package import variables as glv
     

def validate_input_content(username, password):
    """校验账号密码是否符合验证规则"""
    assert bool(username) and isinstance(username, str), "检查登录账号密码是否为字符串类型且不为空"
    assert bool(password) and isinstance(password, str), "检查登录账号密码是否为字符串类型且不为空"


def deal_verification(web_page: WebBrowser):
    if web_page.find("支付宝_验证码_图片").is_displayed():
        return

    for i in range(5):
        captcha_result = web_service.captcha(
            engine_type="shadowbot",
            captcha_type="3",
            third_party_code="ttshitu_3_predict",
            image_source="web_element",
            image_browser=web_page,
            image_web_selector=package.selector("验证码元素"),
        )
        if len(captcha_result) == 4:
            web.find("支付宝_验证码_图片").click(simulate=False, move_mouse=False)
            continue
        web_page.find("支付宝_验证码_输入框").click()
        web_page.find("支付宝_验证码_输入框").input(captcha_result)
        if web_page.wait_appear("验证码输入正确", timeout="5"): return
        if xbot_visual.web.browser.contains_element_or_text(
                browser=web_page,
                content_type="contains_element",
                selector=package.selector("验证码输入正确")):
            break
        else:
            web_page.find("支付宝_验证码_图片").click()


def main(args):
    url = "https://auth.alipay.com/login/index.htm"
    mode = "chrome"
    username = ""
    password = ""
    phonenum_verification_url = "https://authsa127.alipay.com/login/checkSecurity.htm"
    validate_input_content(username, password)
    web_page = web.create(url, mode="chrome", stop_if_timeout=True)
    web_page.find("支付宝_切换登录_账密登录", timeout=10).click(simulative=True)
    wait_result = web_page.wait_appear("支付宝_账号_输入框", timeout=60)
    web_page.find("支付宝_账号_输入框").input(username)
    web_page.find("支付宝_密码_输入框").click()
    xbot.win32.manual_motion_on()
    web_page.find("支付宝_密码_输入框").input(password, simulative=True)
    xbot.win32.manual_motion_off()
    input_value = web_page.find("支付宝_密码_输入框").get_value()
    web_page.find("支付宝_登录_按钮2").click()
    deal_verification(web_page)
    web_page = web.get_active(mode=mode)
    assert web_page.get_url() != phonenum_verification_url, "请先填写手机验证码登录"

    

    # 点击登录后, 出现短信验证码, 填写

    pass
