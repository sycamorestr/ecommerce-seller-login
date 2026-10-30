import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        web_page = None
    else:
        web_page = args.get("web_page", None)
    try:
        # web.get
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("生意参谋_客服弹窗_窗体"), _block=("关闭右侧客服弹窗", 2, "IF 元素可见(web)")):
            xbot_visual.programing.log(type="info", text="检测到 客服弹窗 窗体", _block=("关闭右侧客服弹窗", 3, "打印日志"))
            xbot_visual.web.element.set_attribute(browser=web_page, element=package.selector("生意参谋_客服弹窗_窗体"), attribute_name="style", value="dispaly:None", timeout="20", _block=("关闭右侧客服弹窗", 4, "设置元素属性(web)"))
        #endif
        # web.browser.element_display
        # programing.log
        # web.element.set_attribute
        # workflow.endif
    finally:
        pass
