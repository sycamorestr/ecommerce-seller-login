import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        滑块元素 = None
        滑动条背景图元素 = None
    else:
        网页对象 = args.get("网页对象", None)
        滑块元素 = args.get("滑块元素", None)
        滑动条背景图元素 = args.get("滑动条背景图元素", None)
    try:
        # web.get
        web_element = xbot_visual.web.element.get_element(browser=网页对象, select_type="selector", selector=滑动条背景图元素, css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("美团开店宝滑块", 2, "获取元素对象(web)"))
        bound = xbot_visual.web.element.get_bounding(browser=网页对象, element=web_element, to96dpi=True, relative_to="screen", timeout="20", _block=("美团开店宝滑块", 3, "获取元素位置(web)"))
        bound_1 = xbot_visual.web.element.get_bounding(browser=网页对象, element=滑块元素, to96dpi=True, relative_to="screen", timeout="20", _block=("美团开店宝滑块", 4, "获取元素位置(web)"))
        xbot_visual.win32.move_mouse(point_x=bound_1.center_x, point_y=bound_1.center_y, relative_to="screen", move_speed="slow", delay_after="1", _block=("美团开店宝滑块", 5, "移动鼠标"))
        distance = xbot_visual.programing.variable(value=lambda: bound.width - bound_1.width
        , _block=("美团开店宝滑块", 6, "设置变量"))
        point_x, point_y = xbot_visual.win32.get_mouse_position(relative_to="screen", _block=("美团开店宝滑块", 7, "获取鼠标当前位置"))
        #region 滑块拖动算法
        invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="time_ease", params={
            "xOffset": int(distance),
        }, _block=("美团开店宝滑块", 9, "调用模块"))
        # programing.log
        xPoint = xbot_visual.programing.variable(value=point_x
        , _block=("美团开店宝滑块", 11, "设置变量"))
        yPoint = xbot_visual.programing.variable(value=point_y
        , _block=("美团开店宝滑块", 12, "设置变量"))
        xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="down", hardware_driver_click=False, keys="null", delay_after="1", _block=("美团开店宝滑块", 13, "鼠标点击"))
        for loop_item in xbot_visual.workflow.list_iterator(list=lambda: invoke_result[25:], loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("美团开店宝滑块", 14, "ForEach列表循环")):
            xPoint = xbot_visual.programing.variable(value=lambda: point_x + loop_item[0]
            , _block=("美团开店宝滑块", 15, "设置变量"))
            invoke_result2 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="y_offset", params={
            }, _block=("美团开店宝滑块", 16, "调用模块"))
            # programing.log
            yPoint = xbot_visual.programing.variable(value=point_y
            , _block=("美团开店宝滑块", 18, "设置变量"))
            if xbot_visual.workflow.test(operand1=invoke_result2, operator="!=", operand2="0", operator_options="{}", _block=("美团开店宝滑块", 19, "IF 条件")):
                yPoint = xbot_visual.programing.variable(value=lambda: int(yPoint+invoke_result2)
                , _block=("美团开店宝滑块", 20, "设置变量"))
            #endif
            xbot_visual.win32.move_mouse(point_x=lambda: int(xPoint), point_y=yPoint, relative_to="screen", move_speed="fast", delay_after=lambda: loop_item[1], _block=("美团开店宝滑块", 22, "移动鼠标"))
        #endloop
        xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="up", hardware_driver_click=False, keys="null", delay_after="1", _block=("美团开店宝滑块", 24, "鼠标点击"))
        #endregion
    finally:
        pass
