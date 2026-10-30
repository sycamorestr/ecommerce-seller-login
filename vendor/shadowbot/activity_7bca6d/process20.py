import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    web_page = None
    if args is None:
        浏览器类型 = ""
        登录账号 = ""
        登录密码 = ""
        重试次数 = 5
    else:
        浏览器类型 = args.get("浏览器类型", "")
        登录账号 = args.get("登录账号", "")
        登录密码 = args.get("登录密码", "")
        重试次数 = args.get("重试次数", 5)
    try:
        # 目前版本仅支持chrome浏览器
        # 登录逻辑: 先尝试手动登录, 然后利用设置元素值, 键盘输入回车绕过去
        invoke_result = xbot_visual.process.invoke_module(module="zfb_login", package=__name__, function="zfb_login", params={
            "browser_mode": 浏览器类型,
            "username": 登录账号,
            "password": 登录密码,
            "retry_count": 重试次数,
        }, _block=("支付宝登录", 3, "调用模块"))
        web_page = xbot_visual.programing.variable(value=invoke_result
        , _block=("支付宝登录", 4, "设置变量"))
        # workflow.if
        # web.create
        # workflow.elseif
        # web.create
        # workflow.elseif
        # web.create
        # workflow.elseif
        # web.create
        # workflow.elseif
        # web.create
        # workflow.endif
        # programing.comment
        # web.element.click
        # web.element.wait
        # web.element.input
        # web.element.click
        # win32.manual_motion_on
        # web.element.input_password
        # web.element.click
        # win32.manual_motion_off
        # programing.comment
        # xbot_extensions.web_action.获取当前激活的网页对象
        # web.browser.element_display
        # process.exit
        # process.return
        # workflow.endif
        # workflow.for
        # web.browser.element_display
        # programing.raise
        # web.element.click
        # workflow.endif
        # web.browser.element_display
        # programing.try
        # xbot_extensions.activity_jfbym.std_slider_captcha
        # programing.catch
        # web.element.click
        # xbot_extensions.activity_jfbym.std_slider_captcha
        # programing.endtry
        # workflow.endif
        # web.browser.element_display
        # xbot_extensions.activity_bintuo.zfb_click
        # workflow.endif
        # programing.sleep
        # web.browser.element_display
        # programing.raise
        # workflow.endif
        # workflow.endloop
        # programing.comment
        # web.browser.element_display
        # programing.raise
        # workflow.endif
        # web.browser.element_display
        # programing.raise
        # workflow.endif
        # web.browser.element_display
        # programing.raise
        # workflow.endif
    finally:
        args["web_page"] = web_page
