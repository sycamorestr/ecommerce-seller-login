import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        web_page = None
        登录账号 = ""
        登录密码 = ""
        识别引擎 = "影刀引擎"
        云码Token = ""
    else:
        web_page = args.get("web_page", None)
        登录账号 = args.get("登录账号", "")
        登录密码 = args.get("登录密码", "")
        识别引擎 = args.get("识别引擎", "影刀引擎")
        云码Token = args.get("云码Token", "")
    try:
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://auth.orangebank.com.cn/cimp-ccs-pc/#/p/ebank-login", ignore_cache=False, load_timeout="20", _block=("平安银行登录-流程版", 1, "跳转至新网址"))
        xbot_visual.web.element.input(browser=web_page, element=package.selector("平安银行-账号输入框"), text=登录账号, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("平安银行登录-流程版", 2, "填写输入框(web)"))
        xbot_visual.web.element.input(browser=web_page, element=package.selector("平安银行-密码输入框"), text=登录密码, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=True, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("平安银行登录-流程版", 3, "填写输入框(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("平安银行-登录按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("平安银行登录-流程版", 4, "点击元素(web)"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("平安银行登录-流程版", 5, "等待"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("平安银行-验证码背景图"), _block=("平安银行登录-流程版", 6, "IF 元素可见(web)")):
            _ = xbot_visual.process.run(process="orangebank_slider_captcha", package=__name__, inputs={
                "web_page": lambda: web_page,
                "background_ele": package.selector("平安银行-验证码背景图"),
                "drag_ele": package.selector("平安银行-验证码滑块图"),
                "retry_count": lambda: 5,
                "gap_ele": package.selector("平安银行-验证码缺口图片"),
                "refresh_ele": package.selector("平安银行-验证码刷新图片"),
                "ym_token": 云码Token,
                }, outputs=[
            ], _block=("平安银行登录-流程版", 7, "调用流程"))
            xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("平安银行登录-流程版", 8, "等待"))
        #endif
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("平安银行-登录信息"), _block=("平安银行登录-流程版", 10, "IF 元素可见(web)")):
            web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("平安银行-登录信息"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("平安银行登录-流程版", 11, "获取元素信息(web)"))
            raise Exception(web_element_attribute)
        #endif
    finally:
        pass
