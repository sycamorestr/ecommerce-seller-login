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
        抓取的页码数 = 5
        开启页面统计时间校验 = True
        等待时间 = "3"
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", None)
        抓取的页码数 = args.get("抓取的页码数", 5)
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
        等待时间 = args.get("等待时间", "3")
    try:
        response_body_list = xbot_visual.programing.variable(value=lambda: []
        , _block=("流量_商品来源_本店商品排行榜", 1, "设置变量"))
        整体访客榜_数据列表 = xbot_visual.programing.variable(value=lambda: []
        , _block=("流量_商品来源_本店商品排行榜", 2, "设置变量"))
        #region 获取并跳转目标页面
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("流量_商品来源_本店商品排行榜", 4, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("流量_商品来源_本店商品排行榜", 4,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/flow/monitor/itemsource", ignore_cache=False, load_timeout="20", _block=("流量_商品来源_本店商品排行榜", 5, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("流量_商品来源_本店商品排行榜", 6, "等待"))
        #endregion
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
            "页面统计时间",
        ], _block=("流量_商品来源_本店商品排行榜", 8, "品类/流量/内容-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("流量_商品来源_本店商品排行榜", 10, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("流量_商品来源_本店商品排行榜", 11, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("流量_商品来源_本店商品排行榜", 12, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("流量_商品来源_本店商品排行榜", 13, "设置变量"))
                return
            #endif
        #endif
        #endregion
        页码_相似元素组列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("流量_商品来源_页码相似元素组"), css_selector="", xpath_selector="", is_related_parent=False, parent="", operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("流量_商品来源_本店商品排行榜", 18, "获取相似元素列表(web)"))
        最大页码 = xbot_visual.programing.variable(value=lambda: 页码_相似元素组列表[-1]
        , _block=("流量_商品来源_本店商品排行榜", 19, "设置变量"))
        if xbot_visual.workflow.test(operand1=抓取的页码数, operator=">", operand2=最大页码, operator_options="{}", _block=("流量_商品来源_本店商品排行榜", 20, "IF 条件")):
            raise Exception("抓取页码数大于最大页码数")
        #endif
        for loop_index2 in xbot_visual.workflow.range_iterator(start="1", stop=抓取的页码数, step="1", _block=("流量_商品来源_本店商品排行榜", 23, "For次数循环")):
            #region 网络监听 获取数据
            xbot_visual.web.browser.start_monitor_network(browser=web_page, url="https://sycm.taobao.com/flow/new/monitor/item/tops/rank.json?dateRange=*%7C*&dateType=*&pageSize=10&page=*&order=desc&orderBy=uv&device=2&indexCode=uv%2CpayOrderByrCnt%2CpayRate&_=*&token=*", use_wildcard=True, resource_type="Fetch|XHR", _block=("流量_商品来源_本店商品排行榜", 25, "开始监听网页请求"))
            if xbot_visual.workflow.test(operand1=loop_index2, operator="==", operand2=lambda: 1, operator_options="{}", _block=("流量_商品来源_本店商品排行榜", 26, "IF 条件")):
                xbot_visual.web.browser.navigate(browser=web_page, mode="reload", url="", ignore_cache=False, load_timeout="20", _block=("流量_商品来源_本店商品排行榜", 27, "跳转至新网址"))
            else:
                xbot_visual.programing.sleep(random_number=True, seconds="1", start_number="1", stop_number="2", _block=("流量_商品来源_本店商品排行榜", 29, "等待"))
                xbot_visual.web.element.click(browser=web_page, element=package.selector("流量_商品来源_下一页按钮"), simulate=False, move_mouse=True, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_商品来源_本店商品排行榜", 30, "点击元素(web)"))
            #endif
            xbot_visual.programing.sleep(random_number=False, seconds=等待时间, start_number="1", stop_number="5", _block=("流量_商品来源_本店商品排行榜", 32, "等待"))
            loop_index = -1
            while True:
                loop_index += 1
                response_body_list = xbot_visual.web.browser.get_responses(browser=web_page, url="", use_wildcard=False, resource_type="All", _block=("流量_商品来源_本店商品排行榜", 34, "获取网页监听结果"))
                if xbot_visual.workflow.test(operand1=len(response_body_list), operator="!=", operand2=lambda: 0, operator_options="{}", _block=("流量_商品来源_本店商品排行榜", 35, "IF 条件")):
                    break
                #endif
            #endloop
            xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("流量_商品来源_本店商品排行榜", 39, "停止监听网页请求"))
            # programing.log
            数据字典 = xbot_visual.json.to_json(text=lambda: response_body_list[0]["body"], _block=("流量_商品来源_本店商品排行榜", 41, "转换成Json对象"))
            数据列表 = xbot_visual.programing.variable(value=lambda: 数据字典["data"]["data"]
            , _block=("流量_商品来源_本店商品排行榜", 42, "设置变量"))
            # programing.log
            #endregion
            for 当前数据_index, 当前数据 in enumerate(xbot_visual.workflow.list_iterator(list=数据列表, loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("流量_商品来源_本店商品排行榜", 45, "ForEach列表循环"))):
                list_instance = xbot_visual.list.create(_block=("流量_商品来源_本店商品排行榜", 46, "新建列表"))
                排名 = xbot_visual.programing.variable(value=lambda: 当前数据_index+1+(loop_index2-1)*10
                , _block=("流量_商品来源_本店商品排行榜", 47, "设置变量"))
                商品名称 = xbot_visual.programing.variable(value=lambda: 当前数据["item"].get("title", "该商品已下架，暂无法获取商品信息")
                , _block=("流量_商品来源_本店商品排行榜", 48, "设置变量"))
                商品ID = xbot_visual.programing.variable(value=lambda: 当前数据["item"].get("itemId", "")
                , _block=("流量_商品来源_本店商品排行榜", 49, "设置变量"))
                商品url = xbot_visual.programing.variable(value=lambda: 当前数据["item"].get("detailUrl", "")
                , _block=("流量_商品来源_本店商品排行榜", 50, "设置变量"))
                访客数 = xbot_visual.programing.variable(value=lambda: 当前数据["uv"].get("value", "")
                , _block=("流量_商品来源_本店商品排行榜", 51, "设置变量"))
                支付买家数 = xbot_visual.programing.variable(value=lambda: 当前数据["payOrderByrCnt"]["value"]
                , _block=("流量_商品来源_本店商品排行榜", 52, "设置变量"))
                支付转化率 = xbot_visual.programing.variable(value=lambda: 当前数据["payRate"]["value"]
                , _block=("流量_商品来源_本店商品排行榜", 53, "设置变量"))
                xbot_visual.list.append_or_insert(lst=list_instance, insert_way="append", index="0", elem=排名, _block=("流量_商品来源_本店商品排行榜", 54, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=list_instance, insert_way="append", index="0", elem=商品名称, _block=("流量_商品来源_本店商品排行榜", 55, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=list_instance, insert_way="append", index="0", elem=商品ID, _block=("流量_商品来源_本店商品排行榜", 56, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=list_instance, insert_way="append", index="0", elem=商品url, _block=("流量_商品来源_本店商品排行榜", 57, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=list_instance, insert_way="append", index="0", elem=访客数, _block=("流量_商品来源_本店商品排行榜", 58, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=list_instance, insert_way="append", index="0", elem=支付买家数, _block=("流量_商品来源_本店商品排行榜", 59, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=list_instance, insert_way="append", index="0", elem=支付转化率, _block=("流量_商品来源_本店商品排行榜", 60, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=整体访客榜_数据列表, insert_way="append", index="0", elem=list_instance, _block=("流量_商品来源_本店商品排行榜", 61, "列表插入一项"))
            #endloop
        #endloop
        本店商品排行榜_数据字段列表 = xbot_visual.programing.variable(value=lambda: ["排名" , "商品名称" , "商品ID" , "商品URL" , "访客数" , "支付买家数" , "支付转化率"]
        , _block=("流量_商品来源_本店商品排行榜", 64, "设置变量"))
        输出文件路径 = xbot_visual.programing.variable(value=lambda: "{}\\流量_商品来源_本店商品排行榜_{}.xlsx".format(保存文件夹,查询日期)
        , _block=("流量_商品来源_本店商品排行榜", 65, "设置变量"))
        if xbot_visual.file.if_exist(path=输出文件路径, expect_exist="exist", _block=("流量_商品来源_本店商品排行榜", 66, "IF 文件存在")):
            xbot_visual.file.remove(paths=输出文件路径, not_move_to_trash=True, _block=("流量_商品来源_本店商品排行榜", 67, "删除文件"))
        #endif
        excel_instance = xbot_visual.excel.launch(launch_way="create", driver_way="auto_check", open_filename="", save_filename=输出文件路径, isvisible=False, ignoreformula=False, password=xbot_visual.decrypt(""), write_password=xbot_visual.decrypt(""), update_links=False, _block=("流量_商品来源_本店商品排行榜", 69, "打开/新建Excel"))
        xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="area", write_way="append", write_column_way="override", row_num="1", column_name="A", begin_row_num="0", begin_column_name="", content=本店商品排行榜_数据字段列表, sheet_name="", write_as_text_cols=None, _block=("流量_商品来源_本店商品排行榜", 70, "写入内容至Excel工作表"))
        xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="area", write_way="append", write_column_way="override", row_num="2", column_name="A", begin_row_num="0", begin_column_name="", content=整体访客榜_数据列表, sheet_name="", write_as_text_cols=None, _block=("流量_商品来源_本店商品排行榜", 71, "写入内容至Excel工作表"))
        xbot_visual.excel.close(operation="close_specified", excel_instance=excel_instance, close_way="save", filename=None, overwrite_file=True, close_process="office", task_kill=False, _block=("流量_商品来源_本店商品排行榜", 72, "关闭Excel"))
        xbot_visual.programing.log(type="info", text=lambda: "文件路径：{}".format(输出文件路径), _block=("流量_商品来源_本店商品排行榜", 73, "打印日志"))
        # programing.databook.remove_all_rows
        # programing.databook.write_data_to_workbook
        # programing.databook.write_data_to_workbook
        # programing.databook.export_data
        # programing.log
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
