# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, win32
from .import package
from .package import variables as glv
import sqlite3
import xbot_visual
import random
import ast
import json
import ctypes
from xbot.web.element import WebElement
from xbot.web.chrome import ChromeAutomation
import os
if os.name == 'nt':
    from ctypes import windll


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

def get_data_by_distance(distance, one=True):
    db_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="mouse_tracker_20260721.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # print(distance)
    if distance < 50:
        di = 50
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 50")
    elif 50 < distance < 150:
        di = 100
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 100")
    else:
        di = 370
        cursor.execute(f"SELECT * FROM Tracker WHERE distance = 370")

    rows = cursor.fetchall()
    # print(len(rows))

    if one:
        random_index = random.randint(0, len(rows) - 1)
        data = json.loads(rows[random_index][2])
        tmp = []
        di = data[-1][0]
        for item in data:
            tmp.append([item[0] / di * distance, item[1], item[2]])
        # print("rows[random_index][2]:", rows[random_index][2])
        # result = ast.literal_eval(rows[random_index][2])
        # for i in range(len(result)):
        #     result[i][0] = result[i][0] / di * distance
        # print("result:", result)
        result = json.dumps(tmp)
        return json.loads(result)
    return [json.loads(row[2]) for row in rows]


def drag_gen(drag_ele:WebElement, distance:int):
    point_x, point_y, width, height = drag_ele.get_bounding()
    mouse_pos_path = get_data_by_distance(distance - 40)
    drag_ele.hover(simulative=True)
    xbot.win32.manual_motion_on()
    point_x, point_y, width, height = drag_ele.get_bounding(to96dpi=True)
    point_x = int(point_x + (width/2)) + random.randint(-10, 10)
    point_y = int(point_y + (height/2)) + random.randint(-10, 10)
    win32.mouse_move(point_x, point_y)
    win32.mouse_click(button="left", click_type="down")

    for offset_x, offset_y, t in mouse_pos_path:
        # print(offset_x, offset_y, t)
        xPoint = int((point_x + int(offset_x ))/get_ppi())
        yPoint = int((point_y + int(offset_y ))/get_ppi())
        sleep(t / 1000)
        _moveTo(xPoint, yPoint)

    sleep(2)
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
    ctypes.windll.user32.SetCursorPos(x, y)

def move_captcha(web_page, distance, drag_ele):
    ''' 移动滑块
    ''' 
    drag_ele = web_page.find(drag_ele)
    drag_gen(drag_ele, distance)


def main(args):
    web_page = args.get('web_page')
    distance = args.get('distance')
    drag_ele = args.get('drag_ele')
    move_captcha(web_page, distance, drag_ele)
