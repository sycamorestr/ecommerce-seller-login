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
        开启页面统计时间校验 = True
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", "")
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
    try:
        #region 获取网页进行跳转
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("品类-宏观监控核心指标监控数据获取", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("品类-宏观监控核心指标监控数据获取", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/cc/macro_monitor", ignore_cache=False, load_timeout="20", _block=("品类-宏观监控核心指标监控数据获取", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("品类-宏观监控核心指标监控数据获取", 4, "等待"))
        #endregion
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
            "页面统计时间",
        ], _block=("品类-宏观监控核心指标监控数据获取", 6, "品类/流量/内容-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("品类-宏观监控核心指标监控数据获取", 8, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("品类-宏观监控核心指标监控数据获取", 9, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("品类-宏观监控核心指标监控数据获取", 10, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("品类-宏观监控核心指标监控数据获取", 11, "设置变量"))
                return
            #endif
        #endif
        #endregion
        #region 数据文件下载
        输出文件路径 = xbot_visual.web.element.download(browser=web_page, scene="Button", download_button=package.selector("品类-宏观监控-核心指标监控下载按钮"), download_url=None, file_folder=保存文件夹, use_custom_filename=True, file_name="品类宏观监控商品效率核心指标_" + xbot_visual.sh_str(页面统计时间) + ".xls", save_behavior="overwrite", wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_dialog_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("品类-宏观监控核心指标监控数据获取", 17, "下载文件"))
        # web.handle_save_dialog
        xbot_visual.programing.log(type="info", text="文件输出路径: " + xbot_visual.sh_str(输出文件路径), _block=("品类-宏观监控核心指标监控数据获取", 19, "打印日志"))
        #endregion
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
