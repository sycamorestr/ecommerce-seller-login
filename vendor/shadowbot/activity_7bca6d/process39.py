import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    process_result = False
    if args is None:
        用户名 = ""
        密码 = ""
    else:
        用户名 = args.get("用户名", "")
        密码 = args.get("密码", "")
    try:
        xbot_visual.win32.element.input(window="0", element=package.selector("旺店通用户名-企业"), text=用户名, append=False, simulate=True, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("旺店通登录", 1, "填写输入框(win)"))
        xbot_visual.win32.element.input_password(window="0", element=package.selector("旺店通密码框-企业"), text=xbot_visual.decrypt(密码), simulate=True, save_to_clipboard=False, input_type="simulate", send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("旺店通登录", 2, "填写密码框(win)"))
        xbot_visual.win32.element.click(window="0", element=package.selector("旺店通登录"), clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_mouse=True, simulate=True, timeout="20", _block=("旺店通登录", 3, "点击元素(win)"))
        if xbot_visual.win32.window.contains_element(window="0", content_type="contains_element", element=package.selector("文本_旺店通客户端版本与服务器端版本不一致立即下载"), _block=("旺店通登录", 4, "IF 窗口包含")):
            xbot_visual.win32.element.click(window="0", element=package.selector("按钮_是Y"), clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_mouse=True, simulate=True, timeout="20", _block=("旺店通登录", 5, "点击元素(win)"))
            xbot_visual.programing.sleep(random_number=False, seconds="30", start_number="1", stop_number="5", _block=("旺店通登录", 6, "等待"))
            xbot_visual.win32.element.input(window="0", element=package.selector("旺店通用户名-企业"), text=用户名, append=False, simulate=True, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="30", _block=("旺店通登录", 7, "填写输入框(win)"))
            xbot_visual.win32.element.input_password(window="0", element=package.selector("旺店通密码框-企业"), text=xbot_visual.decrypt(密码), simulate=True, save_to_clipboard=False, input_type="simulate", send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("旺店通登录", 8, "填写密码框(win)"))
            xbot_visual.win32.element.click(window="0", element=package.selector("旺店通登录"), clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_mouse=True, simulate=True, timeout="20", _block=("旺店通登录", 9, "点击元素(win)"))
        #endif
        if xbot_visual.image.exist(window_kind="currentactivatewindow", window="", exist_mode="exist", template_images=[package.image_selector("旺店通图像")], is_find_all_images=False, _block=("旺店通登录", 11, "IF 图像存在")):
            software_window = xbot_visual.win32.window.get(window_type="window_selector", selector=package.selector("旺店通验证码"), handle="", title="", handle_checked=False, class_name="", use_wildcard=False, _block=("旺店通登录", 12, "获取窗口对象"))
            captcha_result = xbot_visual.web_service.captcha(engine_type="shadowbot", username=None, password=xbot_visual.decrypt(""), captcha_type="3", third_party_code="ttshitu_3_predict", image_source="win_element", image_file=None, image_browser="", image_web_selector=None, image_window="", image_win_selector=package.selector("旺店通验证码"), image_region_x1="0", image_region_y1="0", image_region_x2="0", image_region_y2="0", imageback_source="screen", back_image_file=None, imageback_browser="", imageback_web_selector=None, imageback_window="", imageback_win_selector=None, imageback_region_x1="0", imageback_region_y1="0", imageback_region_x2="0", imageback_region_y2="0", typename=None, is_to96dpi=False, remark=None, _block=("旺店通登录", 13, "验证码识别"))
            xbot_visual.win32.element.input(window="0", element=package.selector("旺店通验证码输入"), text=captcha_result, append=False, simulate=True, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("旺店通登录", 14, "填写输入框(win)"))
            xbot_visual.win32.element.click(window="0", element=package.selector("验证码确定"), clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_mouse=True, simulate=True, timeout="20", _block=("旺店通登录", 15, "点击元素(win)"))
        #endif
        if xbot_visual.win32.window.contains_element(window="0", content_type="contains_element", element=package.selector("块元素_search"), _block=("旺店通登录", 17, "IF 窗口包含")):
            process_result = xbot_visual.programing.variable(value=True
            , _block=("旺店通登录", 18, "设置变量"))
        else:
            if xbot_visual.win32.window.contains_element(window="0", content_type="contains_element", element=package.selector("列表_menu-bar"), _block=("旺店通登录", 20, "IF 窗口包含")):
                process_result = xbot_visual.programing.variable(value=True
                , _block=("旺店通登录", 21, "设置变量"))
            #endif
        #endif
    finally:
        args["process_result"] = process_result
