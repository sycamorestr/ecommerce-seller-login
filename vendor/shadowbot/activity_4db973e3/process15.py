import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    if args is None:
        验证码图片 = None
        滑块元素 = None
        网页对象 = None
        滑动条 = None
        图鉴账号 = ""
        图鉴密码 = ""
        偏移 = 0
        是否模拟人工 = False
    else:
        验证码图片 = args.get("验证码图片", None)
        滑块元素 = args.get("滑块元素", None)
        网页对象 = args.get("网页对象", None)
        滑动条 = args.get("滑动条", None)
        图鉴账号 = args.get("图鉴账号", "")
        图鉴密码 = args.get("图鉴密码", "")
        偏移 = args.get("偏移", 0)
        是否模拟人工 = args.get("是否模拟人工", False)
    try:
        try:
            xbot_visual.web.browser.wait_load_completed(browser=网页对象, load_timeout="20", action_after_load_timeout="stopLoad", _block=("图片旋转验证", 1, "等待网页加载完成"))
        except Exception as e:
            xbot_visual.programing.log(type='info',text=e,_block=("图片旋转验证", 1,"等待网页加载完成"))
        滑动条 = xbot_visual.web.element.get_bounding(browser=网页对象, element=滑动条, to96dpi=True, relative_to="screen", timeout="20", _block=("图片旋转验证", 2, "获取元素位置(web)"))
        滑块 = xbot_visual.web.element.get_bounding(browser=网页对象, element=滑块元素, to96dpi=True, relative_to="screen", timeout="20", _block=("图片旋转验证", 3, "获取元素位置(web)"))
        # 判断 AI 引擎
        captcha_result = xbot_visual.programing.variable(value=lambda: 0
        , _block=("图片旋转验证", 5, "设置变量"))
        if xbot_visual.workflow.test(operand1=lambda: bool(图鉴账号) and bool(图鉴密码), operator="is true", operand2="", operator_options="{}", _block=("图片旋转验证", 6, "IF 条件")):
            captcha_result = xbot_visual.web_service.captcha(engine_type="ttshitu", username=图鉴账号, password=xbot_visual.decrypt(图鉴密码), captcha_type="29", third_party_code="ttshitu_29_predict", image_source="web_element", image_file=None, image_browser=网页对象, image_web_selector=验证码图片, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("图片旋转验证", 7, "验证码识别"))
        else:
            captcha_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="29", third_party_code="ttshitu_29_predict", image_source="web_element", image_file=None, image_browser=网页对象, image_web_selector=验证码图片, image_window="", image_win_selector=None, image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("图片旋转验证", 9, "验证码识别"))
        #endif
        xbot_visual.web.element.hover(browser=网页对象, element=验证码图片, simulate=True, delay_after="1", anchor_type="random", sudoku_part="Random", offset_x="0", offset_y="0", timeout="20", _block=("图片旋转验证", 11, "鼠标悬停在元素上(web)"))
        xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("图片旋转验证", 12, "等待"))
        xbot_visual.web.element.hover(browser=网页对象, element=滑块元素, simulate=True, delay_after="1", anchor_type="random", sudoku_part="Random", offset_x="0", offset_y="0", timeout="20", _block=("图片旋转验证", 13, "鼠标悬停在元素上(web)"))
        # win32.click_mouse
        distant = xbot_visual.programing.variable(value=""
        , _block=("图片旋转验证", 15, "设置变量"))
        ppi = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_ppi", params={
        }, _block=("图片旋转验证", 16, "调用模块"))
        if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": int(captcha_result),"operand2": "0","operator": ">"}], _block=("图片旋转验证", 17, "IF 多条件")):
            distant = xbot_visual.programing.variable(value=lambda: int((int((滑动条.width-滑块.width)*int(captcha_result)/360) + 偏移))
            , _block=("图片旋转验证", 18, "设置变量"))
        else:
            distant = xbot_visual.programing.variable(value=lambda: int((int((滑动条.width-滑块.width)*(360+int(captcha_result))/360) + 偏移))
            , _block=("图片旋转验证", 20, "设置变量"))
        #endif
        # process.invoke_module
        # process.invoke_module
        xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=False, min_time="1", max_time="3", _block=("图片旋转验证", 24, "开启模拟真人操作"))
        xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="down", hardware_driver_click=False, keys="null", delay_after="1", _block=("图片旋转验证", 25, "鼠标点击"))
        xbot_visual.win32.move_mouse(point_x=distant, point_y="0", relative_to="currentmouseposition", move_speed="slow", delay_after="0", _block=("图片旋转验证", 26, "移动鼠标"))
        xbot_visual.win32.manual_motion_off(_block=("图片旋转验证", 27, "结束模拟真人操作"))
        xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="up", hardware_driver_click=False, keys="null", delay_after="1", _block=("图片旋转验证", 28, "鼠标点击"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("图片旋转验证", 29, "等待"))
    finally:
        pass
