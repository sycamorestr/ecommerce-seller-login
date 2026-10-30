import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    try:
        # web.get
        # dir.find_files
        # web.element.get_element
        # web.element.click
        # web.element.click
        # process.run
        # programing.log
        process_result2 = xbot_visual.process.run(process="process1", package=__name__, inputs={
            "压缩文件路径": "C:\\Users\\45124\\Downloads\\直通车_报表_店铺基础报表_计划报表_20230630-091420_单元.zip",
            "删除原文件": False,
            }, outputs=[
            "文件路径列表",
        ], _block=("main", 8, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result2, _block=("main", 9, "打印日志"))
    finally:
        pass
