import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        web_page = None
    else:
        web_page = args.get("web_page", None)
    try:
        xbot_visual.programing.log(type="info", text="-----点选验证-----", _block=("_抖音平台登录-文字点选验证", 1, "打印日志"))
        验证码_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"captcha_verify_container\")]", is_related_parent=False, parent=None, timeout="20", _block=("_抖音平台登录-文字点选验证", 2, "获取元素对象(web)"))
        xbot_visual.web.element.hover(browser=web_page, element=验证码_元素对象, simulate=True, delay_after="1", anchor_type="custom", sudoku_part="TopLeft", offset_x="0", offset_y="0", timeout="20", _block=("_抖音平台登录-文字点选验证", 3, "鼠标悬停在元素上(web)"))
        captcha_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username="", password=xbot_visual.decrypt("{\"secret\":0,\"value\":\"REDACTED\"}"), captcha_type="27", third_party_code="ttshitu_27_predict", image_source="web_element", image_file=None, image_browser=web_page, image_web_selector=验证码_元素对象, image_window="", image_win_selector=None, image_region_x1="650", image_region_y1="280", image_region_x2="949", image_region_y2="583", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("_抖音平台登录-文字点选验证", 4, "验证码识别"))
        坐标列表 = xbot_visual.text.split_text_to_list(text_to_split=captcha_result, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="|", is_regular_expression=False, remove_empty=False, _block=("_抖音平台登录-文字点选验证", 5, "文本分割成列表"))
        for loop_item in xbot_visual.workflow.list_iterator(list=坐标列表, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("_抖音平台登录-文字点选验证", 6, "ForEach列表循环")):
            坐标对 = xbot_visual.text.split_text_to_list(text_to_split=loop_item, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter=",", is_regular_expression=False, remove_empty=False, _block=("_抖音平台登录-文字点选验证", 7, "文本分割成列表"))
            xbot_visual.win32.move_mouse(point_x=坐标对[0], point_y=坐标对[1], relative_to="currentmouseposition", move_speed="middle", delay_after="1", _block=("_抖音平台登录-文字点选验证", 8, "移动鼠标"))
            xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="click", hardware_driver_click=False, keys="null", delay_after="1", _block=("_抖音平台登录-文字点选验证", 9, "鼠标点击"))
            xbot_visual.web.element.hover(browser=web_page, element=验证码_元素对象, simulate=True, delay_after="1", anchor_type="custom", sudoku_part="TopLeft", offset_x="0", offset_y="0", timeout="20", _block=("_抖音平台登录-文字点选验证", 10, "鼠标悬停在元素上(web)"))
        #endloop
        if xbot_visual.workflow.test(operand1="//*[text()=\"确认\"]", operator="!=", operand2="None", operator_options="{}", _block=("_抖音平台登录-文字点选验证", 12, "IF 条件")):
            确认_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[text()=\"确认\"]", is_related_parent=False, parent=None, timeout="20", _block=("_抖音平台登录-文字点选验证", 13, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=确认_元素对象, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="3", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("_抖音平台登录-文字点选验证", 14, "点击元素(web)"))
        #endif
    finally:
        pass
