import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    web_page = None
    if args is None:
        登录邮箱 = ""
        登录密码 = ""
        验证邮箱 = ""
        邮箱授权码 = ""
        获取授权码间隔时长 = 20
        验证码失败最大重试次数 = 10
        退出已登录账户 = False
        retry_cnt = 3
    else:
        登录邮箱 = args.get("登录邮箱", "")
        登录密码 = args.get("登录密码", "")
        验证邮箱 = args.get("验证邮箱", "")
        邮箱授权码 = args.get("邮箱授权码", "")
        获取授权码间隔时长 = args.get("获取授权码间隔时长", 20)
        验证码失败最大重试次数 = args.get("验证码失败最大重试次数", 10)
        退出已登录账户 = args.get("退出已登录账户", False)
        retry_cnt = args.get("retry_cnt", 3)
    try:
        # 巨量引擎邮箱登录----邮箱验证
        xbot_visual.programing.log(type="info", text="触发，巨量纵横登录", _block=("巨量引擎邮箱登录", 2, "打印日志"))
        web_page = xbot_visual.web.create(web_type="chrome", value="https://business.oceanengine.com/login?appKey=51", silent_running=False, wait_load_completed=True, load_timeout="120", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("巨量引擎邮箱登录", 3, "打开网页"))
        # ------新旧版选择检查
        try:
            check_t_flag = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//span[contains(@class, \"typography\")][text()=\"请选择工作台版本\"]", is_related_parent=False, parent=None, timeout="3", _block=("巨量引擎邮箱登录", 5, "获取元素对象(web)"))
        except Exception as e:
            pass
            check_t_flag = None
        if xbot_visual.workflow.test(operand1=check_t_flag, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量引擎邮箱登录", 6, "IF 条件")):
            点击进入元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"card-body\"][.//span[normalize-space(.)=\"旧版巨量引擎工作台\"]]//button", is_related_parent=False, parent=None, timeout="20", _block=("巨量引擎邮箱登录", 7, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=点击进入元素, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎邮箱登录", 8, "点击元素(web)"))
        #endif
        # ---------账户是否已登录判断，是否退出账户
        try:
            账号对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@id=\"header-user\" or @id=\"navigator-right-account\" or @class=\"navigator-user-button\"]", is_related_parent=False, parent=None, timeout="4", _block=("巨量引擎邮箱登录", 11, "获取元素对象(web)"))
        except Exception as e:
            pass
            账号对象 = None
        if xbot_visual.workflow.test(operand1=账号对象, operator="!=", operand2=lambda: None, operator_options="{}", _block=("巨量引擎邮箱登录", 12, "IF 条件")):
            if xbot_visual.workflow.test(operand1=退出已登录账户, operator="is true", operand2="", operator_options="{}", _block=("巨量引擎邮箱登录", 13, "IF 条件")):
                xbot_visual.web.element.hover(browser=web_page, element=账号对象, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎邮箱登录", 14, "鼠标悬停在元素上(web)"))
                退出账号 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[contains(text(), \"退出\")]", is_related_parent=False, parent=None, timeout="20", _block=("巨量引擎邮箱登录", 15, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=web_page, element=退出账号, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎邮箱登录", 16, "点击元素(web)"))
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("巨量引擎邮箱登录", 17, "等待"))
            else:
                xbot_visual.programing.log(type="info", text="不退出已登录的账户，登录流程结束。", _block=("巨量引擎邮箱登录", 19, "打印日志"))
                return
            #endif
        #endif
        # ---------邮箱登录
        try:
            邮箱登录切换按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"account-center-switch-button\")][contains(text(), \"邮箱\")]", is_related_parent=False, parent=None, timeout="5", _block=("巨量引擎邮箱登录", 24, "获取元素对象(web)"))
        except Exception as e:
            pass
            邮箱登录切换按钮 = None
        if xbot_visual.workflow.test(operand1=邮箱登录切换按钮, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量引擎邮箱登录", 25, "IF 条件")):
            xbot_visual.web.element.click(browser=web_page, element=邮箱登录切换按钮, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎邮箱登录", 26, "点击元素(web)"))
        #endif
        账号_输入框 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//input[contains(@placeholder , \"邮箱\")]", is_related_parent=False, parent=None, timeout="20", _block=("巨量引擎邮箱登录", 28, "获取元素对象(web)"))
        xbot_visual.web.element.input(browser=web_page, element=账号_输入框, text=登录邮箱, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="20", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎邮箱登录", 29, "填写输入框(web)"))
        密码_输入框 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//input[@placeholder = \"密码\"]", is_related_parent=False, parent=None, timeout="20", _block=("巨量引擎邮箱登录", 30, "获取元素对象(web)"))
        登录密码 = xbot_visual.decrypt(登录密码)
        xbot_visual.web.element.input(browser=web_page, element=密码_输入框, text=登录密码, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="20", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎邮箱登录", 32, "填写输入框(web)"))
        # programing.sleep
        # 勾选同意隐私条款
        xbot_visual.programing.log(type="info", text="勾选同意隐私条款", _block=("巨量引擎邮箱登录", 35, "打印日志"))
        同意隐私条款_勾选框_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"account-center-agreement-check\")]", is_related_parent=False, parent=None, timeout="10", _block=("巨量引擎邮箱登录", 36, "获取元素对象(web)"))
        元素勾选框_class = xbot_visual.web.element.get_details(browser=web_page, element=同意隐私条款_勾选框_元素对象, operation="other", absolute_url=False, attribute_name="class", relative_to="screen", to96dpi=True, timeout="20", _block=("巨量引擎邮箱登录", 37, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=元素勾选框_class, operator="not in", operand2="checked", operator_options="{\"ignoreCase\":\"True\"}", _block=("巨量引擎邮箱登录", 38, "IF 条件")):
            xbot_visual.web.element.click(browser=web_page, element=同意隐私条款_勾选框_元素对象, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎邮箱登录", 39, "点击元素(web)"))
        #endif
        # 结束
        纵横_登录 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//button[text() = \"登录\"]", is_related_parent=False, parent=None, timeout="10", _block=("巨量引擎邮箱登录", 42, "获取元素对象(web)"))
        xbot_visual.web.element.click(browser=web_page, element=纵横_登录, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="2", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎邮箱登录", 43, "点击元素(web)"))
        # ------新旧版选择检查
        try:
            check_t_flag = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//span[contains(@class, \"typography\")][text()=\"请选择工作台版本\"]", is_related_parent=False, parent=None, timeout="3", _block=("巨量引擎邮箱登录", 45, "获取元素对象(web)"))
        except Exception as e:
            pass
            check_t_flag = None
        if xbot_visual.workflow.test(operand1=check_t_flag, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量引擎邮箱登录", 46, "IF 条件")):
            点击进入元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"card-body\"][.//span[normalize-space(.)=\"旧版巨量引擎工作台\"]]//button", is_related_parent=False, parent=None, timeout="20", _block=("巨量引擎邮箱登录", 47, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=点击进入元素, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎邮箱登录", 48, "点击元素(web)"))
        #endif
        # 验证码验证【滑块验证或文字点选验证】
        web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("抖音滑块验证_背景图"), state="appear", iswait=True, timeout="5", _block=("巨量引擎邮箱登录", 51, "等待元素(web)"))
        _ = xbot_visual.process.run(process="process48", package=__name__, inputs={
            "web_page": web_page,
            "验证码失败最大重试次数": 验证码失败最大重试次数,
            }, outputs=[
        ], _block=("巨量引擎邮箱登录", 52, "调用流程"))
        # --------------检查是否需要邮箱验证-邮箱授权码获取
        _ = xbot_visual.process.run(process="process49", package=__name__, inputs={
            "web_page": web_page,
            "验证邮箱": 验证邮箱,
            "邮箱授权码": 邮箱授权码,
            "获取授权码间隔时长": 获取授权码间隔时长,
            "验证码失败最大重试次数": 验证码失败最大重试次数,
            }, outputs=[
        ], _block=("巨量引擎邮箱登录", 54, "调用流程"))
        # ------登录成功判断
        try:
            店铺名 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetShopName", package=__name__, inputs={
                "平台名称": "巨量引擎",
                "web_page": web_page,
                }, outputs=[
                "店铺名",
            ], _block=("巨量引擎邮箱登录", 56, "获取店铺名"))
        except Exception as e:
            pass
            店铺名 = None
        if xbot_visual.workflow.test(operand1=店铺名, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量引擎邮箱登录", 57, "IF 条件")):
            try:
                店铺名 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="(//div[@id=\"header-user\" or @id=\"navigator-right-account\" or @class=\"navigator-user-button\"]//div[contains(@class,\"bp-tree-container-name\")])[1]", is_related_parent=False, parent=None, timeout="4", _block=("巨量引擎邮箱登录", 58, "获取元素对象(web)"))
            except Exception as e:
                pass
                店铺名 = None
            店铺名 = xbot_visual.web.element.get_details(browser=web_page, element=店铺名, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("巨量引擎邮箱登录", 59, "获取元素信息(web)"))
        #endif
        if xbot_visual.workflow.test(operand1=店铺名, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量引擎邮箱登录", 61, "IF 条件")):
            # ------登录失败处理
            if xbot_visual.workflow.test(operand1=retry_cnt, operator="<=", operand2=lambda: 0, operator_options="{}", _block=("巨量引擎邮箱登录", 63, "IF 条件")):
                raise Exception("登录流程失败！")
            #endif
            retry_cnt = xbot_visual.programing.variable(value=lambda: retry_cnt - 1
            , _block=("巨量引擎邮箱登录", 66, "设置变量"))
            xbot_visual.web.browser.close(operation="close_specified", browser=web_page, web_type="cef", task_kill=False, ignore_beforeunload=False, _block=("巨量引擎邮箱登录", 67, "关闭网页"))
            登录结果 = xbot_visual.process.run(process="xbot_extensions.dynamic_call.process1", package=__name__, inputs={
                "流程名": "巨量引擎邮箱登录",
                "流程参数": lambda: {"username": username, "password":password, "验证邮箱": 验证邮箱, "邮箱授权码": 邮箱授权码, "获取授权码间隔时长": 获取授权码间隔时长, "验证码失败最大重试次数": 验证码失败最大重试次数, "退出已登录账户": 退出已登录账户, "retry_cnt": retry_cnt},
                "file_path": lambda: __file__,
                }, outputs=[
                "process_result",
            ], _block=("巨量引擎邮箱登录", 68, "动态调用子流程"))
            web_page = xbot_visual.programing.variable(value=lambda: 登录结果["web_page"]
            , _block=("巨量引擎邮箱登录", 69, "设置变量"))
            return
        #endif
        xbot_visual.programing.log(type="info", text="登录完成。  欢迎： " + xbot_visual.sh_str(店铺名), _block=("巨量引擎邮箱登录", 72, "打印日志"))
        # ------新旧版选择检查
        try:
            check_t_flag = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//span[contains(@class, \"typography\")][text()=\"请选择工作台版本\"]", is_related_parent=False, parent=None, timeout="3", _block=("巨量引擎邮箱登录", 74, "获取元素对象(web)"))
        except Exception as e:
            pass
            check_t_flag = None
        if xbot_visual.workflow.test(operand1=check_t_flag, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("巨量引擎邮箱登录", 75, "IF 条件")):
            点击进入元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"card-body\"][.//span[normalize-space(.)=\"旧版巨量引擎工作台\"]]//button", is_related_parent=False, parent=None, timeout="20", _block=("巨量引擎邮箱登录", 76, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=点击进入元素, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("巨量引擎邮箱登录", 77, "点击元素(web)"))
        #endif
    finally:
        args["web_page"] = web_page
