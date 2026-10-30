import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        背景元素 = None
        缺块元素 = None
        拖拽滑块 = None
        偏移距离 = 0
        重试次数 = "3"
    else:
        网页对象 = args.get("网页对象", None)
        背景元素 = args.get("背景元素", None)
        缺块元素 = args.get("缺块元素", None)
        拖拽滑块 = args.get("拖拽滑块", None)
        偏移距离 = args.get("偏移距离", 0)
        重试次数 = args.get("重试次数", "3")
    try:
        xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=False, min_time="1", max_time="3", _block=("通用滑块拼图验证码", 1, "开启模拟真人操作"))
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=lambda: int(重试次数)+1, step="1", _block=("通用滑块拼图验证码", 2, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=网页对象, content_type="undisplay", selector=背景元素, _block=("通用滑块拼图验证码", 3, "IF 元素可见(web)")):
                break
            #endif
            if xbot_visual.web.browser.element_display(browser=网页对象, content_type="undisplay", selector=拖拽滑块, _block=("通用滑块拼图验证码", 6, "IF 元素可见(web)")):
                break
            #endif
            if xbot_visual.workflow.test(operand1=偏移距离, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("通用滑块拼图验证码", 9, "IF 条件")):
                偏移距离 = xbot_visual.programing.variable(value=lambda: 0
                , _block=("通用滑块拼图验证码", 10, "设置变量"))
            #endif
            scaling = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_scaling", params={
            }, _block=("通用滑块拼图验证码", 12, "调用模块"))
            dir_path = xbot_visual.process.invoke_module(module="utils", package=__name__, function="create_cache_dir", params={
            }, _block=("通用滑块拼图验证码", 13, "调用模块"))
            web_element_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=缺块元素, operation="bound", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("通用滑块拼图验证码", 14, "获取元素信息(web)"))
            背景元素_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=背景元素, operation="bound", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("通用滑块拼图验证码", 15, "获取元素信息(web)"))
            _ = xbot_visual.system.take_screenshot(image_source="screen", window=None, image_region="all_region", region_x1="0", region_y1="0", region_x2="0", region_y2="0", save_to="file", image_path=xbot_visual.sh_str(dir_path) + "\\quanpingjietu.png", _block=("通用滑块拼图验证码", 16, "截屏"))
            box = xbot_visual.programing.variable(value=lambda: [背景元素_attribute.left*scaling,背景元素_attribute.top*scaling,背景元素_attribute.right*scaling,背景元素_attribute.bottom*scaling]
            , _block=("通用滑块拼图验证码", 17, "设置变量"))
            invoke_result2 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="cutbg", params={
                "path": xbot_visual.sh_str(dir_path) + "\\quanpingjietu.png",
                "bigbox": box,
            }, _block=("通用滑块拼图验证码", 18, "调用模块"))
            缺块宽度 = xbot_visual.programing.variable(value=lambda: web_element_attribute.width*scaling
            , _block=("通用滑块拼图验证码", 19, "设置变量"))
            缺块左边缘 = xbot_visual.programing.variable(value=lambda: (web_element_attribute.left-背景元素_attribute.left)*scaling
            , _block=("通用滑块拼图验证码", 20, "设置变量"))
            invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="main", params={
                "path": invoke_result2,
                "quekuai_left": 缺块左边缘,
                "a_width": 缺块宽度,
                "offset": 偏移距离,
            }, _block=("通用滑块拼图验证码", 21, "调用模块"))
            # file.remove
            # file.remove
            拖拽滑块位置 = xbot_visual.web.element.get_details(browser=网页对象, element=拖拽滑块, operation="bound", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("通用滑块拼图验证码", 24, "获取元素信息(web)"))
            web_element = xbot_visual.web.element.get_element(browser=网页对象, select_type="selector", selector=拖拽滑块, css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("通用滑块拼图验证码", 25, "获取元素对象(web)"))
            invoke_result3 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="drag", params={
                "drag_ele": web_element,
                "distance": lambda: int(invoke_result/scaling)+偏移距离,
            }, _block=("通用滑块拼图验证码", 26, "调用模块"))
            xbot_visual.programing.sleep(random_number=False, seconds="5", start_number="1", stop_number="5", _block=("通用滑块拼图验证码", 27, "等待"))
        #endloop
        xbot_visual.win32.manual_motion_off(_block=("通用滑块拼图验证码", 29, "结束模拟真人操作"))
    finally:
        pass
