# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import os
import xbot_visual
import base64
import json
import base64
import io
import urllib
import http.client
from PIL import ImageGrab, Image
import time

from PIL import Image
from io import BytesIO
from ctypes import windll
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation

from xbot import print, sleep, win32, web
from .import package
from .package import variables as glv

from xbot._core import robot
from .utils import get_xbot_activity_cache_folder, file2base64, get_ppi
from xbot_extensions.activity_jfbym import std_slider_captcha
import ddddocr 

def _read_image(image_path_or_url):
    """
    读取图片信息
    兼容本地路径和网络链接
    :param image_path_or_url: 图片路径,支持本地路径或网络链接
    """
    image = None
    # 判断传入的是本地文件路径还是链接
    if os.path.isfile(image_path_or_url):
        # 本地路径，直接读取图片
        with open(image_path_or_url, 'rb') as f:
            image = f.read()
        if image is None:
            raise(f"Failed to read image from local file: {image_path_or_url}")

    return image


def _ocr_by_path_or_url(image_path_or_url):
    image = _read_image(image_path_or_url)
    ocr = ddddocr.DdddOcr(show_ad=False)
    res = ocr.classification(image)
    return res


def get_xbot_client():
    common_info = robot.execute(f'Common.CommonConfig', None)
    return common_info.get("token")


def drag(web_page:xbot.web.WebBrowser,background_ele, gap_ele,drag_ele,drag_distance, refresh_ele, ym_token):
    # 获取背景图的位置
    background_position = web_page.find(background_ele).get_bounding(relative_to='screen')
    # 获取缺口滑块图的位置
    gap_block = web_page.find(gap_ele).get_bounding(relative_to='screen')
    # 获取偏移量
    offset = gap_block[0] - background_position[0]
    x, y, width, height = web_page.find(drag_ele).get_bounding(relative_to='screen')
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2
    move_speed = "middle"
    win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time=0.1, max_time=0.5)
    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)
    win32.mouse_click(button="left", click_type="down", delay_after=0)
    
    # 第一次获取当前缺口滑块的位置
    gap_block_first = web_page.find(gap_ele).get_bounding(relative_to='window')

    # 移动滑块
    win32.mouse_move(point_x = pos_center_x + 25*get_ppi_result, point_y=pos_center_y, relative_to='screen',move_speed=move_speed)
    print(web_page.find_by_xpath('//div[contains(@id,"dx_captcha_basic_sub-slider_")]').get_attribute('style').split('margin-left: '))
    back_ele_distance = web_page.find_by_xpath('//div[contains(@id,"dx_captcha_basic_sub-slider_")]').get_attribute('style').split('margin-left: ')[1].split('px;')[0]
    drag_ele_distance = web_page.find_by_xpath('//div[contains(@id,"dx_captcha_basic_slider_")]').get_attribute('style').split('margin-left: ')[1].split('px;')[0]
    win32.mouse_move(point_x = pos_center_x, point_y=pos_center_y, relative_to='screen',move_speed=move_speed)
    win32.mouse_click(button="left", click_type="up", delay_after=0)
    win32.manual_motion_off()
    offset_percent = round(float(back_ele_distance)/float(drag_ele_distance), 1)
    print(f'加速度为{offset_percent}')
    if ym_token == '':
        std_slider_captcha.main({'web_page': web_page, 'background_ele': package.selector(background_ele), 'slider_ele':package.selector(drag_ele), 'retry_count':1, 'offset': 0, 'speed': offset_percent, 'refresh_elem':None, "engine": "xbot"})
    else:
        std_slider_captcha.main({'web_page': web_page, 'background_ele': package.selector(background_ele), 'slider_ele':package.selector(drag_ele), 'retry_count':1, 'offset': 0, 'speed': offset_percent, 'refresh_elem':None, "engine": "ym", "ym_token": ym_token})


def deal_deal_handle_captcha(web_page,background_ele,drag_ele,gap_ele,refresh_ele,retry_count,ym_token,drag_distance):
    global get_ppi_result
    get_ppi_result = int(get_ppi())
    if not retry_count: retry_count=5
    if not drag_distance: drag_distance=0
    for i in range(retry_count):
        drag(web_page =web_page, background_ele =background_ele,gap_ele=gap_ele,drag_ele=drag_ele,drag_distance=drag_distance, refresh_ele=refresh_ele, ym_token=ym_token)
        time.sleep(3)
        if not web_page.is_element_displayed(background_ele):
            break
        else:
            web_page.find(refresh_ele).click()
            time.sleep(3)


def main(args):
    
    web_page = args.get("web_page", web.get_active('chrome'))
    background_ele = args.get("background_ele")
    gap_ele = args.get("gap_ele")
    drag_ele = args.get("drag_ele")
    refresh_ele = args.get("refresh_ele")
    retry_count = args.get("retry_count")
    ym_token = args.get("ym_token")
    drag_distance = args.get("drag_distance")
    deal_deal_handle_captcha(web_page = web_page,
                            background_ele = background_ele,
                            gap_ele = gap_ele,drag_ele = drag_ele, 
                            refresh_ele= refresh_ele,
                            retry_count=retry_count,
                            ym_token=ym_token,
                            drag_distance = drag_distance)


    # deal_deal_handle_captcha(web_page = web_page,
    #                                 background_ele = '中信银行-个人版验证码背景图',
    #                                 drag_ele = '中信银行-个人版验证码滑块',
    #                                 gap_ele = '中信银行-个人版验证码缺口图',
    #                                 refresh_ele = '中信银行-个人版验证码刷新按钮',
    #                                 retry_count = 5,
    #                                 ym_token = ym_token,
    #                                 drag_distance = drag_distance)
    # if not retry_count: retry_count=5

    # for i in range(retry_count):
    #     distance = handle_captcha(web_page,background_ele,drag_ele,ym_token)
    #     drag(web_page =web_page,captcha_result= distance,background_ele =background_ele,gap_ele=gap_ele,drag_ele=drag_ele)
    #     if not web_page.is_element_displayed(background_ele):
    #         break
    #     else:
    #         web_page.find(refresh_ele).click()
    #         time.sleep(2)
