import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    输出文件路径 = ""
    if args is None:
        查询日期 = "2024-01-01"
        保存文件夹 = ""
        终端选择 = "PC"
    else:
        查询日期 = args.get("查询日期", "2024-01-01")
        保存文件夹 = args.get("保存文件夹", "")
        终端选择 = args.get("终端选择", "PC")
    try:
        xbot_visual.process.run(process="xbot_extensions.popup_detector.process1", package=__name__, inputs={
            }, outputs=[
        ], _block=("交易-交易构成-类目构成数据获取", 1, "智能屏蔽弹窗(web)"))
        #region 跳转至目标页面
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("交易-交易构成-类目构成数据获取", 3, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("交易-交易构成-类目构成数据获取", 3,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/fa/frame/trade_constitute", ignore_cache=False, load_timeout="20", _block=("交易-交易构成-类目构成数据获取", 4, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("交易-交易构成-类目构成数据获取", 5, "等待"))
        #endregion
        # 此处插入时间选择&校验指令
        # 此处插入时间选择&校验指令
        xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process12", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
        ], _block=("交易-交易构成-类目构成数据获取", 9, "交易-交易构成时间选择"))
        #region 终端选择
        交易_交易构成_类目构成父元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("交易-交易构成-类目构成navbar"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("交易-交易构成-类目构成数据获取", 11, "获取元素对象(web)"))
        package.variables['交易_交易构成_终端选择'] = xbot_visual.programing.variable(value=终端选择
        , _block=("交易-交易构成-类目构成数据获取", 12, "设置变量"))
        交易_交易构成_类目构成终端选择 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("交易-交易构成-通用终端选择"), css_selector="", xpath_selector="", is_related_parent=True, parent=交易_交易构成_类目构成父元素, timeout="20", _block=("交易-交易构成-类目构成数据获取", 13, "获取元素对象(web)"))
        xbot_visual.web.element.click(browser=web_page, element=交易_交易构成_类目构成终端选择, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="2", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("交易-交易构成-类目构成数据获取", 14, "点击元素(web)"))
        #endregion
        #region 下载
        交易_交易构成_类目构成下载按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("交易-通用下载按钮"), css_selector="", xpath_selector="", is_related_parent=True, parent=交易_交易构成_类目构成父元素, timeout="20", _block=("交易-交易构成-类目构成数据获取", 17, "获取元素对象(web)"))
        xbot_visual.web.element.click(browser=web_page, element=交易_交易构成_类目构成下载按钮, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("交易-交易构成-类目构成数据获取", 18, "点击元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("交易-交易构成-下载通用二次确定"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("交易-交易构成-类目构成数据获取", 19, "点击元素(web)"))
        输出文件路径 = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=保存文件夹, use_custom_filename=True, file_name="交易类目构成数据_" + xbot_visual.sh_str(查询日期) + ".xls", save_behavior="overwrite", wait_complete=False, wait_complete_timeout="", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("交易-交易构成-类目构成数据获取", 20, "处理下载对话框"))
        #endregion
    finally:
        args["输出文件路径"] = 输出文件路径
