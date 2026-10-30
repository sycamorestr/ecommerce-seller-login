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
                web_page = xbot_visual.web.get(web_type="ziniaobrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("TEST 库存报告", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("TEST 库存报告", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        dir_path = xbot_visual.dir.get_special_dir(special_dir_name="DesktopDirectory", _block=("TEST 库存报告", 2, "获取系统文件夹路径"))
        new_folder = xbot_visual.dir.makedir(parent=xbot_visual.sh_str(dir_path) + "\\亚马逊", name="买家退货", _block=("TEST 库存报告", 3, "创建文件夹"))
        process_result = xbot_visual.process.run(process="process27", package=__name__, inputs={
            "网页对象": web_page,
            "站点名称": glv['测试_站点'],
            "报告类型": "InactiveListingsReport",
            "保存文件夹": dir_path,
            "保存文件名": "",
            }, outputs=[
            "run_status",
            "err_msg",
            "download_file_path",
        ], _block=("TEST 库存报告", 4, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result, _block=("TEST 库存报告", 5, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.run_status, _block=("TEST 库存报告", 6, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.err_msg, _block=("TEST 库存报告", 7, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.download_file_path, _block=("TEST 库存报告", 8, "打印日志"))
    finally:
        pass
