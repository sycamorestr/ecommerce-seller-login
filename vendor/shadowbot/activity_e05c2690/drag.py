# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块


import xbot
from xbot import print, sleep, win32
from .import package
from .package import variables as glv

from xbot.win32.element import Win32Element




def drag(drag_ele:Win32Element, distance:int, move_speed = "middle"):
    x, y, width, height = drag_ele.get_bounding()
    pos_center_x = x + width / 2
    pos_center_y = y + height / 2

    win32.mouse_move(point_x=pos_center_x, point_y=pos_center_y, move_speed=move_speed)

    poit_x, point_y = win32.get_mouse_position(relative_to="screen")
    win32.mouse_click(button="left", click_type="down")
    win32.manual_motion_on()
    win32.mouse_move(pos_center_x + distance, pos_center_y, move_speed="middle")
    win32.manual_motion_off()
    win32.mouse_click(button="left", click_type="up")   



def main(args):
    slider_ele:Win32Element = args.get("slider_ele", "")
    background_ele: Win32Element = args.get("background_ele", "")
    move_speed: Win32Element = args.get("move_speed", "")

    target_wnd = win32.get_by_selector(slider_ele)
    slider_ele = target_wnd.find(slider_ele)
    background_ele = target_wnd.find(background_ele)

    s_x, s_y, s_width, s_height = slider_ele.get_bounding()
    b_x, b_y, b_width, b_height = background_ele.get_bounding()

    

    drag(slider_ele, int(b_width-s_width), move_speed)

    pass
