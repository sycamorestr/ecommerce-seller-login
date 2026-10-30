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
        开始日期 = "2022/11/01 00:00:00"
        结束日期 = "2022/11/19 23:59:59"
    else:
        网页对象 = args.get("网页对象", None)
        筛选类别 = args.get("筛选类别", "下单时间")
        时间类别 = args.get("时间类别", "手动时间输入")
        开始日期 = args.get("开始日期", "2022/11/01 00:00:00")
        结束日期 = args.get("结束日期", "2022/11/19 23:59:59")
    try:
        # web.get
        # 判断时间输入框是否可见
        #region 展开时间输入框
        loop_index = -1
        while True:
            loop_index += 1
            抖店订单管理时间选择_展开_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_展开"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 5, "获取元素信息(web)"))
            if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 抖店订单管理时间选择_展开_attribute,"operand2": "展开","operator": "=="},{"operand1": 抖店订单管理时间选择_展开_attribute,"operand2": "更多筛选","operator": "=="}], _block=("抖店订单管理时间选择-新版", 6, "IF 多条件")):
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_展开"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 7, "点击元素(web)"))
            else:
                break
                #endregion
            #endif
        #endloop
        # 选择筛选类别
        #region 选择筛选类别
        抖店订单管理时间选择_筛选类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_筛选类别"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 15, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=筛选类别, operator="!=", operand2=抖店订单管理时间选择_筛选类别_attribute, operator_options="{}", _block=("抖店订单管理时间选择-新版", 16, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_筛选类别"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 17, "点击元素(web)"))
            for 筛选类别_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_筛选类别_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 18, "循环相似元素(web)")):
                筛选类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=筛选类别_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 19, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=筛选类别_attribute, operator="==", operand2=筛选类别, operator_options="{}", _block=("抖店订单管理时间选择-新版", 20, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=筛选类别_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 21, "点击元素(web)"))
                    break
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        #region 选择常见日期
        if xbot_visual.workflow.test(operand1=时间类别, operator="!=", operand2="手动时间输入", operator_options="{}", _block=("抖店订单管理时间选择-新版", 29, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_时间类别"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 30, "点击元素(web)"))
            for 时间类别_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_时间类别_相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 31, "循环相似元素(web)")):
                时间类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时间类别_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 32, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时间类别_attribute, operator="==", operand2=时间类别, operator_options="{}", _block=("抖店订单管理时间选择-新版", 33, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时间类别_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 34, "点击元素(web)"))
                    break
                #endif
            #endloop
            return
        #endif
        #endregion
        # programing.comment
        # programing.comment
        开始日期_datetime = xbot_visual.datetime.from_string(text=开始日期, is_custom_format=True, format="%Y/%m/%d %H:%M:%S", _block=("抖店订单管理时间选择-新版", 43, "转换到日期时间"))
        结束日期_datetime = xbot_visual.datetime.from_string(text=结束日期, is_custom_format=True, format="%Y/%m/%d %H:%M:%S", _block=("抖店订单管理时间选择-新版", 44, "转换到日期时间"))
        开始日期_datetime_parts = xbot_visual.datetime.get_parts(datetime=开始日期_datetime, _block=("抖店订单管理时间选择-新版", 45, "获取时间详细信息"))
        结束日期_datetime_parts = xbot_visual.datetime.get_parts(datetime=结束日期_datetime, _block=("抖店订单管理时间选择-新版", 46, "获取时间详细信息"))
        # programing.comment
        if xbot_visual.web.browser.contains_element_or_text(browser=网页对象, content_type="not_contains_element", selector=package.selector("订单管理时间选择_开始日期_年"), text="", _block=("抖店订单管理时间选择-新版", 48, "IF 网页包含")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_输入框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 49, "点击元素(web)"))
        #endif
        # programing.comment
        #region 开始日期-年份选择
        开始日期_年_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_年"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 53, "获取元素信息(web)"))
        开始日期_年_attribute = xbot_visual.text.extract_content_from_text(text=开始日期_年_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择-新版", 54, "从文本中提取内容"))
        if xbot_visual.workflow.test(operand1=开始日期_年_attribute, operator="!=", operand2=开始日期_datetime_parts.year, operator_options="{}", _block=("抖店订单管理时间选择-新版", 55, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_年"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 56, "点击元素(web)"))
            for 开始日期_年_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_年相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 57, "循环相似元素(web)")):
                开始日期__年_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=开始日期_年_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 58, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=开始日期__年_attribute, operator="==", operand2=开始日期_datetime_parts.year, operator_options="{}", _block=("抖店订单管理时间选择-新版", 59, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=开始日期_年_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 60, "点击元素(web)"))
                    break
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        #region 开始日期-月份选择
        开始日期_月_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_月"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 68, "获取元素信息(web)"))
        开始日期_月_attribute = xbot_visual.text.extract_content_from_text(text=开始日期_月_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择-新版", 69, "从文本中提取内容"))
        if xbot_visual.workflow.test(operand1=开始日期_月_attribute, operator="!=", operand2=开始日期_datetime_parts.month, operator_options="{}", _block=("抖店订单管理时间选择-新版", 70, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_月"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 71, "点击元素(web)"))
            for 开始日期_月_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_月相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 72, "循环相似元素(web)")):
                开始日期_月_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=开始日期_月_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 73, "获取元素信息(web)"))
                开始日期_月_attribute = xbot_visual.text.extract_content_from_text(text=开始日期_月_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择-新版", 74, "从文本中提取内容"))
                if xbot_visual.workflow.test(operand1=开始日期_月_attribute, operator="==", operand2=开始日期_datetime_parts.month, operator_options="{}", _block=("抖店订单管理时间选择-新版", 75, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=开始日期_月_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 76, "点击元素(web)"))
                    break
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        for 日期_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_日相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 83, "循环相似元素(web)")):
            日期_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=日期_element, operation="other", absolute_url=False, attribute_name="title", relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 84, "获取元素信息(web)"))
            if xbot_visual.workflow.test(operand1=日期_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.year)+"-"+str(开始日期_datetime_parts.month).zfill(2)+"-"+str(开始日期_datetime_parts.day).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择-新版", 85, "IF 条件")):
                xbot_visual.web.element.click(browser=网页对象, element=日期_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 86, "点击元素(web)"))
                break
            #endif
        #endloop
        # programing.comment
        #region 结束日期-年份选择
        结束日期_年_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_年"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 92, "获取元素信息(web)"))
        结束日期_年_attribute = xbot_visual.text.extract_content_from_text(text=结束日期_年_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择-新版", 93, "从文本中提取内容"))
        if xbot_visual.workflow.test(operand1=结束日期_年_attribute, operator="!=", operand2=结束日期_datetime_parts.year, operator_options="{}", _block=("抖店订单管理时间选择-新版", 94, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_年"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 95, "点击元素(web)"))
            for 结束日期_年_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_年相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 96, "循环相似元素(web)")):
                结束日期__年_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=结束日期_年_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 97, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=结束日期__年_attribute, operator="==", operand2=结束日期_datetime_parts.year, operator_options="{}", _block=("抖店订单管理时间选择-新版", 98, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=结束日期_年_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 99, "点击元素(web)"))
                    break
                #endif
            #endloop
            for 结束日期_月_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_月相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 103, "循环相似元素(web)")):
                结束日期_月_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=结束日期_月_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 104, "获取元素信息(web)"))
                结束日期_月_attribute = xbot_visual.text.extract_content_from_text(text=结束日期_月_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择-新版", 105, "从文本中提取内容"))
                if xbot_visual.workflow.test(operand1=结束日期_月_attribute, operator="==", operand2=结束日期_datetime_parts.month, operator_options="{}", _block=("抖店订单管理时间选择-新版", 106, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=结束日期_月_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 107, "点击元素(web)"))
                    break
                #endif
            #endloop
        else:
            # programing.comment
            #region 结束日期-月份选择
            结束日期_月_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_月"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 114, "获取元素信息(web)"))
            结束日期_月_attribute = xbot_visual.text.extract_content_from_text(text=结束日期_月_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择-新版", 115, "从文本中提取内容"))
            if xbot_visual.workflow.test(operand1=结束日期_月_attribute, operator="!=", operand2=结束日期_datetime_parts.month, operator_options="{}", _block=("抖店订单管理时间选择-新版", 116, "IF 条件")):
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_月"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 117, "点击元素(web)"))
                for 结束日期_月_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_月相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 118, "循环相似元素(web)")):
                    结束日期_月_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=结束日期_月_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 119, "获取元素信息(web)"))
                    结束日期_月_attribute = xbot_visual.text.extract_content_from_text(text=结束日期_月_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店订单管理时间选择-新版", 120, "从文本中提取内容"))
                    if xbot_visual.workflow.test(operand1=结束日期_月_attribute, operator="==", operand2=结束日期_datetime_parts.month, operator_options="{}", _block=("抖店订单管理时间选择-新版", 121, "IF 条件")):
                        xbot_visual.web.element.click(browser=网页对象, element=结束日期_月_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 122, "点击元素(web)"))
                        break
                    #endif
                #endloop
            #endif
            #endregion
        #endif
        #endregion
        # programing.comment
        #region 结束日期-日期选择
        for 日期_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_日相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 132, "循环相似元素(web)")):
            日期_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=日期_element, operation="other", absolute_url=False, attribute_name="title", relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 133, "获取元素信息(web)"))
            if xbot_visual.workflow.test(operand1=日期_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.year)+"-"+str(结束日期_datetime_parts.month).zfill(2)+"-"+str(结束日期_datetime_parts.day).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择-新版", 134, "IF 条件")):
                xbot_visual.web.element.click(browser=网页对象, element=日期_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 135, "点击元素(web)"))
                break
            #endif
        #endloop
        #endregion
        # programing.comment
        #region 开始日期-时分秒选择
        开始日期_时分秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_时分秒"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 142, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=开始日期_时分秒_attribute, operator="!=", operand2=lambda: str(开始日期_datetime_parts.hour).zfill(2)+":"+str(开始日期_datetime_parts.minute).zfill(2)+":"+str(开始日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择-新版", 143, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_时分秒"), simulate=True, move_mouse=False, clicks="dbclick", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 144, "点击元素(web)"))
            for 时分秒_时_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_时相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 145, "循环相似元素(web)")):
                时分秒_时_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_时_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 146, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_时_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.hour).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择-新版", 147, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_时_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 148, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_分_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_分相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 151, "循环相似元素(web)")):
                时分秒_分_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_分_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 152, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_分_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.minute).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择-新版", 153, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_分_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 154, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_秒_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_开始日期_秒相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 157, "循环相似元素(web)")):
                时分秒_秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_秒_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 158, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_秒_attribute, operator="==", operand2=lambda: str(开始日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择-新版", 159, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_秒_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 160, "点击元素(web)"))
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        #region 结束日期-时分秒选择
        结束日期_时分秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_时分秒"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 167, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=结束日期_时分秒_attribute, operator="!=", operand2=lambda: str(结束日期_datetime_parts.hour).zfill(2)+":"+str(结束日期_datetime_parts.minute).zfill(2)+":"+str(结束日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择-新版", 168, "IF 条件")):
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_时分秒"), simulate=True, move_mouse=False, clicks="dbclick", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 169, "点击元素(web)"))
            for 时分秒_时_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_结束日期_时相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 170, "循环相似元素(web)")):
                时分秒_时_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_时_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 171, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_时_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.hour).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择-新版", 172, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_时_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 173, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_分_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_结束日期_分相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 176, "循环相似元素(web)")):
                时分秒_分_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_分_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 177, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_分_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.minute).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择-新版", 178, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_分_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 179, "点击元素(web)"))
                #endif
            #endloop
            for 时分秒_秒_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("订单管理时间选择_结束日期_秒相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店订单管理时间选择-新版", 182, "循环相似元素(web)")):
                时分秒_秒_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=时分秒_秒_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 183, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=时分秒_秒_attribute, operator="==", operand2=lambda: str(结束日期_datetime_parts.second).zfill(2), operator_options="{}", _block=("抖店订单管理时间选择-新版", 184, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=时分秒_秒_element, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="0", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 185, "点击元素(web)"))
                #endif
            #endloop
        #endif
        #endregion
        # programing.comment
        xbot_visual.web.element.click(browser=网页对象, element=package.selector("订单管理时间选择_确定按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店订单管理时间选择-新版", 191, "点击元素(web)"))
        开始日期_结果_str = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_开始日期_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 192, "获取元素信息(web)"))
        结束日期_结果_str = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("订单管理时间选择_结束日期_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店订单管理时间选择-新版", 193, "获取元素信息(web)"))
        if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 开始日期_结果_str,"operand2": 开始日期,"operator": "!="},{"operand1": 结束日期_结果_str,"operand2": 结束日期,"operator": "!="}], _block=("抖店订单管理时间选择-新版", 194, "IF 多条件")):
            raise Exception("时间选择失败，请重新尝试，如果依旧失败请联系指令开发人员")
        #endif
    finally:
        pass
