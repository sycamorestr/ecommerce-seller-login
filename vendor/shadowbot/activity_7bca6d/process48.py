import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        web_page = None
        验证码失败最大重试次数 = 0
    else:
        web_page = args.get("web_page", None)
        验证码失败最大重试次数 = args.get("验证码失败最大重试次数", 0)
    try:
        for idx in xbot_visual.workflow.range_iterator(start="1", stop=验证码失败最大重试次数, step="1", _block=("抖音平台登录验证", 1, "For次数循环")):
            # 判断验证码类型
            xbot_visual.programing.log(type="info", text="抖音平台登录验证： 第" + xbot_visual.sh_str(idx) + "次", _block=("抖音平台登录验证", 3, "打印日志"))
            # ----------------滑块验证
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("抖店_目标滑块_ifream"), _block=("抖音平台登录验证", 5, "IF 元素可见(web)")):
                _ = xbot_visual.process.run(process="process45", package=__name__, inputs={
                    "web_page": web_page,
                    }, outputs=[
                ], _block=("抖音平台登录验证", 6, "调用流程"))
            #endif
            # -----------------文字点选验证
            try:
                点选验证_元素对象 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@id=\"verify-bar-code\"]", is_related_parent=False, parent=None, timeout="1", _block=("抖音平台登录验证", 9, "获取元素对象(web)"))
            except Exception as e:
                pass
                点选验证_元素对象 = None
            if xbot_visual.workflow.test(operand1=点选验证_元素对象, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖音平台登录验证", 10, "IF 条件")):
                _ = xbot_visual.process.run(process="process44", package=__name__, inputs={
                    "web_page": web_page,
                    }, outputs=[
                ], _block=("抖音平台登录验证", 11, "调用流程"))
            #endif
        #endloop
    finally:
        pass
