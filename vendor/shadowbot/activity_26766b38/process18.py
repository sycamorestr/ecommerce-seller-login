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
        保存文件夹 = ""
        质量明细类型 = ""
        开启页面统计时间校验 = True
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", "")
        质量明细类型 = args.get("质量明细类型", "")
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
    try:
        #region 跳转至目标页面
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("服务-绩效明细-质量明细数据获取", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("服务-绩效明细-质量明细数据获取", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/qos/service/frame/performance/detail/new", ignore_cache=False, load_timeout="20", _block=("服务-绩效明细-质量明细数据获取", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("服务-绩效明细-质量明细数据获取", 4, "等待"))
        #endregion
        # 此处插入时间选择&校验指令
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process7", package=__name__, inputs={
            "日期": 查询日期,
            "web_page": "",
            }, outputs=[
            "页面统计时间",
        ], _block=("服务-绩效明细-质量明细数据获取", 7, "服务-绩效-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("服务-绩效明细-质量明细数据获取", 9, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("服务-绩效明细-质量明细数据获取", 10, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("服务-绩效明细-质量明细数据获取", 11, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("服务-绩效明细-质量明细数据获取", 12, "设置变量"))
                return
            #endif
        #endif
        #endregion
        #region 质量明细类型选择
        xbot_visual.web.element.click(browser=web_page, element=package.selector("服务-绩效明细-质量明细"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="2", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("服务-绩效明细-质量明细数据获取", 18, "点击元素(web)"))
        package.variables['服务_通用类型'] = xbot_visual.programing.variable(value=质量明细类型
        , _block=("服务-绩效明细-质量明细数据获取", 19, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("服务-绩效明细-质量明细-类型动态元素"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="2", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("服务-绩效明细-质量明细数据获取", 20, "点击元素(web)"))
        #endregion
        #region 处理下载对话框
        xbot_visual.web.element.click(browser=web_page, element=package.selector("服务-绩效-通用下载"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("服务-绩效明细-质量明细数据获取", 23, "点击元素(web)"))
        web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("服务-绩效明细-二次下载"), state="appear", iswait=True, timeout="20", _block=("服务-绩效明细-质量明细数据获取", 24, "等待元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("服务-绩效明细-二次下载"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("服务-绩效明细-质量明细数据获取", 25, "点击元素(web)"))
        输出文件路径 = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=保存文件夹, use_custom_filename=True, file_name="绩效质量明细_" + xbot_visual.sh_str(glv['服务_通用类型']) + "_" + xbot_visual.sh_str(页面统计时间) + ".xlsx", save_behavior="overwrite", wait_complete=True, wait_complete_timeout="30", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("服务-绩效明细-质量明细数据获取", 26, "处理下载对话框"))
        xbot_visual.programing.log(type="info", text=输出文件路径, _block=("服务-绩效明细-质量明细数据获取", 27, "打印日志"))
        #endregion
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
