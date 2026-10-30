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
                web_page = xbot_visual.web.get(web_type="superbrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("TEST B3 结算一览截图", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("TEST B3 结算一览截图", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        dir_path = xbot_visual.dir.get_special_dir(special_dir_name="DesktopDirectory", _block=("TEST B3 结算一览截图", 2, "获取系统文件夹路径"))
        process_result = xbot_visual.process.run(process="process5", package=__name__, inputs={
            "网页对象": web_page,
            "站点名称": glv['测试_站点'],
            "保存文件夹": "C:\\Users\\58204\\Desktop\\亚马逊",
            "保存文件名": "测试结算一览截图.png",
            "结算周期": "2",
            "账户类型": "标准订单",
            "截图区域": "仅大图",
            }, outputs=[
            "run_status",
            "err_msg",
            "screenshot_file_name",
            "currency_total_amount",
        ], _block=("TEST B3 结算一览截图", 3, "调用流程"))
        xbot_visual.programing.log(type="info", text=process_result, _block=("TEST B3 结算一览截图", 4, "打印日志"))
    finally:
        pass
