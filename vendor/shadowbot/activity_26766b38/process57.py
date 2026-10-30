import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        save = xbot_visual.programing.variable(value="C:\\Users\\45124\\Desktop\\影刀数仓-租户"
        , _block=("测试-流量来源", 1, "设置变量"))
        # process.run
        process_result = xbot_visual.process.run(process="process56", package=__name__, inputs={
            "查询日期": "2024-12-4",
            "保存文件夹": "C:\\Users\\sjcjj\\Desktop\\env_text",
            "选择新版or旧版": "旧版",
            }, outputs=[
            "文件路径",
            "数据集对象列表",
        ], _block=("测试-流量来源", 3, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result, _block=("测试-流量来源", 4, "打印日志"))
    finally:
        pass
