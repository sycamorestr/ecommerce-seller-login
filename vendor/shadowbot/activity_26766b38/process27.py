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
        内容来源 = ""
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", None)
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
        内容来源 = args.get("内容来源", "")
    try:
        #region 获取并跳转目标页面
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("内容_光合视频_商品分析", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("内容_光合视频_商品分析", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/xsite/contentanalysis/duanshipin/guanghe_analysis", ignore_cache=False, load_timeout="20", _block=("内容_光合视频_商品分析", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("内容_光合视频_商品分析", 4, "等待"))
        #endregion
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
            "页面统计时间",
        ], _block=("内容_光合视频_商品分析", 6, "品类/流量/内容-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("内容_光合视频_商品分析", 8, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("内容_光合视频_商品分析", 9, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("内容_光合视频_商品分析", 10, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("内容_光合视频_商品分析", 11, "设置变量"))
                return
            #endif
        #endif
        #endregion
        #region 选择对应的内容来源
        内容来源_相似元素组列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("内容_光合图文_内容来源相似元素组"), css_selector="", xpath_selector="", is_related_parent=False, parent="", operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("内容_光合视频_商品分析", 17, "获取相似元素列表(web)"))
        for 当前内容来源 in xbot_visual.workflow.list_iterator(list=内容来源_相似元素组列表, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("内容_光合视频_商品分析", 18, "ForEach列表循环")):
            if xbot_visual.workflow.test(operand1=当前内容来源.get_text(), operator="==", operand2=内容来源, operator_options="{}", _block=("内容_光合视频_商品分析", 19, "IF 条件")):
                xbot_visual.web.element.click(browser=web_page, element=当前内容来源, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("内容_光合视频_商品分析", 20, "点击元素(web)"))
                break
            #endif
        #endloop
        #endregion
        #region 数据下载
        xbot_visual.web.element.click(browser=web_page, element=package.selector("内容_光合视频_商品分析"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("内容_光合视频_商品分析", 26, "点击元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("内容_光合视频_下载"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("内容_光合视频_商品分析", 27, "点击元素(web)"))
        输出文件路径 = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=保存文件夹, use_custom_filename=True, file_name=lambda: "内容_光合视频_商品分析_{}.xls".format(页面统计时间), save_behavior="overwrite", wait_complete=True, wait_complete_timeout="60", simulate=False, clipboard_input=True, input_type="clipboard", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("内容_光合视频_商品分析", 28, "处理下载对话框"))
        xbot_visual.programing.log(type="info", text=输出文件路径, _block=("内容_光合视频_商品分析", 29, "打印日志"))
        #endregion
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
