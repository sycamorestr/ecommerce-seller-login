import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    输出文件路径 = ""
    执行状态 = "成功"
    数据存放字典 = {}
    if args is None:
        查询日期 = ""
        保存文件夹 = None
        开启页面统计时间校验 = True
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", None)
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
    try:
        response_body_list = xbot_visual.programing.variable(value=lambda: []
        , _block=("流量_流量看板_流量总览", 1, "设置变量"))
        #region 获取并跳转目标页面
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("流量_流量看板_流量总览", 3, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("流量_流量看板_流量总览", 3,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/flow/monitor/overview", ignore_cache=False, load_timeout="20", _block=("流量_流量看板_流量总览", 4, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="5", start_number="1", stop_number="5", _block=("流量_流量看板_流量总览", 5, "等待"))
        #endregion
        _ = xbot_visual.process.run(process="process52", package=__name__, inputs={
            "web_page": web_page,
            }, outputs=[
        ], _block=("流量_流量看板_流量总览", 7, "调用流程"))
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
            "页面统计时间",
        ], _block=("流量_流量看板_流量总览", 8, "品类/流量/内容-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("流量_流量看板_流量总览", 10, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("流量_流量看板_流量总览", 11, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("流量_流量看板_流量总览", 12, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("流量_流量看板_流量总览", 13, "设置变量"))
                return
            #endif
        #endif
        #endregion
        _ = xbot_visual.process.run(process="process52", package=__name__, inputs={
            "web_page": web_page,
            }, outputs=[
        ], _block=("流量_流量看板_流量总览", 18, "调用流程"))
        # 由于监听会出现反复监听不到的情况, 所以改监听为页面抓取 ...
        数据存放字典 = xbot_visual.programing.variable(value=lambda: {}
        , _block=("流量_流量看板_流量总览", 20, "设置变量"))
        # web.get
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("返回旧版_1"), _block=("流量_流量看板_流量总览", 22, "IF 元素可见(web)")):
            for 当前大类模块 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("流量-流量看板-流量总览-大类相似元素组(新版)"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("流量_流量看板_流量总览", 23, "循环相似元素(web)")):
                xbot_visual.web.element.click(browser=web_page, element=当前大类模块, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_流量看板_流量总览", 24, "点击元素(web)"))
                # web.element.get_all_elements
                # web.element.get_element
                当前大类标题 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("访问店铺（新版）"), css_selector="", xpath_selector="", is_related_parent=True, parent=当前大类模块, timeout="20", _block=("流量_流量看板_流量总览", 27, "获取元素对象(web)"))
                当前大类标题文本 = xbot_visual.web.element.get_details(browser=web_page, element=当前大类标题, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("流量_流量看板_流量总览", 28, "获取元素信息(web)"))
                当前大类数据字典 = xbot_visual.dictionary.create(_block=("流量_流量看板_流量总览", 29, "新建字典"))
                for 当前标题数据_index, 当前标题数据 in enumerate(xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("标题数据"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("流量_流量看板_流量总览", 30, "循环相似元素(web)"))):
                    web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("标题名称"), css_selector="", xpath_selector="", is_related_parent=True, parent=当前标题数据, timeout="20", _block=("流量_流量看板_流量总览", 31, "获取元素对象(web)"))
                    # web.element.get_element
                    value = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("当前数据1"), css_selector="", xpath_selector="", is_related_parent=True, parent=当前标题数据, timeout="20", _block=("流量_流量看板_流量总览", 33, "获取元素对象(web)"))
                    当前小标题 = xbot_visual.programing.variable(value=lambda: web_element.get_text().strip()
                    , _block=("流量_流量看板_流量总览", 34, "设置变量"))
                    当前数据值 = xbot_visual.programing.variable(value=lambda: value.get_text().strip()
                    , _block=("流量_流量看板_流量总览", 35, "设置变量"))
                    xbot_visual.dictionary.set(dict=当前大类数据字典, key=web_element.get_text(), value=value.get_text(), _block=("流量_流量看板_流量总览", 36, "设置键值对"))
                #endloop
                xbot_visual.dictionary.set(dict=数据存放字典, key=当前大类标题文本, value=当前大类数据字典, _block=("流量_流量看板_流量总览", 38, "设置键值对"))
            #endloop
            xbot_visual.programing.log(type="info", text=数据存放字典, _block=("流量_流量看板_流量总览", 40, "打印日志"))
        else:
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("前往新版_1"), _block=("流量_流量看板_流量总览", 42, "IF 元素可见(web)")):
                for 当前大类模块 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("流量-流量看板-流量总览-大类相似元素组(旧版)"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("流量_流量看板_流量总览", 43, "循环相似元素(web)")):
                    xbot_visual.web.element.click(browser=web_page, element=当前大类模块, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_流量看板_流量总览", 44, "点击元素(web)"))
                    # web.element.get_all_elements
                    # web.element.get_element
                    当前大类标题 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("访问店铺（旧版）"), css_selector="", xpath_selector="", is_related_parent=True, parent=当前大类模块, timeout="20", _block=("流量_流量看板_流量总览", 47, "获取元素对象(web)"))
                    当前大类标题文本 = xbot_visual.web.element.get_details(browser=web_page, element=当前大类标题, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("流量_流量看板_流量总览", 48, "获取元素信息(web)"))
                    当前大类数据字典 = xbot_visual.dictionary.create(_block=("流量_流量看板_流量总览", 49, "新建字典"))
                    for 当前标题数据_index, 当前标题数据 in enumerate(xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("标题数据"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("流量_流量看板_流量总览", 50, "循环相似元素(web)"))):
                        web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("标题名称"), css_selector="", xpath_selector="", is_related_parent=True, parent=当前标题数据, timeout="20", _block=("流量_流量看板_流量总览", 51, "获取元素对象(web)"))
                        # web.element.get_element
                        value = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("当前数据1"), css_selector="", xpath_selector="", is_related_parent=True, parent=当前标题数据, timeout="20", _block=("流量_流量看板_流量总览", 53, "获取元素对象(web)"))
                        当前小标题 = xbot_visual.programing.variable(value=lambda: web_element.get_text().strip()
                        , _block=("流量_流量看板_流量总览", 54, "设置变量"))
                        当前数据值 = xbot_visual.programing.variable(value=lambda: value.get_text().strip()
                        , _block=("流量_流量看板_流量总览", 55, "设置变量"))
                        xbot_visual.dictionary.set(dict=当前大类数据字典, key=web_element.get_text(), value=value.get_text(), _block=("流量_流量看板_流量总览", 56, "设置键值对"))
                    #endloop
                    xbot_visual.dictionary.set(dict=数据存放字典, key=当前大类标题文本, value=当前大类数据字典, _block=("流量_流量看板_流量总览", 58, "设置键值对"))
                #endloop
                xbot_visual.programing.log(type="info", text=数据存放字典, _block=("流量_流量看板_流量总览", 60, "打印日志"))
            #endif
        #endif
        输出文件路径 = xbot_visual.programing.variable(value=lambda: "{}\\流量看板流量总览数据_{}.xlsx".format(保存文件夹, 查询日期)
        , _block=("流量_流量看板_流量总览", 63, "设置变量"))
        excel_instance = xbot_visual.excel.launch(launch_way="create", driver_way="auto_check", open_filename="", save_filename=输出文件路径, isvisible=False, ignoreformula=False, password=xbot_visual.decrypt(""), write_password=xbot_visual.decrypt(""), update_links=False, _block=("流量_流量看板_流量总览", 64, "打开/新建Excel"))
        for loop_key, loop_value in xbot_visual.workflow.dict_iterator(dict=数据存放字典, _block=("流量_流量看板_流量总览", 65, "ForEach字典循环")):
            xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="row", write_way="append", write_column_way="override", row_num="0", column_name="", begin_row_num="0", begin_column_name="1", content=loop_key, sheet_name="", write_as_text_cols=None, _block=("流量_流量看板_流量总览", 66, "写入内容至Excel工作表"))
            写入表头 = xbot_visual.programing.variable(value=lambda: []
            , _block=("流量_流量看板_流量总览", 67, "设置变量"))
            写入数值 = xbot_visual.programing.variable(value=lambda: []
            , _block=("流量_流量看板_流量总览", 68, "设置变量"))
            for loop_key2, loop_value2 in xbot_visual.workflow.dict_iterator(dict=loop_value, _block=("流量_流量看板_流量总览", 69, "ForEach字典循环")):
                当前数值 = xbot_visual.programing.variable(value=""
                , _block=("流量_流量看板_流量总览", 70, "设置变量"))
                当前数值 = xbot_visual.text.replace_content_from_text(text=loop_value2, regular_pattern="", replace_way="content", replace_text=",", just_get_first=False, ignore_case=True, new_ignore_case=False, dest_text="", _block=("流量_流量看板_流量总览", 71, "文本替换"))
                xbot_visual.list.append_or_insert(lst=写入表头, insert_way="append", index="0", elem=loop_key2, _block=("流量_流量看板_流量总览", 72, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=写入数值, insert_way="append", index="0", elem=当前数值, _block=("流量_流量看板_流量总览", 73, "列表插入一项"))
            #endloop
            xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="row", write_way="append", write_column_way="override", row_num="0", column_name="", begin_row_num="0", begin_column_name="1", content=写入表头, sheet_name="", write_as_text_cols=None, _block=("流量_流量看板_流量总览", 75, "写入内容至Excel工作表"))
            xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="row", write_way="append", write_column_way="override", row_num="0", column_name="", begin_row_num="0", begin_column_name="1", content=写入数值, sheet_name="", write_as_text_cols=None, _block=("流量_流量看板_流量总览", 76, "写入内容至Excel工作表"))
        #endloop
        xbot_visual.excel.close(operation="close_specified", excel_instance=excel_instance, close_way="save", filename=None, overwrite_file=True, close_process="office", task_kill=False, _block=("流量_流量看板_流量总览", 78, "关闭Excel"))
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
        args["数据存放字典"] = 数据存放字典
