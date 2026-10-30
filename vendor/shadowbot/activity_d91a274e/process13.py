import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    file_path = ""
    if args is None:
        web_page = None
        日期 = ""
        周期 = ""
        效果 = ""
        文件保存路径 = ""
    else:
        web_page = args.get("web_page", None)
        日期 = args.get("日期", "")
        周期 = args.get("周期", "")
        效果 = args.get("效果", "")
        文件保存路径 = args.get("文件保存路径", "")
    try:
        xbot_visual.web.browser.wait_load_completed(browser=web_page, load_timeout="20", action_after_load_timeout="handleExcept", _block=("A4 品销宝", 1, "等待网页加载完成"))
        #region 周期选择
        package.variables['conversion_cycle'] = xbot_visual.programing.variable(value=周期
        , _block=("A4 品销宝", 3, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("品销宝_报表_转化周期下拉框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A4 品销宝", 4, "点击元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("品销宝_报表_转化周期选择"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A4 品销宝", 5, "点击元素(web)"))
        #endregion
        #region 效果选择
        package.variables['effect_select'] = xbot_visual.programing.variable(value=效果
        , _block=("A4 品销宝", 8, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("品销宝_报表_展现效果下拉框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A4 品销宝", 9, "点击元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("品销宝_报表_效果选择"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A4 品销宝", 10, "点击元素(web)"))
        #endregion
        # programing.raise
        xbot_visual.process.run(process="xbot_extensions.activity_d65f9fd7.process32", package=__name__, inputs={
            "web_page": web_page,
            "日期": 日期,
            }, outputs=[
        ], _block=("A4 品销宝", 13, "品销宝报表日期选择(新)"))
        if xbot_visual.workflow.test(operand1=文件保存路径, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("A4 品销宝", 14, "IF 条件")):
            文件保存路径 = xbot_visual.dir.get_special_dir(special_dir_name="DesktopDirectory", _block=("A4 品销宝", 15, "获取系统文件夹路径"))
        #endif
        current_datetime = xbot_visual.datetime.now(_block=("A4 品销宝", 17, "获取当前日期时间"))
        current_time = xbot_visual.datetime.to_string(datetime=current_datetime, format="%Y%m%d%H%M%S", _block=("A4 品销宝", 18, "日期时间转换为文本"))
        文件名 = xbot_visual.programing.variable(value="品销宝_报表_明星店铺报表_" + xbot_visual.sh_str(current_time) + ".xlsx"
        , _block=("A4 品销宝", 19, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("品销宝_报表_下载报表按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A4 品销宝", 20, "点击元素(web)"))
        file_path = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=文件保存路径, use_custom_filename=True, file_name=文件名, save_behavior="overwrite", wait_complete=False, wait_complete_timeout="", simulate=False, clipboard_input=True, input_type="clipboard", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("A4 品销宝", 21, "处理下载对话框"))
        _ = xbot_visual.process.run(process="process19", package=__name__, inputs={
            "文件保存路径": 文件保存路径,
            "文件名": 文件名,
            }, outputs=[
        ], _block=("A4 品销宝", 22, "调用流程"))
    finally:
        args["file_path"] = file_path
