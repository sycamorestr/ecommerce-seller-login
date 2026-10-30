import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    web_page = None
    if args is None:
        账户 = ""
        密码 = ""
        短信验证码接口 = ""
        退出已登录账户 = False
        浏览器类型 = ""
    else:
        账户 = args.get("账户", "")
        密码 = args.get("密码", "")
        短信验证码接口 = args.get("短信验证码接口", "")
        退出已登录账户 = args.get("退出已登录账户", False)
        浏览器类型 = args.get("浏览器类型", "")
    try:
        if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 账户,"operand2": "","operator": "is empty"},{"operand1": 密码,"operand2": "","operator": "is empty"}], _block=("阿里妈妈数智登录", 1, "IF 多条件")):
            raise Exception("账户或密码为空，请检查~")
            return
        #endif
        if xbot_visual.workflow.test(operand1=浏览器类型, operator="==", operand2="chrome", operator_options="{}", _block=("阿里妈妈数智登录", 5, "IF 条件")):
            web_page = xbot_visual.web.create(web_type="chrome", value="https://www.alimama.com/index.htm", silent_running=False, wait_load_completed=True, load_timeout="120", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("阿里妈妈数智登录", 6, "打开网页"))
        elif xbot_visual.workflow.test(operand1=浏览器类型, operator="==", operand2="edge", operator_options="{}", _block=("阿里妈妈数智登录", 7, "Else IF")):
            web_page = xbot_visual.web.create(web_type="edge", value="https://www.alimama.com/index.htm", silent_running=False, wait_load_completed=True, load_timeout="120", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("阿里妈妈数智登录", 8, "打开网页"))
        #endif
        # ------检查登录状态，是否已登录
        xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("阿里妈妈数智登录", 11, "等待"))
        try:
            退出_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@id=\"app\"]//*[text()=\"退出\"]", is_related_parent=False, parent=None, timeout="3", _block=("阿里妈妈数智登录", 12, "获取元素对象(web)"))
        except Exception as e:
            pass
            退出_元素对象 = None
        if xbot_visual.workflow.test(operand1=退出_元素对象, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("阿里妈妈数智登录", 13, "IF 条件")):
            if xbot_visual.workflow.test(operand1=退出已登录账户, operator="is true", operand2="", operator_options="{}", _block=("阿里妈妈数智登录", 14, "IF 条件")):
                xbot_visual.web.element.click(browser=web_page, element=退出_元素对象, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="3", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("阿里妈妈数智登录", 15, "点击元素(web)"))
                xbot_visual.web.browser.navigate(browser=web_page, mode="reload", url="", ignore_cache=True, load_timeout="120", _block=("阿里妈妈数智登录", 16, "跳转至新网址"))
            else:
                xbot_visual.programing.log(type="info", text="账户已登录！", _block=("阿里妈妈数智登录", 18, "打印日志"))
                return
            #endif
        #endif
        # ------是否退出已登录账户
        xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
            "web_page": web_page,
            "xpathSelector": "//div[normalize-space(text())=\"立即登录\"]",
            "获取元素超时": lambda: 5,
            "执行成功后等待": lambda: 2,
            "是否模拟人工": False,
            "按钮": "left",
            "retry_count": lambda: 1,
            "refresh": False,
            "是否为iframe对象": False,
            }, outputs=[
        ], _block=("阿里妈妈数智登录", 23, "点击Xpath元素"))
        登录iframe窗口 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//iframe[contains(@src, \"login.taobao.com\")]", is_related_parent=False, parent=None, timeout="20", _block=("阿里妈妈数智登录", 24, "获取元素对象(web)"))
        登录地址 = xbot_visual.web.element.get_details(browser=web_page, element=登录iframe窗口, operation="other", absolute_url=False, attribute_name="src", relative_to="screen", to96dpi=True, timeout="20", _block=("阿里妈妈数智登录", 25, "获取元素信息(web)"))
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url=登录地址, ignore_cache=False, load_timeout="120", _block=("阿里妈妈数智登录", 26, "跳转至新网址"))
        # xbot_extensions.activity_fe2a1069.InputByXpath
        账号输入框 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@id=\"fm-login-id\"]", is_related_parent=False, parent=None, timeout="20", _block=("阿里妈妈数智登录", 28, "获取元素对象(web)"))
        xbot_visual.web.element.input(browser=web_page, element=账号输入框, text=账户, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="random", sudoku_part="Random", offset_x="0", offset_y="0", timeout="20", _block=("阿里妈妈数智登录", 29, "填写输入框(web)"))
        # 账户输入完成后平台会进行账户检查，风险校验，如果环境安全则直接免密进入，否则就是各种验证码
        try:
            退出_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@id=\"header-info\"]//*[text()=\"退出\"]", is_related_parent=False, parent="", timeout="5", _block=("阿里妈妈数智登录", 31, "获取元素对象(web)"))
        except Exception as e:
            pass
            退出_元素对象 = None
        if xbot_visual.workflow.test(operand1=退出_元素对象, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("阿里妈妈数智登录", 32, "IF 条件")):
            xbot_visual.programing.log(type="info", text="自动登录成功.", _block=("阿里妈妈数智登录", 33, "打印日志"))
            return
        #endif
        密码输入框 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@id=\"fm-login-password\"]", is_related_parent=False, parent=None, timeout="20", _block=("阿里妈妈数智登录", 36, "获取元素对象(web)"))
        密码 = xbot_visual.decrypt(密码)
        xbot_visual.web.element.input(browser=web_page, element=密码输入框, text=密码, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="random", sudoku_part="Random", offset_x="0", offset_y="0", timeout="20", _block=("阿里妈妈数智登录", 38, "填写输入框(web)"))
        # xbot_extensions.activity_fe2a1069.InputByXpath
        xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
            "web_page": web_page,
            "xpathSelector": "//button[text()=\"登录\"]",
            "获取元素超时": lambda: 5,
            "执行成功后等待": lambda: 3,
            "是否模拟人工": True,
            "按钮": "left",
            "retry_count": lambda: 1,
            "refresh": False,
            "是否为iframe对象": False,
            }, outputs=[
        ], _block=("阿里妈妈数智登录", 40, "点击Xpath元素"))
        # 可能存在 >>> 滑块验证，短信验证
        try:
            iframe_滑块_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//iframe[@id=\"baxia-dialog-content\"]", is_related_parent=False, parent="", timeout="3", _block=("阿里妈妈数智登录", 42, "获取元素对象(web)"))
        except Exception as e:
            pass
            iframe_滑块_元素对象 = None
        if xbot_visual.workflow.test(operand1=iframe_滑块_元素对象, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("阿里妈妈数智登录", 43, "IF 条件")):
            xbot_visual.web.element.hover(browser=web_page, element=iframe_滑块_元素对象, simulate=True, delay_after="1", anchor_type="custom", sudoku_part="MiddleLeft", offset_x="0", offset_y="0", timeout="20", _block=("阿里妈妈数智登录", 44, "鼠标悬停在元素上(web)"))
            xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="down", hardware_driver_click=False, keys="null", delay_after="1", _block=("阿里妈妈数智登录", 45, "鼠标点击"))
            xbot_visual.win32.move_mouse(point_x="10", point_y="10", relative_to="currentmouseposition", move_speed="middle", delay_after="1", _block=("阿里妈妈数智登录", 46, "移动鼠标"))
            xbot_visual.win32.move_mouse(point_x="320", point_y="-20", relative_to="currentmouseposition", move_speed="slow", delay_after="3", _block=("阿里妈妈数智登录", 47, "移动鼠标"))
            xbot_visual.win32.click_mouse(is_move_mouse_before_click=False, point_x="0", point_y="0", relative_to="screen", move_speed="middle", button="left", click_type="up", hardware_driver_click=False, keys="null", delay_after="1", _block=("阿里妈妈数智登录", 48, "鼠标点击"))
            try:
                xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                    "web_page": web_page,
                    "xpathSelector": "//button[text()=\"登录\"]",
                    "获取元素超时": lambda: 5,
                    "执行成功后等待": lambda: 3,
                    "是否模拟人工": False,
                    "按钮": "left",
                    "retry_count": lambda: 1,
                    "refresh": False,
                    "是否为iframe对象": False,
                    }, outputs=[
                ], _block=("阿里妈妈数智登录", 49, "点击Xpath元素"))
            except Exception as e:
                pass
        #endif
        # -----------短信验证
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("点击获取验证码_元素对象"), _block=("阿里妈妈数智登录", 52, "IF 元素可见(web)")):
            if xbot_visual.workflow.test(operand1=短信验证码接口, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("阿里妈妈数智登录", 53, "IF 条件")):
                raise Exception("需要进行短信验证！")
            #endif
            # --------------todo: 接口短信验证
            xbot_visual.web.element.click(browser=web_page, element=package.selector("点击获取验证码_元素对象"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("阿里妈妈数智登录", 57, "点击元素(web)"))
        #endif
    finally:
        args["web_page"] = web_page
