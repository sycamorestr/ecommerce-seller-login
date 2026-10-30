import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    web_page = None
    if args is None:
        平台名称 = "引力魔方"
        账户 = ""
        密码 = ""
        浏览器类型 = ""
    else:
        平台名称 = args.get("平台名称", "引力魔方")
        账户 = args.get("账户", "")
        密码 = args.get("密码", "")
        浏览器类型 = args.get("浏览器类型", "")
    try:
        platform_homepage_dict = xbot_visual.programing.variable(value=lambda: {"引力魔方":"https://tuijian.taobao.com/indexbp.html","直通车":"https://subway.simba.taobao.com/index.jsp","万象台":"https://adbrain.taobao.com/indexbp.html","超级钻展":"https://zuanshi.taobao.com/index_poquan.jsp","品销宝":"https://branding.taobao.com/index.action","商家中心":"https://ad.alimama.com/portal/v2/report/promotionDataPage.htm"}
        , _block=("D1 平台登录", 1, "设置变量"))
        homepage = xbot_visual.programing.variable(value=lambda: platform_homepage_dict.get(平台名称,None)
        , _block=("D1 平台登录", 2, "设置变量"))
        if xbot_visual.workflow.test(operand1=homepage, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("D1 平台登录", 3, "IF 条件")):
            raise Exception("当前版本指令仅支持以下六个平台的汇总数据获取【直通车，万象台，商家中心，引力魔方，超级钻展，品销宝】请输入正确的平台名称~")
            return
        #endif
        username = xbot_visual.programing.variable(value=lambda: 账户
        , _block=("D1 平台登录", 7, "设置变量"))
        password = xbot_visual.programing.variable(value=lambda: 密码
        , _block=("D1 平台登录", 8, "设置变量"))
        if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": username,"operand2": "","operator": "is empty"},{"operand1": password,"operand2": "","operator": "is empty"}], _block=("D1 平台登录", 9, "IF 多条件")):
            raise Exception("账户或密码为空，请检查~")
            return
        #endif
        if xbot_visual.workflow.test(operand1=浏览器类型, operator="==", operand2="chrome", operator_options="{}", _block=("D1 平台登录", 13, "IF 条件")):
            web_page = xbot_visual.web.create(web_type="chrome", value=homepage, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, ie_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("D1 平台登录", 14, "打开网页"))
        elif xbot_visual.workflow.test(operand1=浏览器类型, operator="==", operand2="edge", operator_options="{}", _block=("D1 平台登录", 15, "Else IF")):
            web_page = xbot_visual.web.create(web_type="edge", value=homepage, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, ie_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("D1 平台登录", 16, "打开网页"))
        #endif
        xbot_visual.web.browser.wait_load_completed(browser=web_page, load_timeout="30", action_after_load_timeout="handleExcept", _block=("D1 平台登录", 18, "等待网页加载完成"))
        xbot_visual.programing.sleep(random_number=True, seconds="1", start_number="2", stop_number="3", _block=("D1 平台登录", 19, "等待"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("阿里妈妈_退出登录"), _block=("D1 平台登录", 20, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("阿里妈妈_退出登录"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("D1 平台登录", 21, "点击元素(web)"))
            xbot_visual.programing.log(type="info", text="检测到已有账户登录，已退出", _block=("D1 平台登录", 22, "打印日志"))
        #endif
        web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("阿里妈妈_登录iframe_登录按钮"), state="appear", iswait=True, timeout="30", _block=("D1 平台登录", 24, "等待元素(web)"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("阿里妈妈_登录iframe_登录按钮"), _block=("D1 平台登录", 25, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("阿里妈妈_登录iframe_账号输入框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("D1 平台登录", 26, "点击元素(web)"))
            xbot_visual.web.element.input(browser=web_page, element=package.selector("阿里妈妈_登录iframe_账号输入框"), text=lambda: username, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("D1 平台登录", 27, "填写输入框(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("阿里妈妈_登录iframe_密码输入框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("D1 平台登录", 28, "点击元素(web)"))
            xbot_visual.web.element.input_password(browser=web_page, element=package.selector("阿里妈妈_登录iframe_密码输入框"), text=xbot_visual.decrypt(password), input_check=False, retry_times="3", simulate=True, save_to_clipboard=False, input_type="simulate", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", timeout="20", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", _block=("D1 平台登录", 29, "填写密码框(web)"))
            # web.element.input
            # web.get
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("登录滑块"), _block=("D1 平台登录", 32, "IF 元素可见(web)")):
                web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("登录滑块"), state="appear", iswait=True, timeout="10", _block=("D1 平台登录", 33, "等待元素(web)"))
                xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time="1", max_time="2", _block=("D1 平台登录", 34, "开启模拟真人操作"))
                xbot_visual.web.element.drag_to(browser=web_page, element=package.selector("登录滑块"), drag_way="targetElement", target_element=package.selector("阿里妈妈登录_滑块轨道元素"), left="0", top="0", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_speed="middle", release_anchor_type="custom", release_sudoku_part="MiddleRight", release_offset_x="50", release_offset_y="0", timeout="20", _block=("D1 平台登录", 35, "拖拽元素(web)"))
                xbot_visual.win32.manual_motion_off(_block=("D1 平台登录", 36, "结束模拟真人操作"))
            #endif
            xbot_visual.web.element.click(browser=web_page, element=package.selector("阿里妈妈_登录iframe_登录按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("D1 平台登录", 38, "点击元素(web)"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("登录滑块"), _block=("D1 平台登录", 39, "IF 元素可见(web)")):
                web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("登录滑块"), state="appear", iswait=True, timeout="10", _block=("D1 平台登录", 40, "等待元素(web)"))
                xbot_visual.win32.manual_motion_on(motion_move=True, motion_click=True, motion_delay=True, min_time="1", max_time="2", _block=("D1 平台登录", 41, "开启模拟真人操作"))
                xbot_visual.web.element.drag_to(browser=web_page, element=package.selector("登录滑块"), drag_way="targetElement", target_element=package.selector("阿里妈妈登录_滑块轨道元素"), left="0", top="0", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", move_speed="middle", release_anchor_type="custom", release_sudoku_part="MiddleRight", release_offset_x="50", release_offset_y="0", timeout="20", _block=("D1 平台登录", 42, "拖拽元素(web)"))
                xbot_visual.win32.manual_motion_off(_block=("D1 平台登录", 43, "结束模拟真人操作"))
            #endif
            xbot_visual.web.browser.wait_load_completed(browser=web_page, load_timeout="30", action_after_load_timeout="handleExcept", _block=("D1 平台登录", 45, "等待网页加载完成"))
        #endif
    finally:
        args["web_page"] = web_page
