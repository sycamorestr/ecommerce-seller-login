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
        文件保存路径 = ""
        效果 = ""
        周期 = ""
        web_page = None
    else:
        日期 = args.get("日期", "")
        文件保存路径 = args.get("文件保存路径", "")
        效果 = args.get("效果", "")
        周期 = args.get("周期", "")
        web_page = args.get("web_page", None)
    try:
        效果列表 = xbot_visual.programing.variable(value=lambda: ['点击效果','展现效果']
        , _block=("A3 引力魔方", 1, "设置变量"))
        周期列表 = xbot_visual.programing.variable(value=lambda: ['转化效果周期1天','转化效果周期3天','转化效果周期7天','转化效果周期15天','转化效果周期30天']
        , _block=("A3 引力魔方", 2, "设置变量"))
        # web.element.click
        xbot_visual.process.run(process="xbot_extensions.activity_d65f9fd7.process12", package=__name__, inputs={
            "日期": 日期,
            "web_page": web_page,
            }, outputs=[
        ], _block=("A3 引力魔方", 4, "引力魔方汇总数据日期选择"))
        # programing.raise
        #region 效果选择
        if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 效果,"operand2": "","operator": "not empty"},{"operand1": 效果列表,"operand2": 效果,"operator": "in"}], _block=("A3 引力魔方", 7, "IF 多条件")):
            package.variables['effect_select'] = xbot_visual.programing.variable(value=效果
            , _block=("A3 引力魔方", 8, "设置变量"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("引力魔方_报表_效果选择下拉框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A3 引力魔方", 9, "点击元素(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("引力魔方_报表_效果选择"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A3 引力魔方", 10, "点击元素(web)"))
        #endif
        #endregion
        #region 转化周期选择
        if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 周期,"operand2": "","operator": "not empty"},{"operand1": 周期列表,"operand2": 周期,"operator": "in"}], _block=("A3 引力魔方", 14, "IF 多条件")):
            package.variables['conversion_cycle'] = xbot_visual.programing.variable(value=周期
            , _block=("A3 引力魔方", 15, "设置变量"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("引力魔方_报表_转化周期选择下拉框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A3 引力魔方", 16, "点击元素(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("引力魔方_报表_转化周期选择"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A3 引力魔方", 17, "点击元素(web)"))
        #endif
        #endregion
        #region 数据下载
        xbot_visual.web.element.click(browser=web_page, element=package.selector("引力魔方_报表_汇总数据_下载分日汇总数据按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A3 引力魔方", 21, "点击元素(web)"))
        #region 文件名设置
        current_datetime = xbot_visual.datetime.now(_block=("A3 引力魔方", 23, "获取当前日期时间"))
        current_time_text = xbot_visual.datetime.to_string(datetime=current_datetime, format="%Y%m%d%H%M%S", _block=("A3 引力魔方", 24, "日期时间转换为文本"))
        默认文件名 = xbot_visual.programing.variable(value=lambda: '引力魔方_报表_自定义分析_汇总数据_' + current_time_text
        , _block=("A3 引力魔方", 25, "设置变量"))
        package.variables['file_name'] = xbot_visual.programing.variable(value=默认文件名
        , _block=("A3 引力魔方", 26, "设置变量"))
        xbot_visual.web.element.input(browser=web_page, element=package.selector("引力魔方_报表_自定义分析_汇总数据下载_文件名称输入框"), text=package.variables['file_name'], append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A3 引力魔方", 27, "填写输入框(web)"))
        #endregion
        if xbot_visual.workflow.test(operand1=文件保存路径, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("A3 引力魔方", 29, "IF 条件")):
            文件保存路径 = xbot_visual.dir.get_special_dir(special_dir_name="DesktopDirectory", _block=("A3 引力魔方", 30, "获取系统文件夹路径"))
        #endif
        web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("引力魔方_报表_汇总数据_分日汇总数据下载_全部数据指标单选按钮"), state="appear", iswait=True, timeout="20", _block=("A3 引力魔方", 32, "等待元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("引力魔方_报表_汇总数据_分日汇总数据下载_全部数据指标单选按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A3 引力魔方", 33, "点击元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("引力魔方_报表_汇总数据_分日汇总数据下载_下载确认按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A3 引力魔方", 34, "点击元素(web)"))
        web_wait_result2 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("引力魔方_报表_下载任务管理"), state="appear", iswait=True, timeout="30", _block=("A3 引力魔方", 35, "等待元素(web)"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("引力魔方_报表_下载任务管理"), _block=("A3 引力魔方", 36, "IF 元素可见(web)")):
            web_wait_result3 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("引力魔方_报表_下载任务管理_目标文件名"), state="appear", iswait=True, timeout="20", _block=("A3 引力魔方", 37, "等待元素(web)"))
            web_wait_result3 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("引力魔方_报表_自定义分析_下载任务管理_目标文件生成成功"), state="appear", iswait=True, timeout="20", _block=("A3 引力魔方", 38, "等待元素(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("引力魔方_报表_自定义分析_下载任务管理_目标文件生成成功"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A3 引力魔方", 39, "点击元素(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("引力魔方_报表_自定义分析_下载任务管理_文件下载"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A3 引力魔方", 40, "点击元素(web)"))
            file_path = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=文件保存路径, use_custom_filename=False, file_name=None, save_behavior="overwrite", wait_complete=True, wait_complete_timeout="60", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("A3 引力魔方", 41, "处理下载对话框"))
        #endif
        #endregion
    finally:
        args["file_path"] = file_path
