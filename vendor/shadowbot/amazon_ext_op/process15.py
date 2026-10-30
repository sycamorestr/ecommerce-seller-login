import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="superbrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("TEST C2 月度仓储费", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("TEST C2 月度仓储费", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        dir_path = xbot_visual.dir.get_special_dir(special_dir_name="DesktopDirectory", _block=("TEST C2 月度仓储费", 2, "获取系统文件夹路径"))
        new_folder = xbot_visual.dir.makedir(parent=xbot_visual.sh_str(dir_path) + "\\亚马逊", name="买家退货", _block=("TEST C2 月度仓储费", 3, "创建文件夹"))
        process_result = xbot_visual.process.run(process="process14", package=__name__, inputs={
            "网页对象": web_page,
            "保存文件夹": "C:\\Users\\58204\\Desktop\\亚马逊",
            "保存文件名": "阅读仓储费test.csv",
            "下载类型": "csv",
            "下载年月": "2025-12",
            "等待时间": "20",
            }, outputs=[
            "run_status",
            "err_msg",
            "download_file_path",
        ], _block=("TEST C2 月度仓储费", 4, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result, _block=("TEST C2 月度仓储费", 5, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.run_status, _block=("TEST C2 月度仓储费", 6, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.err_msg, _block=("TEST C2 月度仓储费", 7, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.download_file_path, _block=("TEST C2 月度仓储费", 8, "打印日志"))
    finally:
        pass
