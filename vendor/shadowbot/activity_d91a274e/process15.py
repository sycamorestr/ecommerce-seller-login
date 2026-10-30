import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    file_path = ""
    if args is None:
        日期 = ""
        周期 = ""
        效果 = ""
        web_page = None
        文件保存路径 = ""
    else:
        日期 = args.get("日期", "")
        周期 = args.get("周期", "")
        效果 = args.get("效果", "")
        web_page = args.get("web_page", None)
        文件保存路径 = args.get("文件保存路径", "")
    try:
        效果列表 = xbot_visual.programing.variable(value=lambda: ['点击效果','展现效果']
        , _block=("A5 超级钻展", 1, "设置变量"))
        周期列表 = xbot_visual.programing.variable(value=lambda: ['效果转化周期 - 3天','效果转化周期 - 7天','效果转化周期 - 15天','效果转化周期 - 30天']
        , _block=("A5 超级钻展", 2, "设置变量"))
        #region 周期选择
        package.variables['conversion_cycle'] = xbot_visual.programing.variable(value=周期
        , _block=("A5 超级钻展", 4, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("超级钻展_报表_转化周期选择下拉框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A5 超级钻展", 5, "点击元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("超级钻展_报表_周期选择"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A5 超级钻展", 6, "点击元素(web)"))
        #endregion
        #region 效果选择
        package.variables['effect_select'] = xbot_visual.programing.variable(value=效果
        , _block=("A5 超级钻展", 9, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("超级钻展_报表_效果选择下拉框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A5 超级钻展", 10, "点击元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("超级钻展_报表_效果选择"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A5 超级钻展", 11, "点击元素(web)"))
        #endregion
        xbot_visual.process.run(process="xbot_extensions.activity_d65f9fd7.process16", package=__name__, inputs={
            "日期": 日期,
            "web_page": web_page,
            }, outputs=[
        ], _block=("A5 超级钻展", 13, "超级钻展报表日期选择"))
        if xbot_visual.workflow.test(operand1=文件保存路径, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("A5 超级钻展", 14, "IF 条件")):
            文件保存路径 = xbot_visual.dir.get_special_dir(special_dir_name="DesktopDirectory", _block=("A5 超级钻展", 15, "获取系统文件夹路径"))
        #endif
        current_datetime = xbot_visual.datetime.now(_block=("A5 超级钻展", 17, "获取当前日期时间"))
        current_time = xbot_visual.datetime.to_string(datetime=current_datetime, format="%Y%m%d%H%M%S", _block=("A5 超级钻展", 18, "日期时间转换为文本"))
        文件名 = xbot_visual.programing.variable(value="超级钻展_报表_账户汇总报表_" + xbot_visual.sh_str(current_time) + ".xlsx"
        , _block=("A5 超级钻展", 19, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("超级钻展_报表_报表下载按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A5 超级钻展", 20, "点击元素(web)"))
        file_path = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=文件保存路径, use_custom_filename=False, file_name=None, save_behavior="overwrite", wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("A5 超级钻展", 21, "处理下载对话框"))
        # process.run
    finally:
        args["file_path"] = file_path
