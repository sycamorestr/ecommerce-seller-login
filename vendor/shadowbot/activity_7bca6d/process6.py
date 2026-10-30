import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    web_page = None
    if args is None:
        username = ""
        password = ""
        web_mode = ""
        tj_username = ""
        tj_password = ""
        rec_count = 5
        login_url = ""
    else:
        username = args.get("username", "")
        password = args.get("password", "")
        web_mode = args.get("web_mode", "")
        tj_username = args.get("tj_username", "")
        tj_password = args.get("tj_password", "")
        rec_count = args.get("rec_count", 5)
        login_url = args.get("login_url", "")
    try:
        web_page = xbot_visual.programing.variable(value=lambda: None
        , _block=("京东登录", 1, "设置变量"))
        password = xbot_visual.decrypt(password)
        tj_password = xbot_visual.decrypt(tj_password)
        if xbot_visual.workflow.test(operand1=login_url, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("京东登录", 3, "IF 条件")):
            login_url = xbot_visual.programing.variable(value="https://passport.jd.com/new/login.aspx"
            , _block=("京东登录", 4, "设置变量"))
        #endif
        if xbot_visual.workflow.test(operand1=web_mode, operator="==", operand2="0", operator_options="{}", _block=("京东登录", 6, "IF 条件")):
            web_mode = xbot_visual.programing.variable(value="chrome"
            , _block=("京东登录", 7, "设置变量"))
        elif xbot_visual.workflow.test(operand1=web_mode, operator="==", operand2="edge", operator_options="{}", _block=("京东登录", 8, "Else IF")):
            web_mode = xbot_visual.programing.variable(value="edge"
            , _block=("京东登录", 9, "设置变量"))
        elif xbot_visual.workflow.test(operand1=web_mode, operator="==", operand2="1", operator_options="{}", _block=("京东登录", 10, "Else IF")):
            web_mode = xbot_visual.programing.variable(value="cef"
            , _block=("京东登录", 11, "设置变量"))
        #endif
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type=web_mode, mode="title", value=login_url, use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="stopLoad", open_page=True, url=login_url, _block=("京东登录", 13, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 13,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # 如果已经存在登录界面, 且存在弹窗, 会造成登录异常, 刷新网页, 重新加载登录界面
        xbot_visual.programing.sleep(random_number=True, seconds="1", start_number="1", stop_number="2", _block=("京东登录", 15, "等待"))
        try:
            xbot_visual.web.browser.navigate(browser=web_page, mode="reload", url="", ignore_cache=False, load_timeout="40", _block=("京东登录", 16, "跳转至新网址"))
        except Exception as e:
            xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 16,"跳转至新网址"))
        # 退出登录
        web_page_url = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("京东登录", 18, "获取网页信息"))
        # 新版京东页面的登录
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("新版京东登录界面"), _block=("京东登录", 20, "IF 元素可见(web)")):
            xbot_visual.programing.log(type="info", text="当前是新版本的京东登录界面", _block=("京东登录", 21, "打印日志"))
            for loop_index3 in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("京东登录", 22, "For次数循环")):
                # 切换至账号登录
                xbot_visual.web.element.click(browser=web_page, element=package.selector("新版京东界面-密码登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 24, "点击元素(web)"))
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        web_page = xbot_visual.web.get(web_type=web_mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京东登录", 25, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 25,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
                xbot_visual.web.element.input(browser=web_page, element=package.selector("新版京东-账号输入框"), text=lambda: str(username), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 26, "填写输入框(web)"))
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        web_page = xbot_visual.web.get(web_type=web_mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京东登录", 27, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 27,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
                web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("新版京东-账号输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("京东登录", 28, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=web_element_attribute, operator="==", operand2=username, operator_options="{}", _block=("京东登录", 29, "IF 条件")):
                    break
                else:
                    xbot_visual.web.element.input(browser=web_page, element=package.selector("新版京东-账号输入框"), text=lambda: username, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 32, "填写输入框(web)"))
                #endif
                if xbot_visual.workflow.test(operand1=loop_index3, operator="==", operand2="5", operator_options="{}", _block=("京东登录", 34, "IF 条件")):
                    raise Exception("账号输入框填写失败")
                #endif
            #endloop
            xbot_visual.win32.send_keys(keys="{TAB}", hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("京东登录", 38, "键盘输入"))
            xbot_visual.web.element.input(browser=web_page, element=package.selector("新版京东-密码填写框"), text=lambda: str(password), append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="custom", sudoku_part="MiddleLeft", offset_x="5", offset_y="0", timeout="20", _block=("京东登录", 39, "填写输入框(web)"))
            web_page_url = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("京东登录", 40, "获取网页信息"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("新版京东-登录按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 41, "点击元素(web)"))
            # 用户判断网页是否处于加载过程中
            # workflow.if
            # web.get
            # workflow.elseif
            # web.get
            # workflow.else
            # web.get
            # workflow.endif
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type=web_mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京东登录", 50, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 50,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
            try:
                web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("京东首页_搜索框"), state="appear", iswait=True, timeout="5", _block=("京东登录", 51, "等待元素(web)"))
            except Exception as e:
                xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 51,"等待元素(web)"))
                web_wait_result2 = None
            if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("京东首页_搜索框"), text="", _block=("京东登录", 52, "IF 网页包含")):
                if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="not_contains_element", selector=package.selector("京东首页_请登录"), text="", _block=("京东登录", 53, "IF 网页包含")):
                    return
                #endif
            #endif
            for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=rec_count, step="1", _block=("京东登录", 57, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("京东滑块_图像"), _block=("京东登录", 58, "IF 元素可见(web)")):
                    break
                #endif
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 61, "等待"))
                start_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("京东滑块_图像"), css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("京东登录", 62, "获取元素对象(web)"))
                background_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("京东滑块背景_图片"), css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("京东登录", 63, "获取元素对象(web)"))
                drag_start_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("京东拖动滑块_按钮"), css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("京东登录", 64, "获取元素对象(web)"))
                xbot_visual.process.run(process="xbot_extensions.activity_4f0f15d7.slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "background_ele": package.selector("京东滑块背景_图片"),
                    "slider_ele": package.selector("京东滑块_图像"),
                    "drag_ele": package.selector("京东拖动滑块_按钮"),
                    "retry_count": lambda: 5,
                    "offset": lambda: -10,
                    "move_speed": "fast",
                    }, outputs=[
                ], _block=("京东登录", 65, "滑块拼图验证免费版(web)"))
                # process.run
                # programing.comment
                # web.element.get_bounding
                # process.invoke_module
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 70, "等待"))
            #endloop
            for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=rec_count, step="1", _block=("京东登录", 72, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("单滑块图像_new"), _block=("京东登录", 73, "IF 元素可见(web)")):
                    break
                #endif
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 76, "等待"))
                start_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("单滑块图像_new"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("京东登录", 77, "获取元素对象(web)"))
                background_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("单滑块背景_new"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("京东登录", 78, "获取元素对象(web)"))
                drag_start_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("单滑块按钮_new"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("京东登录", 79, "获取元素对象(web)"))
                xbot_visual.process.run(process="xbot_extensions.activity_4f0f15d7.slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "background_ele": package.selector("单滑块背景_new"),
                    "slider_ele": package.selector("单滑块图像_new"),
                    "drag_ele": package.selector("单滑块按钮_new"),
                    "retry_count": lambda: 5,
                    "offset": lambda: -10,
                    "move_speed": "fast",
                    }, outputs=[
                ], _block=("京东登录", 80, "滑块拼图验证免费版(web)"))
                # process.run
                # web.element.get_bounding
                # process.invoke_module
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 84, "等待"))
            #endloop
            for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=rec_count, step="1", _block=("京东登录", 86, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录_背景元素"), _block=("京东登录", 87, "IF 元素可见(web)")):
                    # programing.try
                    xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                        "web_page": web_page,
                        "engine": "xbot",
                        "background_ele": package.selector("京东登录_背景元素"),
                        "slider_ele": package.selector("京东登录_拖拽元素"),
                        "ym_token": "",
                        "retry_count": lambda: 1,
                        "offset": lambda: 0,
                        "speed": lambda: 1,
                        "refresh_elem": None,
                        }, outputs=[
                    ], _block=("京东登录", 89, "通用单图滑块验证"))
                    # programing.catch
                    # programing.log
                    # web.element.click
                    # programing.endtry
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录_点选确定"), _block=("京东登录", 95, "IF 元素可见(web)")):
                    xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 96, "等待"))
                    xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_click_select_captcha_plus", package=__name__, inputs={
                        "web_page": web_page,
                        "engine": "xbot",
                        "web_element": package.selector("京东登录_点选背景"),
                        "direction": "bottom",
                        "ym_token": "",
                        "retry_count": lambda: 1,
                        "confirm": package.selector("京东登录_点选确定"),
                        "timeout": lambda: 10,
                        }, outputs=[
                    ], _block=("京东登录", 97, "通用点选验证(plus)"))
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录_图片提示词"), _block=("京东登录", 99, "IF 元素可见(web)")):
                    xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 100, "等待"))
                    xbot_visual.process.run(process="xbot_extensions.activity_jfbym.jd_click_select_captcha", package=__name__, inputs={
                        "web_page": web_page,
                        "engine": "xbot",
                        "web_element": package.selector("京东点选背景元素"),
                        "ym_token": "",
                        "retry_count": lambda: 1,
                        "sure_element": lambda: None,
                        }, outputs=[
                    ], _block=("京东登录", 101, "京东图片点选验证"))
                #endif
            #endloop
            try:
                web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("京东首页_搜索框"), state="appear", iswait=True, timeout="8", _block=("京东登录", 104, "等待元素(web)"))
            except Exception as e:
                xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 104,"等待元素(web)"))
                web_wait_result2 = None
            # 判断是否成功登录的逻辑
            web_page_url_new = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("京东登录", 106, "获取网页信息"))
            if xbot_visual.workflow.test(operand1=web_page_url, operator="==", operand2=web_page_url_new, operator_options="{}", _block=("京东登录", 107, "IF 条件")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东滑块_图像"), _block=("京东登录", 108, "IF 元素可见(web)")):
                    raise Exception("由于验证码未通过导致登录失败")
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("错误信息"), _block=("京东登录", 111, "IF 元素可见(web)")):
                    web_element_attribute2 = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("错误信息"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("京东登录", 112, "获取元素信息(web)"))
                    raise Exception(web_element_attribute2)
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("正在登录..."), _block=("京东登录", 115, "IF 元素可见(web)")):
                    xbot_visual.programing.log(type="info", text="正在登录", _block=("京东登录", 116, "打印日志"))
                else:
                    raise Exception("验证码通过失败，请增加重试次数")
                #endif
            else:
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("快速验证"), _block=("京东登录", 121, "IF 元素可见(web)")):
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("快速验证"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 122, "点击元素(web)"))
                    xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 123, "等待"))
                    for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=rec_count, step="1", _block=("京东登录", 124, "For次数循环")):
                        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录_背景元素"), _block=("京东登录", 125, "IF 元素可见(web)")):
                            try:
                                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                                    "web_page": web_page,
                                    "engine": "xbot",
                                    "background_ele": package.selector("京东登录_背景元素"),
                                    "slider_ele": package.selector("京东登录_拖拽元素"),
                                    "ym_token": "",
                                    "retry_count": lambda: 1,
                                    "offset": lambda: 0,
                                    "speed": lambda: 1,
                                    "refresh_elem": None,
                                    }, outputs=[
                                ], _block=("京东登录", 127, "通用单图滑块验证"))
                            except Exception as exception:
                                exception = xbot_visual.trace(exception)
                                xbot_visual.programing.log(type="info", text=exception, _block=("京东登录", 129, "打印日志"))
                                xbot_visual.web.element.click(browser=web_page, element=package.selector("京东登录_刷新元素"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 130, "点击元素(web)"))
                            #endtry
                        #endif
                        try:
                            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录_点选确定"), _block=("京东登录", 134, "IF 元素可见(web)")):
                                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 135, "等待"))
                                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_click_select_captcha_plus", package=__name__, inputs={
                                    "web_page": web_page,
                                    "engine": "xbot",
                                    "web_element": package.selector("京东登录_点选背景"),
                                    "direction": "bottom",
                                    "ym_token": "",
                                    "retry_count": lambda: 1,
                                    "confirm": package.selector("京东登录_点选确定"),
                                    "timeout": lambda: 10,
                                    }, outputs=[
                                ], _block=("京东登录", 136, "通用点选验证(plus)"))
                            #endif
                        except Exception as exception2:
                            exception2 = xbot_visual.trace(exception2)
                            # 点击刷新
                            xbot_visual.programing.log(type="info", text=exception2, _block=("京东登录", 140, "打印日志"))
                            xbot_visual.web.element.click(browser=web_page, element=package.selector("京东登录_刷新元素"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 141, "点击元素(web)"))
                        #endtry
                        try:
                            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录_图片提示词"), _block=("京东登录", 144, "IF 元素可见(web)")):
                                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 145, "等待"))
                                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.jd_click_select_captcha", package=__name__, inputs={
                                    "web_page": web_page,
                                    "engine": "xbot",
                                    "web_element": package.selector("京东点选背景元素"),
                                    "ym_token": "",
                                    "retry_count": lambda: 1,
                                    "sure_element": lambda: None,
                                    }, outputs=[
                                ], _block=("京东登录", 146, "京东图片点选验证"))
                            #endif
                        except Exception as exception2:
                            exception2 = xbot_visual.trace(exception2)
                            # 点击刷新
                            xbot_visual.programing.log(type="info", text=exception2, _block=("京东登录", 150, "打印日志"))
                            xbot_visual.web.element.click(browser=web_page, element=package.selector("京东登录_刷新元素"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 151, "点击元素(web)"))
                        #endtry
                        xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("京东登录", 153, "等待"))
                    #endloop
                    try:
                        web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("京东首页_搜索框"), state="appear", iswait=True, timeout="8", _block=("京东登录", 155, "等待元素(web)"))
                    except Exception as e:
                        xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 155,"等待元素(web)"))
                        web_wait_result2 = None
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录-使用完成订单收货人姓名"), _block=("京东登录", 157, "IF 元素可见(web)")):
                    web_element_attribute3 = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("京东登录-使用完成订单收货人姓名"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("京东登录", 158, "获取元素信息(web)"))
                    raise Exception(web_element_attribute3)
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录-登录之后的短信识别验证"), _block=("京东登录", 161, "IF 元素可见(web)")):
                    raise Exception("当前账号需要短信验证")
                #endif
            #endif
        else:
            # 兼容旧版京东登录
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("换个账号登录"), _block=("京东登录", 167, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("换个账号登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 168, "点击元素(web)"))
            #endif
            # 部分网页有此提示, 京东提示_我知道了
            xbot_visual.programing.sleep(random_number=True, seconds="1", start_number="1", stop_number="3", _block=("京东登录", 171, "等待"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东提示_我知道了"), _block=("京东登录", 172, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("京东提示_我知道了"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 173, "点击元素(web)"))
            #endif
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东账户登录_按钮"), _block=("京东登录", 175, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("京东账户登录_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 176, "点击元素(web)"))
            #endif
            for loop_index2 in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("京东登录", 178, "For次数循环")):
                xbot_visual.web.element.input(browser=web_page, element=package.selector("京东账号_输入框"), text=lambda: str(username), append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 179, "填写输入框(web)"))
                web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("京东账号_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("京东登录", 180, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=web_element_attribute, operator="==", operand2=username, operator_options="{}", _block=("京东登录", 181, "IF 条件")):
                    break
                else:
                    xbot_visual.web.element.input(browser=web_page, element=package.selector("京东账号_输入框"), text=None, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 184, "填写输入框(web)"))
                #endif
                if xbot_visual.workflow.test(operand1=loop_index2, operator="==", operand2="5", operator_options="{}", _block=("京东登录", 186, "IF 条件")):
                    raise Exception("账号输入框填写失败")
                #endif
            #endloop
            xbot_visual.web.element.input(browser=web_page, element=package.selector("京东密码_输入框"), text=lambda: str(password), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="custom", sudoku_part="MiddleLeft", offset_x="5", offset_y="0", timeout="20", _block=("京东登录", 190, "填写输入框(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("京东登录_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 191, "点击元素(web)"))
            # 用户判断网页是否处于加载过程中
            if xbot_visual.workflow.test(operand1=web_mode, operator="==", operand2="0", operator_options="{}", _block=("京东登录", 193, "IF 条件")):
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京东登录", 194, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 194,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
            elif xbot_visual.workflow.test(operand1=web_mode, operator="==", operand2="edge", operator_options="{}", _block=("京东登录", 195, "Else IF")):
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        web_page = xbot_visual.web.get(web_type="edge", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京东登录", 196, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 196,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
            else:
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        web_page = xbot_visual.web.get(web_type="cef", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="stopLoad", open_page=False, url=None, _block=("京东登录", 198, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 198,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
            #endif
            try:
                web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("京东滑块_图像"), state="appear", iswait=True, timeout="3", _block=("京东登录", 200, "等待元素(web)"))
            except Exception as e:
                xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 200,"等待元素(web)"))
                web_wait_result = False
            # 等待滑块超时, 应抛出异常, 且滑块内容不可以见, 包含渲染dom, 但是未完全加载出来的场景
            if xbot_visual.workflow.test(operand1=web_wait_result, operator="is false", operand2="", operator_options="{}", _block=("京东登录", 202, "IF 条件")):
                # 企业账号跳转网页略有不同
                web_page_attribute = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("京东登录", 204, "获取网页信息"))
                if xbot_visual.workflow.test(operand1=web_page_attribute, operator="!=", operand2=login_url, operator_options="{}", _block=("京东登录", 205, "IF 条件")):
                    return
                #endif
                try:
                    web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("京东首页_搜索框"), state="appear", iswait=True, timeout="10", _block=("京东登录", 208, "等待元素(web)"))
                except Exception as e:
                    xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 208,"等待元素(web)"))
                    web_wait_result2 = None
                if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("京东首页_搜索框"), text="", _block=("京东登录", 209, "IF 网页包含")):
                    if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="not_contains_element", selector=package.selector("京东首页_请登录"), text="", _block=("京东登录", 210, "IF 网页包含")):
                        return
                    #endif
                #endif
            else:
                web_page_url = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("京东登录", 215, "获取网页信息"))
                for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=rec_count, step="1", _block=("京东登录", 216, "For次数循环")):
                    if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("京东滑块_图像"), _block=("京东登录", 217, "IF 元素可见(web)")):
                        break
                    #endif
                    xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 220, "等待"))
                    start_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("京东滑块_图像"), css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("京东登录", 221, "获取元素对象(web)"))
                    background_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("京东滑块背景_图片"), css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("京东登录", 222, "获取元素对象(web)"))
                    drag_start_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("京东拖动滑块_按钮"), css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("京东登录", 223, "获取元素对象(web)"))
                    process_result = xbot_visual.process.run(process="process2", package=__name__, inputs={
                        "start_element": start_element,
                        "background_element": background_element,
                        "tj_username": lambda: str(tj_username),
                        "tj_password": lambda: str(tj_password),
                        "web_page": web_page,
                        }, outputs=[
                        "distince",
                    ], _block=("京东登录", 224, "调用流程"))
                    # 调整滑块的拖动速度
                    bound = xbot_visual.web.element.get_bounding(browser=web_page, element=drag_start_element, to96dpi=True, relative_to="screen", timeout="20", _block=("京东登录", 226, "获取元素位置(web)"))
                    invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="drag", params={
                        "point_x": bound.center_x,
                        "point_y": bound.center_y,
                        "distance": process_result.distince,
                        "move_speed": "fast",
                    }, _block=("京东登录", 227, "调用模块"))
                    xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 228, "等待"))
                #endloop
            #endif
            # 判断是否成功登录的逻辑
            web_page_url_new = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("京东登录", 232, "获取网页信息"))
            if xbot_visual.workflow.test(operand1=web_page_url, operator="==", operand2=web_page_url_new, operator_options="{}", _block=("京东登录", 233, "IF 条件")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东滑块_图像"), _block=("京东登录", 234, "IF 元素可见(web)")):
                    raise Exception("由于验证码未通过导致登录失败")
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("错误信息"), _block=("京东登录", 237, "IF 元素可见(web)")):
                    web_element_attribute2 = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("错误信息"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("京东登录", 238, "获取元素信息(web)"))
                    raise Exception(web_element_attribute2)
                #endif
            else:
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("快速验证"), _block=("京东登录", 242, "IF 元素可见(web)")):
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("快速验证"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 243, "点击元素(web)"))
                    xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 244, "等待"))
                    for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=rec_count, step="1", _block=("京东登录", 245, "For次数循环")):
                        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录_背景元素"), _block=("京东登录", 246, "IF 元素可见(web)")):
                            try:
                                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                                    "web_page": web_page,
                                    "engine": "xbot",
                                    "background_ele": package.selector("京东登录_背景元素"),
                                    "slider_ele": package.selector("京东登录_拖拽元素"),
                                    "ym_token": "",
                                    "retry_count": lambda: 1,
                                    "offset": lambda: 0,
                                    "speed": lambda: 1,
                                    "refresh_elem": None,
                                    }, outputs=[
                                ], _block=("京东登录", 248, "通用单图滑块验证"))
                            except Exception as exception:
                                exception = xbot_visual.trace(exception)
                                xbot_visual.programing.log(type="info", text=exception, _block=("京东登录", 250, "打印日志"))
                                xbot_visual.web.element.click(browser=web_page, element=package.selector("京东登录_刷新元素"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 251, "点击元素(web)"))
                            #endtry
                        #endif
                        try:
                            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录_点选确定"), _block=("京东登录", 255, "IF 元素可见(web)")):
                                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 256, "等待"))
                                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_click_select_captcha_plus", package=__name__, inputs={
                                    "web_page": web_page,
                                    "engine": "xbot",
                                    "web_element": package.selector("京东登录_点选背景"),
                                    "direction": "bottom",
                                    "ym_token": "",
                                    "retry_count": lambda: 1,
                                    "confirm": package.selector("京东登录_点选确定"),
                                    "timeout": lambda: 10,
                                    }, outputs=[
                                ], _block=("京东登录", 257, "通用点选验证(plus)"))
                            #endif
                        except Exception as exception2:
                            exception2 = xbot_visual.trace(exception2)
                            # 点击刷新
                            xbot_visual.programing.log(type="info", text=exception2, _block=("京东登录", 261, "打印日志"))
                            xbot_visual.web.element.click(browser=web_page, element=package.selector("京东登录_刷新元素"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 262, "点击元素(web)"))
                        #endtry
                        try:
                            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录_图片提示词"), _block=("京东登录", 265, "IF 元素可见(web)")):
                                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京东登录", 266, "等待"))
                                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.jd_click_select_captcha", package=__name__, inputs={
                                    "web_page": web_page,
                                    "engine": "xbot",
                                    "web_element": package.selector("京东点选背景元素"),
                                    "ym_token": "",
                                    "retry_count": lambda: 1,
                                    "sure_element": lambda: None,
                                    }, outputs=[
                                ], _block=("京东登录", 267, "京东图片点选验证"))
                            #endif
                        except Exception as exception2:
                            exception2 = xbot_visual.trace(exception2)
                            # 点击刷新
                            xbot_visual.programing.log(type="info", text=exception2, _block=("京东登录", 271, "打印日志"))
                            xbot_visual.web.element.click(browser=web_page, element=package.selector("京东登录_刷新元素"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京东登录", 272, "点击元素(web)"))
                        #endtry
                        xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("京东登录", 274, "等待"))
                    #endloop
                    try:
                        web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("京东首页_搜索框"), state="appear", iswait=True, timeout="8", _block=("京东登录", 276, "等待元素(web)"))
                    except Exception as e:
                        xbot_visual.programing.log(type='info',text=e,_block=("京东登录", 276,"等待元素(web)"))
                        web_wait_result2 = None
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京东登录-登录之后的短信识别验证"), _block=("京东登录", 278, "IF 元素可见(web)")):
                    raise Exception("当前账号需要短信验证")
                #endif
            #endif
        #endif
        # programing.comment
        # web.browser.element_display
        # programing.raise
        # workflow.endif
    finally:
        args["web_page"] = web_page
