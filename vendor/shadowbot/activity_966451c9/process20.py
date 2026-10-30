import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        web_page = None
        tt_account = ""
        tt_password = ""
        time_out = "20"
    else:
        web_page = args.get("web_page", None)
        tt_account = args.get("tt_account", "")
        tt_password = args.get("tt_password", "")
        time_out = args.get("time_out", "20")
    try:
        #region 前置流程变量
        time_out = xbot_visual.programing.variable(value=lambda: int(time_out)
        , _block=("验证码-点选坐标", 2, "设置变量"))
        #endregion
        bound = xbot_visual.web.element.get_bounding(browser=web_page, element=package.selector("抖店_验证码_点选文字_上部分元素"), to96dpi=True, relative_to="screen", timeout="20", _block=("验证码-点选坐标", 4, "获取元素位置(web)"))
        pc_scaling = xbot_visual.process.invoke_module(module="utils", package=__name__, function="scaling", params={
        }, _block=("验证码-点选坐标", 5, "调用模块"))
        滑动距离 = xbot_visual.programing.variable(value=lambda: 0
        , _block=("验证码-点选坐标", 6, "设置变量"))
        web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("抖店_验证码_点选文字_底图"), state="appear", iswait=True, timeout=time_out, _block=("验证码-点选坐标", 7, "等待元素(web)"))
        if xbot_visual.workflow.test(operand1=web_wait_result, operator="is false", operand2="", operator_options="{}", _block=("验证码-点选坐标", 8, "IF 条件")):
            xbot_visual.programing.log(type="info", text="抖店多店铺登录：未找到点选坐标底图，可能已被处理 ~", _block=("验证码-点选坐标", 9, "打印日志"))
            return
        #endif
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("验证码-点选坐标", 12, "等待"))
        if xbot_visual.workflow.test(operand1=lambda: bool(tt_account) and bool(tt_password), operator="is true", operand2="", operator_options="{}", _block=("验证码-点选坐标", 13, "IF 条件")):
            验证码识别_result = xbot_visual.web_service.captcha(engine_type="ttshitu", username=tt_account, password=xbot_visual.decrypt(tt_password), captcha_type="27", third_party_code="ttshitu_27_predict", image_source="web_element", image_file=None, image_browser=web_page, image_web_selector=package.selector("抖店_验证码_点选文字_整体框"), image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark="", _block=("验证码-点选坐标", 14, "验证码识别"))
            验证码第一次分割_list = xbot_visual.text.split_text_to_list(text_to_split=验证码识别_result, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="|", is_regular_expression=False, remove_empty=False, _block=("验证码-点选坐标", 15, "文本分割成列表"))
            for 当前验证码坐标_str in xbot_visual.workflow.list_iterator(list=验证码第一次分割_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("验证码-点选坐标", 16, "ForEach列表循环")):
                验证码纵横坐标_list = xbot_visual.text.split_text_to_list(text_to_split=当前验证码坐标_str, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter=",", is_regular_expression=False, remove_empty=False, _block=("验证码-点选坐标", 17, "文本分割成列表"))
                滑动距离X = xbot_visual.programing.variable(value=lambda: int(int(验证码纵横坐标_list[0])/pc_scaling)
                , _block=("验证码-点选坐标", 18, "设置变量"))
                滑动距离Y = xbot_visual.programing.variable(value=lambda: int(int(验证码纵横坐标_list[-1])/pc_scaling)-bound.height
                , _block=("验证码-点选坐标", 19, "设置变量"))
                xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_验证码_点选文字_底图"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="custom", sudoku_part="TopLeft", offset_x=滑动距离X, offset_y=滑动距离Y, timeout="20", _block=("验证码-点选坐标", 20, "点击元素(web)"))
            #endloop
        else:
            验证码识别_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="27", third_party_code="ttshitu_27_predict", image_source="web_element", image_file=None, image_browser=web_page, image_web_selector=package.selector("抖店_验证码_点选文字_整体框"), image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("验证码-点选坐标", 23, "验证码识别"))
            验证码第一次分割_list = xbot_visual.text.split_text_to_list(text_to_split=验证码识别_result, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="|", is_regular_expression=False, remove_empty=False, _block=("验证码-点选坐标", 24, "文本分割成列表"))
            for 当前验证码坐标_str in xbot_visual.workflow.list_iterator(list=验证码第一次分割_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("验证码-点选坐标", 25, "ForEach列表循环")):
                验证码纵横坐标_list = xbot_visual.text.split_text_to_list(text_to_split=当前验证码坐标_str, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter=",", is_regular_expression=False, remove_empty=False, _block=("验证码-点选坐标", 26, "文本分割成列表"))
                滑动距离X = xbot_visual.programing.variable(value=lambda: int(int(验证码纵横坐标_list[0])/pc_scaling)
                , _block=("验证码-点选坐标", 27, "设置变量"))
                滑动距离Y = xbot_visual.programing.variable(value=lambda: int(int(验证码纵横坐标_list[-1])/pc_scaling)-bound.height
                , _block=("验证码-点选坐标", 28, "设置变量"))
                xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_验证码_点选文字_底图"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="custom", sudoku_part="TopLeft", offset_x=滑动距离X, offset_y=滑动距离Y, timeout="20", _block=("验证码-点选坐标", 29, "点击元素(web)"))
            #endloop
        #endif
        xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_验证码_点选文字_确认按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("验证码-点选坐标", 32, "点击元素(web)"))
        xbot_visual.programing.sleep(random_number=False, seconds=lambda: max(time_out // 5 + 1, 6), start_number="1", stop_number="5", _block=("验证码-点选坐标", 33, "等待"))
    finally:
        pass
