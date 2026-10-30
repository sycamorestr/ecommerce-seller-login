import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        筛选类别 = "下单时间"
        时间类别 = "手动时间输入"
        开始日期 = "2024/04/04 23:59:59"
        结束日期 = "2024/04/10 23:59:59"
    else:
        网页对象 = args.get("网页对象", None)
        筛选类别 = args.get("筛选类别", "下单时间")
        时间类别 = args.get("时间类别", "手动时间输入")
        开始日期 = args.get("开始日期", "2024/04/04 23:59:59")
        结束日期 = args.get("结束日期", "2024/04/10 23:59:59")
    try:
        开始日期 = xbot_visual.datetime.to_string(datetime=开始日期, format="%Y/%m/%d %H:%M:%S", _block=("抖店订单管理时间选择", 1, "日期时间转换为文本"))
        结束日期 = xbot_visual.datetime.to_string(datetime=结束日期, format="%Y/%m/%d %H:%M:%S", _block=("抖店订单管理时间选择", 2, "日期时间转换为文本"))
        # 判断时间输入框是否可见
        #region 展开时间输入框
        loop_index = -1
        while True:
            loop_index += 1
            # 兼容新版订单管理页面
            if xbot_visual.web.browser.element_display(browser=网页对象, content_type="display", selector=package.selector("抖店订单管理时间选择_展开(新)"), _block=("抖店订单管理时间选择", 7, "IF 元素可见(web)")):
                try:
                    抖店订单管理时间选择_展开_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("抖店订单管理时间选择_展开(新)"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="10", _block=("抖店订单管理时间选择", 8, "获取元素信息(web)"))
                except Exception as e:
                    pass
                    抖店订单管理时间选择_展开_attribute = ''
                xbot_visual.programing.log(type="info", text="当前为新版本页面", _block=("抖店订单管理时间选择", 9, "打印日志"))
                if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 抖店订单管理时间选择_展开_attribute,"operand2": "展开","operator": "in"},{"operand1": 抖店订单管理时间选择_展开_attribute,"operand2": "更多筛选","operator": "in"}], _block=("抖店订单管理时间选择", 10, "IF 多条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=package.selector("抖店订单管理时间选择_展开(新)"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 11, "点击元素(web)"))
                else:
                    break
                #endif
            else:
                try:
                    抖店订单管理时间选择_展开_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_展开"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="10", _block=("抖店订单管理时间选择", 16, "获取元素信息(web)"))
                except Exception as e:
                    pass
                    抖店订单管理时间选择_展开_attribute = ''
                if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 抖店订单管理时间选择_展开_attribute,"operand2": "展开","operator": "in"},{"operand1": 抖店订单管理时间选择_展开_attribute,"operand2": "更多筛选","operator": "in"}], _block=("抖店订单管理时间选择", 17, "IF 多条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_展开"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 18, "点击元素(web)"))
                else:
                    break
                #endif
            #endif
            #endregion
        #endloop
        # 选择筛选类别
        #region 选择筛选类别
        抖店订单管理时间选择_筛选类别_elem = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="(//span[@class='auxo-select-selection-search']/following-sibling::span[text()='下单时间' or text()='完成时间' or text()='预约发货时间' or text()='建议发货时间' or text()='付款时间' or text()='发货时间' or text()='预约送达时间'])[1]", is_related_parent=False, parent=None, timeout="20", _block=("抖店订单管理时间选择", 27, "获取元素对象(web)"))
        抖店订单管理时间选择_筛选类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=抖店订单管理时间选择_筛选类别_elem, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 28, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=筛选类别, operator="!=", operand2=抖店订单管理时间选择_筛选类别_attribute, operator_options="{}", _block=("抖店订单管理时间选择", 29, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=抖店订单管理时间选择_筛选类别_elem, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 30, "点击元素(web)"))
            for 筛选类别_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_筛选类别_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 31, "循环相似元素(web)")):
                筛选类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=筛选类别_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 32, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=筛选类别_attribute, operator="==", operand2=筛选类别, operator_options="{}", _block=("抖店订单管理时间选择", 33, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=筛选类别_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 34, "点击元素(web)"))
                    break
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        #region 选择常见日期
        try:
            订单管理 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=lambda: f'(//div[contains(@class, "styles_formItem")][.//*[text()="{筛选类别}"]]//div[contains(@class, "auxo-select")])[4]', is_related_parent=False, parent=None, timeout="2", _block=("抖店订单管理时间选择", 42, "获取元素对象(web)"))
        except Exception as e:
            pass
            订单管理 = None
        if xbot_visual.workflow.test(operand1=订单管理, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店订单管理时间选择", 43, "IF 条件")):
            if xbot_visual.workflow.test(operand1=时间类别, operator="!=", operand2="手动时间输入", operator_options="{}", _block=("抖店订单管理时间选择", 44, "IF 条件")):
                订单管理 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=lambda: f'(//div[contains(@class, "styles_formItem")][.//*[text()="{筛选类别}"]]//div[contains(@class, "auxo-select")])[4]', is_related_parent=False, parent=None, timeout="20", _block=("抖店订单管理时间选择", 45, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=网页对象, element=订单管理, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 46, "点击元素(web)"))
                # web.element.click
                for 时间类别_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_时间类别_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 48, "循环相似元素(web)")):
                    时间类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时间类别_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 49, "获取元素信息(web)"))
                    if xbot_visual.workflow.test(operand1=时间类别_attribute, operator="==", operand2=时间类别, operator_options="{}", _block=("抖店订单管理时间选择", 50, "IF 条件")):
                        xbot_visual.web.element.click(browser=网页对象, element=时间类别_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 51, "点击元素(web)"))
                        break
                    #endif
                #endloop
                return
            #endif
        else:
            if xbot_visual.workflow.test(operand1=时间类别, operator="==", operand2="昨日", operator_options="{}", _block=("抖店订单管理时间选择", 58, "IF 条件")):
                yesterday_date = xbot_visual.process.run(process="xbot_extensions.shadowbot_datatime.process2", package=__name__, inputs={
                    "humanized_string": "昨日日期",
                    "formatting_string": "YYYY-MM-DD",
                    "without_zeros": False,
                    }, outputs=[
                    "formatted_string",
                ], _block=("抖店订单管理时间选择", 59, "常用日期"))
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_输入框(新)"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="5", _block=("抖店订单管理时间选择", 60, "点击元素(web)"))
                日期框 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"auxo-picker-panels\"]", is_related_parent=False, parent=None, timeout="20", _block=("抖店订单管理时间选择", 61, "获取元素对象(web)"))
                xbot_visual.process.run(process="xbot_extensions.web_action.select_date_v2", package=__name__, inputs={
                    "web_page": 网页对象,
                    "elem": 日期框,
                    "date_start": yesterday_date,
                    "date_end": yesterday_date,
                    "simulative": True,
                    }, outputs=[
                ], _block=("抖店订单管理时间选择", 62, "智能日期 (Beta)"))
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_确定按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 63, "点击元素(web)"))
                return
            elif xbot_visual.workflow.test(operand1=时间类别, operator="==", operand2="今日", operator_options="{}", _block=("抖店订单管理时间选择", 65, "Else IF")):
                today_date = xbot_visual.process.run(process="xbot_extensions.shadowbot_datatime.process2", package=__name__, inputs={
                    "humanized_string": "今日日期",
                    "formatting_string": "YYYY-MM-DD",
                    "without_zeros": False,
                    }, outputs=[
                    "formatted_string",
                ], _block=("抖店订单管理时间选择", 66, "常用日期"))
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_输入框(新)"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="5", _block=("抖店订单管理时间选择", 67, "点击元素(web)"))
                日期框 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"auxo-picker-panels\"]", is_related_parent=False, parent=None, timeout="20", _block=("抖店订单管理时间选择", 68, "获取元素对象(web)"))
                xbot_visual.process.run(process="xbot_extensions.web_action.select_date_v2", package=__name__, inputs={
                    "web_page": 网页对象,
                    "elem": 日期框,
                    "date_start": today_date,
                    "date_end": today_date,
                    "simulative": True,
                    }, outputs=[
                ], _block=("抖店订单管理时间选择", 69, "智能日期 (Beta)"))
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_确定按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 70, "点击元素(web)"))
                return
            elif xbot_visual.workflow.test(operand1=时间类别, operator="==", operand2="近7日", operator_options="{}", _block=("抖店订单管理时间选择", 72, "Else IF")):
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_输入框(新)"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="5", _block=("抖店订单管理时间选择", 73, "点击元素(web)"))
                近7天 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"sp-tag-content\"][text()=\"近7天\"]", is_related_parent=False, parent=None, timeout="20", _block=("抖店订单管理时间选择", 74, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=网页对象, element=近7天, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 75, "点击元素(web)"))
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_确定按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 76, "点击元素(web)"))
                return
            elif xbot_visual.workflow.test(operand1=时间类别, operator="==", operand2="近30日", operator_options="{}", _block=("抖店订单管理时间选择", 78, "Else IF")):
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_输入框(新)"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="5", _block=("抖店订单管理时间选择", 79, "点击元素(web)"))
                近一个月 = xbot_visual.web.element.get_element(browser=网页对象, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"sp-tag-content\"][text()=\"近一个月\"]", is_related_parent=False, parent=None, timeout="20", _block=("抖店订单管理时间选择", 80, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=网页对象, element=近一个月, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 81, "点击元素(web)"))
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_确定按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 82, "点击元素(web)"))
                return
            #endif
        #endif
        #endregion
        # programing.comment
        # programing.comment
        开始日期_datetime = xbot_visual.datetime.from_string(text=开始日期, is_custom_format=True, format="%Y/%m/%d %H:%M:%S", _block=("抖店订单管理时间选择", 89, "转换到日期时间"))
        结束日期_datetime = xbot_visual.datetime.from_string(text=结束日期, is_custom_format=True, format="%Y/%m/%d %H:%M:%S", _block=("抖店订单管理时间选择", 90, "转换到日期时间"))
        开始日期_datetime_parts = xbot_visual.datetime.get_parts(datetime=开始日期_datetime, _block=("抖店订单管理时间选择", 91, "获取时间详细信息"))
        结束日期_datetime_parts = xbot_visual.datetime.get_parts(datetime=结束日期_datetime, _block=("抖店订单管理时间选择", 92, "获取时间详细信息"))
        # programing.comment
        if xbot_visual.web.browser.contains_element_or_text(browser=网页对象, content_type="not_contains_element", selector=package.selector("订单管理时间选择_开始日期_年"), text="", _block=("抖店订单管理时间选择", 94, "IF 网页包含")):
            try:
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_输入框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="5", _block=("抖店订单管理时间选择", 96, "点击元素(web)"))
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_输入框(新)"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="5", _block=("抖店订单管理时间选择", 98, "点击元素(web)"))
            #endtry
        #endif
        # programing.comment
        #region 开始日期-年份选择
        开始日期_年_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_年"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 103, "获取元素信息(web)"))
        开始日期_年_attribute = xbot_visual.text.extract_content_from_text(text=开始日期_年_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择", 104, "从文本中提取内容"))
        if xbot_visual.workflow.test(operand1=开始日期_年_attribute, operator="!=", operand2=开始日期_datetime_parts.year, operator_options="{}", _block=("抖店订单管理时间选择", 105, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_年"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 106, "点击元素(web)"))
            for 开始日期_年_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_年相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 107, "循环相似元素(web)")):
                开始日期__年_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=开始日期_年_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 108, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=开始日期__年_attribute, operator="==", operand2=开始日期_datetime_parts.year, operator_options="{}", _block=("抖店订单管理时间选择", 109, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=开始日期_年_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 110, "点击元素(web)"))
                    break
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        #region 开始日期-月份选择
        开始日期_月_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_月"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 118, "获取元素信息(web)"))
        开始日期_月_attribute = xbot_visual.text.extract_content_from_text(text=开始日期_月_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择", 119, "从文本中提取内容"))
        if xbot_visual.workflow.test(operand1=开始日期_月_attribute, operator="!=", operand2=开始日期_datetime_parts.month, operator_options="{}", _block=("抖店订单管理时间选择", 120, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_月"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 121, "点击元素(web)"))
            for 开始日期_月_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_月相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 122, "循环相似元素(web)")):
                开始日期_月_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=开始日期_月_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 123, "获取元素信息(web)"))
                开始日期_月_attribute = xbot_visual.text.extract_content_from_text(text=开始日期_月_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择", 124, "从文本中提取内容"))
                if xbot_visual.workflow.test(operand1=开始日期_月_attribute, operator="==", operand2=开始日期_datetime_parts.month, operator_options="{}", _block=("抖店订单管理时间选择", 125, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=开始日期_月_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 126, "点击元素(web)"))
                    break
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        for 日期_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_日相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 133, "循环相似元素(web)")):
            日期_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=日期_element, operation="other", absolute_url=False, attribute_name="title", relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 134, "获取元素信息(web)"))
            if xbot_visual.workflow.test(operand1=日期_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.year)+"-"+str(开始日期_datetime_parts.month).zfill(2)+"-"+str(开始日期_datetime_parts.day).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择", 135, "IF 条件")):
                xbot_visual.web.element.click(browser=网页对象, element=日期_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 136, "点击元素(web)"))
                break
            #endif
        #endloop
        # programing.comment
        结束日期_年_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_年"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 141, "获取元素信息(web)"))
        结束日期_年_attribute = xbot_visual.text.extract_content_from_text(text=结束日期_年_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择", 142, "从文本中提取内容"))
        结束日期_月_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_月"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 143, "获取元素信息(web)"))
        结束日期_月_attribute = xbot_visual.text.extract_content_from_text(text=结束日期_月_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择", 144, "从文本中提取内容"))
        #region 结束日期-年份选择
        if xbot_visual.workflow.test(operand1=结束日期_年_attribute, operator="!=", operand2=结束日期_datetime_parts.year, operator_options="{}", _block=("抖店订单管理时间选择", 146, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_年"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 147, "点击元素(web)"))
            for 结束日期_年_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_年相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 148, "循环相似元素(web)")):
                结束日期__年_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=结束日期_年_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 149, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=结束日期__年_attribute, operator="==", operand2=结束日期_datetime_parts.year, operator_options="{}", _block=("抖店订单管理时间选择", 150, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=结束日期_年_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 151, "点击元素(web)"))
                    break
                #endif
            #endloop
        else:
            pass
        #endif
        # programing.comment
        #region 结束日期-月份选择
        if xbot_visual.workflow.test(operand1=结束日期_月_attribute, operator="!=", operand2=结束日期_datetime_parts.month, operator_options="{}", _block=("抖店订单管理时间选择", 159, "IF 条件")):
            if xbot_visual.web.browser.element_display(browser=网页对象, content_type="display", selector=package.selector("订单管理时间选择_结束日期_月"), _block=("抖店订单管理时间选择", 160, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_月"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 161, "点击元素(web)"))
            #endif
            for 结束日期_月_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_月相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 163, "循环相似元素(web)")):
                结束日期_月_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=结束日期_月_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 164, "获取元素信息(web)"))
                结束日期_月_attribute = xbot_visual.text.extract_content_from_text(text=结束日期_月_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择", 165, "从文本中提取内容"))
                if xbot_visual.workflow.test(operand1=结束日期_月_attribute, operator="==", operand2=结束日期_datetime_parts.month, operator_options="{}", _block=("抖店订单管理时间选择", 166, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=结束日期_月_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 167, "点击元素(web)"))
                    break
                #endif
            #endloop
        #endif
        #endregion
        #endregion
        # programing.comment
        #region 结束日期-日期选择
        for 日期_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_日相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 176, "循环相似元素(web)")):
            日期_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=日期_element, operation="other", absolute_url=False, attribute_name="title", relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 177, "获取元素信息(web)"))
            if xbot_visual.workflow.test(operand1=日期_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.year)+"-"+str(结束日期_datetime_parts.month).zfill(2)+"-"+str(结束日期_datetime_parts.day).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择", 178, "IF 条件")):
                xbot_visual.web.element.click(browser=网页对象, element=日期_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 179, "点击元素(web)"))
                break
            #endif
        #endloop
        #endregion
        # programing.comment
        #region 开始日期-时分秒选择
        开始日期_时分秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_时分秒"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 186, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=开始日期_时分秒_attribute, operator="!=", operand2=lambda: str(开始日期_datetime_parts.hour).zfill(2)+":"+str(开始日期_datetime_parts.minute).zfill(2)+":"+str(开始日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择", 187, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_时分秒"), simulate=True, move_mouse=False, clicks="dbclick", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 188, "点击元素(web)"))
            for 时分秒_时_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_时相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 189, "循环相似元素(web)")):
                时分秒_时_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_时_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 190, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_时_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.hour).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择", 191, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_时_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 192, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_分_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_分相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 195, "循环相似元素(web)")):
                时分秒_分_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_分_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 196, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_分_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.minute).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择", 197, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_分_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 198, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_秒_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_秒相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 201, "循环相似元素(web)")):
                时分秒_秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_秒_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 202, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_秒_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择", 203, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_秒_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 204, "点击元素(web)"))
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        #region 结束日期-时分秒选择
        结束日期_时分秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_时分秒"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 211, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=结束日期_时分秒_attribute, operator="!=", operand2=lambda: str(结束日期_datetime_parts.hour).zfill(2)+":"+str(结束日期_datetime_parts.minute).zfill(2)+":"+str(结束日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择", 212, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_时分秒"), simulate=True, move_mouse=False, clicks="dbclick", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 213, "点击元素(web)"))
            for 时分秒_时_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_结束日期_时相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 214, "循环相似元素(web)")):
                时分秒_时_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_时_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 215, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_时_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.hour).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择", 216, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_时_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 217, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_分_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_结束日期_分相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 220, "循环相似元素(web)")):
                时分秒_分_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_分_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 221, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_分_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.minute).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择", 222, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_分_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 223, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_秒_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_结束日期_秒相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择", 226, "循环相似元素(web)")):
                时分秒_秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_秒_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择", 227, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_秒_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择", 228, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_秒_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 229, "点击元素(web)"))
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_确定按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择", 235, "点击元素(web)"))
        开始日期_结果_str = xbot_visual.programing.variable(value=lambda: None
        , _block=("抖店订单管理时间选择", 236, "设置变量"))
        结束日期_结果_str = xbot_visual.programing.variable(value=lambda: None
        , _block=("抖店订单管理时间选择", 237, "设置变量"))
        try:
            开始日期_结果_str = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="5", _block=("抖店订单管理时间选择", 239, "获取元素信息(web)"))
            结束日期_结果_str = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="5", _block=("抖店订单管理时间选择", 240, "获取元素信息(web)"))
        except Exception as exception2:
            exception2 = xbot_visual.trace(exception2)
            开始日期_结果_str = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_输入框(新)"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="5", _block=("抖店订单管理时间选择", 242, "获取元素信息(web)"))
            结束日期_结果_str = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_输入框(新)"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="5", _block=("抖店订单管理时间选择", 243, "获取元素信息(web)"))
        #endtry
        if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 开始日期_结果_str,"operand2": 开始日期,"operator": "!="},{"operand1": 结束日期_结果_str,"operand2": 结束日期,"operator": "!="}], _block=("抖店订单管理时间选择", 245, "IF 多条件")):
            raise Exception("时间选择失败，请重新尝试，如果依旧失败请联系指令开发人员")
        #endif
    finally:
        pass
