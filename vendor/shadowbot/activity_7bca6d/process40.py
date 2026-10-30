import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    输出网页对象 = None
    if args is None:
        登录用户名 = ""
        登录密码 = ""
        子平台 = ""
        退出已登录账户 = True
        短信验证码获取接口 = ""
        识别引擎 = ""
        网页对象 = None
    else:
        登录用户名 = args.get("登录用户名", "")
        登录密码 = args.get("登录密码", "")
        子平台 = args.get("子平台", "")
        退出已登录账户 = args.get("退出已登录账户", True)
        短信验证码获取接口 = args.get("短信验证码获取接口", "")
        识别引擎 = args.get("识别引擎", "")
        网页对象 = args.get("网页对象", None)
    try:
        web_page = xbot_visual.programing.variable(value=lambda: None
        , _block=("京准通登录", 1, "设置变量"))
        web_mode = xbot_visual.programing.variable(value="chrome"
        , _block=("京准通登录", 2, "设置变量"))
        if xbot_visual.workflow.test(operand1=网页对象, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("京准通登录", 3, "IF 条件")):
            web_page = xbot_visual.web.create(web_type="chrome", value="https://jzt.jd.com/gw/index", silent_running=False, wait_load_completed=True, load_timeout="120", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("京准通登录", 4, "打开网页"))
        else:
            web_mode = xbot_visual.programing.variable(value=lambda: 网页对象.product_name
            , _block=("京准通登录", 6, "设置变量"))
            web_page = xbot_visual.web.create(web_type=web_mode, value="https://jzt.jd.com/gw/index", silent_running=False, wait_load_completed=True, load_timeout="120", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("京准通登录", 7, "打开网页"))
        #endif
        xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("京准通登录", 9, "等待"))
        for loop_index in xbot_visual.workflow.range_iterator(start="0", stop="3", step="1", _block=("京准通登录", 10, "For次数循环")):
            web_page_url = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("京准通登录", 11, "获取网页信息"))
            if xbot_visual.workflow.test(operand1=web_page_url, operator="in", operand2="https://jzt.jd.com/gw/index", operator_options="{\"ignoreCase\":\"False\"}", _block=("京准通登录", 12, "IF 条件")):
                break
            else:
                web_page = xbot_visual.web.create(web_type=web_mode, value="https://jzt.jd.com/gw/index", silent_running=False, wait_load_completed=True, load_timeout="120", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("京准通登录", 15, "打开网页"))
                xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("京准通登录", 16, "等待"))
            #endif
        #endloop
        # --------已登录状态是否需要退出登录--------
        try:
            立即投放_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//button[contains(string(),'立即投放')]", is_related_parent=False, parent="", timeout="5", _block=("京准通登录", 20, "获取元素对象(web)"))
        except Exception as e:
            pass
            立即投放_元素对象 = None
        if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 立即投放_元素对象,"operand2": "","operator": "not none"},{"operand1": 退出已登录账户,"operand2": "","operator": "is true"}], _block=("京准通登录", 21, "IF 多条件")):
            for loop_index2 in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("京准通登录", 22, "For次数循环")):
                try:
                    xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                        "web_page": web_page,
                        "xpathSelector": "//a[contains(text(),\"退出登录\")]",
                        "获取元素超时": lambda: 5,
                        "执行成功后等待": lambda: 1,
                        "是否模拟人工": False,
                        "按钮": "left",
                        "retry_count": lambda: 1,
                        "refresh": False,
                        "是否为iframe对象": False,
                        }, outputs=[
                    ], _block=("京准通登录", 23, "点击Xpath元素"))
                except Exception as e:
                    pass
                # 校验是否退出登录
                try:
                    check_ele = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//a[contains(text(),\"退出登录\")]", is_related_parent=False, parent=None, timeout="1", _block=("京准通登录", 25, "获取元素对象(web)"))
                except Exception as e:
                    pass
                    check_ele = None
                if xbot_visual.workflow.test(operand1=check_ele, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("京准通登录", 26, "IF 条件")):
                    break
                #endif
            #endloop
        elif xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 立即投放_元素对象,"operand2": "","operator": "not none"},{"operand1": 退出已登录账户,"operand2": "","operator": "is false"}], _block=("京准通登录", 30, "Else IF 多条件")):
            xbot_visual.programing.log(type="info", text="已登录， 退出登录流程", _block=("京准通登录", 31, "打印日志"))
            return
        #endif
        # --------登录操作
        for idx in xbot_visual.workflow.range_iterator(start="1", stop="10", step="1", _block=("京准通登录", 35, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("登录京东账号_登录框"), _block=("京准通登录", 36, "IF 元素可见(web)")):
                break
            #endif
            xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                "web_page": web_page,
                "xpathSelector": "//*[text()=\" 登录 \"]",
                "获取元素超时": lambda: 5,
                "执行成功后等待": lambda: 3,
                "是否模拟人工": False,
                "按钮": "left",
                "retry_count": lambda: 1,
                "refresh": False,
                "是否为iframe对象": False,
                }, outputs=[
            ], _block=("京准通登录", 39, "点击Xpath元素"))
        #endloop
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type=web_mode, mode="activated", value="", use_wildcard=False, silent_running=True, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京准通登录", 41, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("京准通登录", 41,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.element.input(browser=web_page, element=package.selector("京准通登录_账号输入框"), text=登录用户名, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京准通登录", 42, "填写输入框(web)"))
        登录密码 = xbot_visual.decrypt(登录密码)
        xbot_visual.web.element.input(browser=web_page, element=package.selector("京准通登录_密码输入框"), text=登录密码, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京准通登录", 44, "填写输入框(web)"))
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type=web_mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京准通登录", 45, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("京准通登录", 45,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.element.click(browser=web_page, element=package.selector("京准通登录_登录按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京准通登录", 46, "点击元素(web)"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京准通登录", 47, "等待"))
        # --------滑块验证------------重试次数 --- 10
        for idx in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("京准通登录", 49, "For次数循环")):
            xbot_visual.programing.log(type="info", text="滑块验证尝试 >> " + xbot_visual.sh_str(idx), _block=("京准通登录", 50, "打印日志"))
            xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("京准通登录", 51, "等待"))
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type=web_mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京准通登录", 52, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("京准通登录", 52,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("jzt背景元素"), _block=("京准通登录", 53, "IF 元素可见(web)")):
                xbot_visual.programing.log(type="info", text="滑块验证成功", _block=("京准通登录", 54, "打印日志"))
                break
            else:
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "engine": "xbot",
                    "background_ele": package.selector("jzt背景元素"),
                    "slider_ele": package.selector("jzt滑块"),
                    "ym_token": "",
                    "retry_count": lambda: 5,
                    "offset": lambda: 0,
                    "speed": lambda: 1,
                    "refresh_elem": None,
                    }, outputs=[
                ], _block=("京准通登录", 57, "通用单图滑块验证"))
            #endif
        #endloop
        # -------判断是否需要短信验证
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type=web_mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京准通登录", 61, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("京准通登录", 61,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        web_page_url = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("京准通登录", 62, "获取网页信息"))
        if xbot_visual.workflow.test(operand1=web_page_url, operator="==", operand2="https://b.jd.com/", operator_options="{}", _block=("京准通登录", 63, "IF 条件")):
            xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://jzt.jd.com/gw/index", ignore_cache=False, load_timeout="20", _block=("京准通登录", 64, "跳转至新网址"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("京准通-当前登录的账号"), _block=("京准通登录", 65, "IF 元素可见(web)")):
                当前登录的账号 = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("京准通-当前登录的账号"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("京准通登录", 66, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=当前登录的账号, operator="==", operand2=登录用户名, operator_options="{}", _block=("京准通登录", 67, "IF 条件")):
                    xbot_visual.programing.log(type="info", text="登录成功，跳转至目标平台  > " + xbot_visual.sh_str(子平台), _block=("京准通登录", 68, "打印日志"))
                    # -------跳转到目标平台
                    _ = xbot_visual.process.run(process="process41", package=__name__, inputs={
                        "平台名称": 子平台,
                        "web_mode": web_mode,
                        }, outputs=[
                    ], _block=("京准通登录", 70, "调用流程"))
                    return
                else:
                    raise Exception("登录出错，请重试指令")
                #endif
            #endif
        #endif
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("账号名与密码不匹配，请重新输入_1"), _block=("京准通登录", 77, "IF 元素可见(web)")):
            web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("账号名与密码不匹配，请重新输入_1"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("京准通登录", 78, "获取元素信息(web)"))
            raise Exception(web_element_attribute)
        #endif
        try:
            短信验证_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[text()=\"使用 手机短信验证码\"]", is_related_parent=False, parent=None, timeout="5", _block=("京准通登录", 81, "获取元素对象(web)"))
        except Exception as e:
            pass
            短信验证_元素对象 = None
        if xbot_visual.workflow.test(operand1=短信验证_元素对象, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("京准通登录", 82, "IF 条件")):
            # ------是否短信验证
            if xbot_visual.workflow.test(operand1=短信验证码获取接口, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("京准通登录", 84, "IF 条件")):
                raise Exception("需要进行短信验证码，请手动通过！")
            #endif
            xbot_visual.web.element.click(browser=web_page, element=短信验证_元素对象, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京准通登录", 87, "点击元素(web)"))
            # ------todo: 短信接收指令
            # ------todo: 获取验证码
            xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                "web_page": web_page,
                "xpathSelector": "//button[contains(string(), \"获取短信验证\")]",
                "获取元素超时": lambda: 5,
                "执行成功后等待": lambda: 0,
                "是否模拟人工": False,
                "按钮": "left",
                "retry_count": lambda: 1,
                "refresh": False,
                "是否为iframe对象": False,
                }, outputs=[
            ], _block=("京准通登录", 90, "点击Xpath元素"))
            验证码 = xbot_visual.programing.variable(value=""
            , _block=("京准通登录", 91, "设置变量"))
            # ------ 输入验证码
            xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.InputByXpath", package=__name__, inputs={
                "web_page": web_page,
                "xpath": "//input[@placeholder=\"请输入手机验证码\"]",
                "输入内容": 验证码,
                "iframe跨域元素": False,
                "输入方式": "剪切板",
                "追加按键": "{ENTER}",
                "等待元素存在": lambda: 20,
                "操作完成后等待": lambda: 2,
                "追加输入": False,
                }, outputs=[
            ], _block=("京准通登录", 93, "输入内容ByXpath"))
            xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                "web_page": web_page,
                "xpathSelector": "//button[text()=\"提交认证\"]",
                "获取元素超时": lambda: 5,
                "执行成功后等待": lambda: 0,
                "是否模拟人工": True,
                "按钮": "left",
                "retry_count": lambda: 1,
                "refresh": False,
                "是否为iframe对象": False,
                }, outputs=[
            ], _block=("京准通登录", 94, "点击Xpath元素"))
        #endif
        # -------判断是否登录成功
        try:
            立即投放_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//button[contains(string(),'立即投放')]", is_related_parent=False, parent=None, timeout="5", _block=("京准通登录", 97, "获取元素对象(web)"))
        except Exception as e:
            pass
            立即投放_元素对象 = None
        if xbot_visual.workflow.test(operand1=立即投放_元素对象, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("京准通登录", 98, "IF 条件")):
            raise Exception("登录失败，请联系运维人员进行维护。")
        #endif
        xbot_visual.programing.log(type="info", text="登录成功，跳转至目标平台  > " + xbot_visual.sh_str(子平台), _block=("京准通登录", 101, "打印日志"))
        # -------跳转到目标平台
        _ = xbot_visual.process.run(process="process41", package=__name__, inputs={
            "平台名称": 子平台,
            "web_mode": web_mode,
            }, outputs=[
        ], _block=("京准通登录", 103, "调用流程"))
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type=web_mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京准通登录", 104, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("京准通登录", 104,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
    finally:
        args["输出网页对象"] = 输出网页对象
