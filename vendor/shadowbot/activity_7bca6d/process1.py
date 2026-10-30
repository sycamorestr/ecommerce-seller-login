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
        tj_username = ""
        tj_password = ""
        web_type = ""
        status = False
    else:
        username = args.get("username", "")
        password = args.get("password", "")
        tj_username = args.get("tj_username", "")
        tj_password = args.get("tj_password", "")
        web_type = args.get("web_type", "")
        status = args.get("status", False)
    try:
        web_page = xbot_visual.programing.variable(value=lambda: None
        , _block=("巨量登录", 1, "设置变量"))
        if xbot_visual.workflow.test(operand1=web_type, operator="==", operand2="0", operator_options="{}", _block=("巨量登录", 2, "IF 条件")):
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="chrome", mode="url", value="https://business.oceanengine.com/login", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="handleExcept", open_page=True, url="https://business.oceanengine.com/login", _block=("巨量登录", 3, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("巨量登录", 3,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("巨量登录", 4, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("巨量登录", 4,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        else:
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="cef", mode="url", value="https://business.oceanengine.com/login", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="60", stop_load_if_load_timeout="handleExcept", open_page=True, url="https://business.oceanengine.com/login", _block=("巨量登录", 6, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("巨量登录", 6,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="cef", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("巨量登录", 7, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("巨量登录", 7,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        #endif
        # 校验是否要退出登录
        try:
            已登录元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"style_header\")][text()=\"首页\"]", is_related_parent=False, parent=None, timeout="2", _block=("巨量登录", 10, "获取元素对象(web)"))
        except Exception as e:
            pass
            已登录元素 = None
        if xbot_visual.workflow.test(operand1=已登录元素, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量登录", 11, "IF 条件")):
            if xbot_visual.workflow.test(operand1=status, operator="is true", operand2="", operator_options="{}", _block=("巨量登录", 12, "IF 条件")):
                # 退出登录
                头像元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"index_header-user-info\")]", is_related_parent=False, parent=None, timeout="2", _block=("巨量登录", 14, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=web_page, element=头像元素, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="3", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量登录", 15, "点击元素(web)"))
                退出账号按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"index_header-user-card-layout-item\")]//*[text()=\"退出账号\"]", is_related_parent=False, parent=None, timeout="2", _block=("巨量登录", 16, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=web_page, element=退出账号按钮, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量登录", 17, "点击元素(web)"))
            else:
                # 结束
                xbot_visual.programing.log(type="info", text="已登录，不执行重新登录", _block=("巨量登录", 20, "打印日志"))
                return
            #endif
        #endif
        try:
            邮箱输入框 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("巨量引擎_邮箱_输入框"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="5", _block=("巨量登录", 24, "获取元素对象(web)"))
        except Exception as e:
            pass
            邮箱输入框 = None
        if xbot_visual.workflow.test(operand1=邮箱输入框, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量登录", 25, "IF 条件")):
            # 校验是否要退出登录
            try:
                已登录元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"style_header\")][text()=\"首页\"]", is_related_parent=False, parent=None, timeout="2", _block=("巨量登录", 27, "获取元素对象(web)"))
            except Exception as e:
                pass
                已登录元素 = None
            if xbot_visual.workflow.test(operand1=已登录元素, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量登录", 28, "IF 条件")):
                if xbot_visual.workflow.test(operand1=status, operator="is true", operand2="", operator_options="{}", _block=("巨量登录", 29, "IF 条件")):
                    # 退出登录
                    头像元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"index_header-user-info\")]", is_related_parent=False, parent=None, timeout="2", _block=("巨量登录", 31, "获取元素对象(web)"))
                    xbot_visual.web.element.click(browser=web_page, element=头像元素, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="3", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量登录", 32, "点击元素(web)"))
                    退出账号按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"index_header-user-card-layout-item\")]//*[text()=\"退出账号\"]", is_related_parent=False, parent=None, timeout="2", _block=("巨量登录", 33, "获取元素对象(web)"))
                    xbot_visual.web.element.click(browser=web_page, element=退出账号按钮, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量登录", 34, "点击元素(web)"))
                else:
                    # 结束
                    xbot_visual.programing.log(type="info", text="已登录，不执行重新登录", _block=("巨量登录", 37, "打印日志"))
                    return
                #endif
            #endif
        #endif
        try:
            巨量引擎_邮箱登录_按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[text()=\"邮箱登录\"]", is_related_parent=False, parent=None, timeout="3", _block=("巨量登录", 42, "获取元素对象(web)"))
        except Exception as e:
            pass
            巨量引擎_邮箱登录_按钮 = None
        try:
            xbot_visual.web.element.click(browser=web_page, element=巨量引擎_邮箱登录_按钮, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="3", _block=("巨量登录", 43, "点击元素(web)"))
        except Exception as e:
            pass
        xbot_visual.web.element.input(browser=web_page, element=package.selector("巨量引擎_邮箱_输入框"), text=lambda: str(username), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量登录", 44, "填写输入框(web)"))
        password = xbot_visual.decrypt(password)
        xbot_visual.web.element.input(browser=web_page, element=package.selector("巨量引擎_密码_输入框"), text=lambda: str(password), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量登录", 46, "填写输入框(web)"))
        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("巨量引擎_已阅读并同意 服务协议 勾选状态"), text="", _block=("巨量登录", 47, "IF 网页包含")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("巨量引擎_已阅读并同意 服务协议 勾选状态"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量登录", 48, "点击元素(web)"))
        #endif
        xbot_visual.web.element.click(browser=web_page, element=package.selector("巨量引擎_登录_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量登录", 50, "点击元素(web)"))
        # 验证码验证【滑块验证或文字点选验证】
        _ = xbot_visual.process.run(process="process48", package=__name__, inputs={
            "web_page": web_page,
            "验证码失败最大重试次数": "5",
            }, outputs=[
        ], _block=("巨量登录", 52, "调用流程"))
        # web.element.wait
        # programing.variable
        # workflow.infinite_loop
        # web.browser.element_display
        # workflow.break
        # workflow.endif
        # workflow.if
        # workflow.break
        # workflow.endif
        # web.element.get_element
        # web.element.get_element
        # web.element.get_element
        # process.run
        # process.run
        # programing.variable
        # programing.sleep
        # workflow.endloop
    finally:
        args["web_page"] = web_page
