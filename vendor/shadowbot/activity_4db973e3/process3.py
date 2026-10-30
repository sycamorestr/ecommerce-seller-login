import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    if args is None:
        drag_start_element = None
        web_page = None
        distance = ""
    else:
        drag_start_element = args.get("drag_start_element", None)
        web_page = args.get("web_page", None)
        distance = args.get("distance", "")
    try:
        bound = xbot_visual.web.element.get_bounding(browser=web_page, element=drag_start_element, to96dpi=True, relative_to="screen", timeout="20", _block=("拖动滑块", 1, "获取元素位置(web)"))
        xbot_visual.win32.move_mouse(point_x=bound.center_x, point_y=bound.center_y, relative_to="screen", move_speed="middle", delay_after="1", _block=("拖动滑块", 2, "移动鼠标"))
        point_x, point_y = xbot_visual.win32.get_mouse_position(relative_to="screen", _block=("拖动滑块", 3, "获取鼠标当前位置"))
        xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="down", hardware_driver_click=False, keys="null", delay_after="1", _block=("拖动滑块", 4, "鼠标点击"))
        invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="time_ease", params={
            "xOffset": lambda: int(distance),
        }, _block=("拖动滑块", 5, "调用模块"))
        xPoint = point_x
        yPoint = point_y
        for loop_item in xbot_visual.workflow.list_iterator(list=invoke_result, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("拖动滑块", 8, "ForEach列表循环")):
            xPoint = point_x + loop_item[0]
            invoke_result2 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="y_offset", params={
            }, _block=("拖动滑块", 10, "调用模块"))
            yPoint = point_y
            if xbot_visual.workflow.test(operand1=invoke_result2, operator="!=", operand2="0", operator_options="{}", _block=("拖动滑块", 12, "IF 条件")):
                yPoint = int(yPoint+invoke_result2)
            #endif
            # 增加了模拟真人操作后 ，太慢了，暂时取消
            xbot_visual.win32.move_mouse(point_x=lambda: int(xPoint), point_y=yPoint, relative_to="screen", move_speed="middle", delay_after=lambda: loop_item[1], _block=("拖动滑块", 16, "移动鼠标"))
        #endloop
        xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="3", _block=("拖动滑块", 18, "等待"))
        xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="up", hardware_driver_click=False, keys="null", delay_after="1", _block=("拖动滑块", 19, "鼠标点击"))
    finally:
        pass
