import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("xztest", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("xztest", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # web.element.click
        # web.element.hover
        # win32.click_mouse
        # win32.send_keys
        # web.element.click
        # web.element.click
        # xbot_extensions.activity_jfbym.std_slider_captcha
        # web_service.captcha_paid
        # web.element.get_details
        # web.element.click
        # web.element.input
        # web.element.input
        # win32.manual_motion_on
        # web.element.click
        # win32.send_keys
        # win32.manual_motion_off
        # web_service.captcha_paid
        # web.browser.start_monitor_network
        # web.browser.navigate
        # web.element.click
        # web.browser.get_responses
        # web.browser.stop_monitor_network
        # programing.log
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # xbot_extensions.activity_jfbym.std_slider_captcha
        # process.run
        # process.run
        # web.get
        # web.browser.navigate
        # process.run
        # programing.log
        # process.run
    finally:
        pass
