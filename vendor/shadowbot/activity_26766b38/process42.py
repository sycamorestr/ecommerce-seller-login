import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    输出文件路径 = ""
    执行状态 = "成功"
    if args is None:
        查询日期 = ""
        保存文件夹 = None
        商品ID列表 = []
        开启页面统计时间校验 = True
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", None)
        商品ID列表 = args.get("商品ID列表", [])
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
    try:
        #region 获取并跳转目标页面
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("流量_商品来源_商品进店来源", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("流量_商品来源_商品进店来源", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/flow/monitor/itemsource", ignore_cache=False, load_timeout="20", _block=("流量_商品来源_商品进店来源", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("流量_商品来源_商品进店来源", 4, "等待"))
        #endregion
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
            "页面统计时间",
        ], _block=("流量_商品来源_商品进店来源", 6, "品类/流量/内容-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("流量_商品来源_商品进店来源", 8, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("流量_商品来源_商品进店来源", 9, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("流量_商品来源_商品进店来源", 10, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("流量_商品来源_商品进店来源", 11, "设置变量"))
                return
            #endif
        #endif
        #endregion
        for 当前商品ID in xbot_visual.workflow.list_iterator(list=商品ID列表, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("流量_商品来源_商品进店来源", 16, "ForEach列表循环")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("商品来源_商品取消按钮"), _block=("流量_商品来源_商品进店来源", 17, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("商品来源_商品取消按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_商品来源_商品进店来源", 18, "点击元素(web)"))
            #endif
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("流量_商品来源_商品ID输入框"), _block=("流量_商品来源_商品进店来源", 20, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("流量_商品来源_选择商品"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_商品来源_商品进店来源", 21, "点击元素(web)"))
            #endif
            xbot_visual.web.element.input(browser=web_page, element=package.selector("流量_商品来源_商品ID输入框"), text=当前商品ID, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_商品来源_商品进店来源", 23, "填写输入框(web)"))
            web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("流量_商品来源_第一个搜索到的商品"), state="appear", iswait=True, timeout="5", _block=("流量_商品来源_商品进店来源", 24, "等待元素(web)"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("流量_商品来源_第一个搜索到的商品"), _block=("流量_商品来源_商品进店来源", 25, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("流量_商品来源_第一个搜索到的商品"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_商品来源_商品进店来源", 26, "点击元素(web)"))
            else:
                raise Exception("商品ID错误")
            #endif
            _ = xbot_visual.process.run(process="process52", package=__name__, inputs={
                "web_page": web_page,
                }, outputs=[
            ], _block=("流量_商品来源_商品进店来源", 30, "调用流程"))
            # web.element.click
            点击下载 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//span[.=\"下载\"]", is_related_parent=False, parent=None, timeout="20", _block=("流量_商品来源_商品进店来源", 32, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=点击下载, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_商品来源_商品进店来源", 33, "点击元素(web)"))
            输出文件路径 = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=保存文件夹, use_custom_filename=True, file_name=lambda: "流量_商品来源_商品进店来源_{}_{}.xls".format(当前商品ID,查询日期), save_behavior="overwrite", wait_complete=False, wait_complete_timeout="", simulate=False, clipboard_input=True, input_type="clipboard", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("流量_商品来源_商品进店来源", 34, "处理下载对话框"))
            file_wait_result = xbot_visual.file.wait(path=输出文件路径, desired_state="created", is_wait=True, timeout_seconds="60", _block=("流量_商品来源_商品进店来源", 35, "等待文件"))
            xbot_visual.programing.log(type="info", text=lambda: "文件路径：{}".format(输出文件路径), _block=("流量_商品来源_商品进店来源", 36, "打印日志"))
        #endloop
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
