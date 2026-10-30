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
                web_page = xbot_visual.web.get(web_type="superbrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("TEST C3 增值税交易报告", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("TEST C3 增值税交易报告", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        process_result = xbot_visual.process.run(process="process20", package=__name__, inputs={
            "网页对象": web_page,
            "站点名称": "德国",
            "保存文件夹": "C:\\Users\\58204\\Downloads",
            "保存文件名": "增值税交易报告.xlsx",
            "下载类型": "CSV",
            "日期范围": "2025-11-01_2025-11-02",
            "等待时间": "300",
            }, outputs=[
            "download_file_path",
        ], _block=("TEST C3 增值税交易报告", 2, "调用流程"))
    finally:
        pass
