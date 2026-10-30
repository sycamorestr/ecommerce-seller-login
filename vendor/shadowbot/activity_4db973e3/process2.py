import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    distince = 0
    if args is None:
        start_element = None
        background_element = None
        tj_username = ""
        tj_password = ""
        web_page = None
        缺口类型 = ""
        ai_engine = ""
    else:
        start_element = args.get("start_element", None)
        background_element = args.get("background_element", None)
        tj_username = args.get("tj_username", "")
        tj_password = args.get("tj_password", "")
        web_page = args.get("web_page", None)
        缺口类型 = args.get("缺口类型", "")
        ai_engine = args.get("ai_engine", "")
    try:
        background_bound2 = xbot_visual.web.element.get_bounding(browser=web_page, element=background_element, to96dpi=False, relative_to="screen", timeout="20", _block=("计算滑块距离", 1, "获取元素位置(web)"))
        captcha_result = xbot_visual.programing.variable(value=""
        , _block=("计算滑块距离", 2, "设置变量"))
        distince = xbot_visual.programing.variable(value=lambda: 0
        , _block=("计算滑块距离", 3, "设置变量"))
        ppi = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_ppi", params={
        }, _block=("计算滑块距离", 4, "调用模块"))
        # 利用图鉴进行识别
        if xbot_visual.workflow.test(operand1=ai_engine, operator="==", operand2="TJ", operator_options="{}", _block=("计算滑块距离", 6, "IF 条件")):
            if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 缺口类型,"operand2": "单缺口识别","operator": "=="}], _block=("计算滑块距离", 7, "IF 多条件")):
                image_left = xbot_visual.web_service.captcha(engine_type="ttshitu", username=tj_username, password=xbot_visual.decrypt(tj_password), captcha_type="33", third_party_code="ttshitu_33_predict", image_source="web_element", image_file=None, image_browser=web_page, image_web_selector=background_element, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("计算滑块距离", 8, "验证码识别"))
                distince = xbot_visual.programing.variable(value=lambda: int(image_left)*ppi
                , _block=("计算滑块距离", 9, "设置变量"))
            else:
                start_bound = xbot_visual.web.element.get_bounding(browser=web_page, element=start_element, to96dpi=False, relative_to="screen", timeout="20", _block=("计算滑块距离", 11, "获取元素位置(web)"))
                captcha_result = xbot_visual.web_service.captcha(engine_type="ttshitu", username=tj_username, password=xbot_visual.decrypt(tj_password), captcha_type="18", third_party_code="ttshitu_18_predict", image_source="web_element", image_file=None, image_browser=web_page, image_web_selector=start_element, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser=web_page, imageback_web_selector=None, imageback_window="0", imageback_win_selector=None, imageback_region_x1=lambda: start_bound.right, imageback_region_y1=lambda: background_bound2.top, imageback_region_x2=lambda: background_bound2.right, imageback_region_y2=lambda: background_bound2.bottom, typename=None, is_to96dpi=False, remark=None, _block=("计算滑块距离", 12, "验证码识别"))
                image_left = xbot_visual.text.extract_content_from_text(text=captcha_result, extract_way="custom", regular_pattern="(\\d+),", just_get_first=True, ignore_case=False, _block=("计算滑块距离", 13, "从文本中提取内容"))
                distince = xbot_visual.programing.variable(value=lambda: (int(image_left) + start_bound.width)*ppi
                , _block=("计算滑块距离", 14, "设置变量"))
            #endif
        #endif
        # 利用影刀引擎识别
        if xbot_visual.workflow.test(operand1=ai_engine, operator="==", operand2="YD", operator_options="{}", _block=("计算滑块距离", 18, "IF 条件")):
            if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 缺口类型,"operand2": "单缺口识别","operator": "=="}], _block=("计算滑块距离", 19, "IF 多条件")):
                image_left = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="33", third_party_code="ttshitu_33_predict", image_source="web_element", image_file=None, image_browser=web_page, image_web_selector=background_element, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("计算滑块距离", 20, "验证码识别"))
                distince = xbot_visual.programing.variable(value=lambda: int(image_left)*ppi
                , _block=("计算滑块距离", 21, "设置变量"))
            else:
                start_bound = xbot_visual.web.element.get_bounding(browser=web_page, element=start_element, to96dpi=False, relative_to="screen", timeout="20", _block=("计算滑块距离", 23, "获取元素位置(web)"))
                captcha_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="18", third_party_code="ttshitu_18_predict", image_source="web_element", image_file=None, image_browser=web_page, image_web_selector=start_element, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser=web_page, imageback_web_selector=None, imageback_window="0", imageback_win_selector=None, imageback_region_x1=lambda: start_bound.right, imageback_region_y1=lambda: background_bound2.top, imageback_region_x2=lambda: background_bound2.right, imageback_region_y2=lambda: background_bound2.bottom, typename=None, is_to96dpi=False, remark=None, _block=("计算滑块距离", 24, "验证码识别"))
                image_left = xbot_visual.text.extract_content_from_text(text=captcha_result, extract_way="custom", regular_pattern="(\\d+),", just_get_first=True, ignore_case=False, _block=("计算滑块距离", 25, "从文本中提取内容"))
                distince = xbot_visual.programing.variable(value=lambda: (int(image_left) + start_bound.width)*ppi
                , _block=("计算滑块距离", 26, "设置变量"))
            #endif
        #endif
        # 利用本地引擎识别
        if xbot_visual.workflow.test(operand1=ai_engine, operator="==", operand2="LOCAL", operator_options="{}", _block=("计算滑块距离", 30, "IF 条件")):
            dir_path = xbot_visual.dir.get_special_dir(special_dir_name="TEMP", _block=("计算滑块距离", 31, "获取系统文件夹路径"))
            start_element_save_file_name = xbot_visual.web.element.screenshot(browser=web_page, capture_area="Element", element=start_element, folder_path=dir_path, random_filename=True, filename=None, overwrite_file=True, save_to_clipboard=False, height="25000", piece_height="3000", timeout="20", _block=("计算滑块距离", 32, "网页截图"))
            start_bound = xbot_visual.web.element.get_bounding(browser=web_page, element=start_element, to96dpi=False, relative_to="screen", timeout="20", _block=("计算滑块距离", 33, "获取元素位置(web)"))
            background_bound = xbot_visual.web.element.get_bounding(browser=web_page, element=background_element, to96dpi=False, relative_to="screen", timeout="20", _block=("计算滑块距离", 34, "获取元素位置(web)"))
            current_datetime = xbot_visual.datetime.now(_block=("计算滑块距离", 35, "获取当前日期时间"))
            text = xbot_visual.datetime.to_string(datetime=current_datetime, format="%Y%m%d%H%M%S", _block=("计算滑块距离", 36, "日期时间转换为文本"))
            background_element_save_file_name = xbot_visual.programing.variable(value=xbot_visual.sh_str(dir_path) + "\\" + xbot_visual.sh_str(text) + ".png"
            , _block=("计算滑块距离", 37, "设置变量"))
            _ = xbot_visual.system.take_screenshot(image_source="foreground_window", window=None, image_region="sub_region", region_x1=start_bound.right, region_y1=background_bound.top, region_x2=background_bound.right, region_y2=background_bound.bottom, save_to="file", image_path=background_element_save_file_name, _block=("计算滑块距离", 38, "截屏"))
            invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="distance_ty", params={
                "background_file": background_element_save_file_name,
                "gap_file": start_element_save_file_name,
            }, _block=("计算滑块距离", 39, "调用模块"))
            distince = xbot_visual.programing.variable(value=lambda: int(start_bound.width/2+invoke_result*ppi)
            , _block=("计算滑块距离", 40, "设置变量"))
        #endif
    finally:
        args["distince"] = distince
