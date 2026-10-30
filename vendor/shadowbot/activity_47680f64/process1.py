import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    文件路径列表 = []
    if args is None:
        压缩文件路径 = ""
        删除原文件 = True
    else:
        压缩文件路径 = args.get("压缩文件路径", "")
        删除原文件 = args.get("删除原文件", True)
    try:
        xbot_visual.programing.log(type="info", text="压缩文件路径：" + xbot_visual.sh_str(压缩文件路径), _block=("解压文件到当前目录", 1, "打印日志"))
        import os
        zipFolder = xbot_visual.xzip.unzip(zip_file_path=压缩文件路径, password=xbot_visual.decrypt(""), unzip_dir_path=lambda: os.path.dirname(压缩文件路径), create_dedicated_folder=True, _block=("解压文件到当前目录", 3, "解压文件/文件夹"))
        file_paths = xbot_visual.dir.find_files(path=zipFolder, patterns="*.*", find_subdir=False, skip_hidden_file=False, is_sort=False, sort_by="name", sort_way="increase", _block=("解压文件到当前目录", 4, "获取文件列表"))
        文件路径列表 = []
        for 文件路径 in xbot_visual.workflow.list_iterator(list=file_paths, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("解压文件到当前目录", 6, "ForEach列表循环")):
            移动到上一级路径 = xbot_visual.process.invoke_module(module="MoveToPardir", package=__name__, function="move_to_pardir", params={
                "file_path": 文件路径,
            }, _block=("解压文件到当前目录", 7, "调用模块"))
            xbot_visual.list.append_or_insert(lst=文件路径列表, insert_way="append", index="0", elem=移动到上一级路径, _block=("解压文件到当前目录", 8, "列表插入一项"))
        #endloop
        if xbot_visual.workflow.test(operand1=删除原文件, operator="is true", operand2="", operator_options="{}", _block=("解压文件到当前目录", 10, "IF 条件")):
            xbot_visual.file.remove(paths=压缩文件路径, _block=("解压文件到当前目录", 11, "删除文件"))
        #endif
        xbot_visual.dir.remove(path=zipFolder, _block=("解压文件到当前目录", 13, "删除文件夹"))
        xbot_visual.programing.log(type="info", text="解压后文件路径列表：" + xbot_visual.sh_str(文件路径列表), _block=("解压文件到当前目录", 14, "打印日志"))
    finally:
        args["文件路径列表"] = 文件路径列表
