# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
if os.name == 'nt':
    from ctypes import windll

from typing import *
from PIL import Image
import base64


def get_max_x(coordinates):
    max_x = float('-inf')
    for coordinate in coordinates.split('|'):
        x, y = coordinate.split(',')
        max_x = max(max_x, int(x))
    return max_x


def save_base64_image(base64_str, save_path):
    try:
        img_data = base64.b64decode(base64_str.split(',')[1])
        with open(save_path, 'wb') as f:
            f.write(img_data)
        Image.open(save_path).verify()
        return True
    except Exception as e:
        print(e)
        return False


def main(args):
    ppi=get_ppi()
    print(ppi*1920,ppi*1080)

def get_ppi():
    """
    获取屏幕的缩放
    """
    LOGPIXELSX = 88
    LOGPIXELSY = 90
    user32 = windll.user32
    user32.SetProcessDPIAware()
    dc = user32.GetDC(0)
    pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
    user32.ReleaseDC(0, dc)
    res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
    return res[1] / res[0]
    