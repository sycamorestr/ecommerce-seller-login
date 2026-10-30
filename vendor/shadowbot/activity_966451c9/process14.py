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
        # web.create
        web_page = xbot_visual.programing.variable(value=网页对象
        , _block=("抖店商家体验分", 2, "设置变量"))
        # web.browser.navigate
        # web.browser.contains_element_or_text
        process_result = xbot_visual.process.run(process="process26", package=__name__, inputs={
            "网页对象": lambda: 网页对象,
            }, outputs=[
            "数据字典",
        ], _block=("抖店商家体验分", 5, "调用流程"))
        数据字典 = xbot_visual.programing.variable(value=process_result.数据字典
        , _block=("抖店商家体验分", 6, "设置变量"))
        # workflow.else
        # programing.region
        # web.browser.contains_element_or_text
        # web.element.click
        # web.element.click
        # workflow.endif
        # programing.comment
        # web.element.foreach_element
        # programing.variable
        # programing.variable
        # programing.try
        # web.element.get_element
        # web.element.get_element
        # web.element.get_element
        # workflow.if
        # web.element.get_element
        # workflow.endif
        # web.element.get_element
        # web.element.get_all_elements
        # web.element.get_element
        # programing.catch
        # web.element.get_details
        # dictionary.set
        # workflow.continue
        # programing.endtry
        # web.element.get_element
        # web.element.get_element
        # web.element.get_element
        # web.element.get_details
        # workflow.if
        # web.element.get_details
        # workflow.else
        # programing.variable
        # workflow.endif
        # web.element.get_details
        # web.element.get_element
        # web.element.get_element
        # workflow.if
        # text.replace_content_from_text
        # workflow.endif
        # workflow.if
        # text.replace_content_from_text
        # workflow.endif
        # web.element.get_details
        # dictionary.set
        # workflow.endloop
        # programing.comment
        # programing.variable
        # web.element.get_details
        # text.extract_content_from_text
        # list.append_or_insert
        # web.element.foreach_element
        # web.element.get_details
        # web.element.get_element
        # web.element.get_element
        # workflow.if
        # text.replace_content_from_text
        # workflow.endif
        # workflow.if
        # text.replace_content_from_text
        # workflow.endif
        # list.append_or_insert
        # workflow.endloop
        # dictionary.set
        # programing.log
        # programing.comment
        # programing.variable
        # web.element.foreach_element
        # workflow.if
        # web.element.get_all_elements
        # web.element.get_element
        # web.element.get_element
        # web.element.get_element
        # web.element.get_element
        # web.element.get_details
        # text.extract_content_from_text
        # web.element.get_details
        # web.element.get_element
        # web.element.get_element
        # workflow.if
        # text.replace_content_from_text
        # workflow.endif
        # workflow.if
        # text.replace_content_from_text
        # workflow.endif
        # dictionary.set
        # workflow.endif
        # workflow.endloop
        # programing.log
        # programing.endregion
        # workflow.endif
    finally:
        args["数据字典"] = 数据字典
