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
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("内容_订阅分析_用户分析", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("内容_订阅分析_用户分析", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/xsite/contentanalysis/subscribe/analysis", ignore_cache=False, load_timeout="20", _block=("内容_订阅分析_用户分析", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("内容_订阅分析_用户分析", 4, "等待"))
        #endregion
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
            "页面统计时间",
        ], _block=("内容_订阅分析_用户分析", 6, "品类/流量/内容-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("内容_订阅分析_用户分析", 8, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("内容_订阅分析_用户分析", 9, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("内容_订阅分析_用户分析", 10, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("内容_订阅分析_用户分析", 11, "设置变量"))
                return
            #endif
        #endif
        #endregion
        xbot_visual.web.element.click(browser=web_page, element=package.selector("内容_订阅分析_用户分析"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("内容_订阅分析_用户分析", 16, "点击元素(web)"))
        #region 网页监听 获取用户分析数据
        xbot_visual.web.browser.start_monitor_network(browser=web_page, url="https://sycm.taobao.com/s_content/snsflow/overview/detail.json?dateType=*&dateRange=*%7C*&indexCode=&_=*&token=*", use_wildcard=True, resource_type="Fetch|XHR", _block=("内容_订阅分析_用户分析", 18, "开始监听网页请求"))
        xbot_visual.web.browser.navigate(browser=web_page, mode="reload", url="", ignore_cache=False, load_timeout="20", _block=("内容_订阅分析_用户分析", 19, "跳转至新网址"))
        response_body_list = xbot_visual.programing.variable(value=lambda: []
        , _block=("内容_订阅分析_用户分析", 20, "设置变量"))
        loop_index = -1
        while True:
            loop_index += 1
            response_body_list = xbot_visual.web.browser.get_responses(browser=web_page, url="", use_wildcard=False, resource_type="All", _block=("内容_订阅分析_用户分析", 22, "获取网页监听结果"))
            if xbot_visual.workflow.test(operand1=len(response_body_list), operator="!=", operand2=lambda: 0, operator_options="{}", _block=("内容_订阅分析_用户分析", 23, "IF 条件")):
                break
            #endif
        #endloop
        xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("内容_订阅分析_用户分析", 27, "停止监听网页请求"))
        数据字典 = xbot_visual.json.to_json(text=lambda: response_body_list[0]["body"], _block=("内容_订阅分析_用户分析", 28, "转换成Json对象"))
        数据字典 = xbot_visual.programing.variable(value=lambda: 数据字典["data"]
        , _block=("内容_订阅分析_用户分析", 29, "设置变量"))
        xbot_visual.programing.log(type="info", text=数据字典, _block=("内容_订阅分析_用户分析", 30, "打印日志"))
        #endregion
        #region 用户分享 数据列表
        用户分享_数据列表 = xbot_visual.programing.variable(value=lambda: []
        , _block=("内容_订阅分析_用户分析", 33, "设置变量"))
        累计订阅粉丝数 = xbot_visual.programing.variable(value=lambda: 数据字典["snsFlwMbrCnt"]["value"]
        , _block=("内容_订阅分析_用户分析", 34, "设置变量"))
        累计星标订阅粉丝数 = xbot_visual.programing.variable(value=lambda: 数据字典["snsStarFlwMbrCnt"]["value"]
        , _block=("内容_订阅分析_用户分析", 35, "设置变量"))
        订阅活跃粉丝数 = xbot_visual.programing.variable(value=lambda: 数据字典["snsActFlwMbrCnt"]["value"]
        , _block=("内容_订阅分析_用户分析", 36, "设置变量"))
        订阅触达粉丝数 = xbot_visual.programing.variable(value=lambda: 数据字典["snsTouchFlwMbrCnt"]["value"]
        , _block=("内容_订阅分析_用户分析", 37, "设置变量"))
        取关粉丝数 = xbot_visual.programing.variable(value=lambda: 数据字典["snsCancelFlwMbrCnt"]["value"]
        , _block=("内容_订阅分析_用户分析", 38, "设置变量"))
        屏蔽粉丝数 = xbot_visual.programing.variable(value=lambda: 数据字典["blockFlwMbrCnt"]["value"]
        , _block=("内容_订阅分析_用户分析", 39, "设置变量"))
        负反馈粉丝数 = xbot_visual.programing.variable(value=lambda: 数据字典["subFeedBackMemCnt"]["value"]
        , _block=("内容_订阅分析_用户分析", 40, "设置变量"))
        订阅粉丝活跃占比 = xbot_visual.programing.variable(value=lambda: 数据字典["snsActFlwMbrRatio"]["value"]
        , _block=("内容_订阅分析_用户分析", 41, "设置变量"))
        xbot_visual.list.append_or_insert(lst=用户分享_数据列表, insert_way="append", index="0", elem=累计订阅粉丝数, _block=("内容_订阅分析_用户分析", 42, "列表插入一项"))
        xbot_visual.list.append_or_insert(lst=用户分享_数据列表, insert_way="append", index="0", elem=累计星标订阅粉丝数, _block=("内容_订阅分析_用户分析", 43, "列表插入一项"))
        xbot_visual.list.append_or_insert(lst=用户分享_数据列表, insert_way="append", index="0", elem=订阅活跃粉丝数, _block=("内容_订阅分析_用户分析", 44, "列表插入一项"))
        xbot_visual.list.append_or_insert(lst=用户分享_数据列表, insert_way="append", index="0", elem=订阅触达粉丝数, _block=("内容_订阅分析_用户分析", 45, "列表插入一项"))
        xbot_visual.list.append_or_insert(lst=用户分享_数据列表, insert_way="append", index="0", elem=取关粉丝数, _block=("内容_订阅分析_用户分析", 46, "列表插入一项"))
        xbot_visual.list.append_or_insert(lst=用户分享_数据列表, insert_way="append", index="0", elem=屏蔽粉丝数, _block=("内容_订阅分析_用户分析", 47, "列表插入一项"))
        xbot_visual.list.append_or_insert(lst=用户分享_数据列表, insert_way="append", index="0", elem=负反馈粉丝数, _block=("内容_订阅分析_用户分析", 48, "列表插入一项"))
        xbot_visual.list.append_or_insert(lst=用户分享_数据列表, insert_way="append", index="0", elem=订阅粉丝活跃占比, _block=("内容_订阅分析_用户分析", 49, "列表插入一项"))
        #endregion
        用户分析_字段列表 = xbot_visual.programing.variable(value=lambda: ["累计订阅粉丝数" , "累计星标订阅粉丝数" , "订阅活跃粉丝数" , "订阅触达粉丝数" , "取关粉丝数" , "屏蔽粉丝数" , "负反馈粉丝数" , "订阅粉丝活跃占比"]
        , _block=("内容_订阅分析_用户分析", 51, "设置变量"))
        输出文件路径 = xbot_visual.programing.variable(value=lambda: "{}\\内容_订阅分析_用户分析_{}.xlsx".format(保存文件夹,页面统计时间)
        , _block=("内容_订阅分析_用户分析", 52, "设置变量"))
        if xbot_visual.file.if_exist(path=输出文件路径, expect_exist="exist", _block=("内容_订阅分析_用户分析", 53, "IF 文件存在")):
            xbot_visual.file.remove(paths=输出文件路径, not_move_to_trash=True, _block=("内容_订阅分析_用户分析", 54, "删除文件"))
        #endif
        excel_instance = xbot_visual.excel.launch(launch_way="create", driver_way="auto_check", open_filename="", save_filename=输出文件路径, isvisible=False, ignoreformula=False, password=xbot_visual.decrypt(""), write_password=xbot_visual.decrypt(""), update_links=False, _block=("内容_订阅分析_用户分析", 56, "打开/新建Excel"))
        xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="area", write_way="append", write_column_way="override", row_num="1", column_name="A", begin_row_num="0", begin_column_name="", content=用户分析_字段列表, sheet_name="", write_as_text_cols=None, _block=("内容_订阅分析_用户分析", 57, "写入内容至Excel工作表"))
        xbot_visual.excel.write_data_to_workbook(workbook=excel_instance, write_range="area", write_way="append", write_column_way="override", row_num="2", column_name="A", begin_row_num="0", begin_column_name="", content=用户分享_数据列表, sheet_name="", write_as_text_cols=None, _block=("内容_订阅分析_用户分析", 58, "写入内容至Excel工作表"))
        xbot_visual.excel.close(operation="close_specified", excel_instance=excel_instance, close_way="save", filename=None, overwrite_file=True, close_process="office", task_kill=False, _block=("内容_订阅分析_用户分析", 59, "关闭Excel"))
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
