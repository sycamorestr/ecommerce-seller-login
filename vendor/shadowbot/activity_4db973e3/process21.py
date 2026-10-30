import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        验证码图片 = None
        点选提示 = None
        识别模式 = ""
        图鉴账号 = ""
        图鉴密码 = ""
    else:
        网页对象 = args.get("网页对象", None)
        验证码图片 = args.get("验证码图片", None)
        点选提示 = args.get("点选提示", None)
        识别模式 = args.get("识别模式", "")
        图鉴账号 = args.get("图鉴账号", "")
        图鉴密码 = args.get("图鉴密码", "")
    try:
        # 不使用相对【验证码】元素点击的原因：目前存在验证码在上提示在下，提示在上验证码在下两种情况，故使用移动坐标+点击相对位置的形式实现
        try:
            xbot_visual.web.browser.wait_load_completed(browser=网页对象, load_timeout="20", action_after_load_timeout="stopLoad", _block=("坐标点选验证（去除界面 bug）", 2, "等待网页加载完成"))
        except Exception as e:
            xbot_visual.programing.log(type='info',text=e,_block=("坐标点选验证（去除界面 bug）", 2,"等待网页加载完成"))
        xbot_visual.web.element.hover(browser=网页对象, element=点选提示, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("坐标点选验证（去除界面 bug）", 3, "鼠标悬停在元素上(web)"))
        背景图坐标 = xbot_visual.web.element.get_bounding(browser=网页对象, element=验证码图片, to96dpi=True, relative_to="screen", timeout="20", _block=("坐标点选验证（去除界面 bug）", 4, "获取元素位置(web)"))
        点选坐标 = xbot_visual.web.element.get_bounding(browser=网页对象, element=点选提示, to96dpi=True, relative_to="screen", timeout="20", _block=("坐标点选验证（去除界面 bug）", 5, "获取元素位置(web)"))
        ppi = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_ppi", params={
        }, _block=("坐标点选验证（去除界面 bug）", 6, "调用模块"))
        x_left = xbot_visual.programing.variable(value=lambda: int(float(min(点选坐标.left,背景图坐标.left))/ppi)
        , _block=("坐标点选验证（去除界面 bug）", 7, "设置变量"))
        y_top = xbot_visual.programing.variable(value=lambda: int(float(min(点选坐标.top,背景图坐标.top))/ppi)
        , _block=("坐标点选验证（去除界面 bug）", 8, "设置变量"))
        y_bottom = xbot_visual.programing.variable(value=lambda: int(float(max(点选坐标.bottom,背景图坐标.bottom))/ppi)
        , _block=("坐标点选验证（去除界面 bug）", 9, "设置变量"))
        x_right = xbot_visual.programing.variable(value=lambda: int(float(max(点选坐标.right,背景图坐标.right))/ppi)
        , _block=("坐标点选验证（去除界面 bug）", 10, "设置变量"))
        # 备注: 图鉴接口会报错, 增加重试补偿
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("坐标点选验证（去除界面 bug）", 12, "For次数循环")):
            try:
                if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 识别模式,"operand2": "点选1~4个坐标","operator": "=="}], _block=("坐标点选验证（去除界面 bug）", 14, "IF 多条件")):
                    #region 1~4个坐标
                    验证码坐标List = xbot_visual.programing.variable(value=lambda: ""
                    , _block=("坐标点选验证（去除界面 bug）", 16, "设置变量"))
                    if xbot_visual.workflow.test(operand1=lambda: bool(图鉴账号) and bool(图鉴密码), operator="is true", operand2="", operator_options="{}", _block=("坐标点选验证（去除界面 bug）", 17, "IF 条件")):
                        验证码坐标List = xbot_visual.web_service.captcha(engine_type="ttshitu", username=图鉴账号, password=xbot_visual.decrypt(图鉴密码), captcha_type="27", third_party_code="ttshitu_27_predict", image_source="screen", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1=x_left, image_region_y1=y_top, image_region_x2=x_right, image_region_y2=y_bottom, imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark="", _block=("坐标点选验证（去除界面 bug）", 18, "验证码识别"))
                    else:
                        验证码坐标List = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="27", third_party_code="ttshitu_27_predict", image_source="screen", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1=x_left, image_region_y1=y_top, image_region_x2=x_right, image_region_y2=y_bottom, imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark="", _block=("坐标点选验证（去除界面 bug）", 20, "验证码识别"))
                    #endif
                    验证码_list = xbot_visual.text.split_text_to_list(text_to_split=验证码坐标List, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="|", is_regular_expression=False, remove_empty=False, _block=("坐标点选验证（去除界面 bug）", 22, "文本分割成列表"))
                    for 当前验证坐标 in xbot_visual.workflow.list_iterator(list=验证码_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("坐标点选验证（去除界面 bug）", 23, "ForEach列表循环")):
                        当前验证坐标 = xbot_visual.text.split_text_to_list(text_to_split=当前验证坐标, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter=",", is_regular_expression=False, remove_empty=False, _block=("坐标点选验证（去除界面 bug）", 24, "文本分割成列表"))
                        x_坐标定位 = xbot_visual.programing.variable(value=lambda: int(float(当前验证坐标[0])*ppi)+min(点选坐标.left,背景图坐标.left)
                        , _block=("坐标点选验证（去除界面 bug）", 25, "设置变量"))
                        y_坐标定位 = xbot_visual.programing.variable(value=lambda: int(float(当前验证坐标[1])*ppi)+min(点选坐标.top,背景图坐标.top)
                        , _block=("坐标点选验证（去除界面 bug）", 26, "设置变量"))
                        xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time="1", max_time="2", _block=("坐标点选验证（去除界面 bug）", 27, "开启模拟真人操作"))
                        xbot_visual.win32.click_mouse(is_move_mouse_before_click=True, point_x=x_坐标定位, point_y=y_坐标定位, relative_to="screen", move_speed="middle", button="left", click_type="click", hardware_driver_click=False, keys="null", delay_after="1", _block=("坐标点选验证（去除界面 bug）", 28, "鼠标点击"))
                        xbot_visual.win32.manual_motion_off(_block=("坐标点选验证（去除界面 bug）", 29, "结束模拟真人操作"))
                    #endloop
                    #endregion
                elif xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 识别模式,"operand2": "点选1个坐标","operator": "=="}], _block=("坐标点选验证（去除界面 bug）", 32, "Else IF 多条件")):
                    #region 点选1个坐标
                    验证码坐标 = xbot_visual.programing.variable(value=""
                    , _block=("坐标点选验证（去除界面 bug）", 34, "设置变量"))
                    if xbot_visual.workflow.test(operand1=lambda: bool(图鉴账号) and bool(图鉴密码), operator="is true", operand2="", operator_options="{}", _block=("坐标点选验证（去除界面 bug）", 35, "IF 条件")):
                        验证码坐标 = xbot_visual.web_service.captcha(engine_type="ttshitu", username=图鉴账号, password=xbot_visual.decrypt(图鉴密码), captcha_type="19", third_party_code="ttshitu_19_predict", image_source="screen", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1=x_left, image_region_y1=y_top, image_region_x2=x_right, image_region_y2=y_bottom, imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("坐标点选验证（去除界面 bug）", 36, "验证码识别"))
                    else:
                        验证码坐标 = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="19", third_party_code="ttshitu_19_predict", image_source="screen", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1=x_left, image_region_y1=y_top, image_region_x2=x_right, image_region_y2=y_bottom, imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("坐标点选验证（去除界面 bug）", 38, "验证码识别"))
                    #endif
                    当前验证坐标 = xbot_visual.text.split_text_to_list(text_to_split=验证码坐标, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter=",", is_regular_expression=False, remove_empty=False, _block=("坐标点选验证（去除界面 bug）", 40, "文本分割成列表"))
                    x_坐标定位 = xbot_visual.programing.variable(value=lambda: int(float(当前验证坐标[0])*ppi)+min(点选坐标.left,背景图坐标.left)
                    , _block=("坐标点选验证（去除界面 bug）", 41, "设置变量"))
                    y_坐标定位 = xbot_visual.programing.variable(value=lambda: int(float(当前验证坐标[1])*ppi)+min(点选坐标.top,背景图坐标.top)
                    , _block=("坐标点选验证（去除界面 bug）", 42, "设置变量"))
                    xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time="1", max_time="2", _block=("坐标点选验证（去除界面 bug）", 43, "开启模拟真人操作"))
                    xbot_visual.win32.click_mouse(is_move_mouse_before_click=True, point_x=x_坐标定位, point_y=y_坐标定位, relative_to="screen", move_speed="middle", button="left", click_type="click", hardware_driver_click=False, keys="null", delay_after="1", _block=("坐标点选验证（去除界面 bug）", 44, "鼠标点击"))
                    xbot_visual.win32.manual_motion_off(_block=("坐标点选验证（去除界面 bug）", 45, "结束模拟真人操作"))
                    #endregion
                elif xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 识别模式,"operand2": "点选3个坐标","operator": "=="}], _block=("坐标点选验证（去除界面 bug）", 47, "Else IF 多条件")):
                    #region 点选3个坐标
                    验证码坐标List = xbot_visual.programing.variable(value=""
                    , _block=("坐标点选验证（去除界面 bug）", 49, "设置变量"))
                    if xbot_visual.workflow.test(operand1=lambda: bool(图鉴账号) and bool(图鉴密码), operator="is true", operand2="", operator_options="{}", _block=("坐标点选验证（去除界面 bug）", 50, "IF 条件")):
                        验证码坐标List = xbot_visual.web_service.captcha(engine_type="ttshitu", username=图鉴账号, password=xbot_visual.decrypt(图鉴密码), captcha_type="20", third_party_code="ttshitu_20_predict", image_source="screen", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1=x_left, image_region_y1=y_top, image_region_x2=x_right, image_region_y2=y_bottom, imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark="", _block=("坐标点选验证（去除界面 bug）", 51, "验证码识别"))
                    else:
                        验证码坐标List = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="20", third_party_code="ttshitu_20_predict", image_source="screen", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1=x_left, image_region_y1=y_top, image_region_x2=x_right, image_region_y2=y_bottom, imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark="", _block=("坐标点选验证（去除界面 bug）", 53, "验证码识别"))
                    #endif
                    验证码_list = xbot_visual.text.split_text_to_list(text_to_split=验证码坐标List, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="|", is_regular_expression=False, remove_empty=False, _block=("坐标点选验证（去除界面 bug）", 55, "文本分割成列表"))
                    for 当前验证坐标 in xbot_visual.workflow.list_iterator(list=验证码_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("坐标点选验证（去除界面 bug）", 56, "ForEach列表循环")):
                        当前验证坐标 = xbot_visual.text.split_text_to_list(text_to_split=当前验证坐标, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter=",", is_regular_expression=False, remove_empty=False, _block=("坐标点选验证（去除界面 bug）", 57, "文本分割成列表"))
                        x_坐标定位 = xbot_visual.programing.variable(value=lambda: int(float(当前验证坐标[0])*ppi)+min(点选坐标.left,背景图坐标.left)
                        , _block=("坐标点选验证（去除界面 bug）", 58, "设置变量"))
                        y_坐标定位 = xbot_visual.programing.variable(value=lambda: int(float(当前验证坐标[1])*ppi)+min(点选坐标.top,背景图坐标.top)
                        , _block=("坐标点选验证（去除界面 bug）", 59, "设置变量"))
                        xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time="1", max_time="2", _block=("坐标点选验证（去除界面 bug）", 60, "开启模拟真人操作"))
                        xbot_visual.win32.click_mouse(is_move_mouse_before_click=True, point_x=x_坐标定位, point_y=y_坐标定位, relative_to="screen", move_speed="middle", button="left", click_type="click", hardware_driver_click=False, keys="null", delay_after="1", _block=("坐标点选验证（去除界面 bug）", 61, "鼠标点击"))
                        xbot_visual.win32.manual_motion_off(_block=("坐标点选验证（去除界面 bug）", 62, "结束模拟真人操作"))
                    #endloop
                    #endregion
                elif xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 识别模式,"operand2": "点选3~5个坐标","operator": "=="}], _block=("坐标点选验证（去除界面 bug）", 65, "Else IF 多条件")):
                    #region 点选3~5个坐标
                    验证码坐标List = xbot_visual.programing.variable(value=""
                    , _block=("坐标点选验证（去除界面 bug）", 67, "设置变量"))
                    if xbot_visual.workflow.test(operand1=lambda: bool(图鉴账号) and bool(图鉴密码), operator="is true", operand2="", operator_options="{}", _block=("坐标点选验证（去除界面 bug）", 68, "IF 条件")):
                        验证码坐标List = xbot_visual.web_service.captcha(engine_type="ttshitu", username=图鉴账号, password=xbot_visual.decrypt(图鉴密码), captcha_type="21", third_party_code="ttshitu_21_predict", image_source="screen", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1=x_left, image_region_y1=y_top, image_region_x2=x_right, image_region_y2=y_bottom, imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("坐标点选验证（去除界面 bug）", 69, "验证码识别"))
                    else:
                        验证码坐标List = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="21", third_party_code="ttshitu_21_predict", image_source="screen", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1=x_left, image_region_y1=y_top, image_region_x2=x_right, image_region_y2=y_bottom, imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("坐标点选验证（去除界面 bug）", 71, "验证码识别"))
                    #endif
                    验证码_list = xbot_visual.text.split_text_to_list(text_to_split=验证码坐标List, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="|", is_regular_expression=False, remove_empty=False, _block=("坐标点选验证（去除界面 bug）", 73, "文本分割成列表"))
                    for 当前验证坐标 in xbot_visual.workflow.list_iterator(list=验证码_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("坐标点选验证（去除界面 bug）", 74, "ForEach列表循环")):
                        当前验证坐标 = xbot_visual.text.split_text_to_list(text_to_split=当前验证坐标, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter=",", is_regular_expression=False, remove_empty=False, _block=("坐标点选验证（去除界面 bug）", 75, "文本分割成列表"))
                        x_坐标定位 = xbot_visual.programing.variable(value=lambda: int(float(当前验证坐标[0])*ppi)+min(点选坐标.left,背景图坐标.left)
                        , _block=("坐标点选验证（去除界面 bug）", 76, "设置变量"))
                        y_坐标定位 = xbot_visual.programing.variable(value=lambda: int(float(当前验证坐标[1])*ppi)+min(点选坐标.top,背景图坐标.top)
                        , _block=("坐标点选验证（去除界面 bug）", 77, "设置变量"))
                        xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time="1", max_time="2", _block=("坐标点选验证（去除界面 bug）", 78, "开启模拟真人操作"))
                        xbot_visual.win32.click_mouse(is_move_mouse_before_click=True, point_x=x_坐标定位, point_y=y_坐标定位, relative_to="screen", move_speed="middle", button="left", click_type="click", hardware_driver_click=False, keys="null", delay_after="1", _block=("坐标点选验证（去除界面 bug）", 79, "鼠标点击"))
                        xbot_visual.win32.manual_motion_off(_block=("坐标点选验证（去除界面 bug）", 80, "结束模拟真人操作"))
                    #endloop
                    #endregion
                elif xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 识别模式,"operand2": "点选5~8个坐标","operator": "=="}], _block=("坐标点选验证（去除界面 bug）", 83, "Else IF 多条件")):
                    #region 点选5~8个坐标
                    验证码坐标List = xbot_visual.programing.variable(value=""
                    , _block=("坐标点选验证（去除界面 bug）", 85, "设置变量"))
                    if xbot_visual.workflow.test(operand1=lambda: bool(图鉴账号) and bool(图鉴密码), operator="is true", operand2="", operator_options="{}", _block=("坐标点选验证（去除界面 bug）", 86, "IF 条件")):
                        验证码坐标List = xbot_visual.web_service.captcha(engine_type="ttshitu", username=图鉴账号, password=xbot_visual.decrypt(图鉴密码), captcha_type="22", third_party_code="ttshitu_22_predict", image_source="screen", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1=x_left, image_region_y1=y_top, image_region_x2=x_right, image_region_y2=y_bottom, imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("坐标点选验证（去除界面 bug）", 87, "验证码识别"))
                    else:
                        验证码坐标List = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="22", third_party_code="ttshitu_22_predict", image_source="screen", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=None, image_region_x1=x_left, image_region_y1=y_top, image_region_x2=x_right, image_region_y2=y_bottom, imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("坐标点选验证（去除界面 bug）", 89, "验证码识别"))
                    #endif
                    验证码_list = xbot_visual.text.split_text_to_list(text_to_split=验证码坐标List, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="|", is_regular_expression=False, remove_empty=False, _block=("坐标点选验证（去除界面 bug）", 91, "文本分割成列表"))
                    for 当前验证坐标 in xbot_visual.workflow.list_iterator(list=验证码_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("坐标点选验证（去除界面 bug）", 92, "ForEach列表循环")):
                        当前验证坐标 = xbot_visual.text.split_text_to_list(text_to_split=当前验证坐标, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter=",", is_regular_expression=False, remove_empty=False, _block=("坐标点选验证（去除界面 bug）", 93, "文本分割成列表"))
                        x_坐标定位 = xbot_visual.programing.variable(value=lambda: int(float(当前验证坐标[0])*ppi)+min(点选坐标.left,背景图坐标.left)
                        , _block=("坐标点选验证（去除界面 bug）", 94, "设置变量"))
                        y_坐标定位 = xbot_visual.programing.variable(value=lambda: int(float(当前验证坐标[1])*ppi)+min(点选坐标.top,背景图坐标.top)
                        , _block=("坐标点选验证（去除界面 bug）", 95, "设置变量"))
                        xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time="1", max_time="2", _block=("坐标点选验证（去除界面 bug）", 96, "开启模拟真人操作"))
                        xbot_visual.win32.click_mouse(is_move_mouse_before_click=True, point_x=x_坐标定位, point_y=y_坐标定位, relative_to="screen", move_speed="middle", button="left", click_type="click", hardware_driver_click=False, keys="null", delay_after="1", _block=("坐标点选验证（去除界面 bug）", 97, "鼠标点击"))
                        xbot_visual.win32.manual_motion_off(_block=("坐标点选验证（去除界面 bug）", 98, "结束模拟真人操作"))
                    #endloop
                    #endregion
                #endif
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("坐标点选验证（去除界面 bug）", 102, "等待"))
                break
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                xbot_visual.programing.log(type="info", text=exception, _block=("坐标点选验证（去除界面 bug）", 105, "打印日志"))
            #endtry
        #endloop
    finally:
        pass
