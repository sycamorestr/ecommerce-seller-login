import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    web_page = None
    if args is None:
        网页对象 = None
        username = ""
        password = ""
        tj_username = ""
        tj_password = ""
        登录的店铺名称 = ""
        是否要退出已登录账号 = False
        wait_time = ""
    else:
        网页对象 = args.get("网页对象", None)
        username = args.get("username", "")
        password = args.get("password", "")
        tj_username = args.get("tj_username", "")
        tj_password = args.get("tj_password", "")
        登录的店铺名称 = args.get("登录的店铺名称", "")
        是否要退出已登录账号 = args.get("是否要退出已登录账号", False)
        wait_time = args.get("wait_time", "")
    try:
        # 2023/04/13 星辰修复除验证码外所有元素
        if xbot_visual.workflow.test(operand1=wait_time, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("电商罗盘登录", 2, "IF 条件")):
            wait_time = xbot_visual.programing.variable(value="3"
            , _block=("电商罗盘登录", 3, "设置变量"))
        #endif
        wait_time = xbot_visual.programing.variable(value=lambda: int(wait_time)
        , _block=("电商罗盘登录", 5, "设置变量"))
        web_page = xbot_visual.programing.variable(value=lambda: 网页对象
        , _block=("电商罗盘登录", 6, "设置变量"))
        if xbot_visual.workflow.test(operand1=web_page, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("电商罗盘登录", 7, "IF 条件")):
            web_page = xbot_visual.web.create(web_type="chrome", value="https://compass.jinritemai.com/login", silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("电商罗盘登录", 8, "打开网页"))
        #endif
        loading_element_xpath = xbot_visual.programing.variable(value="//span[contains(@class, \"dot-spin\")]"
        , _block=("电商罗盘登录", 10, "设置变量"))
        if xbot_visual.workflow.test(operand1=web_page.get_url(), operator="not in", operand2="compass.jinritemai.com/shop", operator_options="{\"ignoreCase\":\"False\"}", _block=("电商罗盘登录", 11, "IF 条件")):
            xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://compass.jinritemai.com/login", ignore_cache=False, load_timeout="20", _block=("电商罗盘登录", 12, "跳转至新网址"))
        #endif
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("电商罗盘_我是商家"), _block=("电商罗盘登录", 14, "IF 元素可见(web)")):
            xbot_visual.programing.sleep(random_number=False, seconds=wait_time, start_number="1", stop_number="5", _block=("电商罗盘登录", 15, "等待"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("电商罗盘_我是商家"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 16, "点击元素(web)"))
        #endif
        if xbot_visual.workflow.test(operand1=是否要退出已登录账号, operator="is true", operand2="", operator_options="{}", _block=("电商罗盘登录", 18, "IF 条件")):
            for loop_index4 in xbot_visual.workflow.range_iterator(start="0", stop="8", step="1", _block=("电商罗盘登录", 19, "For次数循环")):
                try:
                    xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("电商罗盘登录", 21, "等待"))
                    try:
                        右上角店铺名称 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@id=\"compass-shop-header\"]//div[contains(@class, \"userName\")]", is_related_parent=False, parent=None, timeout="2", _block=("电商罗盘登录", 22, "获取元素对象(web)"))
                    except Exception as e:
                        pass
                        右上角店铺名称 = None
                    if xbot_visual.workflow.test(operand1=右上角店铺名称, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("电商罗盘登录", 23, "IF 条件")):
                        xbot_visual.web.element.click(browser=web_page, element=右上角店铺名称, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 24, "点击元素(web)"))
                        xbot_visual.web.element.click(browser=web_page, element=package.selector("退出登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 25, "点击元素(web)"))
                    else:
                        break
                    #endif
                except Exception as exception2:
                    exception2 = xbot_visual.trace(exception2)
                    pass
                #endtry
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("电商罗盘登录", 31, "等待"))
            #endloop
        else:
            try:
                右上角店铺名称 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@id=\"compass-shop-header\"]//div[contains(@class, \"userName\")]", is_related_parent=False, parent=None, timeout="2", _block=("电商罗盘登录", 34, "获取元素对象(web)"))
            except Exception as e:
                pass
                右上角店铺名称 = None
            if xbot_visual.workflow.test(operand1=右上角店铺名称, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("电商罗盘登录", 35, "IF 条件")):
                xbot_visual.programing.log(type="info", text="当前账号已经登录，不必再重新登录", _block=("电商罗盘登录", 36, "打印日志"))
                return
            #endif
        #endif
        xbot_visual.programing.sleep(random_number=False, seconds=wait_time, start_number="1", stop_number="5", _block=("电商罗盘登录", 40, "等待"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("电商罗盘_我是商家"), _block=("电商罗盘登录", 41, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("电商罗盘_我是商家"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 42, "点击元素(web)"))
        #endif
        xbot_visual.programing.sleep(random_number=False, seconds=wait_time, start_number="1", stop_number="5", _block=("电商罗盘登录", 44, "等待"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("电商罗盘_请选择店铺"), _block=("电商罗盘登录", 45, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("电商罗盘_返回"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 46, "点击元素(web)"))
        #endif
        xbot_visual.programing.sleep(random_number=False, seconds=wait_time, start_number="1", stop_number="5", _block=("电商罗盘登录", 48, "等待"))
        # 处理点击邮箱登录失败的问题
        for loop_index5 in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("电商罗盘登录", 50, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("电商罗盘_邮箱登录"), _block=("电商罗盘登录", 51, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("电商罗盘_切换登_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="custom", sudoku_part="MiddleCenter", offset_x="3", offset_y="3", timeout="20", _block=("电商罗盘登录", 52, "点击元素(web)"))
                web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("电商罗盘_邮箱登录"), state="appear", iswait=True, timeout="3", _block=("电商罗盘登录", 53, "等待元素(web)"))
            else:
                break
            #endif
        #endloop
        for loop_index2 in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("电商罗盘登录", 58, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("电商罗盘_发送验证码"), _block=("电商罗盘登录", 59, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("电商罗盘_邮箱登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 60, "点击元素(web)"))
            else:
                break
            #endif
        #endloop
        网页类型 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_mode", params={
            "web_page": web_page,
        }, _block=("电商罗盘登录", 65, "调用模块"))
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type=网页类型, mode="activated", value="", use_wildcard=False, silent_running=True, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("电商罗盘登录", 66, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("电商罗盘登录", 66,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        try:
            try:
                web_element2 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=loading_element_xpath, is_related_parent=False, parent=None, timeout="5", _block=("电商罗盘登录", 68, "获取元素对象(web)"))
            except Exception as e:
                xbot_visual.programing.log(type='info',text=e,_block=("电商罗盘登录", 68,"获取元素对象(web)"))
                web_element2 = None
            try:
                web_wait_result4 = xbot_visual.web.element.wait(browser=web_page, element=web_element2, state="disappear", iswait=True, timeout="600", _block=("电商罗盘登录", 69, "等待元素(web)"))
            except Exception as e:
                xbot_visual.programing.log(type='info',text=e,_block=("电商罗盘登录", 69,"等待元素(web)"))
                web_wait_result4 = "加载元素加载超时"
        except Exception as exception3:
            exception3 = xbot_visual.trace(exception3)
            pass
        #endtry
        xbot_visual.web.element.input(browser=web_page, element=package.selector("电商罗盘_账号_输入框"), text=lambda: str(username), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 72, "填写输入框(web)"))
        password = xbot_visual.decrypt(password)
        xbot_visual.web.element.input(browser=web_page, element=package.selector("电商罗盘_密码_输入框"), text=lambda: str(password), append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 74, "填写输入框(web)"))
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type=网页类型, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("电商罗盘登录", 75, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("电商罗盘登录", 75,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("电商罗盘_复选框_同意协议"), text="", _block=("电商罗盘登录", 76, "IF 网页包含")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("电商罗盘_复选框_同意协议"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 77, "点击元素(web)"))
        #endif
        xbot_visual.web.element.click(browser=web_page, element=package.selector("电商罗盘_登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="2", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 79, "点击元素(web)"))
        # 验证码验证【滑块验证或文字点选验证】
        xbot_visual.programing.sleep(random_number=False, seconds=wait_time, start_number="1", stop_number="5", _block=("电商罗盘登录", 81, "等待"))
        for loop_index3 in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("电商罗盘登录", 82, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("电商罗盘_背景元素"), _block=("电商罗盘登录", 83, "IF 元素可见(web)")):
                xbot_visual.web.element.hover(browser=web_page, element=package.selector("罗盘-拖拽元素"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 84, "鼠标悬停在元素上(web)"))
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("电商罗盘登录", 85, "等待"))
                xbot_visual.process.run(process="xbot_extensions.activity_jfbym.dy_slider_captcha", package=__name__, inputs={
                    "web_page": web_page,
                    "engine": "xbot",
                    "background_ele": package.selector("电商罗盘_背景元素"),
                    "slider_ele": package.selector("罗盘-拖拽元素"),
                    "refresh_ele": package.selector("抖店_验证码刷新元素"),
                    "offset": lambda: 0,
                    "token": "",
                    "retry_count": lambda: 5,
                    }, outputs=[
                ], _block=("电商罗盘登录", 86, "抖音滑块验证"))
            else:
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("电商罗盘登录", 88, "等待"))
            #endif
        #endloop
        try:
            try:
                web_element2 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=loading_element_xpath, is_related_parent=False, parent=None, timeout="5", _block=("电商罗盘登录", 92, "获取元素对象(web)"))
            except Exception as e:
                xbot_visual.programing.log(type='info',text=e,_block=("电商罗盘登录", 92,"获取元素对象(web)"))
                web_element2 = None
            try:
                web_wait_result4 = xbot_visual.web.element.wait(browser=web_page, element=web_element2, state="disappear", iswait=True, timeout="600", _block=("电商罗盘登录", 93, "等待元素(web)"))
            except Exception as e:
                xbot_visual.programing.log(type='info',text=e,_block=("电商罗盘登录", 93,"等待元素(web)"))
                web_wait_result4 = "加载元素加载超时"
        except Exception as exception4:
            exception4 = xbot_visual.trace(exception4)
            pass
        #endtry
        # 进行多店铺选择
        if xbot_visual.workflow.test(operand1=登录的店铺名称, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("电商罗盘登录", 97, "IF 条件")):
            if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("选择店铺_返回"), text="", _block=("电商罗盘登录", 98, "IF 网页包含")):
                xbot_visual.programing.sleep(random_number=False, seconds=wait_time, start_number="1", stop_number="5", _block=("电商罗盘登录", 99, "等待"))
                店铺名称元素列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[text()='请选择店铺']/following-sibling::div/div", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout="10", output_with_element_count=False, _block=("电商罗盘登录", 100, "获取相似元素列表(web)"))
                未找到店铺 = xbot_visual.programing.variable(value=True
                , _block=("电商罗盘登录", 101, "设置变量"))
                shop_name_list = xbot_visual.programing.variable(value=lambda: []
                , _block=("电商罗盘登录", 102, "设置变量"))
                for 当前循环的店铺名称 in xbot_visual.workflow.list_iterator(list=店铺名称元素列表, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("电商罗盘登录", 103, "ForEach列表循环")):
                    try:
                        web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=".//div[@class='index_introName__2tsRs']", is_related_parent=True, parent=当前循环的店铺名称, timeout="20", _block=("电商罗盘登录", 105, "获取元素对象(web)"))
                        xbot_visual.list.append_or_insert(lst=shop_name_list, insert_way="append", index="0", elem=lambda: web_element.get_text(), _block=("电商罗盘登录", 106, "列表插入一项"))
                        if xbot_visual.workflow.test(operand1=lambda: web_element.get_text(), operator="==", operand2=登录的店铺名称, operator_options="{}", _block=("电商罗盘登录", 107, "IF 条件")):
                            xbot_visual.web.element.click(browser=web_page, element=当前循环的店铺名称, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="custom", sudoku_part="TopCenter", offset_x="0", offset_y="0", timeout="20", _block=("电商罗盘登录", 108, "点击元素(web)"))
                            未找到店铺 = xbot_visual.programing.variable(value=False
                            , _block=("电商罗盘登录", 109, "设置变量"))
                            break
                        #endif
                    except Exception as exception:
                        exception = xbot_visual.trace(exception)
                        xbot_visual.programing.log(type="info", text=exception, _block=("电商罗盘登录", 113, "打印日志"))
                        continue
                    #endtry
                #endloop
                xbot_visual.programing.log(type="info", text=shop_name_list, _block=("电商罗盘登录", 117, "打印日志"))
                if xbot_visual.workflow.test(operand1=未找到店铺, operator="is true", operand2="", operator_options="{}", _block=("电商罗盘登录", 118, "IF 条件")):
                    raise Exception("未找到店铺" + xbot_visual.sh_str(登录的店铺名称) + "，请检查店铺名是否正确后重新运行")
                #endif
            #endif
        #endif
        wait_result3 = xbot_visual.programing.variable(value=False
        , _block=("电商罗盘登录", 123, "设置变量"))
        for loop_index6 in xbot_visual.workflow.range_iterator(start="1", stop="30", step="1", _block=("电商罗盘登录", 124, "For次数循环")):
            try:
                右上角店铺名称 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@id=\"compass-shop-header\"]//div[contains(@class, \"userName\")]", is_related_parent=False, parent=None, timeout="2", _block=("电商罗盘登录", 125, "获取元素对象(web)"))
            except Exception as e:
                pass
                右上角店铺名称 = None
            if xbot_visual.workflow.test(operand1=右上角店铺名称, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("电商罗盘登录", 126, "IF 条件")):
                wait_result3 = xbot_visual.programing.variable(value=True
                , _block=("电商罗盘登录", 127, "设置变量"))
                break
            #endif
        #endloop
        if xbot_visual.workflow.test(operand1=wait_result3, operator="is true", operand2="", operator_options="{}", _block=("电商罗盘登录", 131, "IF 条件")):
            xbot_visual.programing.log(type="info", text="抖音罗盘登录成功", _block=("电商罗盘登录", 132, "打印日志"))
        else:
            raise Exception("抖音罗盘登录失败")
        #endif
    finally:
        args["web_page"] = web_page
