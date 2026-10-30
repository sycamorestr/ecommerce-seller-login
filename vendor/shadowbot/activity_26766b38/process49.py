import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    输出文件路径 = ""
    if args is None:
        保存文件夹 = None
    else:
        保存文件夹 = args.get("保存文件夹", None)
    try:
        #region 获取网页进行跳转
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("直播-本店商品分场次效果明细获取", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("直播-本店商品分场次效果明细获取", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/xsite/contentanalysis/frame/lives/data", ignore_cache=False, load_timeout="20", _block=("直播-本店商品分场次效果明细获取", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("直播-本店商品分场次效果明细获取", 4, "等待"))
        #endregion
        #region 数据下载
        xbot_visual.web.element.click(browser=web_page, element=package.selector("直播-本店商品成交-分场次效果-下载"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("直播-本店商品分场次效果明细获取", 7, "点击元素(web)"))
        输出文件路径 = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=保存文件夹, use_custom_filename=True, file_name="直播本店商品成交分场次效果数据.xlsx", save_behavior="overwrite", wait_complete=True, wait_complete_timeout="30", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("直播-本店商品分场次效果明细获取", 8, "处理下载对话框"))
        #endregion
    finally:
        args["输出文件路径"] = 输出文件路径
