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
    else:
        web_page = args.get("web_page", None)
        登录账号 = args.get("登录账号", "")
        登录密码 = args.get("登录密码", "")
    try:
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("中国银行登录-流程版", 1, "For次数循环")):
            xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://netc1.igtb.bankofchina.com/#/login-page?redirect=%2Findex", ignore_cache=False, load_timeout="20", _block=("中国银行登录-流程版", 2, "跳转至新网址"))
            xbot_visual.web.browser.navigate(browser=web_page, mode="reload", url="", ignore_cache=False, load_timeout="20", _block=("中国银行登录-流程版", 3, "跳转至新网址"))
            xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("中国银行登录-流程版", 4, "等待"))
            web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("中国银行-页面打开提示文案"), state="disappear", iswait=True, timeout="20", _block=("中国银行登录-流程版", 5, "等待元素(web)"))
            xbot_visual.web.element.input(browser=web_page, element=package.selector("中国银行-账号输入框"), text=登录账号, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("中国银行登录-流程版", 6, "填写输入框(web)"))
            xbot_visual.web.element.input(browser=web_page, element=package.selector("中国银行-密码输入框"), text=登录密码, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=True, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("中国银行登录-流程版", 7, "填写输入框(web)"))
            xbot_visual.web.element.hover(browser=web_page, element=package.selector("中国银行-验证码滑块"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("中国银行登录-流程版", 8, "鼠标悬停在元素上(web)"))
            xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="down", hardware_driver_click=False, keys="null", delay_after="1", _block=("中国银行登录-流程版", 9, "鼠标点击"))
            web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("中国银行-验证码背景图"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("中国银行登录-流程版", 10, "获取元素对象(web)"))
            xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="up", hardware_driver_click=False, keys="null", delay_after="1", _block=("中国银行登录-流程版", 11, "鼠标点击"))
            xbot_visual.web.element.set_attribute(browser=web_page, element=web_element, attribute_name="style", value="display: block;opacity: 1;", timeout="20", _block=("中国银行登录-流程版", 12, "设置元素属性(web)"))
            xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                "web_page": web_page,
                "engine": "xbot",
                "background_ele": package.selector("中国银行-验证码背景图"),
                "slider_ele": package.selector("中国银行-验证码滑块"),
                "ym_token": "",
                "retry_count": lambda: 5,
                "offset": lambda: 0,
                "speed": lambda: 1,
                "refresh_elem": None,
                }, outputs=[
            ], _block=("中国银行登录-流程版", 13, "通用单图滑块验证"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("中国银行-验证码验证成功"), _block=("中国银行登录-流程版", 14, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("中国银行-登录按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("中国银行登录-流程版", 15, "点击元素(web)"))
                break
            #endif
        #endloop
    finally:
        pass
