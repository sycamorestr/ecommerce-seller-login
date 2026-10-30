import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        # process.run
        process_result2 = xbot_visual.process.run(process="process11", package=__name__, inputs={
            "查询日期": "2025-01-20",
            "保存文件夹": "D:\\env_text\\生意参谋",
            "专项分析类型": "",
            "分析内容": "",
            "开启页面统计时间校验": True,
            }, outputs=[
            "输出文件路径",
            "执行状态",
        ], _block=("测试_服务-客服绩效-专项分析数据获取", 2, "调用流程"))
    finally:
        pass
