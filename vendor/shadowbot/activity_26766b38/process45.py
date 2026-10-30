import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    网页对象 = None
    if args is None:
        账号 = ""
        密码 = ""
        web_page = None
    else:
        账号 = args.get("账号", "")
        密码 = args.get("密码", "")
        web_page = args.get("web_page", None)
    try:
        网页对象类型 = xbot_visual.programing.variable(value=lambda: 'chrome'
        , _block=("生意参谋登录", 1, "设置变量"))
        if xbot_visual.workflow.test(operand1=web_page, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("生意参谋登录", 2, "IF 条件")):
            网页对象类型 = xbot_visual.programing.variable(value=lambda: web_page.product_name
            , _block=("生意参谋登录", 3, "设置变量"))
            xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/custom/login.htm", ignore_cache=False, load_timeout="20", _block=("生意参谋登录", 4, "跳转至新网址"))
        else:
            web_page = xbot_visual.web.create(web_type=网页对象类型, value="https://sycm.taobao.com/custom/login.htm", silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("生意参谋登录", 6, "打开网页"))
        #endif
        #region 已登录状态检测
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("登录页_已登录提示文本"), _block=("生意参谋登录", 9, "IF 元素可见(web)")):
            # 监测到已登录的状态, 直接跳转生意参谋首页
            xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/portal/home.htm", ignore_cache=False, load_timeout="60", _block=("生意参谋登录", 11, "跳转至新网址"))
            web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("生意参谋-首页-首页标题框元素"), state="appear", iswait=True, timeout="20", _block=("生意参谋登录", 12, "等待元素(web)"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("生意参谋-首页-首页标题框元素"), _block=("生意参谋登录", 13, "IF 元素可见(web)")):
                xbot_visual.programing.log(type="info", text="生意参谋登录成功", _block=("生意参谋登录", 14, "打印日志"))
                return
            #endif
        #endif
        #endregion
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type=网页对象类型, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("生意参谋登录", 19, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("生意参谋登录", 19,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        #region 账号密码输入
        xbot_visual.web.element.hover(browser=web_page, element=package.selector("登录页_账号输入框"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("生意参谋登录", 21, "鼠标悬停在元素上(web)"))
        # web.get
        try:
            xbot_visual.web.element.input(browser=web_page, element=package.selector("登录页_账号输入框"), text=账号, append=False, input_check=True, check_value=账号, retry_times="0", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("生意参谋登录", 24, "填写输入框(web)"))
        except Exception as exception:
            exception = xbot_visual.trace(exception)
            xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/custom/login.htm", ignore_cache=False, load_timeout="60", _block=("生意参谋登录", 26, "跳转至新网址"))
            xbot_visual.web.element.input(browser=web_page, element=package.selector("登录页_账号输入框"), text=账号, append=False, input_check=True, check_value=账号, retry_times="0", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("生意参谋登录", 27, "填写输入框(web)"))
        #endtry
        xbot_visual.web.element.click(browser=web_page, element=package.selector("登录页_密码输入框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("生意参谋登录", 29, "点击元素(web)"))
        xbot_visual.web.element.input(browser=web_page, element=package.selector("登录页_密码输入框"), text=密码, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=False, anchor_type="center", sudoku_part="middleCenter", offset_x="0", offset_y="0", timeout="20", _block=("生意参谋登录", 30, "填写输入框(web)"))
        # web.get
        #endregion
        for loop_index2 in xbot_visual.workflow.range_iterator(start="1", stop="3", step="1", _block=("生意参谋登录", 33, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("登录页面_滑块验证_div"), _block=("生意参谋登录", 34, "IF 元素可见(web)")):
                xbot_visual.web.element.hover(browser=web_page, element=package.selector("登录页面_滑块验证_div"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("生意参谋登录", 35, "鼠标悬停在元素上(web)"))
                xbot_visual.web.element.click(browser=web_page, element=package.selector("登录页面_滑块验证_div"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("生意参谋登录", 36, "点击元素(web)"))
                back_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("登录页面_滑块验证_div"), operation="bound", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("生意参谋登录", 37, "获取元素信息(web)"))
                front_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("登录页面_滑块_滑动div"), operation="bound", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("生意参谋登录", 38, "获取元素信息(web)"))
                xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process11", package=__name__, inputs={
                    "web_page": web_page,
                    "drag_start_element": package.selector("登录页面_滑块_滑动div"),
                    "background_element": package.selector("登录页面_滑块验证_div"),
                    }, outputs=[
                ], _block=("生意参谋登录", 39, "滑块拖动"))
                # TODO：输入密码后验证码重试，点击错误标识
                # web.browser.element_display
                # web.element.click
                # workflow.endif
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("生意参谋登录", 44, "等待"))
            #endif
        #endloop
        #region 登录
        xbot_visual.web.element.click(browser=web_page, element=package.selector("登录页_登录按钮"), simulate=True, move_mouse=True, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("生意参谋登录", 48, "点击元素(web)"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("生意参谋登录", 49, "等待"))
        #endregion
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("生意参谋登录", 51, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("登录页面_滑块验证_div"), _block=("生意参谋登录", 52, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("登录页面_滑块验证_div"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("生意参谋登录", 53, "点击元素(web)"))
                xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process11", package=__name__, inputs={
                    "web_page": web_page,
                    "drag_start_element": package.selector("登录页面_滑块_滑动div"),
                    "background_element": package.selector("登录页面_滑块验证_div"),
                    }, outputs=[
                ], _block=("生意参谋登录", 54, "滑块拖动"))
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("err_mark"), _block=("生意参谋登录", 55, "IF 元素可见(web)")):
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("err_handle"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("生意参谋登录", 56, "点击元素(web)"))
                #endif
            #endif
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("登录页面_阿里滑块"), _block=("生意参谋登录", 59, "IF 元素可见(web)")):
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.ali_slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "engine": "xbot",
                    "drag_ele": package.selector("登录页面_滑块元素"),
                    "refresh_ele": package.selector("登录页面_刷新元素"),
                    "ym_token": "",
                    "retry_count": lambda: 3,
                    "offset": lambda: 0,
                    "speed": "middle",
                    "monitor_time": lambda: 3,
                    "background_ele": lambda: None,
                    }, outputs=[
                ], _block=("生意参谋登录", 60, "阿里滑块验证"))
            #endif
        #endloop
        xbot_visual.web.browser.wait_load_completed(browser=web_page, load_timeout="20", action_after_load_timeout="handleExcept", _block=("生意参谋登录", 63, "等待网页加载完成"))
        #region 登录异常监测
        try:
            web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("登录-安全产品-标志"), state="appear", iswait=True, timeout="3", _block=("生意参谋登录", 65, "等待元素(web)"))
        except Exception as e:
            xbot_visual.programing.log(type='info',text=e,_block=("生意参谋登录", 65,"等待元素(web)"))
            web_wait_result2 = None
        if xbot_visual.workflow.test(operand1=web_wait_result2, operator="is true", operand2="", operator_options="{}", _block=("生意参谋登录", 66, "IF 条件")):
            try:
                web_wait_result_check = xbot_visual.web.element.wait(browser=web_page, element=package.selector("登录-安全产品-标志"), state="disappear", iswait=True, timeout="20", _block=("生意参谋登录", 67, "等待元素(web)"))
            except Exception as e:
                xbot_visual.programing.log(type='info',text=e,_block=("生意参谋登录", 67,"等待元素(web)"))
                web_wait_result_check = None
        #endif
        #region 账户/密码不正确检测
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("登录页_账户名或密码不正确提示"), _block=("生意参谋登录", 70, "IF 元素可见(web)")):
            raise Exception("生意参谋登录出错 : 登录账号或者密码不正确")
        #endif
        #endregion
        #endregion
        #region 登录成功检测
        web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("生意参谋-首页-首页标题框元素"), state="appear", iswait=True, timeout="20", _block=("生意参谋登录", 76, "等待元素(web)"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("生意参谋-首页-首页标题框元素"), _block=("生意参谋登录", 77, "IF 元素可见(web)")):
            xbot_visual.programing.log(type="info", text="生意参谋登录成功", _block=("生意参谋登录", 78, "打印日志"))
            网页对象 = xbot_visual.programing.variable(value=web_page
            , _block=("生意参谋登录", 79, "设置变量"))
            return
        #endif
        # 可能没有首页标签
        try:
            退出元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//span[@type=\"quitBold\"]", is_related_parent=False, parent=None, timeout="5", _block=("生意参谋登录", 83, "获取元素对象(web)"))
        except Exception as e:
            pass
            退出元素 = None
        if xbot_visual.workflow.test(operand1=退出元素, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("生意参谋登录", 84, "IF 条件")):
            xbot_visual.programing.log(type="info", text="生意参谋登录成功", _block=("生意参谋登录", 85, "打印日志"))
            网页对象 = xbot_visual.programing.variable(value=web_page
            , _block=("生意参谋登录", 86, "设置变量"))
            return
        #endif
        web_page_attribute = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("生意参谋登录", 89, "获取网页信息"))
        if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": web_page_attribute,"operand2": "https://sycm.taobao.com/portal/home.htm","operator": "in"},{"operand1": web_page_attribute,"operand2": "login","operator": "not in"}], _block=("生意参谋登录", 90, "IF 多条件")):
            xbot_visual.programing.log(type="info", text="生意参谋登录成功", _block=("生意参谋登录", 91, "打印日志"))
            网页对象 = xbot_visual.programing.variable(value=web_page
            , _block=("生意参谋登录", 92, "设置变量"))
            return
        #endif
        #endregion
        raise Exception("生意参谋登录出错 : 请人工介入处理 ~~")
    finally:
        args["网页对象"] = 网页对象
