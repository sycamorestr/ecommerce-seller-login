import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        开始时间 = ""
        结束时间 = ""
        开始日期触发器 = None
        结束日期触发器 = None
    else:
        开始时间 = args.get("开始时间", "")
        结束时间 = args.get("结束时间", "")
        开始日期触发器 = args.get("开始日期触发器", None)
        结束日期触发器 = args.get("结束日期触发器", None)
    try:
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("抖店评价管理时间选择", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("抖店评价管理时间选择", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        开始年_月_日_时_分_秒_list = xbot_visual.text.split_text_to_list(text_to_split=开始时间, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="_", is_regular_expression=False, remove_empty=False, _block=("抖店评价管理时间选择", 2, "文本分割成列表"))
        结束年_月_日_时_分_秒_list = xbot_visual.text.split_text_to_list(text_to_split=结束时间, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="_", is_regular_expression=False, remove_empty=False, _block=("抖店评价管理时间选择", 3, "文本分割成列表"))
        开始年_月_日_时_分_秒_list[1] = 开始年_月_日_时_分_秒_list[1].replace(":", "-")
        
        结束年_月_日_时_分_秒_list[1] = 结束年_月_日_时_分_秒_list[1].replace(":", "-")
        xbot_visual.web.element.click(browser=web_page, element=开始日期触发器, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店评价管理时间选择", 5, "点击元素(web)"))
        xbot_visual.process.run(process="xbot_extensions.web_action.select_date", package=__name__, inputs={
            "web_page": web_page,
            "date_elem": package.selector("10"),
            "date_start": 开始年_月_日_时_分_秒_list[0],
            "date_end": 结束年_月_日_时_分_秒_list[0],
            "simulative": False,
            }, outputs=[
        ], _block=("抖店评价管理时间选择", 6, "智能日期选择器"))
        开始时间时分秒输入框 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//input[@placeholder=\"开始时间\"]", is_related_parent=False, parent=None, timeout="20", _block=("抖店评价管理时间选择", 7, "获取元素对象(web)"))
        xbot_visual.process.run(process="xbot_extensions.shadowbot_date_select.process4", package=__name__, inputs={
            "网页对象": web_page,
            "具体时间": lambda: 开始年_月_日_时_分_秒_list[1],
            "元素_点开日期选择器": 开始时间时分秒输入框,
            "通用时_相似元素组": package.selector("通用时_相似元素组"),
            "通用分_相似元素组": package.selector("通用分_相似元素组"),
            "通用秒_相似元素组": package.selector("通用秒_相似元素组"),
            }, outputs=[
        ], _block=("抖店评价管理时间选择", 8, "通用时分秒选择"))
        结束时间时分秒输入框 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//input[@placeholder=\"结束时间\"]", is_related_parent=False, parent=None, timeout="20", _block=("抖店评价管理时间选择", 9, "获取元素对象(web)"))
        xbot_visual.process.run(process="xbot_extensions.shadowbot_date_select.process4", package=__name__, inputs={
            "网页对象": web_page,
            "具体时间": lambda: 结束年_月_日_时_分_秒_list[1],
            "元素_点开日期选择器": 结束时间时分秒输入框,
            "通用时_相似元素组": package.selector("通用时_相似元素组"),
            "通用分_相似元素组": package.selector("通用分_相似元素组"),
            "通用秒_相似元素组": package.selector("通用秒_相似元素组"),
            }, outputs=[
        ], _block=("抖店评价管理时间选择", 10, "通用时分秒选择"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("时间选择确定"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店评价管理时间选择", 11, "点击元素(web)"))
    finally:
        pass
