import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    if args is None:
        网页对象 = None
        验证码图片 = None
        图鉴账号 = ""
        图鉴密码 = ""
    else:
        网页对象 = args.get("网页对象", None)
        验证码图片 = args.get("验证码图片", None)
        图鉴账号 = args.get("图鉴账号", "")
        图鉴密码 = args.get("图鉴密码", "")
    try:
        try:
            xbot_visual.web.browser.wait_load_completed(browser=网页对象, load_timeout="20", action_after_load_timeout="stopLoad", _block=("推理拼图验证", 1, "等待网页加载完成"))
        except Exception as e:
            xbot_visual.programing.log(type='info', text=f'第1条指令: {e}')
        # 添加 AI 引擎的选择
        captcha_result = " "
        if xbot_visual.workflow.test(operand1=lambda: bool(图鉴账号) and bool(图鉴密码), operator="is true", operand2="", operator_options="{}", _block=("推理拼图验证", 4, "IF 条件")):
            captcha_result = xbot_visual.web_service.captcha(engine_type="ttshitu", username=图鉴账号, password=xbot_visual.decrypt(图鉴密码), captcha_type="53", third_party_code="ttshitu_53_predict", image_source="web_element", image_file=None, image_browser=网页对象, image_web_selector=验证码图片, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("推理拼图验证", 5, "验证码识别"))
        else:
            captcha_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="53", third_party_code="ttshitu_53_predict", image_source="web_element", image_file=None, image_browser=网页对象, image_web_selector=验证码图片, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("推理拼图验证", 7, "验证码识别"))
        #endif
        交换项 = xbot_visual.text.extract_content_from_text(text=captcha_result, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=False, ignore_case=False, _block=("推理拼图验证", 9, "从文本中提取内容"))
        验证码图片信息 = xbot_visual.web.element.get_bounding(browser=网页对象, element=验证码图片, to96dpi=True, relative_to="screen", timeout="20", _block=("推理拼图验证", 10, "获取元素位置(web)"))
        坐标 = [[验证码图片信息.left+验证码图片信息.width/8,验证码图片信息.top+验证码图片信息.height/4],[验证码图片信息.left+验证码图片信息.width/8*3,验证码图片信息.top+验证码图片信息.height/4],[验证码图片信息.left+验证码图片信息.width/8*5,验证码图片信息.top+验证码图片信息.height/4],[验证码图片信息.left+验证码图片信息.width/8*7,验证码图片信息.top+验证码图片信息.height/4],[验证码图片信息.left+验证码图片信息.width/8,验证码图片信息.top+验证码图片信息.height/4*3],[验证码图片信息.left+验证码图片信息.width/8*3,验证码图片信息.top+验证码图片信息.height/4*3],[验证码图片信息.left+验证码图片信息.width/8*5,验证码图片信息.top+验证码图片信息.height/4*3],[验证码图片信息.left+验证码图片信息.width/8*7,验证码图片信息.top+验证码图片信息.height/4*3]]
        xbot_visual.win32.click_mouse(is_move_mouse_before_click=True, point_x=lambda: int(坐标[int(交换项[0])][0]), point_y=lambda: int(坐标[int(交换项[0])][1]), relative_to="screen", move_speed="middle", button="left", click_type="down", hardware_driver_click=False, keys="null", delay_after="1", _block=("推理拼图验证", 12, "鼠标点击"))
        xbot_visual.win32.move_mouse(point_x=lambda: int(坐标[int(交换项[1])][0]), point_y=lambda: int(坐标[int(交换项[1])][1]), relative_to="screen", move_speed="middle", delay_after="1", _block=("推理拼图验证", 13, "移动鼠标"))
        xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="up", hardware_driver_click=False, keys="null", delay_after="1", _block=("推理拼图验证", 14, "鼠标点击"))
        xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("推理拼图验证", 15, "等待"))
    finally:
        pass
