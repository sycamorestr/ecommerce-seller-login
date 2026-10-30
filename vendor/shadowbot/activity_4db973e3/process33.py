import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    try:
        for _xbot_retry_time in range(4):
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试-淘宝物体识别", 1, "获取已打开的网页对象"))
                break
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info', text=xbot_visual.trace(e))
            time.sleep(3)
        # web.element.get_element
        # web.element.get_element
        # web.element.get_element
        # web.element.get_element
        invoke_result = xbot_visual.process.invoke_module(module="taobo_object_reg", package=__name__, function="handle_verification", params={
            "web_page": web_page,
            "token": "",
            "background_ele": "tb_background_ele",
            "tip_ele": "tip_ele",
            "drag_ele": "tb_drag_ele",
            "slider_ele": "slider_ele",
            "retry_count": lambda: 5,
            "offset": lambda: 0,
        }, _block=("测试-淘宝物体识别", 6, "调用模块"))
    finally:
        pass
