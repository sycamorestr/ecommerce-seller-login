import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    distince = 0
    if args is None:
        start_element = None
        background_element = None
        tj_username = ""
        tj_password = ""
        web_page = None
    else:
        start_element = args.get("start_element", None)
        background_element = args.get("background_element", None)
        tj_username = args.get("tj_username", "")
        tj_password = args.get("tj_password", "")
        web_page = args.get("web_page", None)
    try:
        start_bound = xbot_visual.web.element.get_bounding(browser=web_page, element=start_element, to96dpi=False, relative_to="screen", timeout="20", _block=("计算滑块距离", 1, "获取元素位置(web)"))
        background_bound2 = xbot_visual.web.element.get_bounding(browser=web_page, element=background_element, to96dpi=False, relative_to="screen", timeout="20", _block=("计算滑块距离", 2, "获取元素位置(web)"))
        # web_service.captcha
        captcha_result = xbot_visual.programing.variable(value=""
        , _block=("计算滑块距离", 4, "设置变量"))
        if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": lambda: bool(tj_username),"operand2": "","operator": "is true"}], _block=("计算滑块距离", 5, "IF 多条件")):
            captcha_result = xbot_visual.web_service.captcha(engine_type="ttshitu", username=tj_username, password=xbot_visual.decrypt(tj_password), captcha_type="18", third_party_code="ttshitu_18_predict", image_source="web_element", image_file=None, image_browser=web_page, image_web_selector=start_element, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser=web_page, imageback_web_selector=None, imageback_window="0", imageback_win_selector=None, imageback_region_x1=lambda: start_bound.right, imageback_region_y1=lambda: background_bound2.top, imageback_region_x2=lambda: background_bound2.right, imageback_region_y2=lambda: background_bound2.bottom, typename=None, is_to96dpi=False, remark="", _block=("计算滑块距离", 6, "验证码识别"))
        else:
            captcha_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="18", third_party_code="ttshitu_18_predict", image_source="web_element", image_file=None, image_browser=web_page, image_web_selector=start_element, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser=web_page, imageback_web_selector=None, imageback_window="0", imageback_win_selector=None, imageback_region_x1=lambda: start_bound.right, imageback_region_y1=lambda: background_bound2.top, imageback_region_x2=lambda: background_bound2.right, imageback_region_y2=lambda: background_bound2.bottom, typename=None, is_to96dpi=False, remark=None, _block=("计算滑块距离", 8, "验证码识别"))
        #endif
        image_left = xbot_visual.text.extract_content_from_text(text=captcha_result, extract_way="custom", regular_pattern="(\\d+),", just_get_first=True, ignore_case=False, _block=("计算滑块距离", 10, "从文本中提取内容"))
        ppi = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_ppi", params={
        }, _block=("计算滑块距离", 11, "调用模块"))
        distince = xbot_visual.programing.variable(value=lambda: (int(image_left) + start_bound.width)*ppi
        , _block=("计算滑块距离", 12, "设置变量"))
    finally:
        args["distince"] = distince
