import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    数据字典 = {}
    if args is None:
        网页对象 = None
    else:
        网页对象 = args.get("网页对象", None)
    try:
        # web.get
        web_page = xbot_visual.programing.variable(value=网页对象
        , _block=("抖店商家体验分(新版)", 2, "设置变量"))
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://fxg.jinritemai.com/ffa/eco/experience-score", ignore_cache=False, load_timeout="20", _block=("抖店商家体验分(新版)", 3, "跳转至新网址"))
        if xbot_visual.web.browser.contains_element_or_text(browser=web_page, content_type="contains_element", selector=package.selector("抖店_体验分_提示1"), text="", _block=("抖店商家体验分(新版)", 4, "IF 网页包含")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_提示_下一步"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店商家体验分(新版)", 5, "点击元素(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_提示_完成"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店商家体验分(新版)", 6, "点击元素(web)"))
        #endif
        # 常规11条分数
        for 元素框_element in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("新版_抖店_体验分相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店商家体验分(新版)", 9, "循环相似元素(web)")):
            title_element = xbot_visual.programing.variable(value=lambda: None
            , _block=("抖店商家体验分(新版)", 10, "设置变量"))
            较前一日_element = xbot_visual.programing.variable(value=lambda: None
            , _block=("抖店商家体验分(新版)", 11, "设置变量"))
            try:
                title_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("新版_DSR_标题相似元素组"), css_selector="", xpath_selector="", is_related_parent=True, parent=元素框_element, timeout="1", _block=("抖店商家体验分(新版)", 13, "获取元素对象(web)"))
                try:
                    较前一日_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("新版_DSR_较前一日相似元素组"), css_selector="", xpath_selector="", is_related_parent=True, parent=元素框_element, timeout="1", _block=("抖店商家体验分(新版)", 14, "获取元素对象(web)"))
                except Exception as e:
                    pass
                    较前一日_element = None
                try:
                    特殊较前一日_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("新版_DSR_特殊较前一日相似元素组"), css_selector="", xpath_selector="", is_related_parent=True, parent=元素框_element, timeout="1", _block=("抖店商家体验分(新版)", 15, "获取元素对象(web)"))
                except Exception as e:
                    pass
                    特殊较前一日_element = None
                if xbot_visual.workflow.test(operand1=特殊较前一日_element, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店商家体验分(新版)", 16, "IF 条件")):
                    try:
                        较前一日_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=特殊较前一日_element, css_selector="", xpath_selector="", is_related_parent=True, parent=元素框_element, timeout="1", _block=("抖店商家体验分(新版)", 17, "获取元素对象(web)"))
                    except Exception as e:
                        pass
                        较前一日_element = None
                #endif
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                continue
            #endtry
            try:
                值_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("新版_DSR_值相似元素组"), css_selector="", xpath_selector="", is_related_parent=True, parent=元素框_element, timeout="5", _block=("抖店商家体验分(新版)", 22, "获取元素对象(web)"))
            except Exception as e:
                pass
                值_element = None
            同行比较_element = xbot_visual.web.element.get_element(browser=较前一日_element, select_type="selector", selector=package.selector("新版_DSR_同行对比相似元素组"), css_selector="", xpath_selector="", is_related_parent=True, parent=元素框_element, timeout="20", _block=("抖店商家体验分(新版)", 23, "获取元素对象(web)"))
            title_attribute = xbot_visual.web.element.get_details(browser=web_page, element=title_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店商家体验分(新版)", 24, "获取元素信息(web)"))
            if xbot_visual.workflow.test(operand1=值_element, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店商家体验分(新版)", 25, "IF 条件")):
                值_attribute = xbot_visual.web.element.get_details(browser=web_page, element=值_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店商家体验分(新版)", 26, "获取元素信息(web)"))
            else:
                值_attribute = xbot_visual.programing.variable(value=""
                , _block=("抖店商家体验分(新版)", 28, "设置变量"))
            #endif
            较前一日_attribute = xbot_visual.web.element.get_details(browser=web_page, element=较前一日_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店商家体验分(新版)", 30, "获取元素信息(web)"))
            try:
                上涨图标_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("商家体验分_上涨图标_新版"), css_selector="", xpath_selector="", is_related_parent=True, parent=元素框_element, timeout="0", _block=("抖店商家体验分(新版)", 31, "获取元素对象(web)"))
            except Exception as e:
                pass
                上涨图标_element = None
            try:
                下降图标_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("商家体验分_下降图标_新版"), css_selector="", xpath_selector="", is_related_parent=True, parent=元素框_element, timeout="0", _block=("抖店商家体验分(新版)", 32, "获取元素对象(web)"))
            except Exception as e:
                pass
                下降图标_element = None
            if xbot_visual.workflow.test(operand1=上涨图标_element, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店商家体验分(新版)", 33, "IF 条件")):
                较前一日_attribute = xbot_visual.text.replace_content_from_text(text=较前一日_attribute, regular_pattern="", replace_way="content", replace_text=lambda: "\n", just_get_first=False, ignore_case=False, new_ignore_case=False, dest_text="上涨", _block=("抖店商家体验分(新版)", 34, "文本替换"))
            #endif
            if xbot_visual.workflow.test(operand1=下降图标_element, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店商家体验分(新版)", 36, "IF 条件")):
                较前一日_attribute = xbot_visual.text.replace_content_from_text(text=较前一日_attribute, regular_pattern="", replace_way="content", replace_text=lambda: "\n", just_get_first=False, ignore_case=False, new_ignore_case=False, dest_text="下降", _block=("抖店商家体验分(新版)", 37, "文本替换"))
            #endif
            同行比较_attribute = xbot_visual.web.element.get_details(browser=web_page, element=同行比较_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店商家体验分(新版)", 39, "获取元素信息(web)"))
            xbot_visual.dictionary.set(dict=数据字典, key=title_attribute, value=lambda: [值_attribute,较前一日_attribute,同行比较_attribute], _block=("抖店商家体验分(新版)", 40, "设置键值对"))
        #endloop
        # 我的体验分
        当前体验分_比较数据_list = xbot_visual.programing.variable(value=lambda: []
        , _block=("抖店商家体验分(新版)", 43, "设置变量"))
        当前体验分_attribute = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("新版_商家体验分_当前体验分"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店商家体验分(新版)", 44, "获取元素信息(web)"))
        当前体验分_attribute = xbot_visual.text.extract_content_from_text(text=当前体验分_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店商家体验分(新版)", 45, "从文本中提取内容"))
        xbot_visual.list.append_or_insert(lst=当前体验分_比较数据_list, insert_way="append", index="0", elem=当前体验分_attribute, _block=("抖店商家体验分(新版)", 46, "列表插入一项"))
        for 比较数据_element in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("新版_商家体验分_数据组"), operation="element", absolute_url=False, attribute_name=None, timeout="5", loop_start_index="1", loop_end_index="2", output_with_index=False, _block=("抖店商家体验分(新版)", 47, "循环相似元素(web)")):
            比较数据_attribute = xbot_visual.web.element.get_details(browser=web_page, element=比较数据_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店商家体验分(新版)", 48, "获取元素信息(web)"))
            try:
                上涨图标_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("商家体验分_上涨图标_新版"), css_selector="", xpath_selector="", is_related_parent=True, parent=比较数据_element, timeout="0", _block=("抖店商家体验分(新版)", 49, "获取元素对象(web)"))
            except Exception as e:
                pass
                上涨图标_element = None
            try:
                下降图标_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("商家体验分_下降图标_新版"), css_selector="", xpath_selector="", is_related_parent=True, parent=比较数据_element, timeout="0", _block=("抖店商家体验分(新版)", 50, "获取元素对象(web)"))
            except Exception as e:
                pass
                下降图标_element = None
            if xbot_visual.workflow.test(operand1=上涨图标_element, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店商家体验分(新版)", 51, "IF 条件")):
                比较数据_attribute = xbot_visual.text.replace_content_from_text(text=比较数据_attribute, regular_pattern="", replace_way="content", replace_text=lambda: "\n", just_get_first=False, ignore_case=False, new_ignore_case=False, dest_text="上涨", _block=("抖店商家体验分(新版)", 52, "文本替换"))
            #endif
            if xbot_visual.workflow.test(operand1=下降图标_element, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店商家体验分(新版)", 54, "IF 条件")):
                比较数据_attribute = xbot_visual.text.replace_content_from_text(text=比较数据_attribute, regular_pattern="", replace_way="content", replace_text=lambda: "\n", just_get_first=False, ignore_case=False, new_ignore_case=False, dest_text="下降", _block=("抖店商家体验分(新版)", 55, "文本替换"))
            #endif
            xbot_visual.list.append_or_insert(lst=当前体验分_比较数据_list, insert_way="append", index="0", elem=比较数据_attribute, _block=("抖店商家体验分(新版)", 57, "列表插入一项"))
        #endloop
        xbot_visual.dictionary.set(dict=数据字典, key="我的体验分", value=当前体验分_比较数据_list, _block=("抖店商家体验分(新版)", 59, "设置键值对"))
        # programing.log
        # 我的体验分下方，3体验分
        我的体验分下方3_title = xbot_visual.programing.variable(value=lambda: ["商品体验","物流体验","服务体验"]
        , _block=("抖店商家体验分(新版)", 62, "设置变量"))
        for 元素框_element_index, 元素框_element in enumerate(xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("新版_三个模块体验分"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("抖店商家体验分(新版)", 63, "循环相似元素(web)"))):
            元素值_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("新版_三个模块体验分_值相似元素组"), css_selector="", xpath_selector="", is_related_parent=True, parent=元素框_element, timeout="20", _block=("抖店商家体验分(新版)", 64, "获取元素对象(web)"))
            较前1日_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("新版_三个模块体验分_较前一日相似元素组"), css_selector="", xpath_selector="", is_related_parent=True, parent=元素框_element, timeout="20", _block=("抖店商家体验分(新版)", 65, "获取元素对象(web)"))
            # web.element.get_element
            体验分_attribute = xbot_visual.web.element.get_details(browser=web_page, element=元素值_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店商家体验分(新版)", 67, "获取元素信息(web)"))
            体验分_attribute = xbot_visual.text.extract_content_from_text(text=体验分_attribute, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("抖店商家体验分(新版)", 68, "从文本中提取内容"))
            较前1日_attribute = xbot_visual.web.element.get_details(browser=web_page, element=较前1日_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店商家体验分(新版)", 69, "获取元素信息(web)"))
            try:
                上涨图标_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("商家体验分_上涨图标_新版"), css_selector="", xpath_selector="", is_related_parent=True, parent=较前1日_element, timeout="0", _block=("抖店商家体验分(新版)", 70, "获取元素对象(web)"))
            except Exception as e:
                pass
                上涨图标_element = None
            try:
                下降图标_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("商家体验分_下降图标_新版"), css_selector="", xpath_selector="", is_related_parent=True, parent=较前1日_element, timeout="0", _block=("抖店商家体验分(新版)", 71, "获取元素对象(web)"))
            except Exception as e:
                pass
                下降图标_element = None
            if xbot_visual.workflow.test(operand1=上涨图标_element, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店商家体验分(新版)", 72, "IF 条件")):
                较前1日_attribute = xbot_visual.text.replace_content_from_text(text=较前1日_attribute, regular_pattern="", replace_way="content", replace_text=lambda: "\n", just_get_first=False, ignore_case=False, new_ignore_case=False, dest_text="上涨", _block=("抖店商家体验分(新版)", 73, "文本替换"))
            #endif
            if xbot_visual.workflow.test(operand1=下降图标_element, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店商家体验分(新版)", 75, "IF 条件")):
                较前1日_attribute = xbot_visual.text.replace_content_from_text(text=较前1日_attribute, regular_pattern="", replace_way="content", replace_text=lambda: "\n", just_get_first=False, ignore_case=False, new_ignore_case=False, dest_text="下降", _block=("抖店商家体验分(新版)", 76, "文本替换"))
            #endif
            xbot_visual.dictionary.set(dict=数据字典, key=lambda: 我的体验分下方3_title[元素框_element_index], value=lambda: [体验分_attribute,较前1日_attribute], _block=("抖店商家体验分(新版)", 78, "设置键值对"))
        #endloop
        # programing.log
    finally:
        args["数据字典"] = 数据字典
