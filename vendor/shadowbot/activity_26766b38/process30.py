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
        内容类型 = ""
        内容来源 = ""
        开启页面统计时间校验 = True
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", None)
        内容类型 = args.get("内容类型", "")
        内容来源 = args.get("内容来源", "")
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
    try:
        #region 获取并跳转目标页面
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("内容_推荐分析_整体概况", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("内容_推荐分析_整体概况", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/xsite/contentanalysis/recommend_analysis", ignore_cache=False, load_timeout="20", _block=("内容_推荐分析_整体概况", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("内容_推荐分析_整体概况", 4, "等待"))
        #endregion
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
            "页面统计时间",
        ], _block=("内容_推荐分析_整体概况", 6, "品类/流量/内容-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("内容_推荐分析_整体概况", 8, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("内容_推荐分析_整体概况", 9, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("内容_推荐分析_整体概况", 10, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("内容_推荐分析_整体概况", 11, "设置变量"))
                return
            #endif
        #endif
        #endregion
        #region 内容类型 和 内容来源 选择
        内容类型_相似元素组列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("内容_推荐分析_内容类型相似元素组"), css_selector="", xpath_selector="", is_related_parent=False, parent="", operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("内容_推荐分析_整体概况", 17, "获取相似元素列表(web)"))
        for 当前内容类型 in xbot_visual.workflow.list_iterator(list=内容类型_相似元素组列表, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("内容_推荐分析_整体概况", 18, "ForEach列表循环")):
            if xbot_visual.workflow.test(operand1=当前内容类型.get_text(), operator="==", operand2=内容类型, operator_options="{}", _block=("内容_推荐分析_整体概况", 19, "IF 条件")):
                xbot_visual.web.element.click(browser=web_page, element=当前内容类型, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("内容_推荐分析_整体概况", 20, "点击元素(web)"))
                break
            #endif
        #endloop
        内容来源_相似元素组列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("内容_推荐分析_内容来源相似元素组"), css_selector="", xpath_selector="", is_related_parent=False, parent="", operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("内容_推荐分析_整体概况", 24, "获取相似元素列表(web)"))
        for 当前内容来源 in xbot_visual.workflow.list_iterator(list=内容来源_相似元素组列表, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("内容_推荐分析_整体概况", 25, "ForEach列表循环")):
            if xbot_visual.workflow.test(operand1=当前内容来源.get_text(), operator="==", operand2=内容来源, operator_options="{}", _block=("内容_推荐分析_整体概况", 26, "IF 条件")):
                xbot_visual.web.element.click(browser=web_page, element=当前内容来源, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("内容_推荐分析_整体概况", 27, "点击元素(web)"))
                break
            #endif
        #endloop
        #endregion
        一级_字段列表 = xbot_visual.programing.variable(value=lambda: []
        , _block=("内容_推荐分析_整体概况", 32, "设置变量"))
        一级_数据列表 = xbot_visual.programing.variable(value=lambda: []
        , _block=("内容_推荐分析_整体概况", 33, "设置变量"))
        loop_index = -1
        while True:
            loop_index += 1
            一级_字段列表相似元素组 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("内容_推荐分析_一级字段相似元素组"), css_selector="", xpath_selector="", is_related_parent=False, parent="", operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("内容_推荐分析_整体概况", 35, "获取相似元素列表(web)"))
            一级_数据列表相似元素组 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("内容_推荐分析_一级数据相似元素组"), css_selector="", xpath_selector="", is_related_parent=False, parent="", operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("内容_推荐分析_整体概况", 36, "获取相似元素列表(web)"))
            一级_字段列表.extend(一级_字段列表相似元素组)
            一级_数据列表.extend(一级_数据列表相似元素组)
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("内容_推荐分析_下一页按钮"), _block=("内容_推荐分析_整体概况", 38, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("内容_推荐分析_下一页按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("内容_推荐分析_整体概况", 39, "点击元素(web)"))
            else:
                break
            #endif
        #endloop
        二级_字段列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("内容_推荐分析_二级字段相似元素组"), css_selector="", xpath_selector="", is_related_parent=False, parent="", operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("内容_推荐分析_整体概况", 44, "获取相似元素列表(web)"))
        二级_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("内容_推荐分析_二级数据相似元素组"), css_selector="", xpath_selector="", is_related_parent=False, parent="", operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("内容_推荐分析_整体概况", 45, "获取相似元素列表(web)"))
        一级_字段列表.extend(二级_字段列表)
        一级_数据列表.extend(二级_数据列表)
        输出文件路径 = xbot_visual.programing.variable(value=lambda: "{}\\内容_推荐分析_整体概况_{}.xlsx".format(保存文件夹,页面统计时间)
        , _block=("内容_推荐分析_整体概况", 47, "设置变量"))
        if xbot_visual.file.if_exist(path=输出文件路径, expect_exist="exist", _block=("内容_推荐分析_整体概况", 48, "IF 文件存在")):
            xbot_visual.file.remove(paths=输出文件路径, not_move_to_trash=True, _block=("内容_推荐分析_整体概况", 49, "删除文件"))
        #endif
        excel_instance = xbot_visual.excel.launch(launch_way="create", driver_way="auto_check", open_filename="", save_filename=输出文件路径, isvisible=False, ignoreformula=False, password=xbot_visual.decrypt(""), write_password=xbot_visual.decrypt(""), update_links=False, _block=("内容_推荐分析_整体概况", 51, "打开/新建Excel"))
        xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="area", write_way="append", write_column_way="override", row_num="1", column_name="A", begin_row_num="0", begin_column_name="", content=一级_字段列表, sheet_name="", write_as_text_cols=None, _block=("内容_推荐分析_整体概况", 52, "写入内容至Excel工作表"))
        xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="area", write_way="append", write_column_way="override", row_num="2", column_name="A", begin_row_num="0", begin_column_name="", content=一级_数据列表, sheet_name="", write_as_text_cols=None, _block=("内容_推荐分析_整体概况", 53, "写入内容至Excel工作表"))
        xbot_visual.excel.close(operation="close_specified", excel_instance=excel_instance, close_way="save", filename=None, overwrite_file=True, close_process="office", task_kill=False, _block=("内容_推荐分析_整体概况", 54, "关闭Excel"))
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
