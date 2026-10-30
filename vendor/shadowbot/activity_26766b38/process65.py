import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # xbot_extensions.popup_detector.A1 智能屏蔽弹窗(web)
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("测试_jc", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("测试_jc", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        # process.run
        # web.browser.navigate
        # process.run
        process_result25 = xbot_visual.process.run(process="process3", package=__name__, inputs={
            "保存文件夹": "D:\\env_text\\生意参谋",
            "查询日期": "2026-02-20",
            "开启页面统计时间校验": True,
            "网页对象": lambda: web_page,
            "选择视角": "整体视角",
            "文件名": "全部商品",
            }, outputs=[
            "输出文件路径",
            "执行状态",
            "数据集对象列表",
        ], _block=("测试_jc", 6, "调用流程"))
        process_result25 = xbot_visual.process.run(process="process3", package=__name__, inputs={
            "保存文件夹": "D:\\env_text\\生意参谋",
            "查询日期": "2026-02-10",
            "开启页面统计时间校验": True,
            "网页对象": lambda: web_page,
            "选择视角": "整体视角",
            "文件名": "全部商品",
            }, outputs=[
            "输出文件路径",
            "执行状态",
            "数据集对象列表",
        ], _block=("测试_jc", 7, "调用流程"))
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # process.run
        # programing.log
        # web.element.click
        # process.run
        # process.run
        # process.run
        # programing.log
        # win32.window.get_window
        # win32.element.click
        # win32.element.input
        # process.run
        # process.run
        # process.run
        # process.run
        # programing.log
        # web.get
        # web.element.get_all_elements
        # programing.log
        # process.run
        # process.run
        # process.run
        # process.run
    finally:
        pass
