import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    data = {}
    if args is None:
        web_page = None
        日期 = "今日实时"
    else:
        web_page = args.get("web_page", None)
        日期 = args.get("日期", "今日实时")
    try:
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("A6 淘宝客", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("A6 淘宝客", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.wait_load_completed(browser=web_page, load_timeout="20", action_after_load_timeout="handleExcept", _block=("A6 淘宝客", 2, "等待网页加载完成"))
        xbot_visual.process.run(process="xbot_extensions.activity_d65f9fd7.process18", package=__name__, inputs={
            "日期": 日期,
            "web_page": web_page,
            }, outputs=[
        ], _block=("A6 淘宝客", 3, "商家中心数据分析日期选择"))
        # programing.raise
        #region 数据获取
        for web_loop_element in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("淘宝联盟_商家中心_数据分析_推广概览_数据汇总_字段名相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("A6 淘宝客", 6, "循环相似元素(web)")):
            字段名 = xbot_visual.programing.variable(value=web_loop_element.get_text()
            , _block=("A6 淘宝客", 7, "设置变量"))
            web_element_parent = xbot_visual.web.element.get_associated_elements(browser=web_page, element=web_loop_element, associated_kind="parent", child_access_kind="all", child_index="0", sibling_direction="next", timeout="20", _block=("A6 淘宝客", 8, "获取关联元素(web)"))
            web_element_parent_next = xbot_visual.web.element.get_associated_elements(browser=web_page, element=web_element_parent, associated_kind="sibling", child_access_kind="all", child_index="0", sibling_direction="next", timeout="20", _block=("A6 淘宝客", 9, "获取关联元素(web)"))
            web_element_parent_next_son = xbot_visual.web.element.get_associated_elements(browser=web_page, element=web_element_parent_next, associated_kind="child", child_access_kind="all", child_index="0", sibling_direction="next", timeout="20", _block=("A6 淘宝客", 10, "获取关联元素(web)"))
            数据 = xbot_visual.programing.variable(value=lambda: ''
            , _block=("A6 淘宝客", 11, "设置变量"))
            for loop_item in xbot_visual.workflow.list_iterator(list=web_element_parent_next_son, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("A6 淘宝客", 12, "ForEach列表循环")):
                web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=loop_item, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("A6 淘宝客", 13, "获取元素信息(web)"))
                数据 = xbot_visual.programing.variable(value=lambda: 数据+web_element_attribute
                , _block=("A6 淘宝客", 14, "设置变量"))
            #endloop
            数据 = xbot_visual.programing.variable(value=lambda: 数据 if ',' not in 数据 else 数据.replace(',','')
            , _block=("A6 淘宝客", 16, "设置变量"))
            xbot_visual.dictionary.set(dict=data, key=字段名, value=数据, _block=("A6 淘宝客", 17, "设置键值对"))
        #endloop
        #endregion
        # workflow.if
        # dir.get_special_dir
        # workflow.endif
        # web.element.click
        # web.handle_save_dialog
    finally:
        args["data"] = data
