import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    保存网页对象 = None
    if args is None:
        京麦账号 = ""
        京麦密码 = ""
        图鉴账号 = ""
        图鉴密码 = ""
        重试次数 = 5
        识别引擎 = ""
        浏览器类型 = ""
    else:
        京麦账号 = args.get("京麦账号", "")
        京麦密码 = args.get("京麦密码", "")
        图鉴账号 = args.get("图鉴账号", "")
        图鉴密码 = args.get("图鉴密码", "")
        重试次数 = args.get("重试次数", 5)
        识别引擎 = args.get("识别引擎", "")
        浏览器类型 = args.get("浏览器类型", "")
    try:
        保存网页对象 = xbot_visual.programing.variable(value=lambda: None
        , _block=("京麦登录", 1, "设置变量"))
        tj_username = xbot_visual.programing.variable(value=图鉴账号
        , _block=("京麦登录", 2, "设置变量"))
        tj_password = xbot_visual.programing.variable(value=图鉴密码
        , _block=("京麦登录", 3, "设置变量"))
        password = xbot_visual.programing.variable(value=京麦密码
        , _block=("京麦登录", 4, "设置变量"))
        username = xbot_visual.programing.variable(value=lambda: 京麦账号.strip()
        , _block=("京麦登录", 5, "设置变量"))
        password = xbot_visual.decrypt(password)
        tj_password = xbot_visual.decrypt(tj_password)
        login_url = xbot_visual.programing.variable(value="https://passport.shop.jd.com/login/index.action/jdm?ReturnUrl=https%3A%2F%2Fshop.jd.com%2FvcIndex.action"
        , _block=("京麦登录", 7, "设置变量"))
        if xbot_visual.workflow.test(operand1=浏览器类型, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("京麦登录", 8, "IF 条件")):
            浏览器类型 = xbot_visual.programing.variable(value="chrome"
            , _block=("京麦登录", 9, "设置变量"))
        #endif
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                保存网页对象 = xbot_visual.web.get(web_type=浏览器类型, mode="url", value=login_url, use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="handleExcept", open_page=True, url=login_url, _block=("京麦登录", 11, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("京麦登录", 11,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # 如果已经存在登录界面, 且存在弹窗, 会造成登录异常, 刷新网页, 重新加载登录界面
        xbot_visual.programing.sleep(random_number=True, seconds="1", start_number="1", stop_number="2", _block=("京麦登录", 13, "等待"))
        xbot_visual.web.browser.navigate(browser=保存网页对象, mode="reload", url="", ignore_cache=False, load_timeout="20", _block=("京麦登录", 14, "跳转至新网址"))
        # 退出登录
        if xbot_visual.web.browser.element_display(browser=保存网页对象, content_type="display", selector=package.selector("京麦二维码扫码图像"), _block=("京麦登录", 16, "IF 元素可见(web)")):
            try:
                xbot_visual.web.element.click(browser=保存网页对象, element=package.selector("京麦_切换账号密码登陆0706"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="3", _block=("京麦登录", 17, "点击元素(web)"))
            except Exception as e:
                pass
        #endif
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("京麦登录", 19, "For次数循环")):
            xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("京麦登录", 20, "等待"))
            if xbot_visual.web.browser.element_display(browser=保存网页对象, content_type="display", selector=package.selector("京麦账户输入框0706"), _block=("京麦登录", 21, "IF 元素可见(web)")):
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        保存网页对象 = xbot_visual.web.get(web_type=浏览器类型, mode="activated", value="", use_wildcard=False, silent_running=True, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京麦登录", 22, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("京麦登录", 22,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
                xbot_visual.programing.log(type="info", text="开始账号输入", _block=("京麦登录", 23, "打印日志"))
                xbot_visual.web.element.input(browser=保存网页对象, element=package.selector("京麦账户输入框0706"), text=lambda: str(username), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=True, save_to_clipboard=False, input_type="driver", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京麦登录", 24, "填写输入框(web)"))
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        保存网页对象 = xbot_visual.web.get(web_type=浏览器类型, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京麦登录", 25, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("京麦登录", 25,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
                web_element_attribute = xbot_visual.web.element.get_details(browser=保存网页对象, element=package.selector("京麦账户输入框0706"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("京麦登录", 26, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=web_element_attribute, operator="==", operand2=京麦账号.strip(), operator_options="{}", _block=("京麦登录", 27, "IF 条件")):
                    xbot_visual.programing.log(type="info", text="账号输入完成", _block=("京麦登录", 28, "打印日志"))
                    break
                #endif
                if xbot_visual.workflow.test(operand1=loop_index, operator="==", operand2="5", operator_options="{}", _block=("京麦登录", 31, "IF 条件")):
                    raise Exception("账号输入框填写失败")
                #endif
            #endif
        #endloop
        if xbot_visual.web.browser.element_display(browser=保存网页对象, content_type="display", selector=package.selector("京麦密码输入框0706"), _block=("京麦登录", 36, "IF 元素可见(web)")):
            xbot_visual.programing.log(type="info", text="开始密码输入", _block=("京麦登录", 37, "打印日志"))
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    保存网页对象 = xbot_visual.web.get(web_type=浏览器类型, mode="activated", value="", use_wildcard=False, silent_running=True, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京麦登录", 38, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("京麦登录", 38,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
            xbot_visual.web.element.input(browser=保存网页对象, element=package.selector("京麦密码输入框0706"), text=lambda: str(password), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=True, save_to_clipboard=False, input_type="driver", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="custom", sudoku_part="MiddleLeft", offset_x="5", offset_y="0", timeout="20", _block=("京麦登录", 39, "填写输入框(web)"))
            xbot_visual.programing.log(type="info", text="密码输入完成", _block=("京麦登录", 40, "打印日志"))
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    保存网页对象 = xbot_visual.web.get(web_type=浏览器类型, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京麦登录", 41, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("京麦登录", 41,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        #endif
        if xbot_visual.web.browser.element_display(browser=保存网页对象, content_type="display", selector=package.selector("京麦登录按钮0706"), _block=("京麦登录", 43, "IF 元素可见(web)")):
            xbot_visual.programing.log(type="info", text="点击登录按钮", _block=("京麦登录", 44, "打印日志"))
            xbot_visual.web.element.click(browser=保存网页对象, element=package.selector("京麦登录按钮0706"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京麦登录", 45, "点击元素(web)"))
        #endif
        xbot_visual.programing.sleep(random_number=False, seconds="5", start_number="1", stop_number="5", _block=("京麦登录", 47, "等待"))
        # 用户判断网页是否处于加载过程中
        try:
            web_wait_result = xbot_visual.web.element.wait(browser=保存网页对象, element=package.selector("京麦验证码滑块0706"), state="appear", iswait=True, timeout="5", _block=("京麦登录", 49, "等待元素(web)"))
        except Exception as e:
            xbot_visual.programing.log(type='info',text=e,_block=("京麦登录", 49,"等待元素(web)"))
            web_wait_result = False
        # 等待滑块超时, 应抛出异常, 且滑块内容不可以见, 包含渲染dom, 但是未完全加载出来的场景
        xbot_visual.programing.log(type="info", text=web_wait_result, _block=("京麦登录", 51, "打印日志"))
        if xbot_visual.workflow.test(operand1=web_wait_result, operator="is false", operand2="", operator_options="{}", _block=("京麦登录", 52, "IF 条件")):
            # 企业账号跳转网页略有不同
            web_page_attribute = xbot_visual.web.browser.get_details(browser=保存网页对象, operation="url", _block=("京麦登录", 54, "获取网页信息"))
            if xbot_visual.workflow.test(operand1=web_page_attribute, operator="!=", operand2=login_url, operator_options="{}", _block=("京麦登录", 55, "IF 条件")):
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("京麦登录", 56, "等待"))
                xbot_visual.programing.log(type="info", text="登录成功", _block=("京麦登录", 57, "打印日志"))
                return
            #endif
        else:
            web_page_url = xbot_visual.web.browser.get_details(browser=保存网页对象, operation="url", _block=("京麦登录", 61, "获取网页信息"))
            for loop_index in xbot_visual.workflow.range_iterator(start="1", stop=重试次数, step="1", _block=("京麦登录", 62, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=保存网页对象, content_type="display", selector=package.selector("京麦验证码滑块0706"), _block=("京麦登录", 63, "IF 元素可见(web)")):
                    try:
                        _xbot_retry_time = 0
                        while _xbot_retry_time <= 3:
                            try:
                                web_page = xbot_visual.web.get(web_type=浏览器类型, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("京麦登录", 65, "获取已打开的网页对象"))
                                _xbot_retry_time = 5
                            except Exception as e:
                                if _xbot_retry_time == 3:
                                    raise e
                                else:
                                    xbot_visual.programing.log(type='info',text=e,_block=("京麦登录", 65,"获取已打开的网页对象"))
                                _xbot_retry_time += 1
                                time.sleep(3)
                        xbot_visual.process.run(process="xbot_extensions.activity_jfbym.std_slider_captcha", package=__name__, inputs={
                            "web_page": web_page,
                            "engine": "xbot",
                            "background_ele": package.selector("京麦验证码背景图0706"),
                            "slider_ele": package.selector("京麦验证码滑动按钮0706"),
                            "ym_token": "",
                            "retry_count": lambda: 5,
                            "offset": lambda: 0,
                            "speed": lambda: 1,
                            "refresh_elem": None,
                            }, outputs=[
                        ], _block=("京麦登录", 66, "通用单图滑块验证"))
                    except Exception as exception:
                        exception = xbot_visual.trace(exception)
                        xbot_visual.web.element.click(browser=保存网页对象, element=package.selector("京麦登录_刷新元素"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("京麦登录", 68, "点击元素(web)"))
                    #endtry
                    # web.element.get_element
                    # web.element.get_element
                    # web.element.get_element
                    # process.run
                    # programing.comment
                    # web.element.get_bounding
                    # process.invoke_module
                    # programing.sleep
                #endif
            #endloop
        #endif
        if xbot_visual.web.browser.element_display(browser=保存网页对象, content_type="display", selector=package.selector("京麦登录失败后的标注"), _block=("京麦登录", 81, "IF 元素可见(web)")):
            raise Exception("账户密码错误")
        #endif
        if xbot_visual.web.browser.element_display(browser=保存网页对象, content_type="display", selector=package.selector("账号名与密码不匹配，请重新输入"), _block=("京麦登录", 84, "IF 元素可见(web)")):
            raise Exception("账户密码错误")
        #endif
        if xbot_visual.workflow.test(operand1=lambda: loop_index, operator="==", operand2=lambda: 重试次数, operator_options="{}", _block=("京麦登录", 87, "IF 条件")):
            xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("京麦登录", 88, "等待"))
            if xbot_visual.web.browser.element_display(browser=保存网页对象, content_type="display", selector=package.selector("京麦验证码滑块"), _block=("京麦登录", 89, "IF 元素可见(web)")):
                raise Exception("登录失败")
            #endif
            if xbot_visual.web.browser.element_display(browser=保存网页对象, content_type="display", selector=package.selector("京麦验证码滑块0706"), _block=("京麦登录", 92, "IF 元素可见(web)")):
                raise Exception("登录失败")
            #endif
        #endif
        # 判断是否登录成功
        web_page_attribute2 = xbot_visual.web.browser.get_details(browser=保存网页对象, operation="url", _block=("京麦登录", 97, "获取网页信息"))
        if xbot_visual.workflow.test(operand1=web_page_attribute2, operator="in", operand2="https://passport.shop.jd.com/login/index.action/jdm", operator_options="{\"ignoreCase\":\"False\"}", _block=("京麦登录", 98, "IF 条件")):
            # programing.raise
            xbot_visual.web.browser.navigate(browser=保存网页对象, mode="url", url="https://shop.jd.com/jdm/home", ignore_cache=False, load_timeout="20", _block=("京麦登录", 100, "跳转至新网址"))
        elif xbot_visual.workflow.test(operand1=web_page_attribute2, operator="not in", operand2="shop.jd.com/jdm/home", operator_options="{\"ignoreCase\":\"True\"}", _block=("京麦登录", 101, "Else IF")):
            xbot_visual.web.browser.navigate(browser=保存网页对象, mode="url", url="https://shop.jd.com/jdm/home", ignore_cache=False, load_timeout="20", _block=("京麦登录", 102, "跳转至新网址"))
        #endif
    finally:
        args["保存网页对象"] = 保存网页对象
