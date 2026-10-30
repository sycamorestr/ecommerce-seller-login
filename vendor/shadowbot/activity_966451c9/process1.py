import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    web_page = None
    if args is None:
        账号 = ""
        密码 = ""
        店铺名称 = ""
        图鉴账号 = ""
        图鉴密码 = ""
        是否退出已登录 = True
        加载超时时间 = "20"
        浏览器对象 = None
        验证重试次数 = 5
    else:
        账号 = args.get("账号", "")
        密码 = args.get("密码", "")
        店铺名称 = args.get("店铺名称", "")
        图鉴账号 = args.get("图鉴账号", "")
        图鉴密码 = args.get("图鉴密码", "")
        是否退出已登录 = args.get("是否退出已登录", True)
        加载超时时间 = args.get("加载超时时间", "20")
        浏览器对象 = args.get("浏览器对象", None)
        验证重试次数 = args.get("验证重试次数", 5)
    try:
        # 参数赋值
        account = xbot_visual.programing.variable(value=账号
        , _block=("抖店多店铺登录", 2, "设置变量"))
        password = xbot_visual.programing.variable(value=密码
        , _block=("抖店多店铺登录", 3, "设置变量"))
        shop_name = xbot_visual.programing.variable(value=店铺名称
        , _block=("抖店多店铺登录", 4, "设置变量"))
        need_logout = xbot_visual.programing.variable(value=是否退出已登录
        , _block=("抖店多店铺登录", 5, "设置变量"))
        tt_account = xbot_visual.programing.variable(value=图鉴账号
        , _block=("抖店多店铺登录", 6, "设置变量"))
        tt_password = xbot_visual.programing.variable(value=图鉴密码
        , _block=("抖店多店铺登录", 7, "设置变量"))
        time_out = xbot_visual.programing.variable(value=lambda: int(加载超时时间)
        , _block=("抖店多店铺登录", 8, "设置变量"))
        web_page = xbot_visual.programing.variable(value=lambda: None
        , _block=("抖店多店铺登录", 9, "设置变量"))
        web_page_mode = xbot_visual.programing.variable(value=""
        , _block=("抖店多店铺登录", 10, "设置变量"))
        # 业务逻辑, 是否传网页对象, 传的话从网页对象中提取浏览器类型, 不传默认chrome
        web_page_mode = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_active_by_web_page", params={
            "web_page": 浏览器对象,
        }, _block=("抖店多店铺登录", 12, "调用模块"))
        for retry_times in xbot_visual.workflow.range_iterator(start="1", stop="3", step="1", _block=("抖店多店铺登录", 13, "For次数循环")):
            try:
                #region 判断 登录状态 及 是否需要退出已登录
                web_page = xbot_visual.web.create(web_type=web_page_mode, value="https://fxg.jinritemai.com/login/common", silent_running=False, wait_load_completed=True, load_timeout=time_out, stop_load_if_load_timeout="stopLoad", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments="--start-maximized", _block=("抖店多店铺登录", 16, "打开网页"))
                xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("抖店多店铺登录", 17, "等待"))
                for loop_index in xbot_visual.workflow.range_iterator(start="0", stop=lambda: 5, step="1", _block=("抖店多店铺登录", 18, "For次数循环")):
                    web_page_网页链接 = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("抖店多店铺登录", 19, "获取网页信息"))
                    if xbot_visual.workflow.test(operand1=web_page_网页链接, operator="in", operand2="https://fxg.jinritemai.com/login/common", operator_options="{\"ignoreCase\":\"False\"}", _block=("抖店多店铺登录", 20, "IF 条件")):
                        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("抖店_多店铺登录_请选择店铺_返回按钮"), text="", _block=("抖店多店铺登录", 21, "IF 网页包含")):
                            xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_多店铺登录_请选择店铺_返回按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="3", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("抖店多店铺登录", 22, "点击元素(web)"))
                            break
                        #endif
                    else:
                        if xbot_visual.workflow.test(operand1=need_logout, operator="is true", operand2="", operator_options="{}", _block=("抖店多店铺登录", 26, "IF 条件")):
                            web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("店铺名称"), state="appear", iswait=True, timeout="200", _block=("抖店多店铺登录", 27, "等待元素(web)"))
                            _ = xbot_visual.process.run(process="process21", package=__name__, inputs={
                                "web_page": web_page,
                                "time_out": time_out,
                                }, outputs=[
                            ], _block=("抖店多店铺登录", 28, "调用流程"))
                            break
                        else:
                            xbot_visual.programing.log(type="info", text="抖店已登录，且您选择无需退出已登录，开始为您切换店铺 ~", _block=("抖店多店铺登录", 31, "打印日志"))
                            xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("抖店多店铺登录", 32, "等待"))
                            web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("抖店_切换店铺/组织"), state="appear", iswait=True, timeout="5", _block=("抖店多店铺登录", 33, "等待元素(web)"))
                            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("抖店_切换店铺/组织"), _block=("抖店多店铺登录", 34, "IF 元素可见(web)")):
                                xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_切换店铺/组织"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店多店铺登录", 35, "点击元素(web)"))
                                for 当前循环的店铺 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("店铺名称_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店多店铺登录", 36, "循环相似元素(web)")):
                                    if xbot_visual.workflow.test(operand1=当前循环的店铺.get_text(), operator="==", operand2=shop_name, operator_options="{}", _block=("抖店多店铺登录", 37, "IF 条件")):
                                        xbot_visual.web.element.click(browser=web_page, element=当前循环的店铺, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店多店铺登录", 38, "点击元素(web)"))
                                        xbot_visual.programing.log(type="info", text="已经切换到" + xbot_visual.sh_str(shop_name) + "店铺", _block=("抖店多店铺登录", 39, "打印日志"))
                                        return
                                    #endif
                                #endloop
                            else:
                                _ = xbot_visual.process.run(process="process17", package=__name__, inputs={
                                    "网页对象": web_page,
                                    "目标店铺名称": shop_name,
                                    "全局超时时间": time_out,
                                    }, outputs=[
                                ], _block=("抖店多店铺登录", 44, "调用流程"))
                            #endif
                            return
                        #endif
                    #endif
                #endloop
                #endregion
                # ¦---                  到此为止，必须保证网页在登录页面                  ---¦
                # ¦---   后面流程只负责从登录页面的登录操作，请勿杂糅其它操作   ---¦
                if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("商家助手"), text="", _block=("抖店多店铺登录", 53, "IF 网页包含")):
                    _ = xbot_visual.process.run(process="process5", package=__name__, inputs={
                        "web_page": web_page,
                        "隐藏显示": "隐藏",
                        }, outputs=[
                    ], _block=("抖店多店铺登录", 54, "调用流程"))
                #endif
                #region 输入账密，点击登录
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("抖店_多店铺登录_切换账密登录_按钮"), _block=("抖店多店铺登录", 57, "IF 元素可见(web)")):
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_多店铺登录_切换账密登录_按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("抖店多店铺登录", 58, "点击元素(web)"))
                #endif
                xbot_visual.web.element.click(browser=web_page, element=package.selector("邮箱登录"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店多店铺登录", 60, "点击元素(web)"))
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("抖店_多店铺登录_邮箱_输入框"), _block=("抖店多店铺登录", 61, "IF 元素可见(web)")):
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("邮箱登录"), simulate=True, move_mouse=True, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店多店铺登录", 62, "点击元素(web)"))
                #endif
                xbot_visual.web.element.input(browser=web_page, element=package.selector("抖店_多店铺登录_邮箱_输入框"), text=account, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="80", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("抖店多店铺登录", 64, "填写输入框(web)"))
                invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="read_text", params={
                }, _block=("抖店多店铺登录", 65, "调用模块"))
                # 增加剪贴板内容校验
                if xbot_visual.workflow.test(operand1=invoke_result, operator="!=", operand2=账号, operator_options="{}", _block=("抖店多店铺登录", 67, "IF 条件")):
                    # 使用手动方式添加
                    invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="write", params={
                        "text": 账号,
                        "verify": True,
                        "max_retry": lambda: 3,
                    }, _block=("抖店多店铺登录", 69, "调用模块"))
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_多店铺登录_邮箱_输入框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店多店铺登录", 70, "点击元素(web)"))
                    xbot_visual.win32.send_keys(keys="^{a}", hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("抖店多店铺登录", 71, "键盘输入"))
                    xbot_visual.win32.send_keys(keys="{DELETE}", hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("抖店多店铺登录", 72, "键盘输入"))
                    xbot_visual.win32.send_keys(keys="^{v}", hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("抖店多店铺登录", 73, "键盘输入"))
                    xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("抖店多店铺登录", 74, "等待"))
                #endif
                xbot_visual.web.element.input_password(browser=web_page, element=package.selector("抖店_多店铺登录_密码_输入框"), text=xbot_visual.decrypt(密码.strip()), input_check=False, retry_times="3", simulate=False, save_to_clipboard=True, input_type="clipboard", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", timeout=time_out, click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", _block=("抖店多店铺登录", 76, "填写密码框(web)"))
                invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="read_text", params={
                }, _block=("抖店多店铺登录", 77, "调用模块"))
                # 增加剪贴板内容校验
                if xbot_visual.workflow.test(operand1=invoke_result, operator="!=", operand2=密码, operator_options="{}", _block=("抖店多店铺登录", 79, "IF 条件")):
                    # 使用手动方式添加
                    invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="write", params={
                        "text": 密码,
                        "verify": True,
                        "max_retry": lambda: 3,
                    }, _block=("抖店多店铺登录", 81, "调用模块"))
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_多店铺登录_密码_输入框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店多店铺登录", 82, "点击元素(web)"))
                    xbot_visual.win32.send_keys(keys="^{a}", hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("抖店多店铺登录", 83, "键盘输入"))
                    xbot_visual.win32.send_keys(keys="{DELETE}", hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("抖店多店铺登录", 84, "键盘输入"))
                    xbot_visual.win32.send_keys(keys="^{v}", hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("抖店多店铺登录", 85, "键盘输入"))
                    xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("抖店多店铺登录", 86, "等待"))
                #endif
                if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("抖店_多店铺登录_同意用户协议复选框"), text="", _block=("抖店多店铺登录", 88, "IF 网页包含")):
                    xbot_visual.web.element.check(browser=web_page, element=package.selector("抖店_多店铺登录_同意用户协议复选框"), mode="check", delay_after="1", timeout=time_out, _block=("抖店多店铺登录", 89, "设置复选框(web)"))
                #endif
                #endregion
                #region 过验证码
                if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("抖店_滑块登录底图(新)"), text="", _block=("抖店多店铺登录", 93, "IF 网页包含")):
                    xbot_visual.process.run(process="xbot_extensions.activity_jfbym.dy_slider_captcha", package=__name__, inputs={
                        "web_page": web_page,
                        "engine": "xbot",
                        "background_ele": package.selector("抖店_滑块登录底图(新)"),
                        "slider_ele": package.selector("抖店_滑块登录滑块(新)"),
                        "refresh_ele": package.selector("抖店_滑块登录刷新(新)"),
                        "offset": lambda: 0,
                        "token": "",
                        "retry_count": lambda: 验证重试次数,
                        }, outputs=[
                    ], _block=("抖店多店铺登录", 94, "抖音滑块验证"))
                #endif
                for vc_retry_times in xbot_visual.workflow.range_iterator(start="1", stop=验证重试次数, step="1", _block=("抖店多店铺登录", 96, "For次数循环")):
                    try:
                        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("抖店_验证码_点选文字_确认按钮"), text="", _block=("抖店多店铺登录", 98, "IF 网页包含")):
                            xbot_visual.programing.log(type="info", text="检测到点选坐标验证码", _block=("抖店多店铺登录", 99, "打印日志"))
                            _ = xbot_visual.process.run(process="process20", package=__name__, inputs={
                                "web_page": web_page,
                                "tt_account": tt_account,
                                "tt_password": tt_password,
                                "time_out": time_out,
                                }, outputs=[
                            ], _block=("抖店多店铺登录", 100, "调用流程"))
                        #endif
                        xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("抖店多店铺登录", 102, "等待"))
                        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="not_contains_element", selector=package.selector("抖店_多店铺登录_登录_按钮"), text="", _block=("抖店多店铺登录", 103, "IF 网页包含")):
                            break
                        #endif
                        # 增加刷新操作
                    except Exception as exception:
                        exception = xbot_visual.trace(exception)
                        xbot_visual.programing.log(type="info", text="验证码第" + xbot_visual.sh_str(vc_retry_times) + "次识别失败：" + xbot_visual.sh_str(exception), _block=("抖店多店铺登录", 108, "打印日志"))
                        if xbot_visual.workflow.test(operand1=vc_retry_times, operator="==", operand2=验证重试次数, operator_options="{}", _block=("抖店多店铺登录", 109, "IF 条件")):
                            raise Exception("验证码识别失败，需人工确认！（" + xbot_visual.sh_str(exception) + "）")
                        #endif
                    #endtry
                #endloop
                #endregion
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("抖店_多店铺登录_登录_按钮"), _block=("抖店多店铺登录", 115, "IF 元素可见(web)")):
                    xbot_visual.web.element.hover(browser=web_page, element=package.selector("抖店_多店铺登录_登录_按钮"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店多店铺登录", 116, "鼠标悬停在元素上(web)"))
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_多店铺登录_登录_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after=lambda: time_out  // 6 + 1, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("抖店多店铺登录", 117, "点击元素(web)"))
                #endif
                #region 过验证码
                if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("抖店_滑块登录底图(新)"), text="", _block=("抖店多店铺登录", 120, "IF 网页包含")):
                    xbot_visual.programing.log(type="info", text="检测到滑块验证码", _block=("抖店多店铺登录", 121, "打印日志"))
                    xbot_visual.process.run(process="xbot_extensions.activity_jfbym.dy_slider_captcha", package=__name__, inputs={
                        "web_page": web_page,
                        "engine": "xbot",
                        "background_ele": package.selector("抖店_滑块登录底图(新)"),
                        "slider_ele": package.selector("抖店_滑块登录滑块(新)"),
                        "refresh_ele": package.selector("抖店_滑块登录刷新(新)"),
                        "offset": lambda: 0,
                        "token": "",
                        "retry_count": lambda: 1,
                        }, outputs=[
                    ], _block=("抖店多店铺登录", 122, "抖音滑块验证"))
                #endif
                for vc_retry_times in xbot_visual.workflow.range_iterator(start="1", stop=验证重试次数, step="1", _block=("抖店多店铺登录", 124, "For次数循环")):
                    try:
                        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("抖店_验证码_点选文字_确认按钮"), text="", _block=("抖店多店铺登录", 126, "IF 网页包含")):
                            xbot_visual.programing.log(type="info", text="检测到点选坐标验证码", _block=("抖店多店铺登录", 127, "打印日志"))
                            _ = xbot_visual.process.run(process="process20", package=__name__, inputs={
                                "web_page": web_page,
                                "tt_account": tt_account,
                                "tt_password": tt_password,
                                "time_out": time_out,
                                }, outputs=[
                            ], _block=("抖店多店铺登录", 128, "调用流程"))
                        #endif
                        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="not_contains_element", selector=package.selector("抖店_多店铺登录_登录_按钮"), text="", _block=("抖店多店铺登录", 130, "IF 网页包含")):
                            break
                        #endif
                    except Exception as exception:
                        exception = xbot_visual.trace(exception)
                        xbot_visual.programing.log(type="info", text="验证码第" + xbot_visual.sh_str(vc_retry_times) + "次识别失败：" + xbot_visual.sh_str(exception), _block=("抖店多店铺登录", 134, "打印日志"))
                        if xbot_visual.workflow.test(operand1=vc_retry_times, operator="==", operand2=验证重试次数, operator_options="{}", _block=("抖店多店铺登录", 135, "IF 条件")):
                            raise Exception("验证码识别失败，需人工确认！（" + xbot_visual.sh_str(exception) + "）")
                        #endif
                    #endtry
                #endloop
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("抖店多店铺登录", 140, "等待"))
                #endregion
                #region 处理登录后杂项
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("抖店_多店铺登录_抖店工作台"), _block=("抖店多店铺登录", 143, "IF 元素可见(web)")):
                    web_element_list = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("抖店_多店铺登录_抖店工作台"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("抖店多店铺登录", 144, "获取相似元素列表(web)"))
                    web_element_count = len(web_element_list)
                    if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": web_element_count,"operand2": lambda: 1,"operator": "=="}], _block=("抖店多店铺登录", 145, "IF 多条件")):
                        xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_多店铺登录_抖店工作台"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="3", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("抖店多店铺登录", 146, "点击元素(web)"))
                    #endif
                #endif
                #endregion
                xbot_visual.programing.log(type="info", text=店铺名称, _block=("抖店多店铺登录", 150, "打印日志"))
                if xbot_visual.workflow.test(operand1=店铺名称, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店多店铺登录", 151, "IF 条件")):
                    return
                #endif
                _ = xbot_visual.process.run(process="process17", package=__name__, inputs={
                    "网页对象": web_page,
                    "目标店铺名称": shop_name,
                    "全局超时时间": time_out,
                    }, outputs=[
                ], _block=("抖店多店铺登录", 154, "调用流程"))
                break
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                xbot_visual.web.browser.close(operation="close_specified", browser=web_page, web_type="cef", task_kill=False, ignore_beforeunload=False, _block=("抖店多店铺登录", 157, "关闭网页"))
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("抖店多店铺登录", 158, "等待"))
                xbot_visual.programing.log(type="info", text="抖店多店铺登录【" + xbot_visual.sh_str(retry_times) + "】：" + xbot_visual.sh_str(exception), _block=("抖店多店铺登录", 159, "打印日志"))
                if xbot_visual.workflow.test(operand1=retry_times, operator="==", operand2="3", operator_options="{}", _block=("抖店多店铺登录", 160, "IF 条件")):
                    raise Exception("抖店多店铺登录：" + xbot_visual.sh_str(exception))
                elif xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": exception,"operand2": "当前店铺已停用","operator": "in"},{"operand1": exception,"operand2": "未找到目标店铺","operator": "in"}], _block=("抖店多店铺登录", 162, "Else IF 多条件")):
                    raise Exception("抖店多店铺登录（登录成功）：" + xbot_visual.sh_str(exception))
                #endif
            #endtry
        #endloop
        web_wait_result3 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("抖店_当前店铺名称"), state="appear", iswait=True, timeout="20", _block=("抖店多店铺登录", 167, "等待元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_当前店铺名称"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店多店铺登录", 168, "点击元素(web)"))
    finally:
        args["web_page"] = web_page
