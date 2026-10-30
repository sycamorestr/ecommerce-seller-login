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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("main", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("main", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # process.run
        # xbot_extensions.activity_jfbym.std_click_select_captcha
        # datetime.to_string
        # web_service.download
        # programing.log
        # web.get
        # xbot_extensions.activity_jfbym.std_click_select_captcha
        # xbot_extensions.activity_jfbym.std_alphanum_captcha
        # web_service.captcha_paid
        # web_service.captcha_paid
        # xbot_extensions.activity_jfbym.std_click_select_captcha
        # xbot_extensions.activity_jfbym.jd_click_select_captcha
        # xbot_extensions.activity_4db973e3.坐标点选验证（去除界面 bug）
        xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
            "web_page": web_page,
            "engine": "ym",
            "background_ele": package.selector("中信银行-个人版验证码背景图"),
            "slider_ele": package.selector("中信银行-个人版验证码滑块"),
            "ym_token": "",
            "retry_count": lambda: 0,
            "offset": lambda: 0,
            "speed": lambda: 1.3,
            "refresh_elem": None,
            }, outputs=[
        ], _block=("main", 15, "通用单图滑块验证"))
    finally:
        pass
