import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        邮箱账号 = ""
        邮箱密码 = ""
        图鉴账号 = None
        图鉴密码 = None
        是否退出已登录 = True
    else:
        邮箱账号 = args.get("邮箱账号", "")
        邮箱密码 = args.get("邮箱密码", "")
        图鉴账号 = args.get("图鉴账号", None)
        图鉴密码 = args.get("图鉴密码", None)
        是否退出已登录 = args.get("是否退出已登录", True)
    try:
        登录_web_page = xbot_visual.web.create(web_type="chrome", value="https://business.oceanengine.com/login?appKey=51", silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="stopLoad", chrome_file_name="", edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments="--start-maximized", _block=("巨量引擎登录", 1, "打开网页"))
        # 判断是否已经处于登录状态
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                登录_web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("巨量引擎登录", 3, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("巨量引擎登录", 3,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("巨量引擎登录", 4, "等待"))
        web_page_网页链接 = xbot_visual.web.browser.get_details(browser=登录_web_page, operation="url", _block=("巨量引擎登录", 5, "获取网页信息"))
        #region 已登录进行退出操作
        if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": web_page_网页链接,"operand2": "https://business.oceanengine.com/","operator": "in"}], _block=("巨量引擎登录", 7, "IF 多条件")):
            if xbot_visual.web.browser.element_display(browser=登录_web_page, content_type="display", selector=package.selector("账号界面_账号名称"), _block=("巨量引擎登录", 8, "IF 元素可见(web)")):
                if xbot_visual.workflow.test(operand1=是否退出已登录, operator="is true", operand2="", operator_options="{}", _block=("巨量引擎登录", 9, "IF 条件")):
                    xbot_visual.web.element.click(browser=登录_web_page, element=package.selector("账号界面_账号名称"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎登录", 10, "点击元素(web)"))
                    xbot_visual.web.element.click(browser=登录_web_page, element=package.selector("巨量引擎登录_退出账号按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎登录", 11, "点击元素(web)"))
                    xbot_visual.web.browser.close(operation="close_specified", browser=登录_web_page, web_type="cef", task_kill=False, ignore_beforeunload=False, _block=("巨量引擎登录", 12, "关闭网页"))
                    登录_web_page = xbot_visual.web.create(web_type="chrome", value="https://business.oceanengine.com/login?appKey=51", silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("巨量引擎登录", 13, "打开网页"))
                #endif
            #endif
            try:
                账号界面_账号名称_新 = xbot_visual.web.element.get_element(browser=登录_web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"navigator-user-account-info\"]", is_related_parent=False, parent=None, timeout="3", _block=("巨量引擎登录", 16, "获取元素对象(web)"))
            except Exception as e:
                pass
                账号界面_账号名称_新 = None
            if xbot_visual.workflow.test(operand1=账号界面_账号名称_新, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量引擎登录", 17, "IF 条件")):
                if xbot_visual.workflow.test(operand1=是否退出已登录, operator="is true", operand2="", operator_options="{}", _block=("巨量引擎登录", 18, "IF 条件")):
                    xbot_visual.web.element.click(browser=登录_web_page, element=账号界面_账号名称_新, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎登录", 19, "点击元素(web)"))
                    巨量引擎登录_退出登录按钮_新 = xbot_visual.web.element.get_element(browser=登录_web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//li[normalize-space(.)=\"退出登录\"]", is_related_parent=False, parent=None, timeout="20", _block=("巨量引擎登录", 20, "获取元素对象(web)"))
                    xbot_visual.web.element.click(browser=登录_web_page, element=巨量引擎登录_退出登录按钮_新, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎登录", 21, "点击元素(web)"))
                    xbot_visual.web.browser.close(operation="close_specified", browser=登录_web_page, web_type="cef", task_kill=False, ignore_beforeunload=False, _block=("巨量引擎登录", 22, "关闭网页"))
                    登录_web_page = xbot_visual.web.create(web_type="chrome", value="https://business.oceanengine.com/login?appKey=51", silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("巨量引擎登录", 23, "打开网页"))
                #endif
            #endif
        #endif
        #endregion
        # 切换至邮箱登录
        #region 进入至邮箱登录
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop="30", step="1", _block=("巨量引擎登录", 30, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=登录_web_page, content_type="undisplay", selector=package.selector("巨量引擎登录_邮箱登录"), _block=("巨量引擎登录", 31, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=登录_web_page, element=package.selector("巨量引擎登录_切换登录方式"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎登录", 32, "点击元素(web)"))
            else:
                xbot_visual.web.element.click(browser=登录_web_page, element=package.selector("巨量引擎登录_邮箱登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎登录", 34, "点击元素(web)"))
                break
            #endif
            xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("巨量引擎登录", 37, "等待"))
        #endloop
        #endregion
        # 输入账号密码进行登录
        #region 登录流程
        xbot_visual.web.element.input(browser=登录_web_page, element=package.selector("巨量引擎登录_邮箱输入框"), text=邮箱账号, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎登录", 42, "填写输入框(web)"))
        xbot_visual.web.element.input_password(browser=登录_web_page, element=package.selector("巨量引擎登录_密码输入框"), text=xbot_visual.decrypt(邮箱密码), input_check=False, retry_times="3", simulate=False, save_to_clipboard=True, input_type="clipboard", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", timeout="20", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", _block=("巨量引擎登录", 43, "填写密码框(web)"))
        if xbot_visual.web.browser.contains_element_or_text(browser=登录_web_page, content_type="not_contains_element", selector=package.selector("巨量引擎登录_我已阅读并同意_已勾选状态"), text="", _block=("巨量引擎登录", 44, "IF 网页包含")):
            xbot_visual.web.element.click(browser=登录_web_page, element=package.selector("巨量引擎登录_我已阅读并同意勾选框"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎登录", 45, "点击元素(web)"))
        #endif
        xbot_visual.web.element.click(browser=登录_web_page, element=package.selector("巨量引擎登录_登录按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎登录", 47, "点击元素(web)"))
        #endregion
        # 滑块验证码，尝试7次
        #region 滑块验证
        for loop_index3 in xbot_visual.workflow.range_iterator(start="1", stop="7", step="1", _block=("巨量引擎登录", 51, "For次数循环")):
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    登录_web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="stopLoad", open_page=False, url=None, _block=("巨量引擎登录", 52, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("巨量引擎登录", 52,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
            if xbot_visual.web.browser.contains_element_or_text(browser=登录_web_page, content_type="contains_element", selector=package.selector("巨量引擎登录_滑块验证_拖拽滑块"), text="", _block=("巨量引擎登录", 53, "IF 网页包含")):
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.dy_slider_captcha", package=__name__, inputs={
                    "web_page": 登录_web_page,
                    "engine": "",
                    "background_ele": package.selector("巨量引擎登录_滑块验证_底图"),
                    "slider_ele": package.selector("巨量引擎登录_滑块验证_拖拽滑块"),
                    "refresh_ele": lambda: None,
                    "offset": lambda: 0,
                    "token": "",
                    "retry_count": lambda: 5,
                    }, outputs=[
                ], _block=("巨量引擎登录", 54, "抖音滑块验证"))
                continue
            #endif
            if xbot_visual.web.browser.contains_element_or_text(browser=登录_web_page, content_type="not_contains_element", selector=package.selector("巨量引擎登录_邮箱登录"), text="", _block=("巨量引擎登录", 57, "IF 网页包含")):
                break
            #endif
            xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("巨量引擎登录", 60, "等待"))
        #endloop
        #endregion
        # 选择要进入的工作台
    finally:
        pass
