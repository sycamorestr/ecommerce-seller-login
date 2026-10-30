import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    消耗汇总数据 = {}
    推广汇总数据 = {}
    if args is None:
        web_page = None
        日期 = ""
        周期 = ""
    else:
        web_page = args.get("web_page", None)
        日期 = args.get("日期", "")
        周期 = args.get("周期", "")
    try:
        周期列表 = xbot_visual.programing.variable(value=lambda: ['效果转化周期7天','效果转化周期15天','效果转化周期30天']
        , _block=("A2 万象台", 1, "设置变量"))
        # web.element.click
        xbot_visual.web.browser.wait_load_completed(browser=web_page, load_timeout="20", action_after_load_timeout="handleExcept", _block=("A2 万象台", 3, "等待网页加载完成"))
        #region 周期选择
        if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 日期,"operand2": "","operator": "not empty"},{"operand1": 周期列表,"operand2": 周期,"operator": "in"}], _block=("A2 万象台", 5, "IF 多条件")):
            package.variables['conversion_cycle'] = xbot_visual.programing.variable(value=周期
            , _block=("A2 万象台", 6, "设置变量"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("万象台-报表-账户总览-转化周期选择"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A2 万象台", 7, "点击元素(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("万象台-报表-账户总览-转化周期选项"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A2 万象台", 8, "点击元素(web)"))
        elif xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 周期,"operand2": "","operator": "not empty"},{"operand1": 周期列表,"operand2": 周期,"operator": "not in"}], _block=("A2 万象台", 9, "Else IF 多条件")):
            raise Exception("当前版本指令仅支持以下周期的选择：['效果转化周期7天','效果转化周期15天','效果转化周期30天']")
            return
        #endif
        #endregion
        xbot_visual.process.run(process="xbot_extensions.activity_d65f9fd7.process11", package=__name__, inputs={
            "日期": 日期,
            "web_page": web_page,
            }, outputs=[
        ], _block=("A2 万象台", 14, "万象台报表账户概览日期选择"))
        推广汇总数据 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_page_data", params={
            "web_page": web_page,
            "similer_element_group": "万象台_报表_推广数据汇总_字段名",
        }, _block=("A2 万象台", 15, "调用模块"))
        消耗汇总数据 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_page_data", params={
            "web_page": web_page,
            "similer_element_group": "万象台_报表_消耗数据汇总_字段名",
        }, _block=("A2 万象台", 16, "调用模块"))
    finally:
        args["消耗汇总数据"] = 消耗汇总数据
        args["推广汇总数据"] = 推广汇总数据
