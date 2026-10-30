# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv


import json
import os
from codecs import encode
if os.name =='nt':
    from ctypes import windll
import xbot_visual
import http.client
import mimetypes
import urllib.request
import urllib.parse
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation
from PIL import Image, ImageChops, ImageOps, ImageFont, ImageDraw
from xbot import print, sleep, win32
from .resources import trace_api
from . import package
import xbot
from xbot import print, sleep, win32
from .import package
from .package import variables as glv
from xbot.win32.element import Win32Element

def drag2(web_page:xbot.web.WebBrowser, distance:int, move_speed = "slow"): 
    drag_element = web_page.find("拖拽")
    x, y, width, height = drag_element.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time="1", max_time="3", _block=("滑动验证", 11, "开启模拟真人操作"))
    xbot_visual.web.element.drag_to(browser=web_page, element=package.selector("拖拽"), drag_way="default", target_element=None, left=lambda: int(pos_center_x+distance), top=int(pos_center_y), delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_speed=move_speed, release_anchor_type="random", release_sudoku_part="Random", release_offset_x="0", release_offset_y="0", timeout="20", _block=("滑动验证", 12, "拖拽元素(web)"))
    xbot_visual.win32.manual_motion_off()

def main(args):
    pass