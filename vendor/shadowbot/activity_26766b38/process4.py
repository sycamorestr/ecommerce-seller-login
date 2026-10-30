import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    执行状态 = "成功"
    失败sku列表 = []
    文件下载路径 = []
    if args is None:
        sku列表 = []
        终端选择 = "无线端"
        保存文件夹 = ""
        查询日期 = ""
        开启页面统计时间校验 = True
    else:
        sku列表 = args.get("sku列表", [])
        终端选择 = args.get("终端选择", "无线端")
        保存文件夹 = args.get("保存文件夹", "")
        查询日期 = args.get("查询日期", "")
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
    try:
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("品类-商品360销售分析核心概况数据获取", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("品类-商品360销售分析核心概况数据获取", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        失败sku列表 = xbot_visual.programing.variable(value=lambda: []
        , _block=("品类-商品360销售分析核心概况数据获取", 2, "设置变量"))
        文件下载路径 = xbot_visual.programing.variable(value=lambda: []
        , _block=("品类-商品360销售分析核心概况数据获取", 3, "设置变量"))
        for loop_item_index, 当前操作sku in enumerate(xbot_visual.workflow.list_iterator(list=sku列表, loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("品类-商品360销售分析核心概况数据获取", 4, "ForEach列表循环"))):
            try:
                #region sku 搜索, 进入详情页 点击销售分析 标签
                xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/cc/item_archives", ignore_cache=False, load_timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 7, "跳转至新网址"))
                # 滑块处理
                for loop_index in xbot_visual.workflow.range_iterator(start="0", stop="3", step="1", _block=("品类-商品360销售分析核心概况数据获取", 9, "For次数循环")):
                    if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("商品360-销售分析-滑块长条元素"), _block=("品类-商品360销售分析核心概况数据获取", 10, "IF 元素可见(web)")):
                        xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process11", package=__name__, inputs={
                            "web_page": web_page,
                            "drag_start_element": package.selector("商品360-销售分析-滑块拖动元素"),
                            "background_element": package.selector("商品360-销售分析-滑块长条元素"),
                            }, outputs=[
                        ], _block=("品类-商品360销售分析核心概况数据获取", 11, "滑块拖动"))
                    else:
                        break
                    #endif
                #endloop
                _ = xbot_visual.web.element.wait(browser=web_page, element=package.selector("品类-商品360-sku输入框"), state="appear", iswait=True, timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 16, "等待元素(web)"))
                xbot_visual.web.element.input(browser=web_page, element=package.selector("品类-商品360-sku输入框"), text=当前操作sku, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 17, "填写输入框(web)"))
                # 滑块处理
                for loop_index in xbot_visual.workflow.range_iterator(start="0", stop="3", step="1", _block=("品类-商品360销售分析核心概况数据获取", 19, "For次数循环")):
                    if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("商品360-销售分析-滑块长条元素"), _block=("品类-商品360销售分析核心概况数据获取", 20, "IF 元素可见(web)")):
                        xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process11", package=__name__, inputs={
                            "web_page": web_page,
                            "drag_start_element": package.selector("商品360-销售分析-滑块拖动元素"),
                            "background_element": package.selector("商品360-销售分析-滑块长条元素"),
                            }, outputs=[
                        ], _block=("品类-商品360销售分析核心概况数据获取", 21, "滑块拖动"))
                    else:
                        break
                    #endif
                #endloop
                _ = xbot_visual.web.element.wait(browser=web_page, element=package.selector("品类-商品360-搜索结果"), state="appear", iswait=True, timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 26, "等待元素(web)"))
                xbot_visual.web.element.click(browser=web_page, element=package.selector("品类-商品360-搜索结果"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 27, "点击元素(web)"))
                # 滑块处理
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("品类-商品360销售分析核心概况数据获取", 29, "等待"))
                for loop_index in xbot_visual.workflow.range_iterator(start="0", stop="3", step="1", _block=("品类-商品360销售分析核心概况数据获取", 30, "For次数循环")):
                    if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("商品360-销售分析-滑块长条元素"), _block=("品类-商品360销售分析核心概况数据获取", 31, "IF 元素可见(web)")):
                        xbot_visual.process.run(process="xbot_extensions.activity_7bca6d.process11", package=__name__, inputs={
                            "web_page": web_page,
                            "drag_start_element": package.selector("商品360-销售分析-滑块拖动元素"),
                            "background_element": package.selector("商品360-销售分析-滑块长条元素"),
                            }, outputs=[
                        ], _block=("品类-商品360销售分析核心概况数据获取", 32, "滑块拖动"))
                    else:
                        break
                    #endif
                #endloop
                xbot_visual.web.element.click(browser=web_page, element=package.selector("品类-商品360-详情页-销售分析标签"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 37, "点击元素(web)"))
                _ = xbot_visual.process.run(process="process52", package=__name__, inputs={
                    "web_page": web_page,
                    }, outputs=[
                ], _block=("品类-商品360销售分析核心概况数据获取", 38, "调用流程"))
                #endregion
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("品类-商品360-销售分析-选择事件"), _block=("品类-商品360销售分析核心概况数据获取", 40, "IF 元素可见(web)")):
                    xbot_visual.web.element.check(browser=web_page, element=package.selector("商品360-销售分析-选择事件复选框1"), mode="uncheck", delay_after="1", timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 41, "设置复选框(web)"))
                    xbot_visual.web.element.check(browser=web_page, element=package.selector("商品360-销售分析-选择事件复选框2"), mode="uncheck", delay_after="1", timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 42, "设置复选框(web)"))
                #endif
                页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
                    "日期": 查询日期,
                    }, outputs=[
                    "页面统计时间",
                ], _block=("品类-商品360销售分析核心概况数据获取", 44, "品类/流量/内容-通用时间选择"))
                if xbot_visual.workflow.test(operand1=loop_item_index, operator="==", operand2="0", operator_options="{}", _block=("品类-商品360销售分析核心概况数据获取", 45, "IF 条件")):
                    #region 功能模块 : 开启页面统计时间校验 
                    if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("品类-商品360销售分析核心概况数据获取", 47, "IF 条件")):
                        _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                            "查询日期": 查询日期,
                            "页面统计时间": 页面统计时间,
                            }, outputs=[
                            "判断结果",
                        ], _block=("品类-商品360销售分析核心概况数据获取", 48, "调用流程"))
                        if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("品类-商品360销售分析核心概况数据获取", 49, "IF 条件")):
                            执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                            , _block=("品类-商品360销售分析核心概况数据获取", 50, "设置变量"))
                            return
                        #endif
                    #endif
                    #endregion
                #endif
                #region 定位点击终端选择下拉框
                品类_商品360_详情页_销售分析_核心概况父元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("品类-商品360-详情页-销售分析-核心概况div"), css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 57, "获取元素对象(web)"))
                核心概况下拉框 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("品类-通用-所有终端下拉框"), css_selector="", xpath_selector="", is_related_parent=True, parent=品类_商品360_详情页_销售分析_核心概况父元素, timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 58, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=web_page, element=核心概况下拉框, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 59, "点击元素(web)"))
                #endregion
                #region 终端选择
                if xbot_visual.workflow.test(operand1=终端选择, operator="==", operand2="所有终端", operator_options="{}", _block=("品类-商品360销售分析核心概况数据获取", 62, "IF 条件")):
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("品类-通用-终端选择-所有终端"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 63, "点击元素(web)"))
                elif xbot_visual.workflow.test(operand1=终端选择, operator="==", operand2="无线端", operator_options="{}", _block=("品类-商品360销售分析核心概况数据获取", 64, "Else IF")):
                    xbot_visual.web.element.click(browser=web_page, element=package.selector("品类-通用-终端选择-无线端"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 65, "点击元素(web)"))
                #endif
                #endregion
                #region 数据下载
                核心概况数据下载按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("品类-通用-下载按钮"), css_selector="", xpath_selector="", is_related_parent=True, parent=品类_商品360_详情页_销售分析_核心概况父元素, timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 69, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=web_page, element=核心概况数据下载按钮, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-商品360销售分析核心概况数据获取", 70, "点击元素(web)"))
                输出文件路径 = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=保存文件夹, use_custom_filename=True, file_name=xbot_visual.sh_str(当前操作sku) + "-单品销售分析核心概况数据_" + xbot_visual.sh_str(页面统计时间) + ".xls", save_behavior="overwrite", wait_complete=True, wait_complete_timeout="30", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("品类-商品360销售分析核心概况数据获取", 71, "处理下载对话框"))
                #endregion
                xbot_visual.programing.log(type="info", text="已完成 sku : " + xbot_visual.sh_str(当前操作sku) + " 的数据下载", _block=("品类-商品360销售分析核心概况数据获取", 73, "打印日志"))
                xbot_visual.list.append_or_insert(lst=文件下载路径, insert_way="append", index="0", elem=输出文件路径, _block=("品类-商品360销售分析核心概况数据获取", 74, "列表插入一项"))
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                xbot_visual.programing.log(type="info", text="执行异常 sku : " + xbot_visual.sh_str(当前操作sku) + " ", _block=("品类-商品360销售分析核心概况数据获取", 76, "打印日志"))
                xbot_visual.list.append_or_insert(lst=失败sku列表, insert_way="append", index="0", elem=当前操作sku, _block=("品类-商品360销售分析核心概况数据获取", 77, "列表插入一项"))
            #endtry
        #endloop
    finally:
        args["执行状态"] = 执行状态
        args["失败sku列表"] = 失败sku列表
        args["文件下载路径"] = 文件下载路径
