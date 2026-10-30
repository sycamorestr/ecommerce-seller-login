import os
import sys
import http.client
import base64
import json


from PIL import ImageGrab, Image
from io import BytesIO
from ctypes import windll

import xbot
import xbot_visual
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation
from xbot import print, sleep, win32, web
from .package import variables as glv
from .utils import create_cache_dir

# Setting up environment paths
arch = 'x86' if '86' in os.environ['PROCESSOR_ARCHITECTURE'] else 'x64'

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.environ['PYTHONPATH'])), f"support_{arch}/cv-engine/site-packages"))

import numpy as np
import cv2


def get_ppi():
    """获取屏幕的缩放"""
    LOGPIXELSX = 88
    LOGPIXELSY = 90
    user32 = windll.user32
    user32.SetProcessDPIAware()
    dc = user32.GetDC(0)
    pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
    user32.ReleaseDC(0, dc)
    res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
    return res[1] / res[0]



def drag(drag_ele: WebElement, distance: int):
    """Simulates a drag action for a specified element over a given distance."""
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=0.1, max_time=0.5)
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed="middle")
    win32.mouse_click(button="left", click_type="down")
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed="middle")
    win32.mouse_click(button="left", click_type="up")
    win32.manual_motion_off()


def get_x(left_image: str, right_image: str) -> int:
    """计算验证码x轴的偏移距离"""
    right_img = cv2.imread(right_image)
    left_img = cv2.imread(left_image)

    bg_edge = cv2.Canny(right_img, 150, 152)
    tp_edge = cv2.Canny(left_img, 150, 152)

    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(res)

    return max_loc[0] + int(left_img.shape[1])


def handle_captcha(
    web_page: xbot.web.WebBrowser,
    background_ele: str,
    slider_ele: str,
    drag_ele: str,
    retry_count: int = 5,
    offset: int = 0,
    ym_token: str = ""
):
    """Handles slider CAPTCHA by calculating and simulating the drag distance."""
    cache_folder = create_cache_dir()
    # xbot.logging.info(f"Cache Dir: {cache_folder}")

    for _ in range(retry_count):
        drag_element = web_page.find(drag_ele)

        # 将背景图片按照滑块所在的位置截成左右两张图片
        left_img_path = os.path.join(cache_folder, "std_captcha_left.png")
        rigt_img_path = os.path.join(cache_folder, "std_captcha_right.png")
        b_x, b_y, b_w, b_h = web_page.find(background_ele).get_bounding(to96dpi=False)
        s_x, s_y, s_w, s_h = web_page.find(slider_ele).get_bounding(to96dpi=False)
        
        xbot.win32.screenshot.save_screen_to_file(left_img_path, "png", b_x, b_y, b_x + s_w, b_y + b_h)
        xbot.win32.screenshot.save_screen_to_file(rigt_img_path, "png", s_x + s_w, b_y, b_x + b_w, b_y + b_h)

        # 识别出 x 轴的滑块距离
        distance = get_x(left_img_path, rigt_img_path)

        # Calculate distance
        distance = int((distance + offset) * get_ppi())
        # xbot.logging.info(f"Distance: {distance}")
        
        drag(drag_element, distance)
        sleep(3)

        try:
            x, y, width, height = drag_element.get_bounding()
            if width == 0 and height == 0:
                print("Captcha is no longer present, exiting.")
                break
        except:
            pass

        if not xbot_visual.web.browser.element_display(browser=web_page, selector=background_ele, content_type="display"):
            break


def main(args):
    web_page = args.get("web_page")
    background_ele = args.get("background_ele")
    slider_ele = args.get("slider_ele")
    drag_ele = args.get("drag_ele")
    retry_count = args.get("retry_count")
    offset = args.get("offset")

    # test
    # web_page = web.get_active(mode="edge")
    # background_ele = "std_captcha_background_ele"
    # slider_ele = "std_captcha_slider_ele"
    # drag_ele = "std_captcha_drag_ele"
    # retry_count = 5
    # offset = 0


    handle_captcha(web_page, background_ele, slider_ele, drag_ele, retry_count, offset)