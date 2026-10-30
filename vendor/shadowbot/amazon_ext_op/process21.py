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
                web_page = xbot_visual.web.get(web_type="superbrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("TEST B1 付款报告下载", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("TEST B1 付款报告下载", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        process_result = xbot_visual.process.run(process="process3", package=__name__, inputs={
            "网页对象": web_page,
            "站点名称": glv['测试_站点'],
            "报告类型": "汇总",
            "报告标签": "test",
            "日期范围": glv['测试_日期范围'],
            "保存文件夹": "C:\\Users\\58204\\Desktop\\亚马逊",
            "保存文件名": "423.pdf",
            "超时时间": "300",
            "账户类型": "",
            }, outputs=[
            "run_status",
            "err_msg",
            "download_file_path",
        ], _block=("TEST B1 付款报告下载", 2, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result.run_status, _block=("TEST B1 付款报告下载", 3, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.err_msg, _block=("TEST B1 付款报告下载", 4, "打印日志"))
        xbot_visual.programing.log(type="info", text=process_result.download_file_path, _block=("TEST B1 付款报告下载", 5, "打印日志"))
    finally:
        pass
