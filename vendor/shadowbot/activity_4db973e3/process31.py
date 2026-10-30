import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    if args is None:
        web_page = None
        最大重试次数 = 20
        偏移量 = 1
    else:
        web_page = args.get("web_page", None)
        最大重试次数 = args.get("最大重试次数", 20)
        偏移量 = args.get("偏移量", 1)
    try:
        if xbot_visual.workflow.test(operand1=web_page, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("淘宝新滑动验证-禁用", 1, "IF 条件")):
            for _xbot_retry_time in range(4):
                try:
                    web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("淘宝新滑动验证-禁用", 2, "获取已打开的网页对象"))
                    break
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info', text=f'第2条指令: {e}')
                time.sleep(3)
        #endif
        # ---------- 检查页面存在多少个iframe验证容器，只保留最后一个最新的！-------------------------
        验证码_弹窗_元素对象 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@class=\"J_MIDDLEWARE_FRAME_WIDGET\"]", is_related_parent=False, parent="", operation="element", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("淘宝新滑动验证-禁用", 5, "获取相似元素列表(web)"))
        元素个数 = len(验证码_弹窗_元素对象)
        if xbot_visual.workflow.test(operand1=元素个数, operator=">", operand2=lambda: 1, operator_options="{}", _block=("淘宝新滑动验证-禁用", 6, "IF 条件")):
            for idx in xbot_visual.workflow.range_iterator(start="0", stop=lambda: 元素个数 - 2, step=lambda: 1, _block=("淘宝新滑动验证-禁用", 7, "For次数循环")):
                element = 验证码_弹窗_元素对象[idx]
                web_js_result = xbot_visual.web.browser.execute_javascript(browser=web_page, element=element, argument="", code="function (element, input) {\r\n    // 在此处编写您的Javascript代码\r\n    // element表示选择的操作目标(HTML元素)\r\n    // input表示输入的参数(字符串)\r\n    element.remove()\r\n    return null;\r\n}", timeout="20", _block=("淘宝新滑动验证-禁用", 9, "执行JS脚本"))
            #endloop
        #endif
        # ---------- 开始！-------------------------
        xbot_visual.programing.log(type="info", text="warning: 此指令废弃，最大重试次数3.", _block=("淘宝新滑动验证-禁用", 13, "打印日志"))
        最大重试次数 = 3
        for idx in xbot_visual.workflow.range_iterator(start="1", stop=最大重试次数, step="1", _block=("淘宝新滑动验证-禁用", 15, "For次数循环")):
            背景图片_元素对象 = xbot_visual.process.run(process="xbot_extensions.activity_ea8fd401.iframeElement", package=__name__, inputs={
                "web_page": web_page,
                "xpathSelector": "//*[@id=\"scratch-captcha-question-container\"]//img",
                "异常处理": "忽略异常",
                "失败返回值": lambda: None,
                }, outputs=[
                "元素对象",
            ], _block=("淘宝新滑动验证-禁用", 16, "跨全局查找xpath元素"))
            if xbot_visual.workflow.test(operand1=背景图片_元素对象, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("淘宝新滑动验证-禁用", 17, "IF 条件")):
                xbot_visual.programing.log(type="info", text="成功通过，退出！", _block=("淘宝新滑动验证-禁用", 18, "打印日志"))
                break
            #endif
            滑块_元素对象 = xbot_visual.process.run(process="xbot_extensions.activity_ea8fd401.iframeElement", package=__name__, inputs={
                "web_page": web_page,
                "xpathSelector": "//*[@id=\"scratch-captcha-inner-btn\"]",
                "异常处理": "停止运行",
                "失败返回值": lambda: None,
                }, outputs=[
                "元素对象",
            ], _block=("淘宝新滑动验证-禁用", 21, "跨全局查找xpath元素"))
            提示语_元素对象 = xbot_visual.process.run(process="xbot_extensions.activity_ea8fd401.iframeElement", package=__name__, inputs={
                "web_page": web_page,
                "xpathSelector": "//*[@class=\"scratch-captcha-question-header\"]//img",
                "异常处理": "停止运行",
                "失败返回值": lambda: None,
                }, outputs=[
                "元素对象",
            ], _block=("淘宝新滑动验证-禁用", 22, "跨全局查找xpath元素"))
            _ = xbot_visual.process.run(process="process32", package=__name__, inputs={
                "背景图片_元素对象": 背景图片_元素对象,
                "提示词_元素对象": 提示语_元素对象,
                "偏移": lambda: 偏移量,
                "滑块_元素对象": 滑块_元素对象,
                }, outputs=[
            ], _block=("淘宝新滑动验证-禁用", 23, "调用流程"))
            # ---------- ---------------验证失败，继续验证
            xbot_visual.programing.log(type="info", text="第" + xbot_visual.sh_str(idx) + "次失败", _block=("淘宝新滑动验证-禁用", 25, "打印日志"))
        #endloop
    finally:
        pass
