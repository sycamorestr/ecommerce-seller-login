import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        筛选类别 = "申请时间"
        时间类别 = "手动时间输入"
        开始日期 = "2026/08/03 00:00:00"
        结束日期 = "2026/09/05 23:59:59"
    else:
        网页对象 = args.get("网页对象", None)
        筛选类别 = args.get("筛选类别", "申请时间")
        时间类别 = args.get("时间类别", "手动时间输入")
        开始日期 = args.get("开始日期", "2026/08/03 00:00:00")
        结束日期 = args.get("结束日期", "2026/09/05 23:59:59")
    try:
        # web.get
        # 判断时间输入框是否可见
        #region 展开时间输入框
        loop_index = -1
        while True:
            loop_index += 1
            try:
                抖店售后工作台时间选择_展开_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("售后工作台时间选择_展开"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="5", _block=("抖店售后工作台时间选择", 5, "获取元素信息(web)"))
            except Exception as e:
                pass
                抖店售后工作台时间选择_展开_attribute = None
            if xbot_visual.workflow.test(operand1=抖店售后工作台时间选择_展开_attribute, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店售后工作台时间选择", 6, "IF 条件")):
                break
            #endif
            if xbot_visual.workflow.test(operand1=抖店售后工作台时间选择_展开_attribute.strip(), operator="==", operand2="更多筛选", operator_options="{}", _block=("抖店售后工作台时间选择", 9, "IF 条件")):
                try:
                    xbot_visual.web.element.click(browser=网页对象, element=package.selector("售后工作台时间选择_展开"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="10", _block=("抖店售后工作台时间选择", 11, "点击元素(web)"))
                except Exception as exception:
                    exception = xbot_visual.trace(exception)
                    pass
                #endtry
            else:
                break
            #endif
        #endloop
        #endregion
        # 选择筛选类别
        #region 选择筛选类别
        抖店售后工作台时间选择_筛选类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("售后工作台时间选择_筛选类别"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 21, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=筛选类别, operator="!=", operand2=抖店售后工作台时间选择_筛选类别_attribute, operator_options="{}", _block=("抖店售后工作台时间选择", 22, "IF 条件")):
            # web.element.click
            try:
                抖店售后工作台时间选择_时间筛选类别 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="(//span[contains(@class, \"auxo-input-group auxo-input-group-compact\")]//div[contains(@class, \"auxo-select\")][.//span[contains(text(), \"时间\")]])[1]", is_related_parent=False, parent=None, timeout="3", _block=("抖店售后工作台时间选择", 25, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=网页对象, element=抖店售后工作台时间选择_时间筛选类别, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 26, "点击元素(web)"))
                xbot_visual.process.run(process="xbot_extensions.web_action.process1", package=__name__, inputs={
                    "网页对象": 网页对象,
                    "操作目标": 抖店售后工作台时间选择_时间筛选类别,
                    "垂直方向": "结尾",
                    "水平方向": "开始",
                    }, outputs=[
                ], _block=("抖店售后工作台时间选择", 27, "滚动元素至可视区域"))
                # xbot_extensions.activity_fe2a1069.ClickByXpath
                for 筛选类别_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("售后工作台时间选择_筛选类别相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="3", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店售后工作台时间选择", 29, "循环相似元素(web)")):
                    筛选类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=筛选类别_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 30, "获取元素信息(web)"))
                    if xbot_visual.workflow.test(operand1=筛选类别_attribute, operator="==", operand2=筛选类别, operator_options="{}", _block=("抖店售后工作台时间选择", 31, "IF 条件")):
                        xbot_visual.web.element.click(browser=网页对象, element=筛选类别_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 32, "点击元素(web)"))
                        break
                    #endif
                #endloop
            except Exception as exception2:
                exception2 = xbot_visual.trace(exception2)
                抖店售后工作台时间选择_时间筛选类别_新版 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class,\"select-content-value\") and contains(text(),\"时间\")]", is_related_parent=False, parent=None, timeout="20", _block=("抖店售后工作台时间选择", 37, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=网页对象, element=抖店售后工作台时间选择_时间筛选类别_新版, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 38, "点击元素(web)"))
                xbot_visual.process.run(process="xbot_extensions.web_action.process1", package=__name__, inputs={
                    "网页对象": 网页对象,
                    "操作目标": 抖店售后工作台时间选择_时间筛选类别_新版,
                    "垂直方向": "结尾",
                    "水平方向": "开始",
                    }, outputs=[
                ], _block=("抖店售后工作台时间选择", 39, "滚动元素至可视区域"))
                # xbot_extensions.activity_fe2a1069.ClickByXpath
                for 筛选类别_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("售后工作台时间选择_筛选类别相似元素组(新)"), operation="element", absolute_url=False, attribute_name=None, timeout="5", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店售后工作台时间选择", 41, "循环相似元素(web)")):
                    筛选类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=筛选类别_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 42, "获取元素信息(web)"))
                    if xbot_visual.workflow.test(operand1=筛选类别_attribute, operator="==", operand2=筛选类别, operator_options="{}", _block=("抖店售后工作台时间选择", 43, "IF 条件")):
                        xbot_visual.web.element.click(browser=网页对象, element=筛选类别_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 44, "点击元素(web)"))
                        break
                    #endif
                #endloop
            #endtry
        #endif
        #endregion
        # 选择常见日期
        #region 选择常见日期
        if xbot_visual.workflow.test(operand1=时间类别, operator="!=", operand2="手动时间输入", operator_options="{}", _block=("抖店售后工作台时间选择", 53, "IF 条件")):
            try:
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("售后工作台时间选择_时间类别"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="3", _block=("抖店售后工作台时间选择", 55, "点击元素(web)"))
                for 时间类别_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("售后工作台时间选择_时间类别_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店售后工作台时间选择", 56, "循环相似元素(web)")):
                    时间类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时间类别_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 57, "获取元素信息(web)"))
                    if xbot_visual.workflow.test(operand1=时间类别_attribute, operator="==", operand2=时间类别, operator_options="{}", _block=("抖店售后工作台时间选择", 58, "IF 条件")):
                        xbot_visual.web.element.click(browser=网页对象, element=时间类别_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 59, "点击元素(web)"))
                        break
                    #endif
                #endloop
                return
            except Exception as exception3:
                exception3 = xbot_visual.trace(exception3)
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("售后工作台时间选择_时间类别(新)"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 65, "点击元素(web)"))
                for 时间类别_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("售后工作台时间选择_时间类别_相似元素组(新)"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店售后工作台时间选择", 66, "循环相似元素(web)")):
                    时间类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时间类别_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 67, "获取元素信息(web)"))
                    if xbot_visual.workflow.test(operand1=时间类别_attribute, operator="==", operand2=时间类别, operator_options="{}", _block=("抖店售后工作台时间选择", 68, "IF 条件")):
                        xbot_visual.web.element.click(browser=网页对象, element=时间类别_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 69, "点击元素(web)"))
                        break
                    #endif
                #endloop
                return
            #endtry
        #endif
        #endregion
        # 选择手动输入时间
        # 这个地方有点多，先选年，再选月，然后选日期，最后选时分秒
        开始年_月_日_时_分_秒_list = xbot_visual.text.split_text_to_list(text_to_split=开始日期, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter=" ", is_regular_expression=False, remove_empty=False, _block=("抖店售后工作台时间选择", 79, "文本分割成列表"))
        结束年_月_日_时_分_秒_list = xbot_visual.text.split_text_to_list(text_to_split=结束日期, delimiter_way="custom", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter=" ", is_regular_expression=False, remove_empty=False, _block=("抖店售后工作台时间选择", 80, "文本分割成列表"))
        开始年_月_日_时_分_秒_list[1] = 开始年_月_日_时_分_秒_list[1].replace(":", "-")
        
        结束年_月_日_时_分_秒_list[1] = 结束年_月_日_时_分_秒_list[1].replace(":", "-")
        
        开始年_月_日_时_分_秒_list[0] = 开始年_月_日_时_分_秒_list[0].replace("/", "-")
        
        结束年_月_日_时_分_秒_list[0] = 结束年_月_日_时_分_秒_list[0].replace("/", "-")
        售后工作台_开始日期触发器 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="(//input[@placeholder=\"开始日期\"])[1]", is_related_parent=False, parent=None, timeout="20", _block=("抖店售后工作台时间选择", 82, "获取元素对象(web)"))
        xbot_visual.web.element.click(browser=网页对象, element=售后工作台_开始日期触发器, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 83, "点击元素(web)"))
        售后工作台_日期框元素 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class,\"picker-panels\")]", is_related_parent=False, parent=None, timeout="20", _block=("抖店售后工作台时间选择", 84, "获取元素对象(web)"))
        xbot_visual.process.run(process="xbot_extensions.web_action.process1", package=__name__, inputs={
            "网页对象": 网页对象,
            "操作目标": 售后工作台_日期框元素,
            "垂直方向": "居中",
            "水平方向": "开始",
            }, outputs=[
        ], _block=("抖店售后工作台时间选择", 85, "滚动元素至可视区域"))
        # xbot_extensions.web_action.select_date_v2
        xbot_visual.process.run(process="xbot_extensions.web_action.select_date", package=__name__, inputs={
            "web_page": 网页对象,
            "date_elem": 售后工作台_日期框元素,
            "date_start": 开始年_月_日_时_分_秒_list[0],
            "date_end": 结束年_月_日_时_分_秒_list[0],
            "simulative": False,
            }, outputs=[
        ], _block=("抖店售后工作台时间选择", 87, "智能日期选择器"))
        开始时间时分秒输入框 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//input[@placeholder=\"开始时间\"]", is_related_parent=False, parent=None, timeout="20", _block=("抖店售后工作台时间选择", 88, "获取元素对象(web)"))
        结束时间时分秒输入框 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//input[@placeholder=\"结束时间\"]", is_related_parent=False, parent=None, timeout="20", _block=("抖店售后工作台时间选择", 89, "获取元素对象(web)"))
        xbot_visual.web.element.click(browser=网页对象, element=开始时间时分秒输入框, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 90, "点击元素(web)"))
        xbot_visual.web.element.click(browser=网页对象, element=结束时间时分秒输入框, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 91, "点击元素(web)"))
        售后工作台时_开始时间_相似元素组 = xbot_visual.web.element.get_all_elements(browser=网页对象, select_type="xpath_selector", selector=结束时间时分秒输入框, css_selector="", xpath_selector="(//ul[contains(@class,\"picker-time-panel-column\")])[1]//li", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("抖店售后工作台时间选择", 92, "获取相似元素列表(web)"))
        售后工作台分_开始时间_相似元素组 = xbot_visual.web.element.get_all_elements(browser=网页对象, select_type="xpath_selector", selector=结束时间时分秒输入框, css_selector="", xpath_selector="(//ul[contains(@class,\"picker-time-panel-column\")])[2]//li", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("抖店售后工作台时间选择", 93, "获取相似元素列表(web)"))
        售后工作台秒_开始时间_相似元素组 = xbot_visual.web.element.get_all_elements(browser=网页对象, select_type="xpath_selector", selector=结束时间时分秒输入框, css_selector="", xpath_selector="(//ul[contains(@class,\"picker-time-panel-column\")])[3]//li", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("抖店售后工作台时间选择", 94, "获取相似元素列表(web)"))
        售后工作台时_结束时间_相似元素组 = xbot_visual.web.element.get_all_elements(browser=网页对象, select_type="xpath_selector", selector=结束时间时分秒输入框, css_selector="", xpath_selector="(//ul[contains(@class,\"picker-time-panel-column\")])[4]//li", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("抖店售后工作台时间选择", 95, "获取相似元素列表(web)"))
        售后工作台分_结束时间_相似元素组 = xbot_visual.web.element.get_all_elements(browser=网页对象, select_type="xpath_selector", selector=结束时间时分秒输入框, css_selector="", xpath_selector="(//ul[contains(@class,\"picker-time-panel-column\")])[5]//li", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("抖店售后工作台时间选择", 96, "获取相似元素列表(web)"))
        售后工作台秒_结束时间_相似元素组 = xbot_visual.web.element.get_all_elements(browser=网页对象, select_type="xpath_selector", selector=结束时间时分秒输入框, css_selector="", xpath_selector="(//ul[contains(@class,\"picker-time-panel-column\")])[6]//li", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=False, _block=("抖店售后工作台时间选择", 97, "获取相似元素列表(web)"))
        开始日期_datetime = xbot_visual.datetime.from_string(text=开始日期, is_custom_format=True, format="%Y/%m/%d %H:%M:%S", _block=("抖店售后工作台时间选择", 98, "转换到日期时间"))
        结束日期_datetime = xbot_visual.datetime.from_string(text=结束日期, is_custom_format=True, format="%Y/%m/%d %H:%M:%S", _block=("抖店售后工作台时间选择", 99, "转换到日期时间"))
        开始日期_datetime_parts = xbot_visual.datetime.get_parts(datetime=开始日期_datetime, _block=("抖店售后工作台时间选择", 100, "获取时间详细信息"))
        结束日期_datetime_parts = xbot_visual.datetime.get_parts(datetime=结束日期_datetime, _block=("抖店售后工作台时间选择", 101, "获取时间详细信息"))
        #region 弃用
        # programing.comment
        # web.element.get_all_elements
        # web.browser.contains_element_or_text
        # web.element.click
        # workflow.endif
        # programing.comment
        # programing.region
        # web.element.get_details
        # text.extract_content_from_text
        # workflow.if
        # web.element.click
        # web.element.foreach_element
        # web.element.get_details
        # workflow.if
        # web.element.click
        # workflow.break
        # workflow.endif
        # workflow.endloop
        # workflow.endif
        # programing.endregion
        # programing.comment
        # programing.region
        # web.element.get_details
        # text.extract_content_from_text
        # workflow.if
        # web.element.click
        # web.element.foreach_element
        # web.element.get_details
        # text.extract_content_from_text
        # workflow.if
        # web.element.click
        # workflow.break
        # workflow.endif
        # workflow.endloop
        # workflow.endif
        # programing.endregion
        # programing.comment
        # web.element.foreach_element
        # web.element.get_details
        # workflow.if
        # web.element.click
        # workflow.break
        # workflow.endif
        # workflow.endloop
        # programing.comment
        # programing.region
        # web.element.get_details
        # text.extract_content_from_text
        # workflow.if
        # web.element.click
        # web.element.foreach_element
        # web.element.get_details
        # workflow.if
        # web.element.click
        # workflow.break
        # workflow.endif
        # workflow.endloop
        # workflow.endif
        # programing.endregion
        # programing.comment
        # programing.region
        # web.browser.element_display
        # web.element.foreach_element
        # web.element.get_details
        # text.extract_content_from_text
        # workflow.if
        # web.element.click
        # workflow.break
        # workflow.endif
        # workflow.endloop
        # workflow.else
        # web.element.get_details
        # text.extract_content_from_text
        # workflow.if
        # web.element.click
        # web.element.foreach_element
        # web.element.get_details
        # text.extract_content_from_text
        # workflow.if
        # web.element.click
        # workflow.break
        # workflow.endif
        # workflow.endloop
        # workflow.endif
        # workflow.endif
        # programing.endregion
        # programing.comment
        # programing.region
        # web.element.foreach_element
        # web.element.get_details
        # workflow.if
        # web.element.click
        # workflow.break
        # workflow.endif
        # workflow.endloop
        # programing.endregion
        #endregion
        # 开始日期-时分秒选择
        #region 开始日期-时分秒选择
        开始日期_时分秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=开始时间时分秒输入框, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 202, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=开始日期_时分秒_attribute, operator="!=", operand2=lambda: str(开始日期_datetime_parts.hour).zfill(2)+":"+str(开始日期_datetime_parts.minute).zfill(2)+":"+str(开始日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店售后工作台时间选择", 203, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=开始时间时分秒输入框, simulate=False, move_mouse=False, clicks="dbclick", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 204, "点击元素(web)"))
            for 时分秒_时_element in xbot_visual.workflow.list_iterator(list=售后工作台时_开始时间_相似元素组, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店售后工作台时间选择", 205, "ForEach列表循环")):
                时分秒_时_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_时_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 206, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_时_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.hour).zfill(2), operator_options="{}", _block=("抖店售后工作台时间选择", 207, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_时_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 208, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_分_element in xbot_visual.workflow.list_iterator(list=售后工作台分_开始时间_相似元素组, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店售后工作台时间选择", 211, "ForEach列表循环")):
                时分秒_分_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_分_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 212, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_分_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.minute).zfill(2), operator_options="{}", _block=("抖店售后工作台时间选择", 213, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_分_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 214, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_秒_element in xbot_visual.workflow.list_iterator(list=售后工作台秒_开始时间_相似元素组, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店售后工作台时间选择", 217, "ForEach列表循环")):
                时分秒_秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_秒_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 218, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_秒_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店售后工作台时间选择", 219, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_秒_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 220, "点击元素(web)"))
                #endif
            #endloop
        #endif
        #endregion
        # 结束日期-时分秒选择
        #region 结束日期-时分秒选择
        结束日期_时分秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=结束时间时分秒输入框, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 227, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=结束日期_时分秒_attribute, operator="!=", operand2=lambda: str(结束日期_datetime_parts.hour).zfill(2)+":"+str(结束日期_datetime_parts.minute).zfill(2)+":"+str(结束日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店售后工作台时间选择", 228, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=结束时间时分秒输入框, simulate=False, move_mouse=False, clicks="dbclick", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 229, "点击元素(web)"))
            for 时分秒_时_element in xbot_visual.workflow.list_iterator(list=售后工作台时_结束时间_相似元素组, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店售后工作台时间选择", 230, "ForEach列表循环")):
                时分秒_时_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_时_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 231, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_时_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.hour).zfill(2), operator_options="{}", _block=("抖店售后工作台时间选择", 232, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_时_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 233, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_分_element in xbot_visual.workflow.list_iterator(list=售后工作台分_结束时间_相似元素组, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店售后工作台时间选择", 236, "ForEach列表循环")):
                时分秒_分_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_分_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 237, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_分_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.minute).zfill(2), operator_options="{}", _block=("抖店售后工作台时间选择", 238, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_分_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 239, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_秒_element in xbot_visual.workflow.list_iterator(list=售后工作台秒_结束时间_相似元素组, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店售后工作台时间选择", 242, "ForEach列表循环")):
                时分秒_秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_秒_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店售后工作台时间选择", 243, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_秒_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店售后工作台时间选择", 244, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_秒_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 245, "点击元素(web)"))
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        xbot_visual.web.element.click(browser=网页对象, element=package.selector("售后工作台时间选择_日期确定按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店售后工作台时间选择", 251, "点击元素(web)"))
        # web.element.get_details
        # web.element.get_details
        # workflow.multiple_conditions_if
        # programing.raise
        # workflow.endif
    finally:
        pass
