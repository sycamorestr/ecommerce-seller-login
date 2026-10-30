import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    网页对象 = None
    if args is None:
        浏览器类型 = ""
        账号 = ""
        密码 = ""
        识别引擎 = "云码引擎(付费增值服务)"
        验证码重试次数 = 5
        是否创建新页面 = False
    else:
        浏览器类型 = args.get("浏览器类型", "")
        账号 = args.get("账号", "")
        密码 = args.get("密码", "")
        识别引擎 = args.get("识别引擎", "云码引擎(付费增值服务)")
        验证码重试次数 = args.get("验证码重试次数", 5)
        是否创建新页面 = args.get("是否创建新页面", False)
    try:
        if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 账号.strip(),"operand2": "","operator": "is empty"},{"operand1": 密码.strip(),"operand2": "","operator": "is empty"}], _block=("拼多多登录", 1, "IF 多条件")):
            raise Exception("拼多多账号、密码均不能为空")
        #endif
        pdd_login_url = xbot_visual.programing.variable(value="https://mms.pinduoduo.com/login/"
        , _block=("拼多多登录", 4, "设置变量"))
        web_page = xbot_visual.programing.variable(value=lambda: None
        , _block=("拼多多登录", 5, "设置变量"))
        if xbot_visual.workflow.test(operand1=是否创建新页面, operator="is true", operand2="", operator_options="{}", _block=("拼多多登录", 6, "IF 条件")):
            web_page = xbot_visual.process.invoke_module(module="utils", package=__name__, function="sdk_create_web_page", params={
                "url": pdd_login_url,
                "mode": 浏览器类型,
                "load_timeout": lambda: 30,
                "stop_if_timeout": False,
            }, _block=("拼多多登录", 7, "调用模块"))
        else:
            try:
                _xbot_retry_time = 0
                while _xbot_retry_time <= 2:
                    try:
                        web_page = xbot_visual.web.get(web_type=浏览器类型, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="2", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("拼多多登录", 10, "获取已打开的网页对象"))
                        _xbot_retry_time = 4
                    except Exception as e:
                        if _xbot_retry_time == 2:
                            raise e
                        else:
                            pass
                        _xbot_retry_time += 1
                        time.sleep(2)
                xbot_visual.web.browser.navigate(browser=web_page, mode="url", url=pdd_login_url, ignore_cache=False, load_timeout="20", _block=("拼多多登录", 11, "跳转至新网址"))
            except Exception as exception3:
                exception3 = xbot_visual.trace(exception3)
                web_page = xbot_visual.process.invoke_module(module="utils", package=__name__, function="sdk_create_web_page", params={
                    "url": pdd_login_url,
                    "mode": 浏览器类型,
                    "load_timeout": lambda: 30,
                    "stop_if_timeout": False,
                }, _block=("拼多多登录", 13, "调用模块"))
            #endtry
        #endif
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("拼多多登录", 16, "等待"))
        #region 单图滑块验证
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=验证码重试次数, step="1", _block=("拼多多登录", 18, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("拼多多-验证码-背景"), _block=("拼多多登录", 19, "IF 元素可见(web)")):
                break
            #endif
            try:
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "engine": "",
                    "background_ele": package.selector("拼多多-验证码-背景"),
                    "slider_ele": package.selector("拼多多-验证码-拖拽滑块"),
                    "ym_token": "",
                    "retry_count": lambda: 5,
                    "offset": lambda: 0,
                    "speed": lambda: 1,
                    "refresh_elem": None,
                    }, outputs=[
                ], _block=("拼多多登录", 23, "通用单图滑块验证"))
            except Exception as exception2:
                exception2 = xbot_visual.trace(exception2)
                pass
            #endtry
            xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("拼多多登录", 26, "等待"))
        #endloop
        if xbot_visual.workflow.test(operand1=lambda: loop_index, operator="==", operand2=验证码重试次数, operator_options="{}", _block=("拼多多登录", 28, "IF 条件")):
            xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("拼多多登录", 29, "等待"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("拼多多-验证码-背景"), _block=("拼多多登录", 30, "IF 元素可见(web)")):
                raise Exception("拼多多登录失败")
            #endif
        #endif
        #endregion
        #region 空间点选验证
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=验证码重试次数, step="1", _block=("拼多多登录", 36, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("拼多多-验证码-空间点选背景"), _block=("拼多多登录", 37, "IF 元素可见(web)")):
                break
            #endif
            xbot_visual.process.run(process="xbot_extensions.activity_jfbym.cs_temu_captcha", package=__name__, inputs={
                "web_page": web_page,
                "engine": "xbot",
                "background_ele": package.selector("拼多多-验证码-空间点选背景"),
                "text_ele": package.selector("拼多多-验证码-空间点选提示文本"),
                "retry_count": lambda: 5,
                "token": "",
                }, outputs=[
            ], _block=("拼多多登录", 40, "定制-Temu 空间物体选择验证"))
            xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("拼多多登录", 41, "等待"))
        #endloop
        if xbot_visual.workflow.test(operand1=lambda: loop_index, operator="==", operand2=验证码重试次数, operator_options="{}", _block=("拼多多登录", 43, "IF 条件")):
            xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("拼多多登录", 44, "等待"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("拼多多-验证码-背景"), _block=("拼多多登录", 45, "IF 元素可见(web)")):
                raise Exception("拼多多登录失败")
            #endif
        #endif
        #endregion
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("拼多多_登录页_账户登录"), _block=("拼多多登录", 50, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("拼多多_登录页_账户登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("拼多多登录", 51, "点击元素(web)"))
        #endif
        # process.invoke_module
        try:
            web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"tab-operate\"]/div/div[2]", is_related_parent=False, parent=None, timeout="3", _block=("拼多多登录", 55, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=web_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("拼多多登录", 56, "点击元素(web)"))
        except Exception as exception:
            exception = xbot_visual.trace(exception)
            pass
        #endtry
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("拼多多登录", 59, "等待"))
        #region 单图滑块
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=验证码重试次数, step="1", _block=("拼多多登录", 61, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("拼多多-验证码-背景"), _block=("拼多多登录", 62, "IF 元素可见(web)")):
                break
            #endif
            try:
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "engine": "",
                    "background_ele": package.selector("拼多多-验证码-背景"),
                    "slider_ele": package.selector("拼多多-验证码-拖拽滑块"),
                    "ym_token": "",
                    "retry_count": lambda: 5,
                    "offset": lambda: 0,
                    "speed": lambda: 1,
                    "refresh_elem": None,
                    }, outputs=[
                ], _block=("拼多多登录", 66, "通用单图滑块验证"))
            except Exception as exception2:
                exception2 = xbot_visual.trace(exception2)
                pass
            #endtry
            # 增加刷新操作
            web_element2 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"captcha-refresh\"]/img", is_related_parent=False, parent=None, timeout="20", _block=("拼多多登录", 70, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=web_element2, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("拼多多登录", 71, "点击元素(web)"))
            xbot_visual.programing.sleep(random_number=False, seconds="4", start_number="1", stop_number="5", _block=("拼多多登录", 72, "等待"))
        #endloop
        if xbot_visual.workflow.test(operand1=lambda: loop_index, operator="==", operand2=验证码重试次数, operator_options="{}", _block=("拼多多登录", 74, "IF 条件")):
            xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("拼多多登录", 75, "等待"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("拼多多-验证码-背景"), _block=("拼多多登录", 76, "IF 元素可见(web)")):
                raise Exception("拼多多登录失败")
            #endif
        #endif
        #endregion
        #region 空间点选验证
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=验证码重试次数, step="1", _block=("拼多多登录", 82, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("拼多多-验证码-空间点选背景"), _block=("拼多多登录", 83, "IF 元素可见(web)")):
                break
            #endif
            xbot_visual.process.run(process="xbot_extensions.activity_jfbym.cs_temu_captcha", package=__name__, inputs={
                "web_page": web_page,
                "engine": "xbot",
                "background_ele": package.selector("拼多多-验证码-空间点选背景"),
                "text_ele": package.selector("拼多多-验证码-空间点选提示文本"),
                "retry_count": lambda: 5,
                "token": "",
                }, outputs=[
            ], _block=("拼多多登录", 86, "定制-Temu 空间物体选择验证"))
            xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("拼多多登录", 87, "等待"))
        #endloop
        if xbot_visual.workflow.test(operand1=lambda: loop_index, operator="==", operand2=验证码重试次数, operator_options="{}", _block=("拼多多登录", 89, "IF 条件")):
            xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("拼多多登录", 90, "等待"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("拼多多-验证码-背景"), _block=("拼多多登录", 91, "IF 元素可见(web)")):
                raise Exception("拼多多登录失败")
            #endif
        #endif
        #endregion
        # 临时修改, 兼容虚拟机剪切板算法异常的bug; bug修复后, 恢复默认
        # web.element.click
        web_page = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_active_by_web_page", params={
            "web_page": web_page,
            "silent_running": True,
        }, _block=("拼多多登录", 98, "调用模块"))
        # clipboard.set_text
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("拼多多_登录页_账号输入框"), _block=("拼多多登录", 100, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("拼多多_登录页_账户登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("拼多多登录", 101, "点击元素(web)"))
        #endif
        xbot_visual.web.element.input(browser=web_page, element=package.selector("拼多多_登录页_账号输入框"), text=账号, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("拼多多登录", 103, "填写输入框(web)"))
        # 检查是否完成输入
        web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("拼多多_登录页_账号输入框"), operation="other", absolute_url=False, attribute_name="value", relative_to="screen", to96dpi=True, timeout="20", _block=("拼多多登录", 105, "获取元素信息(web)"))
        填写次数 = xbot_visual.programing.variable(value=lambda: 0
        , _block=("拼多多登录", 106, "设置变量"))
        while xbot_visual.workflow.test(operand1=web_element_attribute, operator="!=", operand2=账号, operator_options="{}", _block=("拼多多登录", 107, "While条件循环")):
            if xbot_visual.workflow.test(operand1=填写次数, operator=">", operand2="10", operator_options="{}", _block=("拼多多登录", 108, "IF 条件")):
                raise Exception("账号输入失败，请重试指令")
            #endif
            xbot_visual.web.element.input(browser=web_page, element=package.selector("拼多多_登录页_账号输入框"), text=账号, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("拼多多登录", 111, "填写输入框(web)"))
            web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("拼多多_登录页_账号输入框"), operation="other", absolute_url=False, attribute_name="value", relative_to="screen", to96dpi=True, timeout="20", _block=("拼多多登录", 112, "获取元素信息(web)"))
            填写次数 = xbot_visual.programing.variable(value=lambda: 填写次数+1
            , _block=("拼多多登录", 113, "设置变量"))
        #endloop
        xbot_visual.web.element.input(browser=web_page, element=package.selector("拼多多_登录页_密码输入框"), text=密码.strip(), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("拼多多登录", 115, "填写输入框(web)"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("拼多多登录", 116, "等待"))
        xbot_visual.web.element.input(browser=web_page, element=package.selector("拼多多_登录页_密码输入框"), text=密码.strip(), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("拼多多登录", 117, "填写输入框(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("拼多多_登录页_账户登录(新版)"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("拼多多登录", 118, "点击元素(web)"))
        # clipboard.clear
        web_page = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_active_by_web_page", params={
            "web_page": web_page,
            "silent_running": False,
        }, _block=("拼多多登录", 120, "调用模块"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("拼多多_登录页_登录按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="3", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("拼多多登录", 121, "点击元素(web)"))
        # 添加验证码验证
        try:
            #region 单图滑块验证
            for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=验证码重试次数, step="1", _block=("拼多多登录", 125, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("拼多多-验证码-背景"), _block=("拼多多登录", 126, "IF 元素可见(web)")):
                    break
                #endif
                try:
                    xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                        "web_page": web_page,
                        "engine": "",
                        "background_ele": package.selector("拼多多-验证码-背景"),
                        "slider_ele": package.selector("拼多多-验证码-拖拽滑块"),
                        "ym_token": "",
                        "retry_count": lambda: 5,
                        "offset": lambda: 0,
                        "speed": lambda: 1,
                        "refresh_elem": None,
                        }, outputs=[
                    ], _block=("拼多多登录", 130, "通用单图滑块验证"))
                except Exception as exception2:
                    exception2 = xbot_visual.trace(exception2)
                    pass
                #endtry
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("拼多多登录", 133, "等待"))
            #endloop
            if xbot_visual.workflow.test(operand1=lambda: loop_index, operator="==", operand2=验证码重试次数, operator_options="{}", _block=("拼多多登录", 135, "IF 条件")):
                xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("拼多多登录", 136, "等待"))
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("拼多多-验证码-背景"), _block=("拼多多登录", 137, "IF 元素可见(web)")):
                    raise Exception("拼多多登录失败")
                #endif
            #endif
            #endregion
            #region 空间点选验证
            for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=验证码重试次数, step="1", _block=("拼多多登录", 143, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("拼多多-验证码-空间点选背景"), _block=("拼多多登录", 144, "IF 元素可见(web)")):
                    break
                #endif
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.cs_temu_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "engine": "xbot",
                    "background_ele": package.selector("拼多多-验证码-空间点选背景"),
                    "text_ele": package.selector("拼多多-验证码-空间点选提示文本"),
                    "retry_count": lambda: 5,
                    "token": "",
                    }, outputs=[
                ], _block=("拼多多登录", 147, "定制-Temu 空间物体选择验证"))
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("拼多多登录", 148, "等待"))
            #endloop
            if xbot_visual.workflow.test(operand1=lambda: loop_index, operator="==", operand2=验证码重试次数, operator_options="{}", _block=("拼多多登录", 150, "IF 条件")):
                xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("拼多多登录", 151, "等待"))
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("拼多多-验证码-背景"), _block=("拼多多登录", 152, "IF 元素可见(web)")):
                    raise Exception("拼多多登录失败")
                #endif
            #endif
            #endregion
        except Exception as exception4:
            exception4 = xbot_visual.trace(exception4)
            pass
        #endtry
        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("拼多多_登录页_未登录原因"), text="", _block=("拼多多登录", 159, "IF 网页包含")):
            未登录原因_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("拼多多_登录页_未登录原因"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("拼多多登录", 160, "获取元素信息(web)"))
            raise Exception(未登录原因_attribute)
        #endif
        web_url = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_web_url", params={
            "mode": 浏览器类型,
            "load_timeout": lambda: 30,
            "stop_if_timeout": False,
        }, _block=("拼多多登录", 163, "调用模块"))
        if xbot_visual.workflow.test(operand1=web_url, operator="in", operand2="login", operator_options="{\"ignoreCase\":\"False\"}", _block=("拼多多登录", 164, "IF 条件")):
            raise Exception("当前拼多多账号未成功登录，可能原因是需要手机验证。")
        #endif
        网页对象 = xbot_visual.programing.variable(value=lambda: web_page
        , _block=("拼多多登录", 167, "设置变量"))
    finally:
        args["网页对象"] = 网页对象
