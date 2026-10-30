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

def get_xbot_activity_cache_folder(activity_code):
    """根据指令code 获取本地缓存目录, 不存在则创建"""
    local_appdata_path = os.getenv('LOCALAPPDATA')
    xbot_app_cache_dir = os.path.join(local_appdata_path, "xbot_app", activity_code)
    if not os.path.exists(xbot_app_cache_dir):
        os.makedirs(xbot_app_cache_dir)
    return xbot_app_cache_dir


def file2base64(file_path) -> str:
    """将本地文件转换成 base64"""
    with open(file_path, "rb") as f:
        image_data = f.read()
        base64_str = base64.b64encode(image_data).decode("utf-8")
        return base64_str

def get_ppi():
    """获取屏幕的缩放"""
    for _ in range(5):
        try:
            LOGPIXELSX = 88
            LOGPIXELSY = 90
            user32 = windll.user32
            user32.SetProcessDPIAware()
            dc = user32.GetDC(0)
            pix_per_inch = windll.gdi32.GetDeviceCaps(dc, LOGPIXELSX)
            user32.ReleaseDC(0, dc)
            res = float.as_integer_ratio(round(pix_per_inch / 96, 2))
            return res[1] / res[0]
        except Exception as e:
            sleep(1)
            pass

def main(args):
    for i in range(0, 100):
        data = get_ppi()
        print(data)
