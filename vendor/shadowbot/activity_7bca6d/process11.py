import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        web_page = None
        drag_start_element = None
        background_element = None
    else:
        web_page = args.get("web_page", None)
        drag_start_element = args.get("drag_start_element", None)
        background_element = args.get("background_element", None)
    try:
        # web.get
        web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=background_element, css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("滑块拖动", 2, "获取元素对象(web)"))
        bound = xbot_visual.web.element.get_bounding(browser=web_page, element=web_element, to96dpi=True, relative_to="screen", timeout="20", _block=("滑块拖动", 3, "获取元素位置(web)"))
        # process.run
        _ = xbot_visual.process.run(process="drag_captcha", package=__name__, inputs={
            "web_page": web_page,
            "distance": bound.width,
            "drag_ele": drag_start_element,
            }, outputs=[
        ], _block=("滑块拖动", 5, "调用流程"))
    finally:
        pass
