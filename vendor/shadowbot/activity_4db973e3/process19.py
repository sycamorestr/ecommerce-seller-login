import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    if args is None:
        图块所在背景 = None
        目标图块 = None
        拖拽元素 = None
        网页对象 = None
        缺口or单缺口 = ""
        图鉴帐号 = ""
        图鉴密码 = ""
        重试次数 = 5
        偏移距离 = 0
        识别引擎 = ""
        移动速度 = ""
    else:
        图块所在背景 = args.get("图块所在背景", None)
        目标图块 = args.get("目标图块", None)
        拖拽元素 = args.get("拖拽元素", None)
        网页对象 = args.get("网页对象", None)
        缺口or单缺口 = args.get("缺口or单缺口", "")
        图鉴帐号 = args.get("图鉴帐号", "")
        图鉴密码 = args.get("图鉴密码", "")
        重试次数 = args.get("重试次数", 5)
        偏移距离 = args.get("偏移距离", 0)
        识别引擎 = args.get("识别引擎", "")
        移动速度 = args.get("移动速度", "")
    try:
        try:
            xbot_visual.web.browser.wait_load_completed(browser=网页对象, load_timeout="20", action_after_load_timeout="stopLoad", _block=("滑动拼图验证（去除界面 bug）", 1, "等待网页加载完成"))
        except Exception as e:
            xbot_visual.programing.log(type='info', text=xbot_visual.trace(e))
        assert str(重试次数).isdigit(), "【重试次数】类型为非负整数，请填写正确的参数类型！"
        assert int(重试次数)>=0, "【重试次数】类型为非负整数，请填写正确的参数类型！"
        for loop_index in xbot_visual.workflow.range_iterator(start="0", stop=重试次数, step="1", _block=("滑动拼图验证（去除界面 bug）", 3, "For次数循环")):
            if xbot_visual.web.browser.element_display(browser=网页对象, content_type="display", selector=图块所在背景, _block=("滑动拼图验证（去除界面 bug）", 4, "IF 元素可见(web)")):
                process_result = xbot_visual.process.run(process="process2", package=__name__, inputs={
                    "start_element": lambda: 目标图块,
                    "background_element": lambda: 图块所在背景,
                    "tj_username": 图鉴帐号,
                    "tj_password": 图鉴密码,
                    "web_page": lambda: 网页对象,
                    "缺口类型": lambda: 缺口or单缺口,
                    "ai_engine": 识别引擎,
                    }, outputs=[
                    "distince",
                ], _block=("滑动拼图验证（去除界面 bug）", 5, "调用流程"))
                # 拖动滑块
                # web.element.get_element
                bound = xbot_visual.web.element.get_bounding(browser=网页对象, element=拖拽元素, to96dpi=True, relative_to="screen", timeout="20", _block=("滑动拼图验证（去除界面 bug）", 8, "获取元素位置(web)"))
                invoke_result = xbot_visual.process.invoke_module(module="utils", package=__name__, function="drag", params={
                    "point_x": bound.center_x,
                    "point_y": bound.center_y,
                    "distance": lambda: int(process_result.distince) + 偏移距离,
                    "move_speed": 移动速度,
                }, _block=("滑动拼图验证（去除界面 bug）", 9, "调用模块"))
                # process.run
            else:
                break
            #endif
            xbot_visual.programing.sleep(random_number=True, seconds="1", start_number="2", stop_number="3", _block=("滑动拼图验证（去除界面 bug）", 14, "等待"))
        #endloop
    finally:
        pass
