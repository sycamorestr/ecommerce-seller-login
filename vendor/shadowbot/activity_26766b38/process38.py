import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    流量来源排行TOP10_数据列表 = []
    输出文件路径 = ""
    执行状态 = "成功"
    if args is None:
        查询日期 = "2024-10-23"
        保存文件夹 = "C:\\Users\\charleskeith\\Downloads\\demo"
        开启页面统计时间校验 = True
    else:
        查询日期 = args.get("查询日期", "2024-10-23")
        保存文件夹 = args.get("保存文件夹", "C:\\Users\\charleskeith\\Downloads\\demo")
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
    try:
        #region 获取并跳转目标页面
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("流量_流量看板_流量来源排行TOP10", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("流量_流量看板_流量来源排行TOP10", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/flow/monitor/overview", ignore_cache=False, load_timeout="20", _block=("流量_流量看板_流量来源排行TOP10", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("流量_流量看板_流量来源排行TOP10", 4, "等待"))
        #endregion
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
            "页面统计时间",
        ], _block=("流量_流量看板_流量来源排行TOP10", 6, "品类/流量/内容-通用时间选择"))
        # xbot_extensions.web_action.select_date
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("流量_流量看板_流量来源排行TOP10", 9, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("流量_流量看板_流量来源排行TOP10", 10, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("流量_流量看板_流量来源排行TOP10", 11, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("流量_流量看板_流量来源排行TOP10", 12, "设置变量"))
                return
            #endif
        #endif
        #endregion
        loop_index = -1
        while True:
            loop_index += 1
            try:
                # web.element.get_element
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("流量来源排行_返回旧版"), _block=("流量_流量看板_流量来源排行TOP10", 20, "IF 元素可见(web)")):
                    表格 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("流量来源排行Top10_表格"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="3", _block=("流量_流量看板_流量来源排行TOP10", 21, "获取元素对象(web)"))
                    break
                #endif
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("流量来源排行_前往新版"), _block=("流量_流量看板_流量来源排行TOP10", 24, "IF 元素可见(web)")):
                    表格 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("流量来源排行_表格（旧版）"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="3", _block=("流量_流量看板_流量来源排行TOP10", 25, "获取元素对象(web)"))
                    break
                #endif
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("流量_流量看板_流量来源排行TOP10", 29, "等待"))
                xbot_visual.web.browser.scroll_to(browser=web_page, scroll_on_element=False, element=None, search_up=False, location="screen", behavior="smooth", left="0", top="0", timeout="20", _block=("流量_流量看板_流量来源排行TOP10", 30, "鼠标滚动网页"))
            #endtry
        #endloop
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("流量_流量看板_流量来源排行TOP10", 33, "等待"))
        流量来源排行TOP10_数据列表 = xbot_visual.list.create(_block=("流量_流量看板_流量来源排行TOP10", 34, "新建列表"))
        表格 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class,\"card-header\")]//*[contains(.,\"流量来源排行\")]/../..//tbody", is_related_parent=False, parent=None, timeout="20", _block=("流量_流量看板_流量来源排行TOP10", 35, "获取元素对象(web)"))
        每个商品信息 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=表格, css_selector="", xpath_selector="./tr", is_related_parent=True, parent=表格, operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("流量_流量看板_流量来源排行TOP10", 36, "获取相似元素列表(web)"))
        for 排名, loop_item in enumerate(xbot_visual.workflow.list_iterator(list=每个商品信息, loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("流量_流量看板_流量来源排行TOP10", 37, "ForEach列表循环"))):
            temp_list = xbot_visual.list.create(_block=("流量_流量看板_流量来源排行TOP10", 38, "新建列表"))
            xbot_visual.list.append_or_insert(lst=temp_list, insert_way="append", index="0", elem=lambda: 排名 + 1, _block=("流量_流量看板_流量来源排行TOP10", 39, "列表插入一项"))
            td元素 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=loop_item, css_selector="", xpath_selector="./td", is_related_parent=True, parent=loop_item, operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("流量_流量看板_流量来源排行TOP10", 40, "获取相似元素列表(web)"))
            for loop_item_index2, loop_item2 in enumerate(xbot_visual.workflow.list_iterator(list=td元素, loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("流量_流量看板_流量来源排行TOP10", 41, "ForEach列表循环"))):
                if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": loop_item_index2,"operand2": "0","operator": ">"},{"operand1": loop_item_index2,"operand2": "5","operator": "<"}], _block=("流量_流量看板_流量来源排行TOP10", 42, "IF 多条件")):
                    xbot_visual.list.append_or_insert(lst=temp_list, insert_way="append", index="0", elem=loop_item2.get_text(), _block=("流量_流量看板_流量来源排行TOP10", 43, "列表插入一项"))
                #endif
            #endloop
            xbot_visual.list.append_or_insert(lst=流量来源排行TOP10_数据列表, insert_way="append", index="0", elem=temp_list, _block=("流量_流量看板_流量来源排行TOP10", 46, "列表插入一项"))
        #endloop
        输出文件路径 = xbot_visual.programing.variable(value=lambda: "{}\\流量_流量看板_流量来源排行TOP10_{}.xlsx".format(保存文件夹,查询日期)
        , _block=("流量_流量看板_流量来源排行TOP10", 48, "设置变量"))
        流量来源_字段列表 = xbot_visual.programing.variable(value=lambda: ["排名", "来源名称" , "访客数" , "下单买家数" , "下单转化率"]
        , _block=("流量_流量看板_流量来源排行TOP10", 49, "设置变量"))
        if xbot_visual.file.if_exist(path=输出文件路径, expect_exist="exist", _block=("流量_流量看板_流量来源排行TOP10", 50, "IF 文件存在")):
            xbot_visual.file.remove(paths=输出文件路径, not_move_to_trash=True, _block=("流量_流量看板_流量来源排行TOP10", 51, "删除文件"))
        #endif
        excel_instance = xbot_visual.excel.launch(launch_way="create", driver_way="auto_check", open_filename="", save_filename=输出文件路径, isvisible=False, ignoreformula=False, password=xbot_visual.decrypt(""), write_password=xbot_visual.decrypt(""), update_links=False, _block=("流量_流量看板_流量来源排行TOP10", 53, "打开/新建Excel"))
        xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="area", write_way="append", write_column_way="override", row_num="1", column_name="A", begin_row_num="0", begin_column_name="", content=流量来源_字段列表, sheet_name="", write_as_text_cols=None, _block=("流量_流量看板_流量来源排行TOP10", 54, "写入内容至Excel工作表"))
        xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="area", write_way="append", write_column_way="override", row_num="2", column_name="A", begin_row_num="0", begin_column_name="", content=流量来源排行TOP10_数据列表, sheet_name="", write_as_text_cols=None, _block=("流量_流量看板_流量来源排行TOP10", 55, "写入内容至Excel工作表"))
        xbot_visual.excel.close(operation="close_specified", excel_instance=excel_instance, close_way="save", filename=None, overwrite_file=True, close_process="office", task_kill=False, _block=("流量_流量看板_流量来源排行TOP10", 56, "关闭Excel"))
        xbot_visual.programing.log(type="info", text=lambda: "文件路径：{}".format(输出文件路径), _block=("流量_流量看板_流量来源排行TOP10", 57, "打印日志"))
    finally:
        args["流量来源排行TOP10_数据列表"] = 流量来源排行TOP10_数据列表
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
