import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        web_page = None
        time_out = "20"
    else:
        web_page = args.get("web_page", None)
        time_out = args.get("time_out", "20")
    try:
        #region 前置流程变量
        time_out = xbot_visual.programing.variable(value=lambda: int(time_out)
        , _block=("退出已登录", 2, "设置变量"))
        while_value = xbot_visual.programing.variable(value="True"
        , _block=("退出已登录", 3, "设置变量"))
        #endregion
        while xbot_visual.workflow.test(operand1=while_value, operator="==", operand2="True", operator_options="{}", _block=("退出已登录", 5, "While条件循环")):
            # workflow.for
            # programing.sleep
            # web.element.wait
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("抖店_当前店铺名称"), _block=("退出已登录", 9, "IF 元素可见(web)")):
                while_value = xbot_visual.programing.variable(value="False"
                , _block=("退出已登录", 10, "设置变量"))
                break
                # process.return
            #endif
            xbot_visual.web.element.hover(browser=web_page, element=package.selector("抖店_当前店铺名称"), simulate=False, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("退出已登录", 14, "鼠标悬停在元素上(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_当前店铺名称"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("退出已登录", 15, "点击元素(web)"))
            # web.element.get_element
            # programing.log
            # programing.sleep
            # programing.log
            # xbot_extensions.activity_fe2a1069.ClickByXpath
            xbot_visual.web.element.click(browser=web_page, element=package.selector("退出_1"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="4", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("退出已登录", 21, "点击元素(web)"))
            # programing.sleep
            # workflow.endloop
        #endloop
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://fxg.jinritemai.com/login/common", ignore_cache=False, load_timeout=time_out, _block=("退出已登录", 25, "跳转至新网址"))
        # programing.raise
    finally:
        pass
