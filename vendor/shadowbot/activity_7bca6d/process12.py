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
    else:
        username = args.get("username", "")
        password = args.get("password", "")
        tj_username = args.get("tj_username", "")
        tj_password = args.get("tj_password", "")
        web_type = args.get("web_type", "")
    try:
        browser_type = xbot_visual.programing.variable(value=web_type
        , _block=("巨量纵横登录", 1, "设置变量"))
        process_result = xbot_visual.process.run(process="process36", package=__name__, inputs={
            "browser_type": browser_type,
            }, outputs=[
            "有打开的网页",
            "当前是登录页",
        ], _block=("巨量纵横登录", 2, "调用流程"))
        # 开始登录
        登录页url = xbot_visual.programing.variable(value="https://business.oceanengine.com/login?appKey=51"
        , _block=("巨量纵横登录", 4, "设置变量"))
        web_page = xbot_visual.programing.variable(value=lambda: None
        , _block=("巨量纵横登录", 5, "设置变量"))
        if xbot_visual.workflow.test(operand1=process_result.有打开的网页, operator="is false", operand2="", operator_options="{}", _block=("巨量纵横登录", 6, "IF 条件")):
            web_page = xbot_visual.process.invoke_module(module="utils_douyin", package=__name__, function="open_webpage", params={
                "url": 登录页url,
                "browser_type": browser_type,
                "load_timeout": "20",
                "stop_if_timeout": False,
            }, _block=("巨量纵横登录", 7, "调用模块"))
        else:
            web_page = xbot_visual.process.invoke_module(module="utils_douyin", package=__name__, function="get_webpage", params={
                "browser_type": browser_type,
                "match_type": "3",
                "title": "",
                "url": "",
                "use_wildcard": "",
            }, _block=("巨量纵横登录", 9, "调用模块"))
            url = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("巨量纵横登录", 10, "获取网页信息"))
            if xbot_visual.workflow.test(operand1=url, operator="not in", operand2=登录页url, operator_options="{\"ignoreCase\":\"True\"}", _block=("巨量纵横登录", 11, "IF 条件")):
                web_page = xbot_visual.process.invoke_module(module="utils_douyin", package=__name__, function="open_webpage", params={
                    "url": 登录页url,
                    "browser_type": browser_type,
                    "load_timeout": "20",
                    "stop_if_timeout": False,
                }, _block=("巨量纵横登录", 12, "调用模块"))
            #endif
        #endif
        # programing.comment
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("巨量纵横登录", 16, "等待"))
        # ------新旧版选择检查
        try:
            check_t_flag = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//span[contains(@class, \"typography\")][text()=\"请选择工作台版本\"]", is_related_parent=False, parent=None, timeout="3", _block=("巨量纵横登录", 18, "获取元素对象(web)"))
        except Exception as e:
            pass
            check_t_flag = None
        if xbot_visual.workflow.test(operand1=check_t_flag, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量纵横登录", 19, "IF 条件")):
            点击进入元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"card-body\"][.//span[normalize-space(.)=\"旧版巨量引擎工作台\"]]//button", is_related_parent=False, parent=None, timeout="20", _block=("巨量纵横登录", 20, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=点击进入元素, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量纵横登录", 21, "点击元素(web)"))
        #endif
        # 执行登录
        try:
            xbot_visual.web.element.click(browser=web_page, element=package.selector("巨量纵横_切换账号"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量纵横登录", 24, "点击元素(web)"))
        except Exception as e:
            pass
        xbot_visual.web.element.input(browser=web_page, element=package.selector("巨量纵横_账号_输入框"), text=lambda: str(username), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量纵横登录", 25, "填写输入框(web)"))
        password = xbot_visual.decrypt(password)
        xbot_visual.web.element.input(browser=web_page, element=package.selector("巨量纵横_密码_输入框"), text=lambda: str(password), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量纵横登录", 27, "填写输入框(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("巨量纵横_同意协议"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0.3", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量纵横登录", 28, "点击元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("纵横按钮_登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量纵横登录", 29, "点击元素(web)"))
        # ------新旧版选择检查
        try:
            check_t_flag = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//span[contains(@class, \"typography\")][text()=\"请选择工作台版本\"]", is_related_parent=False, parent=None, timeout="3", _block=("巨量纵横登录", 31, "获取元素对象(web)"))
        except Exception as e:
            pass
            check_t_flag = None
        if xbot_visual.workflow.test(operand1=check_t_flag, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量纵横登录", 32, "IF 条件")):
            点击进入元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"card-body\"][.//span[normalize-space(.)=\"旧版巨量引擎工作台\"]]//button", is_related_parent=False, parent=None, timeout="20", _block=("巨量纵横登录", 33, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=点击进入元素, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量纵横登录", 34, "点击元素(web)"))
        #endif
        # 验证码验证【滑块验证或文字点选验证】
        _ = xbot_visual.process.run(process="process48", package=__name__, inputs={
            "web_page": web_page,
            "验证码失败最大重试次数": "5",
            }, outputs=[
        ], _block=("巨量纵横登录", 37, "调用流程"))
        # ------新旧版选择检查
        try:
            check_t_flag = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//span[contains(@class, \"typography\")][text()=\"请选择工作台版本\"]", is_related_parent=False, parent=None, timeout="3", _block=("巨量纵横登录", 39, "获取元素对象(web)"))
        except Exception as e:
            pass
            check_t_flag = None
        if xbot_visual.workflow.test(operand1=check_t_flag, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量纵横登录", 40, "IF 条件")):
            点击进入元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"card-body\"][.//span[normalize-space(.)=\"旧版巨量引擎工作台\"]]//button", is_related_parent=False, parent=None, timeout="20", _block=("巨量纵横登录", 41, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=点击进入元素, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量纵横登录", 42, "点击元素(web)"))
        #endif
        # web.element.wait
        # workflow.if
        # process.return
        # workflow.endif
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
