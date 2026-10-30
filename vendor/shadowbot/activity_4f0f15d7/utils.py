# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web, win32
from .import package
from .package import variables as glv
from xbot.web import WebElement
from win32.lib import win32con
import win32api, win32gui, win32print
import os
import json 
import re
from os.path import dirname, join
import sys
import numpy as np
import cv2
import xbot_visual
from PIL import Image
import platform
import uuid
from xbot.selector import Selector

if os.name == 'nt':
    from ctypes import windll
import base64
import ctypes

# 使用platform模块来判断架构类型
machine = platform.machine().lower()
if 'x86_64' in machine or 'amd64' in machine:
    arch = 'x64'
elif 'aarch64' in machine or 'arm64' in machine:
    arch = 'arm64'
else:
    arch = 'x64'
# 设置PYTHONPATH
base_path = os.path.dirname(os.path.dirname(os.environ.get('PYTHONPATH', os.path.abspath(__file__))))
cv_engine_path = os.path.join(base_path, f"support_{arch}/cv-engine/site-packages")
if os.path.exists(cv_engine_path):
    sys.path.append(cv_engine_path)

def contains_chinese(text):
    if not isinstance(text, str):
        return False
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    return pattern.search(text) is not None

def create_cache_dir():
    """创建本地缓存文件夹，跨平台兼容"""
    if os.name == 'nt':  # Windows
        local_appdata_path = os.getenv('LOCALAPPDATA')
        if not local_appdata_path:
            local_appdata_path = os.path.expanduser("~\\AppData\\Local")
    else:  # Linux / UOS / macOS
        # 遵循 XDG Base Directory 规范
        local_appdata_path = os.getenv('XDG_CACHE_HOME')
        if not local_appdata_path:
            local_appdata_path = os.path.expanduser("~/.cache")

    # 确保路径是字符串（防御性编程）
    if not isinstance(local_appdata_path, str):
        local_appdata_path = "/tmp"

    # 构建缓存目录
    xbot_app_cache_dir = os.path.join(local_appdata_path, "xbot_activity", "activity_4f0f15d7")

    # 如果路径含中文，为避免某些库（如 OpenCV）对中文路径支持不佳，可选 fallback 到 /tmp
    if contains_chinese(xbot_app_cache_dir):
        xbot_app_cache_dir = os.path.join("/tmp", "xbot_activity", "activity_4f0f15d7")

    # 创建目录
    os.makedirs(xbot_app_cache_dir, exist_ok=True)

    return xbot_app_cache_dir


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

def get_ppi():
    import Quartz

    main_display_id = Quartz.CGMainDisplayID()

    # 获取显示器的物理尺寸（像素）
    width = Quartz.CGDisplayPixelsWide(main_display_id)
    height = Quartz.CGDisplayPixelsHigh(main_display_id)

    # 获取显示器的缩放比例
    # Quartz.CGDisplayBounds(main_display_id) 返回的是显示器的像素边界
    # 物理尺寸和像素边界之间的比率就是缩放比例
    display_bounds = Quartz.CGDisplayBounds(main_display_id)
    display_scale = width / display_bounds.size.width


def get_real_resolution():
    """获取真实的分辨率"""
    hDC = win32gui.GetDC(0)
    wide = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    high = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return {"wide": wide, "high": high}
 
 
def get_screen_size():
    """获取缩放后的分辨率"""
    wide = win32api.GetSystemMetrics(0)
    high = win32api.GetSystemMetrics(1)
    return {"wide": wide, "high": high}

def get_scaling():
    '''获取屏幕的缩放比例'''
    real_resolution = get_real_resolution()
    screen_size = get_screen_size()
    proportion = round(real_resolution['wide'] / screen_size['wide'], 2)
    return proportion

def cutbg1(path,box):
    img = Image.open(path)
    save_path = os.path.join(create_cache_dir(), "yanzhengmajietu_bg.png")
    image1 = img.crop(box)
    image1.save(save_path)
    return save_path

#裁剪背景
def cutbg(path,bigbox):
    img = Image.open(path)
    # print(img.format, img.size, img.mode)
    lp = int(bigbox[0])
    rp = int(bigbox[0]+bigbox[2])
    top = int(bigbox[1])
    button = int(bigbox[1]+bigbox[3])
    box1 = (lp, top, rp, button)
    # print(box1)
    image1 = img.crop(box1)
    save_path = os.path.join(create_cache_dir(), "wanz.png")
    image1.save(save_path)
    return save_path


# 把背景图片分割成缺块部分和缺口部分（一分为二）
def cut_ab(img, save_path_a, save_path_b, quekuai_left, a_width, offset):
    img_a = img.copy()
    # print(img.format, img.size, img.mode)
    lp = quekuai_left  # 左边距
    rp = int(quekuai_left + a_width)  # 右边距
    box1 = (lp, 0, rp, int(img.size[1]))
    image_a = img_a.crop(box1)
    image_a.save(save_path_a)

    lp = int(quekuai_left + a_width)  # 左边距
    rp = int(img.size[0])  # 右边距
    box1 = (lp, 0, rp, int(img.size[1]))
    image_b = img.crop(box1)
    # print(save_path_b)
    image_b.save(save_path_b)


# 识别图片返回缺口距离
def get_x(path_a,path_b):
    bg_img = cv2.imread(path_b)
    tp_img = cv2.imread(path_a)

    bg_edge = cv2.Canny(bg_img, 150, 152) # 原先是50，150，对内发光元素识别不准
    # cv2.imwrite(r'C:\Users\10485\Desktop\bg_edge.jpg', bg_edge)
    tp_edge = cv2.Canny(tp_img, 150, 152) # 原先是50，150，对内发光元素识别不准
    # cv2.imwrite(r'C:\Users\10485\Desktop\tp_edge.jpg', tp_edge)

    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配

    X = max_loc[0] + int(tp_img.shape[1])

    return X

def get_xbot_activity_cache_folder(activity_code):
    """根据指令code 获取本地缓存目录, 不存在则创建 - 跨平台版本"""
    if os.name == 'nt':
        base_cache_path = os.getenv('LOCALAPPDATA', os.getenv('TEMP', '/tmp'))
    elif platform.system() == 'Darwin':
        base_cache_path = os.path.expanduser('~/Library/Caches')
    else:
        base_cache_path = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
    xbot_app_cache_dir = os.path.join(base_cache_path, "xbot_app", activity_code)
    if not os.path.exists(xbot_app_cache_dir):
        os.makedirs(xbot_app_cache_dir, exist_ok=True)
    return xbot_app_cache_dir

def file2base64(file_path) -> str:
    """将本地文件转换成 base64"""
    with open(file_path, "rb") as f:
        image_data = f.read()
        base64_str = base64.b64encode(image_data).decode("utf-8")
        return base64_str

def get_ppi():
    """获取屏幕的缩放 - 跨平台版本"""
    for _ in range(5):
        try:
            if os.name == 'nt':
                # Windows: 使用 ctypes 获取真实 DPI
                LOGPIXELSX = 88
                LOGPIXELSY = 90
                user32 = windll.user32
                user32.SetProcessDPIAware()
                dc = user32.GetDC(0)
                pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
                user32.ReleaseDC(0, dc)
                res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
                return res[1] / res[0]
            else:
                # macOS/Linux: xbot.win32 已处理平台差异，返回 1
                return 1
        except Exception as e:
            sleep(1)
            pass
    else:
        return 1

#主函数
def main(path, quekuai_left, a_width, offset):
    path_a = os.path.join(create_cache_dir(), "yanzhengmaA.png")
    path_b = os.path.join(create_cache_dir(), "yanzhengmaB.png")
    img_bg = Image.open(path)
    cut_ab(img_bg,path_a,path_b,quekuai_left, a_width,offset)
    X = get_x(path_a,path_b)
    # os.remove(path_a)
    # os.remove(path_b)
    # print(X)
    return X


def gen_selector(xpath):
    if isinstance(xpath, str):
        xpath = [xpath]
    uid = str(uuid.uuid4())

    data = {'id': uid, 'name': uid, 'type': 'simple', 'xpath': {'enable': 'true', 'segments': xpath}}

    return Selector(data)

def _moveTo(x, y):
    """移动鼠标到指定位置 - 跨平台版本"""
    if os.name == 'nt':
        ctypes.windll.user32.SetCursorPos(int(x), int(y))
    else:
        win32.mouse_move(x, y, move_speed="instant")