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
        xbot_visual.programing.log(type="info", text="-----滑块验证-----", _block=("_抖音平台登录-滑块验证", 2, "打印日志"))
        web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("抖店拖动滑块_按钮"), state="appear", iswait=True, timeout="3", _block=("_抖音平台登录-滑块验证", 3, "等待元素(web)"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("抖店_背景_ifream"), _block=("_抖音平台登录-滑块验证", 4, "IF 元素可见(web)")):
            xbot_visual.process.run(process="xbot_extensions.activity_jfbym.dy_slider_captcha", package=__name__, inputs={
                "web_page": web_page,
                "engine": "xbot",
                "background_ele": package.selector("抖店_背景_ifream"),
                "slider_ele": package.selector("抖店_目标滑块_ifream"),
                "refresh_ele": package.selector("抖店_验证码刷新元素"),
                "offset": lambda: 0,
                "token": "",
                "retry_count": lambda: 5,
                }, outputs=[
            ], _block=("_抖音平台登录-滑块验证", 5, "抖音滑块验证"))
        else:
            xbot_visual.process.run(process="xbot_extensions.activity_jfbym.dy_slider_captcha", package=__name__, inputs={
                "web_page": web_page,
                "engine": "",
                "background_ele": package.selector("抖店背景_图像"),
                "slider_ele": package.selector("抖店拖动滑块_按钮"),
                "refresh_ele": lambda: None,
                "offset": lambda: 0,
                "token": "",
                "retry_count": lambda: 5,
                }, outputs=[
            ], _block=("_抖音平台登录-滑块验证", 7, "抖音滑块验证"))
        #endif
    finally:
        pass
