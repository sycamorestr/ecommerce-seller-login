import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    web_page = None
    if args is None:
        userid = ""
        password = ""
        mode = "chrome"
        path_to_chrome_exe = ""
        加载超时时间 = "20"
        ym_token = ""
        是否退出已登录 = True
        重试次数 = 5
    else:
        userid = args.get("userid", "")
        password = args.get("password", "")
        mode = args.get("mode", "chrome")
        path_to_chrome_exe = args.get("path_to_chrome_exe", "")
        加载超时时间 = args.get("加载超时时间", "20")
        ym_token = args.get("ym_token", "")
        是否退出已登录 = args.get("是否退出已登录", True)
        重试次数 = args.get("重试次数", 5)
    try:
        if xbot_visual.workflow.test(operand1=lambda: type(userid), operator="!=", operand2=lambda: str, operator_options="{}", _block=("淘宝登录", 1, "IF 条件")):
            raise Exception("登录账号类型错误，应为字符串类型")
        #endif
        if xbot_visual.workflow.test(operand1=lambda: type(password), operator="!=", operand2=lambda: str, operator_options="{}", _block=("淘宝登录", 4, "IF 条件")):
            raise Exception("登录密码类型错误，应为字符串类型")
        #endif
        if xbot_visual.workflow.test(operand1=lambda: bool(加载超时时间), operator="is true", operand2="", operator_options="{}", _block=("淘宝登录", 7, "IF 条件")):
            加载超时时间 = xbot_visual.programing.variable(value=lambda: int(加载超时时间)
            , _block=("淘宝登录", 8, "设置变量"))
        else:
            加载超时时间 = xbot_visual.programing.variable(value=lambda: 20
            , _block=("淘宝登录", 10, "设置变量"))
        #endif
        淘宝网址 = xbot_visual.programing.variable(value=lambda: None
        , _block=("淘宝登录", 12, "设置变量"))
        是否新打开 = xbot_visual.programing.variable(value=False
        , _block=("淘宝登录", 13, "设置变量"))
        web_page2 = xbot_visual.web.create(web_type=mode, value="https://login.taobao.com/member/login.jhtml", silent_running=False, wait_load_completed=True, load_timeout=加载超时时间, stop_load_if_load_timeout="handleExcept", chrome_file_name=lambda: path_to_chrome_exe if path_to_chrome_exe else None, edge_file_name=None, ie_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("淘宝登录", 15, "打开网页"))
        xbot_visual.web.browser.close(operation="close_specified", browser=web_page2, web_type="cef", task_kill=False, ignore_beforeunload=False, _block=("淘宝登录", 16, "关闭网页"))
        web_page = xbot_visual.web.create(web_type=mode, value="https://login.taobao.com/member/login.jhtml", silent_running=False, wait_load_completed=True, load_timeout=加载超时时间, stop_load_if_load_timeout="handleExcept", chrome_file_name=lambda: path_to_chrome_exe if path_to_chrome_exe else None, edge_file_name=None, ie_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("淘宝登录", 17, "打开网页"))
        for loop_index3 in xbot_visual.workflow.range_iterator(start="0", stop=重试次数, step="1", _block=("淘宝登录", 15, "For次数循环")):
            web_wait_result3 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("链接_使用其他帐户登录"), state="appear", iswait=True, timeout="5", _block=("淘宝登录", 16, "等待元素(web)"))
            # 如果出现“快速进入”，需要点击“使用其他账户登录”才能出现用户名、密码输入控件
            if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 是否退出已登录,"operand2": "","operator": "is false"}], _block=("淘宝登录", 18, "IF 多条件")):
                if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("快速进入"), text="", _block=("淘宝登录", 19, "IF 网页包含")):
                    xbot_visual.programing.log(type="info", text="已经快速进入当前账号中", _block=("淘宝登录", 20, "打印日志"))
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("快速进入"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 21, "点击元素(web)"))
                    return
                else:
                    xbot_visual.programing.log(type="info", text="当前没有账号登录中~", _block=("淘宝登录", 24, "打印日志"))
                #endif
            #endif
            if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("链接_使用其他帐户登录"), text="", _block=("淘宝登录", 27, "IF 网页包含")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("链接_使用其他帐户登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 28, "点击元素(web)"))
            #endif
            xbot_visual.web.element.click(browser=web_page, element=package.selector("密码登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 30, "点击元素(web)"))
            for loop_index2 in xbot_visual.workflow.range_iterator(start="1", stop="4", step="1", _block=("淘宝登录", 31, "For次数循环")):
                if xbot_visual.workflow.test(operand1=loop_index2, operator="==", operand2="4", operator_options="{}", _block=("淘宝登录", 32, "IF 条件")):
                    raise Exception("当前输入框内容和实际账号不相等，请重新运行该指令")
                #endif
                xbot_visual.web.element.input(browser=web_page, element=package.selector("淘宝账号_输入框"), text=userid, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 35, "填写输入框(web)"))
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("淘宝登录", 36, "等待"))
                web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("淘宝账号_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("淘宝登录", 37, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=userid, operator="==", operand2=web_element_attribute, operator_options="{}", _block=("淘宝登录", 38, "IF 条件")):
                    break
                #endif
                xbot_visual.web.element.click(browser=web_page, element=package.selector("淘宝账号_输入框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 41, "点击元素(web)"))
                xbot_visual.win32.send_keys(keys="^{a}", hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("淘宝登录", 42, "键盘输入"))
                xbot_visual.win32.send_keys(keys="{DELETE}", hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("淘宝登录", 43, "键盘输入"))
                xbot_visual.web.element.input(browser=web_page, element=package.selector("淘宝账号_输入框"), text=userid, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 44, "填写输入框(web)"))
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("淘宝登录", 45, "等待"))
                web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("淘宝账号_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("淘宝登录", 46, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=userid, operator="==", operand2=web_element_attribute, operator_options="{}", _block=("淘宝登录", 47, "IF 条件")):
                    break
                #endif
            #endloop
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("淘系_新验证码_标识"), _block=("淘宝登录", 51, "IF 元素可见(web)")):
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "engine": "xbot",
                    "background_ele": package.selector("淘系_新验证码_背景图"),
                    "slider_ele": package.selector("淘系_新验证码_拖拽"),
                    "ym_token": ym_token,
                    "retry_count": lambda: 1,
                    "offset": lambda: 0,
                    "speed": lambda: 1,
                    "refresh_elem": None,
                    }, outputs=[
                ], _block=("淘宝登录", 52, "通用单图滑块验证"))
            #endif
            xbot_visual.web.element.click(browser=web_page, element=package.selector("淘宝密码_输入框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 54, "点击元素(web)"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("阿里_滑块"), _block=("淘宝登录", 55, "IF 元素可见(web)")):
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.ali_slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "engine": "xbot",
                    "drag_ele": package.selector("阿里_滑块"),
                    "refresh_ele": package.selector("阿里_刷新"),
                    "ym_token": "",
                    "retry_count": lambda: 重试次数,
                    "offset": lambda: 0,
                    "speed": "middle",
                    "monitor_time": lambda: 3,
                    "background_ele": lambda: None,
                    }, outputs=[
                ], _block=("淘宝登录", 56, "阿里滑块验证"))
            #endif
            for loop_index2 in xbot_visual.workflow.range_iterator(start="1", stop="4", step="1", _block=("淘宝登录", 58, "For次数循环")):
                if xbot_visual.workflow.test(operand1=loop_index2, operator="==", operand2="4", operator_options="{}", _block=("淘宝登录", 59, "IF 条件")):
                    raise Exception("当前输入框内容和实际账号不相等，请重新运行该指令")
                #endif
                xbot_visual.web.element.click(browser=web_page, element=package.selector("淘宝密码_输入框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 62, "点击元素(web)"))
                password = xbot_visual.decrypt(password)
                xbot_visual.web.element.input(browser=web_page, element=package.selector("淘宝密码_输入框"), text=password, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=False, anchor_type="center", sudoku_part="middleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 64, "填写输入框(web)"))
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("淘宝登录", 65, "等待"))
                web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("淘宝密码_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("淘宝登录", 66, "获取元素信息(web)"))
                # programing.log
                # programing.log
                # programing.log
                if xbot_visual.workflow.test(operand1=password, operator="==", operand2=web_element_attribute, operator_options="{}", _block=("淘宝登录", 70, "IF 条件")):
                    break
                #endif
                xbot_visual.web.element.input(browser=web_page, element=package.selector("淘宝密码_输入框"), text=password, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 73, "填写输入框(web)"))
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("淘宝登录", 74, "等待"))
                web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("淘宝密码_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("淘宝登录", 75, "获取元素信息(web)"))
                # programing.log
                # programing.log
                # programing.log
                if xbot_visual.workflow.test(operand1=password, operator="==", operand2=web_element_attribute, operator_options="{}", _block=("淘宝登录", 79, "IF 条件")):
                    break
                #endif
            #endloop
            xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("淘宝登录", 83, "等待"))
            xbot_visual.programing.log(type="info", text="检测滑条是否出现", _block=("淘宝登录", 84, "打印日志"))
            for loop_index in xbot_visual.workflow.range_iterator(start=lambda: 1, stop=重试次数, step="1", _block=("淘宝登录", 85, "For次数循环")):
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        web_page = xbot_visual.web.get(web_type=mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("淘宝登录", 86, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("淘宝登录", 86,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("滑块失败的标志"), _block=("淘宝登录", 87, "IF 元素可见(web)")):
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("滑块失败的标志"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 88, "点击元素(web)"))
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("淘宝登录_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 89, "点击元素(web)"))
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("淘宝登录_横向滑块"), _block=("淘宝登录", 91, "IF 元素可见(web)")):
                    xbot_visual.programing.log(type="info", text="当前检测到滑条，正在拖动", _block=("淘宝登录", 92, "打印日志"))
                    _ = xbot_visual.process.run(process="process11", package=__name__, inputs={
                        "web_page": lambda: web_page,
                        "drag_start_element": package.selector("淘宝滑块"),
                        "background_element": package.selector("请按住滑块，拖动到最右边"),
                        }, outputs=[
                    ], _block=("淘宝登录", 93, "调用流程"))
                else:
                    break
                #endif
            #endloop
            # web.element.check
            xbot_visual.web.element.click(browser=web_page, element=package.selector("淘宝登录_同意协议"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 99, "点击元素(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("淘宝登录_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 100, "点击元素(web)"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("淘宝登录_保持登录_按钮"), _block=("淘宝登录", 101, "IF 元素可见(web)")):
                try:
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("淘宝登录_保持登录_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="5", _block=("淘宝登录", 102, "点击元素(web)"))
                except Exception as e:
                    pass
            #endif
            xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("淘宝登录", 104, "等待"))
            for loop_index in xbot_visual.workflow.range_iterator(start=lambda: 1, stop=重试次数, step="1", _block=("淘宝登录", 105, "For次数循环")):
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        web_page = xbot_visual.web.get(web_type=mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("淘宝登录", 106, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("淘宝登录", 106,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("滑块失败的标志"), _block=("淘宝登录", 107, "IF 元素可见(web)")):
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("滑块失败的标志"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("淘宝登录", 108, "点击元素(web)"))
                    # web.element.click
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("淘宝登录_横向滑块"), _block=("淘宝登录", 111, "IF 元素可见(web)")):
                    xbot_visual.programing.log(type="info", text="当前检测到滑条，正在拖动", _block=("淘宝登录", 112, "打印日志"))
                    _ = xbot_visual.process.run(process="process11", package=__name__, inputs={
                        "web_page": lambda: web_page,
                        "drag_start_element": package.selector("淘宝滑块"),
                        "background_element": package.selector("请按住滑块，拖动到最右边"),
                        }, outputs=[
                    ], _block=("淘宝登录", 113, "调用流程"))
                else:
                    break
                #endif
            #endloop
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("阿里_滑块"), _block=("淘宝登录", 118, "IF 元素可见(web)")):
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.ali_slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "engine": "xbot",
                    "drag_ele": package.selector("阿里_滑块"),
                    "refresh_ele": package.selector("阿里_刷新"),
                    "ym_token": "",
                    "retry_count": lambda: 重试次数,
                    "offset": lambda: 0,
                    "speed": "middle",
                    "monitor_time": lambda: 3,
                    "background_ele": lambda: None,
                    }, outputs=[
                ], _block=("淘宝登录", 119, "阿里滑块验证"))
            #endif
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("淘系_新验证码_标识"), _block=("淘宝登录", 121, "IF 元素可见(web)")):
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "engine": "xbot",
                    "background_ele": package.selector("淘系_新验证码_背景图"),
                    "slider_ele": package.selector("淘系_新验证码_拖拽"),
                    "ym_token": ym_token,
                    "retry_count": lambda: 重试次数,
                    "offset": lambda: 0,
                    "speed": lambda: 1,
                    "refresh_elem": None,
                    }, outputs=[
                ], _block=("淘宝登录", 122, "通用单图滑块验证"))
            #endif
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type=mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("淘宝登录", 124, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("淘宝登录", 124,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("淘宝登录_横向滑块"), _block=("淘宝登录", 125, "IF 元素可见(web)")):
                xbot_visual.programing.log(type="info", text="当前检测到滑条，正在拖动", _block=("淘宝登录", 126, "打印日志"))
                _ = xbot_visual.process.run(process="process11", package=__name__, inputs={
                    "web_page": lambda: web_page,
                    "drag_start_element": package.selector("淘宝登录_横向滑块"),
                    "background_element": package.selector("请按住滑块，拖动到最右边"),
                    }, outputs=[
                ], _block=("淘宝登录", 127, "调用流程"))
            #endif
            xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("淘宝登录", 129, "等待"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("滑块失败的标志"), _block=("淘宝登录", 130, "IF 元素可见(web)")):
                xbot_visual.web.browser.navigate(browser=web_page, mode="reload", url="", ignore_cache=False, load_timeout="20", _block=("淘宝登录", 131, "跳转至新网址"))
                xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://login.taobao.com/member/login.jhtml", ignore_cache=False, load_timeout="20", _block=("淘宝登录", 132, "跳转至新网址"))
                continue
                # web.element.click
                # web.element.click
            #endif
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("淘宝登录_按钮"), _block=("淘宝登录", 137, "IF 元素可见(web)")):
                try:
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("淘宝登录_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="5", _block=("淘宝登录", 138, "点击元素(web)"))
                except Exception as e:
                    pass
            #endif
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("淘宝登录-错误提示"), _block=("淘宝登录", 140, "IF 元素可见(web)")):
                web_element_attribute2 = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("淘宝登录-错误提示"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("淘宝登录", 141, "获取元素信息(web)"))
                raise Exception(web_element_attribute2)
            #endif
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("淘宝登录_保持登录_按钮"), _block=("淘宝登录", 144, "IF 元素可见(web)")):
                try:
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("淘宝登录_保持登录_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="5", _block=("淘宝登录", 145, "点击元素(web)"))
                except Exception as e:
                    pass
            #endif
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("淘宝登录_按钮"), _block=("淘宝登录", 147, "IF 元素可见(web)")):
                raise Exception("登录失败，请手动登录")
            #endif
            try:
                短信验证标志 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//button[@id=\"J_GetCode\"]", is_related_parent=False, parent=None, timeout="5", _block=("淘宝登录", 150, "获取元素对象(web)"))
            except Exception as e:
                pass
                短信验证标志 = None
            if xbot_visual.workflow.test(operand1=短信验证标志, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("淘宝登录", 151, "IF 条件")):
                raise Exception("登录需要短信验证，请手动完成短信验证登录")
            #endif
            break
        #endloop
    finally:
        args["web_page"] = web_page
