import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # process.run
        process_result4 = xbot_visual.process.run(process="process38", package=__name__, inputs={
            "查询日期": "2025-01-03",
            "保存文件夹": "C:\\Users\\charleskeith\\Downloads\\demo",
            "开启页面统计时间校验": True,
            }, outputs=[
            "流量来源排行TOP10_数据列表",
            "输出文件路径",
            "执行状态",
        ], _block=("测试_新版流量看板", 2, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result4.流量来源排行TOP10_数据列表, _block=("测试_新版流量看板", 3, "打印日志"))
        # web.get
        # datetime.to_string
        # process.run
        # process.run
        # process.run
    finally:
        pass
