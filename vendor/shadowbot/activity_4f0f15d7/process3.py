import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        背景元素 = None
        缺块元素 = None
        拖拽滑块 = None
        偏移距离 = 0
        窗口对象 = None
        重试次数 = "3"
    else:
        背景元素 = args.get("背景元素", None)
        缺块元素 = args.get("缺块元素", None)
        拖拽滑块 = args.get("拖拽滑块", None)
        偏移距离 = args.get("偏移距离", 0)
        窗口对象 = args.get("窗口对象", None)
        重试次数 = args.get("重试次数", "3")
    try:
        xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=False, min_time="1", max_time="3", _block=("通用滑块拼图验证码(win)", 1, "开启模拟真人操作"))
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=lambda: int(重试次数)+1, step="1", _block=("通用滑块拼图验证码(win)", 2, "For次数循环")):
            win_wait_result = xbot_visual.win32.element.wait(window=窗口对象, element=拖拽滑块, state="appear", iswait=True, timeout="3", _block=("通用滑块拼图验证码(win)", 3, "等待元素(win)"))
            if xbot_visual.workflow.test(operand1=win_wait_result, operator="==", operand2=False, operator_options="{}", _block=("通用滑块拼图验证码(win)", 4, "IF 条件")):
                break
            #endif
            if xbot_visual.workflow.test(operand1=偏移距离, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("通用滑块拼图验证码(win)", 7, "IF 条件")):
                偏移距离 = xbot_visual.programing.variable(value=lambda: 0
                , _block=("通用滑块拼图验证码(win)", 8, "设置变量"))
            #endif
            # 获取ppi
            scaling = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_scaling", params={
            }, _block=("通用滑块拼图验证码(win)", 11, "调用模块"))
            file_path = xbot_visual.resourcesfile.get_resourcesfile_path(file_name="1.txt", _block=("通用滑块拼图验证码(win)", 12, "获取资源文件路径"))
            dir_path = xbot_visual.text.replace_content_from_text(text=file_path, regular_pattern="", replace_way="content", replace_text=lambda: "\\1.txt", just_get_first=True, ignore_case=False, new_ignore_case=False, dest_text=lambda: "", _block=("通用滑块拼图验证码(win)", 13, "文本替换"))
            Path_result = xbot_visual.process.invoke_module(module="Replace_Chinese_Path", package=__name__, function="main", params={
                "path": dir_path,
            }, _block=("通用滑块拼图验证码(win)", 14, "调用模块"))
            dir_path = xbot_visual.programing.variable(value=Path_result
            , _block=("通用滑块拼图验证码(win)", 15, "设置变量"))
            # dir.get_special_dir
            web_element_attribute = xbot_visual.win32.element.get_details(window=窗口对象, element=缺块元素, operation="bound", attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("通用滑块拼图验证码(win)", 17, "获取元素信息(win)"))
            背景元素_attribute = xbot_visual.win32.element.get_details(window=窗口对象, element=背景元素, operation="bound", attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("通用滑块拼图验证码(win)", 18, "获取元素信息(win)"))
            _ = xbot_visual.system.take_screenshot(image_source="screen", window=None, image_region="all_region", region_x1="0", region_y1="0", region_x2="0", region_y2="0", save_to="file", image_path=xbot_visual.sh_str(dir_path) + "\\quanpingjietu.png", _block=("通用滑块拼图验证码(win)", 19, "截屏"))
            box = xbot_visual.programing.variable(value=lambda: [背景元素_attribute.left*scaling,背景元素_attribute.top*scaling,背景元素_attribute.right*scaling,背景元素_attribute.bottom*scaling]
            , _block=("通用滑块拼图验证码(win)", 20, "设置变量"))
            invoke_result2 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="cutbg1", params={
                "path": xbot_visual.sh_str(dir_path) + "\\quanpingjietu.png",
                "box": box,
            }, _block=("通用滑块拼图验证码(win)", 21, "调用模块"))
            缺块宽度 = xbot_visual.programing.variable(value=lambda: web_element_attribute.width*scaling
            , _block=("通用滑块拼图验证码(win)", 22, "设置变量"))
            缺块左边缘 = xbot_visual.programing.variable(value=lambda: (web_element_attribute.left-背景元素_attribute.left)*scaling
            , _block=("通用滑块拼图验证码(win)", 23, "设置变量"))
            invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="main", params={
                "path": invoke_result2,
                "quekuai_left": 缺块左边缘,
                "a_width": 缺块宽度,
                "offset": 偏移距离,
            }, _block=("通用滑块拼图验证码(win)", 24, "调用模块"))
            xbot_visual.file.remove(paths=xbot_visual.sh_str(dir_path) + "\\quanpingjietu.png", not_move_to_trash=True, _block=("通用滑块拼图验证码(win)", 25, "删除文件"))
            xbot_visual.file.remove(paths=invoke_result2, not_move_to_trash=True, _block=("通用滑块拼图验证码(win)", 26, "删除文件"))
            拖拽滑块位置 = xbot_visual.win32.element.get_details(window=窗口对象, element=拖拽滑块, operation="bound", attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("通用滑块拼图验证码(win)", 27, "获取元素信息(win)"))
            xbot_visual.win32.element.drag_to(window=窗口对象, element=拖拽滑块, drag_way="default", target_element=None, left=lambda: 拖拽滑块位置.center_x+int(invoke_result/scaling)+偏移距离, top=lambda: 拖拽滑块位置.center_y, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_speed="middle", release_anchor_type="center", release_sudoku_part="MiddleCenter", release_offset_x="0", release_offset_y="0", timeout="20", _block=("通用滑块拼图验证码(win)", 28, "拖拽元素(win)"))
            xbot_visual.programing.sleep(random_number=False, seconds="5", start_number="1", stop_number="5", _block=("通用滑块拼图验证码(win)", 29, "等待"))
        #endloop
        xbot_visual.win32.manual_motion_off(_block=("通用滑块拼图验证码(win)", 31, "结束模拟真人操作"))
    finally:
        pass
