import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        开始时间 = ""
        开始日期触发器 = None
        结束时间 = ""
        web_page = None
    else:
        开始时间 = args.get("开始时间", "")
        开始日期触发器 = args.get("开始日期触发器", None)
        结束时间 = args.get("结束时间", "")
        web_page = args.get("web_page", None)
    try:
        if xbot_visual.workflow.test(operand1=web_page, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店时分秒日期选择", 1, "IF 条件")):
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("抖店时分秒日期选择", 2, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("抖店时分秒日期选择", 2,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        #endif
        开始年_月_日_时_分_秒_list = xbot_visual.text.split_text_to_list(text_to_split=开始时间, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="-", is_regular_expression=False, remove_empty=False, _block=("抖店时分秒日期选择", 4, "文本分割成列表"))
        结束年_月_日_时_分_秒_list = xbot_visual.text.split_text_to_list(text_to_split=结束时间, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="-", is_regular_expression=False, remove_empty=False, _block=("抖店时分秒日期选择", 5, "文本分割成列表"))
        xbot_visual.web.element.click(browser=web_page, element=开始日期触发器, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 6, "点击元素(web)"))
        for num in xbot_visual.workflow.range_iterator(start="0", stop="1", step="1", _block=("抖店时分秒日期选择", 7, "For次数循环")):
            if xbot_visual.workflow.test(operand1=num, operator="==", operand2="1", operator_options="{}", _block=("抖店时分秒日期选择", 8, "IF 条件")):
                xbot_visual.process.run(process="xbot_extensions.shadowbot_date_select.p6", package=__name__, inputs={
                    "网页对象": web_page,
                    "日期时间": 结束时间,
                    "元素_年": package.selector("起始年元素"),
                    "元素_月": package.selector("起始月元素"),
                    "日期相似元素组": package.selector("起始元素选择_相似元素组"),
                    "元素_向前切换年": package.selector("元素向前切换年"),
                    "元素_向后切换年": package.selector("元素向后切换年"),
                    "元素_向前切换月": package.selector("元素向前切换月"),
                    "元素_向后切换月": package.selector("元素向后切换月"),
                    "选择年": True,
                    "元素_点开日期选择器": package.selector("奖惩中心_结束日期触发"),
                    }, outputs=[
                ], _block=("抖店时分秒日期选择", 9, "日历日期选择器二(web)"))
                if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("通用时_相似元素组"), text="", _block=("抖店时分秒日期选择", 10, "IF 网页包含")):
                    #region 选择时-分-秒
                    for 当前_时 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用时_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 12, "循环相似元素(web)")):
                        if xbot_visual.workflow.test(operand1=当前_时.get_text(), operator="==", operand2=lambda: 结束年_月_日_时_分_秒_list[3], operator_options="{}", _block=("抖店时分秒日期选择", 13, "IF 条件")):
                            xbot_visual.web.element.click(browser=web_page, element=当前_时, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 14, "点击元素(web)"))
                        #endif
                    #endloop
                    for 当前_分 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用分_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 17, "循环相似元素(web)")):
                        if xbot_visual.workflow.test(operand1=当前_分.get_text(), operator="==", operand2=lambda: 结束年_月_日_时_分_秒_list[4], operator_options="{}", _block=("抖店时分秒日期选择", 18, "IF 条件")):
                            xbot_visual.web.element.click(browser=web_page, element=当前_分, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 19, "点击元素(web)"))
                        #endif
                    #endloop
                    for 当前_秒 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用秒_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 22, "循环相似元素(web)")):
                        if xbot_visual.workflow.test(operand1=当前_秒.get_text(), operator="==", operand2=lambda: 结束年_月_日_时_分_秒_list[5], operator_options="{}", _block=("抖店时分秒日期选择", 23, "IF 条件")):
                            xbot_visual.web.element.click(browser=web_page, element=当前_秒, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 24, "点击元素(web)"))
                        #endif
                    #endloop
                    #endregion
                #endif
                xbot_visual.web.element.click(browser=web_page, element=package.selector("时间选择确定"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 29, "点击元素(web)"))
                return
            #endif
            xbot_visual.process.run(process="xbot_extensions.shadowbot_date_select.p6", package=__name__, inputs={
                "网页对象": web_page,
                "日期时间": 开始时间,
                "元素_年": package.selector("起始年元素"),
                "元素_月": package.selector("起始月元素"),
                "日期相似元素组": package.selector("起始元素选择_相似元素组"),
                "元素_向前切换年": package.selector("元素向前切换年"),
                "元素_向后切换年": package.selector("元素向后切换年"),
                "元素_向前切换月": package.selector("元素向前切换月"),
                "元素_向后切换月": package.selector("元素向后切换月"),
                "选择年": True,
                "元素_点开日期选择器": 开始日期触发器,
                }, outputs=[
            ], _block=("抖店时分秒日期选择", 32, "日历日期选择器二(web)"))
            if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("通用时_相似元素组"), text="", _block=("抖店时分秒日期选择", 33, "IF 网页包含")):
                #region 选择时-分-秒
                for 当前_时 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用时_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 35, "循环相似元素(web)")):
                    if xbot_visual.workflow.test(operand1=当前_时.get_text(), operator="==", operand2=lambda: 开始年_月_日_时_分_秒_list[3], operator_options="{}", _block=("抖店时分秒日期选择", 36, "IF 条件")):
                        xbot_visual.web.element.click(browser=web_page, element=当前_时, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 37, "点击元素(web)"))
                    #endif
                #endloop
                for 当前_分 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用分_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 40, "循环相似元素(web)")):
                    if xbot_visual.workflow.test(operand1=当前_分.get_text(), operator="==", operand2=lambda: 开始年_月_日_时_分_秒_list[4], operator_options="{}", _block=("抖店时分秒日期选择", 41, "IF 条件")):
                        xbot_visual.web.element.click(browser=web_page, element=当前_分, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 42, "点击元素(web)"))
                    #endif
                #endloop
                for 当前_秒 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用秒_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 45, "循环相似元素(web)")):
                    if xbot_visual.workflow.test(operand1=当前_秒.get_text(), operator="==", operand2=lambda: 开始年_月_日_时_分_秒_list[5], operator_options="{}", _block=("抖店时分秒日期选择", 46, "IF 条件")):
                        xbot_visual.web.element.click(browser=web_page, element=当前_秒, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 47, "点击元素(web)"))
                    #endif
                #endloop
                xbot_visual.web.element.click(browser=web_page, element=package.selector("时间选择确定"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 50, "点击元素(web)"))
                #endregion
            #endif
            if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("结束年元素"), text="", _block=("抖店时分秒日期选择", 53, "IF 网页包含")):
                break
            #endif
        #endloop
        xbot_visual.process.run(process="xbot_extensions.shadowbot_date_select.p6", package=__name__, inputs={
            "网页对象": web_page,
            "日期时间": 结束时间,
            "元素_年": package.selector("结束年元素"),
            "元素_月": package.selector("结束月元素"),
            "日期相似元素组": package.selector("结束元素选择_相似元素组"),
            "元素_向前切换年": package.selector("元素向前切换年"),
            "元素_向后切换年": package.selector("元素向后切换年"),
            "元素_向前切换月": package.selector("元素向前切换月"),
            "元素_向后切换月": package.selector("元素向后切换月"),
            "选择年": True,
            "元素_点开日期选择器": 开始日期触发器,
            }, outputs=[
        ], _block=("抖店时分秒日期选择", 57, "日历日期选择器二(web)"))
        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("开始时间_时分秒"), text="", _block=("抖店时分秒日期选择", 58, "IF 网页包含")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("开始时间_时分秒"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 59, "点击元素(web)"))
            #region 选择时-分-秒
            for 当前_时 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用时_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 61, "循环相似元素(web)")):
                if xbot_visual.workflow.test(operand1=当前_时.get_text(), operator="==", operand2=lambda: 开始年_月_日_时_分_秒_list[3], operator_options="{}", _block=("抖店时分秒日期选择", 62, "IF 条件")):
                    xbot_visual.web.element.click(browser=web_page, element=当前_时, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 63, "点击元素(web)"))
                #endif
            #endloop
            for 当前_分 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用分_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 66, "循环相似元素(web)")):
                if xbot_visual.workflow.test(operand1=当前_分.get_text(), operator="==", operand2=lambda: 开始年_月_日_时_分_秒_list[4], operator_options="{}", _block=("抖店时分秒日期选择", 67, "IF 条件")):
                    xbot_visual.web.element.click(browser=web_page, element=当前_分, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 68, "点击元素(web)"))
                #endif
            #endloop
            for 当前_秒 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用秒_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 71, "循环相似元素(web)")):
                if xbot_visual.workflow.test(operand1=当前_秒.get_text(), operator="==", operand2=lambda: 开始年_月_日_时_分_秒_list[5], operator_options="{}", _block=("抖店时分秒日期选择", 72, "IF 条件")):
                    xbot_visual.web.element.click(browser=web_page, element=当前_秒, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 73, "点击元素(web)"))
                #endif
            #endloop
            #endregion
        #endif
        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("结束时间_时分秒"), text="", _block=("抖店时分秒日期选择", 78, "IF 网页包含")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("结束时间_时分秒"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 79, "点击元素(web)"))
            #region 选择时-分-秒
            for 当前_时 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用时_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 81, "循环相似元素(web)")):
                if xbot_visual.workflow.test(operand1=当前_时.get_text(), operator="==", operand2=lambda: 结束年_月_日_时_分_秒_list[3], operator_options="{}", _block=("抖店时分秒日期选择", 82, "IF 条件")):
                    xbot_visual.web.element.click(browser=web_page, element=当前_时, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 83, "点击元素(web)"))
                #endif
            #endloop
            for 当前_分 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用分_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 86, "循环相似元素(web)")):
                if xbot_visual.workflow.test(operand1=当前_分.get_text(), operator="==", operand2=lambda: 结束年_月_日_时_分_秒_list[4], operator_options="{}", _block=("抖店时分秒日期选择", 87, "IF 条件")):
                    xbot_visual.web.element.click(browser=web_page, element=当前_分, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 88, "点击元素(web)"))
                #endif
            #endloop
            for 当前_秒 in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("通用秒_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店时分秒日期选择", 91, "循环相似元素(web)")):
                if xbot_visual.workflow.test(operand1=当前_秒.get_text(), operator="==", operand2=lambda: 结束年_月_日_时_分_秒_list[5], operator_options="{}", _block=("抖店时分秒日期选择", 92, "IF 条件")):
                    xbot_visual.web.element.click(browser=web_page, element=当前_秒, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店时分秒日期选择", 93, "点击元素(web)"))
                #endif
            #endloop
            #endregion
        #endif
        try:
            xbot_visual.web.element.click(browser=web_page, element=package.selector("时间选择确定"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="2", _block=("抖店时分秒日期选择", 98, "点击元素(web)"))
        except Exception as e:
            pass
    finally:
        pass
