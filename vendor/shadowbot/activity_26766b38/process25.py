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
        开启页面统计时间校验 = True
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", None)
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
    try:
        #region 获取并跳转目标页面
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("内容_内容概况_内容全局表现", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("内容_内容概况_内容全局表现", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/xsite/contentanalysis/overview_new", ignore_cache=False, load_timeout="20", _block=("内容_内容概况_内容全局表现", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("内容_内容概况_内容全局表现", 4, "等待"))
        #endregion
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("内容_内容概况_下载按钮"), _block=("内容_内容概况_内容全局表现", 6, "IF 元素可见(web)")):
            #region 新版获取
            xbot_visual.web.element.click(browser=web_page, element=package.selector("内容_内容概况_全部内容"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("内容_内容概况_内容全局表现", 8, "点击元素(web)"))
            页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
                "日期": 查询日期,
                }, outputs=[
                "页面统计时间",
            ], _block=("内容_内容概况_内容全局表现", 9, "品类/流量/内容-通用时间选择"))
            #region 功能模块 : 开启页面统计时间校验 
            if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("内容_内容概况_内容全局表现", 11, "IF 条件")):
                _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                    "查询日期": 查询日期,
                    "页面统计时间": 页面统计时间,
                    }, outputs=[
                    "判断结果",
                ], _block=("内容_内容概况_内容全局表现", 12, "调用流程"))
                if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("内容_内容概况_内容全局表现", 13, "IF 条件")):
                    执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                    , _block=("内容_内容概况_内容全局表现", 14, "设置变量"))
                    return
                #endif
            #endif
            #endregion
            xbot_visual.web.element.click(browser=web_page, element=package.selector("内容_内容概况_下载按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("内容_内容概况_内容全局表现", 19, "点击元素(web)"))
            download_file_name = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=保存文件夹, use_custom_filename=True, file_name=lambda: "内容_内容概况_内容全局表现_{}.xlsx".format(页面统计时间), save_behavior="overwrite", wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("内容_内容概况_内容全局表现", 20, "处理下载对话框"))
            输出文件路径 = xbot_visual.programing.variable(value=lambda: "{}\\内容_内容概况_内容全局表现_{}.xlsx".format(保存文件夹,页面统计时间)
            , _block=("内容_内容概况_内容全局表现", 21, "设置变量"))
            #endregion
        else:
            #region 旧版获取
            xbot_visual.web.browser.start_monitor_network(browser=web_page, url="https://sycm.taobao.com/s_content/portal/board/core/index.json?*", use_wildcard=True, resource_type="Fetch|XHR", _block=("内容_内容概况_内容全局表现", 25, "开始监听网页请求"))
            页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
                "日期": 查询日期,
                }, outputs=[
                "页面统计时间",
            ], _block=("内容_内容概况_内容全局表现", 26, "品类/流量/内容-通用时间选择"))
            #region 功能模块 : 开启页面统计时间校验 
            if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("内容_内容概况_内容全局表现", 28, "IF 条件")):
                _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                    "查询日期": 查询日期,
                    "页面统计时间": 页面统计时间,
                    }, outputs=[
                    "判断结果",
                ], _block=("内容_内容概况_内容全局表现", 29, "调用流程"))
                if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("内容_内容概况_内容全局表现", 30, "IF 条件")):
                    执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                    , _block=("内容_内容概况_内容全局表现", 31, "设置变量"))
                    return
                #endif
            #endif
            #endregion
            #region 网页监听 获取数据
            response_body_list = xbot_visual.programing.variable(value=lambda: []
            , _block=("内容_内容概况_内容全局表现", 37, "设置变量"))
            response_body_list = xbot_visual.web.browser.get_responses(browser=web_page, url="", use_wildcard=False, resource_type="All", _block=("内容_内容概况_内容全局表现", 38, "获取网页监听结果"))
            xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("内容_内容概况_内容全局表现", 39, "停止监听网页请求"))
            http_response = xbot_visual.web_service.rest_request(url=lambda: response_body_list[0]['url'], method="GET", headers=None, body=None, save_to_file=False, save_folder=None, save_filename=None, connect_timeout_seconds="30", send_by_web=True, browser=web_page, _block=("内容_内容概况_内容全局表现", 40, "Http 请求"))
            数据字典 = xbot_visual.json.to_json(text=lambda: http_response.content, _block=("内容_内容概况_内容全局表现", 41, "转换成Json对象"))
            xbot_visual.programing.log(type="info", text=数据字典, _block=("内容_内容概况_内容全局表现", 42, "打印日志"))
            数据字典 = xbot_visual.programing.variable(value=lambda: 数据字典["data"]["self"]
            , _block=("内容_内容概况_内容全局表现", 43, "设置变量"))
            xbot_visual.programing.log(type="info", text=数据字典, _block=("内容_内容概况_内容全局表现", 44, "打印日志"))
            #endregion
            #region 生成数据列表  写入数据
            内容种草人数 = xbot_visual.programing.variable(value=lambda: 数据字典["contentInterestUv"]["value"]
            , _block=("内容_内容概况_内容全局表现", 47, "设置变量"))
            种草粉丝人数 = xbot_visual.programing.variable(value=lambda: 数据字典["interestFansCnt"]["value"]
            , _block=("内容_内容概况_内容全局表现", 48, "设置变量"))
            种草成交金额 = xbot_visual.programing.variable(value=lambda: 数据字典["interestPayAmt"]["value"]
            , _block=("内容_内容概况_内容全局表现", 49, "设置变量"))
            占比全店支付金额 = xbot_visual.programing.variable(value=lambda: 数据字典["interestPayAmtShopRatio"]["value"]
            , _block=("内容_内容概况_内容全局表现", 50, "设置变量"))
            内容引导访客数 = xbot_visual.programing.variable(value=lambda: 数据字典["portalContentGuideUv"]["value"]
            , _block=("内容_内容概况_内容全局表现", 51, "设置变量"))
            占比全店访客数 = xbot_visual.programing.variable(value=lambda: 数据字典["contentUvShopRatio"]["value"]
            , _block=("内容_内容概况_内容全局表现", 52, "设置变量"))
            累计粉丝数 = xbot_visual.programing.variable(value=lambda: 数据字典["totalFans"]["value"]
            , _block=("内容_内容概况_内容全局表现", 53, "设置变量"))
            内容全局表现_字段列表 = xbot_visual.programing.variable(value=lambda: ["内容种草人数" , "种草粉丝人数" , "种草成交金额" , "占比全店支付金额" , "内容引导访客数" , "占比全店访客数" , "累计粉丝数"]
            , _block=("内容_内容概况_内容全局表现", 54, "设置变量"))
            内容全局表现_数据列表 = xbot_visual.programing.variable(value=lambda: []
            , _block=("内容_内容概况_内容全局表现", 55, "设置变量"))
            xbot_visual.list.append_or_insert(lst=内容全局表现_数据列表, insert_way="append", index="0", elem=内容种草人数, _block=("内容_内容概况_内容全局表现", 56, "列表插入一项"))
            xbot_visual.list.append_or_insert(lst=内容全局表现_数据列表, insert_way="append", index="0", elem=种草粉丝人数, _block=("内容_内容概况_内容全局表现", 57, "列表插入一项"))
            xbot_visual.list.append_or_insert(lst=内容全局表现_数据列表, insert_way="append", index="0", elem=种草成交金额, _block=("内容_内容概况_内容全局表现", 58, "列表插入一项"))
            xbot_visual.list.append_or_insert(lst=内容全局表现_数据列表, insert_way="append", index="0", elem=占比全店支付金额, _block=("内容_内容概况_内容全局表现", 59, "列表插入一项"))
            xbot_visual.list.append_or_insert(lst=内容全局表现_数据列表, insert_way="append", index="0", elem=内容引导访客数, _block=("内容_内容概况_内容全局表现", 60, "列表插入一项"))
            xbot_visual.list.append_or_insert(lst=内容全局表现_数据列表, insert_way="append", index="0", elem=占比全店访客数, _block=("内容_内容概况_内容全局表现", 61, "列表插入一项"))
            xbot_visual.list.append_or_insert(lst=内容全局表现_数据列表, insert_way="append", index="0", elem=累计粉丝数, _block=("内容_内容概况_内容全局表现", 62, "列表插入一项"))
            输出文件路径 = xbot_visual.programing.variable(value=lambda: "{}\\内容_内容概况_内容全局表现_{}.xlsx".format(保存文件夹,页面统计时间)
            , _block=("内容_内容概况_内容全局表现", 63, "设置变量"))
            if xbot_visual.file.if_exist(path=输出文件路径, expect_exist="exist", _block=("内容_内容概况_内容全局表现", 64, "IF 文件存在")):
                xbot_visual.file.remove(paths=输出文件路径, not_move_to_trash=True, _block=("内容_内容概况_内容全局表现", 65, "删除文件"))
            #endif
            excel_instance = xbot_visual.excel.launch(launch_way="create", driver_way="auto_check", open_filename="", save_filename=输出文件路径, isvisible=False, ignoreformula=False, password=xbot_visual.decrypt(""), write_password=xbot_visual.decrypt(""), update_links=False, _block=("内容_内容概况_内容全局表现", 67, "打开/新建Excel"))
            xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="area", write_way="append", write_column_way="override", row_num="1", column_name="A", begin_row_num="0", begin_column_name="", content=内容全局表现_字段列表, sheet_name="", write_as_text_cols=None, _block=("内容_内容概况_内容全局表现", 68, "写入内容至Excel工作表"))
            xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="area", write_way="append", write_column_way="override", row_num="2", column_name="A", begin_row_num="0", begin_column_name="", content=内容全局表现_数据列表, sheet_name="", write_as_text_cols=None, _block=("内容_内容概况_内容全局表现", 69, "写入内容至Excel工作表"))
            xbot_visual.excel.close(operation="close_specified", excel_instance=excel_instance, close_way="save", filename=None, overwrite_file=True, close_process="office", task_kill=False, _block=("内容_内容概况_内容全局表现", 70, "关闭Excel"))
            #endregion
            #endregion
        #endif
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
