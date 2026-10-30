import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        文件保存路径 = ""
        文件名 = ""
    else:
        文件保存路径 = args.get("文件保存路径", "")
        文件名 = args.get("文件名", "")
    try:
        file_path = xbot_visual.programing.variable(value=xbot_visual.sh_str(文件保存路径) + "\\" + xbot_visual.sh_str(文件名)
        , _block=("D2 等待文件下载完成", 1, "设置变量"))
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop="30", step="1", _block=("D2 等待文件下载完成", 2, "For次数循环")):
            if xbot_visual.file.if_exist(path=file_path, expect_exist="exist", _block=("D2 等待文件下载完成", 3, "IF 文件存在")):
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("D2 等待文件下载完成", 4, "等待"))
                break
            #endif
            xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("D2 等待文件下载完成", 7, "等待"))
            if xbot_visual.workflow.test(operand1=loop_index, operator="==", operand2="30", operator_options="{}", _block=("D2 等待文件下载完成", 8, "IF 条件")):
                raise Exception("文件下载超时！")
            #endif
        #endloop
    finally:
        pass
