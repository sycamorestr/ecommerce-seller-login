import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    run_status = False
    err_msg = ""
    download_file_path = ""
    if args is None:
        网页对象 = None
        保存文件夹 = ""
        保存文件名 = ""
        下载类型 = ""
        起始日期 = ""
        等待时间 = "300"
        结束日期 = ""
    else:
        网页对象 = args.get("网页对象", None)
        保存文件夹 = args.get("保存文件夹", "")
        保存文件名 = args.get("保存文件名", "")
        下载类型 = args.get("下载类型", "")
        起始日期 = args.get("起始日期", "")
        等待时间 = args.get("等待时间", "300")
        结束日期 = args.get("结束日期", "")
    try:
        invoke_result = xbot_visual.process.invoke_module(module="_reportcentral_api", package=__name__, function="customer_returns", params={
            "web_page": 网页对象,
            "save_dir": 保存文件夹,
            "save_name": 保存文件名,
            "start_date": 起始日期,
            "end_date": 结束日期,
            "report_type": 下载类型,
            "wait_time": 等待时间,
        }, _block=("C1 买家退货", 1, "调用模块"))
        run_status = xbot_visual.programing.variable(value=lambda: invoke_result[0]
        , _block=("C1 买家退货", 2, "设置变量"))
        err_msg = xbot_visual.programing.variable(value=lambda: invoke_result[1]
        , _block=("C1 买家退货", 3, "设置变量"))
        download_file_path = xbot_visual.programing.variable(value=lambda: invoke_result[2]
        , _block=("C1 买家退货", 4, "设置变量"))
        try:
            software_window = xbot_visual.win32.window.get(window_type="win_title_or_class", selector=None, handle="", title="另存为", handle_checked=False, class_name="", use_wildcard=False, _block=("C1 买家退货", 5, "获取窗口对象"))
        except Exception as e:
            pass
            software_window = None
        if xbot_visual.workflow.test(operand1=software_window, operator="!=", operand2="None", operator_options="{}", _block=("C1 买家退货", 6, "IF 条件")):
            xbot_visual.win32.send_keys(keys="{ESCAPE}", hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("C1 买家退货", 7, "键盘输入"))
        #endif
    finally:
        args["run_status"] = run_status
        args["err_msg"] = err_msg
        args["download_file_path"] = download_file_path
