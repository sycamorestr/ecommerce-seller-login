# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import os
import base64
from ctypes import windll

from xbot import print, sleep
from .import package
from .package import variables as glv
from io import BytesIO
import win32api,win32gui, win32print,win32con
def get_ppi():
    """获取屏幕的缩放"""
    LOGPIXELSX = 88
    LOGPIXELSY = 90
    user32 = windll.user32
    user32.SetProcessDPIAware()
    dc = user32.GetDC(0)
    pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
    user32.ReleaseDC(0, dc)
    res = float.as_integer_ratio(round(pix_per_inch / 96,2))
    return res[1]/res[0]

def get_ppi_enlarge():
    """获取屏幕的缩放,放大比例"""
    LOGPIXELSX = 88
    LOGPIXELSY = 90
    user32 = windll.user32
    user32.SetProcessDPIAware()
    dc = user32.GetDC(0)
    pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
    user32.ReleaseDC(0, dc)
    res = float.as_integer_ratio(round(pix_per_inch / 96,2))
    return res[0]/res[1]

def scaling():
    """获取缩放后的分辨率"""
    sX = win32api.GetSystemMetrics(0)   #获得屏幕分辨率X轴
    sY = win32api.GetSystemMetrics(1)   #获得屏幕分辨率Y轴
    """获取真实的分辨率"""
    hDC = win32gui.GetDC(0)
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)  # 横向分辨率
    h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)  # 纵向分辨率
    # 缩放比率
    screen_scale_rate = round(w / sX, 2)
    return screen_scale_rate

def main(args):
    a = scaling()
    print(a)
