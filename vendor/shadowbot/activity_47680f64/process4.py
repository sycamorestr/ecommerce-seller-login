import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    try:
        quick_select_map = {
            1: "昨天",
            7: "过去7天",
            14: "过去14天",
            30: "过去90天",
        }
        process_result = xbot_visual.process.run(process="process3", package=__name__, inputs={
            "日期范围或快捷日期": "2023-01-01~023-01-02",
            "quick_select_map": lambda: quick_select_map,
            }, outputs=[
            "勾选日期",
        ], _block=("测试", 2, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result.勾选日期, _block=("测试", 3, "打印日志"))
    finally:
        pass
