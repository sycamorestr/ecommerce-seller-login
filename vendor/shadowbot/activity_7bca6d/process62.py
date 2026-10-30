import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        账号 = ""
        密码 = ""
        重试次数 = "3"
        浏览器类型 = "chrome"
    else:
        账号 = args.get("账号", "")
        密码 = args.get("密码", "")
        重试次数 = args.get("重试次数", "3")
        浏览器类型 = args.get("浏览器类型", "chrome")
    try:
        web_page = xbot_visual.programing.variable(value="https://loginmyseller.taobao.com"
        , _block=("千牛登录", 1, "设置变量"))
        if xbot_visual.workflow.test(operand1=浏览器类型, operator="==", operand2="chrome", operator_options="{}", _block=("千牛登录", 2, "IF 条件")):
            web_page = xbot_visual.web.create(web_type="chrome", value="https://loginmyseller.taobao.com", silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("千牛登录", 3, "打开网页"))
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("千牛登录", 4, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("千牛登录", 4,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        else:
            web_page = xbot_visual.web.create(web_type="edge", value="https://loginmyseller.taobao.com", silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("千牛登录", 6, "打开网页"))
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="edge", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("千牛登录", 7, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("千牛登录", 7,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        #endif
        xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=False, min_time="1", max_time="3", _block=("千牛登录", 9, "开启模拟真人操作"))
        xbot_visual.web.element.hover(browser=web_page, element=package.selector("qn_uername_input"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("千牛登录", 10, "鼠标悬停在元素上(web)"))
        xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="click", hardware_driver_click=False, keys="null", delay_after="1", _block=("千牛登录", 11, "鼠标点击"))
        xbot_visual.win32.send_keys(keys=账号, hardware_driver_input=False, force_ime_eng=True, contains_hotkey=False, send_key_delay="50", delay_after="1", _block=("千牛登录", 12, "键盘输入"))
        # web.element.input
        # web.element.input_password
        xbot_visual.web.element.hover(browser=web_page, element=package.selector("密码输入框"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("千牛登录", 15, "鼠标悬停在元素上(web)"))
        xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="click", hardware_driver_click=False, keys="null", delay_after="1", _block=("千牛登录", 16, "鼠标点击"))
        密码 = xbot_visual.decrypt(密码)
        xbot_visual.win32.send_keys(keys=密码, hardware_driver_input=False, force_ime_eng=True, contains_hotkey=False, send_key_delay="50", delay_after="1", _block=("千牛登录", 18, "键盘输入"))
        xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("千牛登录", 19, "等待"))
        xbot_visual.programing.log(type="info", text="xxxxx", _block=("千牛登录", 20, "打印日志"))
        _ = xbot_visual.process.run(process="process11", package=__name__, inputs={
            "web_page": lambda: web_page,
            "drag_start_element": package.selector("1688_slide"),
            "background_element": package.selector("1688_login_verify"),
            }, outputs=[
        ], _block=("千牛登录", 21, "调用流程"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("1688_login_verify"), _block=("千牛登录", 22, "IF 元素可见(web)")):
            xbot_visual.programing.log(type="info", text="检查到滑块", _block=("千牛登录", 23, "打印日志"))
            _ = xbot_visual.process.run(process="process11", package=__name__, inputs={
                "web_page": lambda: web_page,
                "drag_start_element": package.selector("1688_slide"),
                "background_element": package.selector("1688_login_verify"),
                }, outputs=[
            ], _block=("千牛登录", 24, "调用流程"))
            xbot_visual.programing.log(type="info", text="已拖动", _block=("千牛登录", 25, "打印日志"))
        #endif
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=重试次数, step="1", _block=("千牛登录", 27, "For次数循环")):
            xbot_visual.programing.log(type="info", text="看看有没有滑块~", _block=("千牛登录", 28, "打印日志"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("1688_login_verify"), _block=("千牛登录", 29, "IF 元素可见(web)")):
                xbot_visual.programing.log(type="info", text="检查到滑块", _block=("千牛登录", 30, "打印日志"))
                _ = xbot_visual.process.run(process="process11", package=__name__, inputs={
                    "web_page": lambda: web_page,
                    "drag_start_element": package.selector("1688_slide"),
                    "background_element": package.selector("1688_login_verify"),
                    }, outputs=[
                ], _block=("千牛登录", 31, "调用流程"))
                xbot_visual.programing.log(type="info", text="已拖动", _block=("千牛登录", 32, "打印日志"))
            else:
                break
            #endif
        #endloop
        xbot_visual.web.element.click(browser=web_page, element=package.selector("qn_login"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("千牛登录", 37, "点击元素(web)"))
        xbot_visual.win32.manual_motion_off(_block=("千牛登录", 38, "结束模拟真人操作"))
    finally:
        pass
