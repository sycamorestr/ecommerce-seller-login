# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, win32
from .import package
from .package import variables as glv
import http
import json
import os
import base64
import xbot_visual
import ctypes
from ctypes import windll
import time
import ast
import numpy as np

from xbot._core import robot
from xbot.selector import Selector
from urllib.parse import urlparse
from xbot_extensions.activity_jfbym import zfb_four_click_captcha
from .click_captcha import handle_captcha as click_handle_captcha
import sqlite3
import random


import sys
arch = 'x86' if '86' in os.environ['PROCESSOR_ARCHITECTURE'] else 'x64'

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.environ['PYTHONPATH'])), f"support_{arch}/cv-engine/site-packages"))

import numpy as np
import cv2

def get_xbot_client_token():
    """获取客户端 token"""
    common_info = xbot._core.robot.execute(f'Common.CommonConfig', None)
    return common_info.get("token")


def drag_gen(drag_ele, distance:int):
    mouse_pos_path = get_data_by_distance(distance)
    xbot.win32.manual_motion_on()

    x, y, width, height = drag_ele.get_bounding()

    point_x = int(x + width / 2)
    point_y = int(y + height / 2)
    xbot.win32.mouse_move(point_x, point_y)
    win32.mouse_click(button="left", click_type="down")

    for offset_x, offset_y, t in mouse_pos_path:
        xPoint = int((point_x + int(offset_x)) / get_ppi()) 
        yPoint = int((point_y + int(offset_y)) / get_ppi())
        _moveTo(xPoint, yPoint)
        sleep(t/2000)
    
    sleep(1)
    
    win32.mouse_click(button="left", click_type="up")
    xbot.win32.manual_motion_off() 

def _moveTo(x, y):
    """Send the mouse move event to Windows by calling SetCursorPos() win32
    function.

    Args:
      button (str): The mouse button, either 'left', 'middle', or 'right'
      x (int): The x position of the mouse event.
      y (int): The y position of the mouse event.

    Returns:
      None
    """
    if os.name == 'nt':
        ctypes.windll.user32.SetCursorPos(x, y)
    else:
        win32.mouse_move(x, y, move_speed="instant")

def get_ppi():
    """
    获取屏幕的缩放
    """
    if os.name == 'nt':
        LOGPIXELSX = 88
        LOGPIXELSY = 90
        user32 = windll.user32
        user32.SetProcessDPIAware()
        dc = user32.GetDC(0)
        pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
        user32.ReleaseDC(0, dc)
        res = float.as_integer_ratio(round(pix_per_inch / 96,2))
        return res[1]/res[0]
    else:
        return 1

def get_data_by_distance(distance, one=True):
    db_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="test_database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if distance <= 50:
        di = 50
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 50")
    elif 50 < distance < 150:
        di = 100
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 100")
    elif 150 <= distance < 200:
        di = 150
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 150")
    else:
        di = 200
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 200")

    rows = cursor.fetchall()

    if one:
        random_index = random.randint(0, len(rows) - 1)

        data = json.loads(rows[random_index][2])
        tmp = []
        for item in data:
            tmp.append([item[0], item[1] + random.randint(-2, 2), item[2]])
        # print("rows[random_index][2]:", rows[random_index][2])
        result = ast.literal_eval(rows[random_index][2])
        for i in range(len(result)):
            result[i][0] = result[i][0] * distance  / di
        result[-1][0] = distance 
        # print("result:", result)
        result = json.dumps(result)
        return json.loads(result)
    return [json.loads(row[2]) for row in rows]


def bt_captcha(payload: dict):
    """使用增值服务请求验证码
    :param payload: 冰拓body参数(除去username和password)
    """
    captcha_type = payload.get("captchaType")
    payload.pop("captchaType")
    common_info = robot.execute(f"Common.CommonConfig", None)

    token = common_info.get("token")
    web_api = common_info.get("webApi")
    is_publish_client = common_info.get("isPublicClient")

    parsed = urlparse(web_api)
    is_ssl = parsed.scheme.lower() == "https"
    host = parsed.hostname

    # 公有云客户端
    if is_publish_client:
        host = "api.yingdao.com"
        is_ssl = True

    if is_ssl:
        conn = http.client.HTTPSConnection(host, timeout=60)
    else:
        conn = http.client.HTTPConnection(host, timeout=60)

    res_payload = json.dumps({
        "aiToolInterfaceCodeId": f"captcha_bingtop_bingtop_{captcha_type}",
        "aiID": "captcha",
        "rule": "bingtop",
        "channel": "bingtop",
        "model": captcha_type,
        "thirdPartyReqData": {
            "headers": {},
            "params": {},
            "body": payload,
        },
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/api/v2/aiservice/call/captcha",
                 res_payload, headers)
    res = conn.getresponse()
    response_data = res.read().decode('utf-8')
    response_json = json.loads(response_data)
    conn.close()
    data = response_json.get("data")
    # print(data)
    if not data:
        raise Exception(f"错误信息: {response_json}")
    return data["response"]["recognition"]


def get_xbot_activity_cache_folder(activity_code):
    """根据指令code 获取本地缓存目录, 不存在则创建"""
    local_appdata_path = os.getenv('LOCALAPPDATA')
    xbot_app_cache_dir = os.path.join(local_appdata_path, "xbot_app", activity_code)
    if not os.path.exists(xbot_app_cache_dir):
        os.makedirs(xbot_app_cache_dir)
    return xbot_app_cache_dir


def imread_unicode(path, flags=cv2.IMREAD_COLOR):
    # 以二进制方式读取文件
    with open(path, 'rb') as f:
        data = f.read()
    img_array = np.frombuffer(data, np.uint8)
    return cv2.imdecode(img_array, flags)


def get_x(left_image: str, right_image: str) -> int:
    """通过 cv 计算验证码x轴的偏移距离"""
    left_img = imread_unicode(left_image, cv2.IMREAD_GRAYSCALE)
    right_img = imread_unicode(right_image, cv2.IMREAD_GRAYSCALE)

    bg_edge = cv2.Canny(right_img, 150, 152)
    tp_edge = cv2.Canny(left_img, 150, 152)

    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(res)

    return max_loc[0] + int(left_img.shape[1])


def get_window_scale():
    """兼容 Win7 的屏幕缩放获取函数"""
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Windows 7 兼容
    except Exception:
        pass  # 在某些系统上可能已经设置或不支持

    hDC = ctypes.windll.user32.GetDC(0)
    LOGPIXELSX = 88
    dpi = ctypes.windll.gdi32.GetDeviceCaps(hDC, LOGPIXELSX)
    ctypes.windll.user32.ReleaseDC(0, hDC)
    scale = dpi / 96.0
    return scale


def drag(web_page, drag_ele: xbot.web.WebElement, distance:int):
    """实现拖拽轨迹"""
    drag_gen(web_page.find(drag_ele), distance)


def file2base64(file_path) -> str:
    """将本地文件转换成 base64"""
    with open(file_path, "rb") as f:
        image_data = f.read()
        base64_str = base64.b64encode(image_data).decode("utf-8")
        return base64_str


def handle_slider_captcha(
    web_page: xbot.web.WebBrowser,
    background_ele: str,
    slider_ele: str,
    drag_ele: str,
):
    """Handles slider CAPTCHA by calculating and simulating the drag distance."""
    cache_folder = get_xbot_activity_cache_folder("xbot_app")
    print(cache_folder)
    
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
    distance = int((distance) / get_window_scale())
    # print(distance)
    # xbot.logging.info(f"Distance: {distance}")
    
    drag(web_page,drag_ele, distance)
    sleep(3)

    try:
        x, y, width, height = web_page.find(drag_ele, timeout=2).get_bounding()
        if width == 0 and height == 0:
            print("Captcha is no longer present, exiting.")
    except:
        pass

def handle_click_captcha(web_page:xbot.web.WebBrowser, captcha_click_selector: xbot.web.WebElement):
    """处理点击验证码"""
    scale = get_window_scale()
    # print(f'缩放为：【{scale}】')
    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    save_path = os.path.join(cache_folder, "zfb_client.png")
    bg_offset_x, bg_offset_y, _, _ = web_page.find(captcha_click_selector).get_bounding(to96dpi=True)

    # 获取未装换成96dpi的坐标
    x, y, width, height = web_page.find(captcha_click_selector).get_bounding(to96dpi=False)
    win32.screenshot.save_screen_to_file(save_path, "png", x, y, x + width, y + height)
    # xbot.logging.info(save_path)

    # 将图片转成 base64
    img_base64 = file2base64(save_path)
    payload = {
        "captchaData": img_base64, #验证码图的base64
        "captchaType": 1311  #类型
    }

    # 识别验证码
    data = bt_captcha(payload)
    positions = [item.split(",") for item in data.split("|")]

    # 根据识别的坐标进行验证
    xbot.win32.manual_motion_on(min_time=0.5, max_time=2)
    for t_x, t_y in positions:
        target_p_x = bg_offset_x + int(int(t_x) / scale)
        target_p_y = bg_offset_y + int(int(t_y) / scale)
        xbot.win32.mouse_move(target_p_x, target_p_y, delay_after=0.1)
        xbot.win32.mouse_click(delay_after=0.5)

    xbot.win32.manual_motion_off()
    

def handle_captcha(web_page: xbot.web.WebBrowser, retry: int =10):
    """处理支付宝验证码, 滑块走cv接口, 点选使用冰拓接口"""
    captcha_click_selector_data =  {'id': 'zhf', 'name': 'zfb', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//div[@class="jshield-captcha-click-container click"]']}}
    captcha_click_selector = Selector(captcha_click_selector_data)

    # //img[@id="puzzle_backimg"]          背景元素
    captcha_background_selector_data = {'id': 'zhf', 'name': 'zfb', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//img[@id="puzzle_backimg"]']}}
    captcha_background_selector = Selector(captcha_background_selector_data)

    # //div[@id="puzzle_slot"]      缺口元素
    captcha_slider_selector_data = {'id': 'zhf', 'name': 'zfb', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//div[@id="puzzle_slot"]']}}
    captcha_slider_selector = Selector(captcha_slider_selector_data)

    # //div[@class="dv_handler baseslider"]        拖拽元素
    captcha_drag_selector_data = {'id': 'zhf', 'name': 'zfb', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//div[@class="dv_handler baseslider"]']}}
    captcha_drag_selector = Selector(captcha_drag_selector_data)

    #//div[@class="jshield-feedback-wrapper captcha"]       反馈窗口元素
    captcha_fankui_selector_data = {'id': 'zhf', 'name': 'zfb', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//div[@class="jshield-feedback-wrapper captcha"]']}}
    captcha_fankui_selector = Selector(captcha_fankui_selector_data)

    #//img[@class="jshield-feedback-close captcha"]         取消反馈窗口元素
    captcha_cancel_selector_data = {'id': 'zhf', 'name': 'zfb', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//img[@class="jshield-feedback-close captcha"]']}}
    captcha_cancel_selector = Selector(captcha_cancel_selector_data)

    #(//img[@class="refresh-button-img puzzle"])[2]     刷新元素
    captcha_refresh_selector_data = {'id': 'zhf', 'name': 'zfb', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['(//img[@class="refresh-button-img puzzle"])[2]']}}
    captcha_refresh_selector = Selector(captcha_refresh_selector_data)

    scale = get_window_scale() # 获取屏幕缩放
    # 获取图片的缓存目录
    cache_folder = get_xbot_activity_cache_folder("activity_jfbym")
    save_path = os.path.join(cache_folder, "zfb_client.png")

    click_captcha_count = 0 # 仅统计点选验证码的验证次数

    captcha_background_selector_data_other = {'id': 'zhf', 'name': 'zfb', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//div[@class="image-container clickpuzzle"]']}}
    captcha_background_selector_data_other = Selector(captcha_background_selector_data_other)

    captcha_sure_selector_data_other = {'id': 'zhf', 'name': 'zfb', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': ['//div[contains(@class, "confirm-button")]']}}
    captcha_sure_selector_data_other = Selector(captcha_sure_selector_data_other)
    
    while 1:
        if click_captcha_count > retry:
            raise Exception("支付宝验证码处理失败")

        # 判断是否误触问题反馈
        if web_page.is_element_displayed(captcha_fankui_selector):
            web_page.find(captcha_cancel_selector).click()
            web_page.find(captcha_refresh_selector).click()
            
        # 如果验证码元素不存在就退出循环
        if web_page.is_element_displayed(captcha_background_selector):
            # xbot.logging.info(f"正在处理拼图验证码")
            handle_slider_captcha(web_page, captcha_background_selector, captcha_slider_selector, captcha_drag_selector)

        elif web_page.is_element_displayed(captcha_click_selector):
            xbot.logging.info(f"正在第{click_captcha_count + 1}处理点选验证码")
            click_handle_captcha(web_page, captcha_click_selector, retry_count=1)
            click_captcha_count += 1
        
        elif len(web_page.find_all_by_xpath('//*[@class="image-item clickpuzzle"]', timeout=1)) == 4:
            sure_xpath = '//div[contains(@class, "confirm-button")]'
            zfb_four_click_captcha.handle_captcha(web_page=web_page, image_ele=captcha_background_selector_data_other, commit_ele=captcha_sure_selector_data_other, ym_token=None)
        else:
            break
        
        sleep(2)
    

def zfb_login(browser_mode, username, password, retry_count=10):
    """支付宝登录"""
    assert str(retry_count).isdigit(), f"retry_count 应该是数字, 而不是{retry_count}"
    retry_count = int(retry_count)

    url = "https://auth.alipay.com/login/index.htm"

    # web_page = xbot.web.create(url=url, mode=browser_mode, load_timeout=20, silent_running=True, stop_if_timeout=True)
    try:
        web_page = xbot.web.get_active(mode=browser_mode, load_timeout=5)
        if url not in web_page.get_url():
            web_page = xbot.web.create(url=url, mode=browser_mode, load_timeout=60, stop_if_timeout=True)
    except:
        web_page = xbot.web.create(url=url, mode=browser_mode, load_timeout=60, stop_if_timeout=True)
    # 使用静默方式输入, 避免ctrl+a导致权限的问题
    web_page.find_by_xpath('//li[@data-status="show_login"]').click()
    sleep(1)
    web_page.find_by_xpath('//input[@id="J-input-user"]').click()
    sleep(1)
    xbot.win32.send_keys(keys="^{a}")
    sleep(1)
    xbot.win32.send_keys(keys="{DELETE}")
    web_page.find_by_xpath('//input[@id="J-input-user"]').input(username)
    password = xbot_visual.decrypt(password)
    web_page.find_by_xpath('//input[@id="password_rsainput"]').input(password)
    # 解除静默输入
    web_page = xbot.web.get_active(mode=browser_mode)
    web_page.find_by_xpath('//input[@id="J-login-simulate-btn"]').click()
    # 等待 2s, 然后判断有无验证码出现, 有就处理验证码
    sleep(2)
    handle_captcha(web_page, retry_count)
    # 判断是否登录成功
    login_error_msg_list = web_page.find_all_by_xpath('//div[@id="J-errorBox"]/span[@class="sl-error-text"]', timeout=3)
    if len(login_error_msg_list) != 0 and login_error_msg_list[0].get_text() != "":
            raise Exception(f"登录失败, 错误元素: {login_error_msg_list[0].get_text()}")
    return web_page


def test_zfb_login():
    """测试支付宝登录"""
    username = ""
    password = ""
    browser_mode = "chrome"
    zfb_login(browser_mode, username, password, 10)

def main(args):
    test_zfb_login()
    # # zfb_login()
