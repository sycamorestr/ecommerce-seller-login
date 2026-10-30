import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    输出文件路径 = ""
    执行状态 = "成功"
    if args is None:
        查询日期 = ""
        类目选择 = "导购类目"
        保存文件夹 = ""
        开启页面统计时间校验 = True
        网页对象 = None
    else:
        查询日期 = args.get("查询日期", "")
        类目选择 = args.get("类目选择", "导购类目")
        保存文件夹 = args.get("保存文件夹", "")
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
        网页对象 = args.get("网页对象", None)
    try:
        #region 获取网页进行跳转
        web_page = xbot_visual.programing.variable(value=lambda: 网页对象
        , _block=("品类-品类360排行数据获取", 2, "设置变量"))
        if xbot_visual.workflow.test(operand1=网页对象, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("品类-品类360排行数据获取", 3, "IF 条件")):
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("品类-品类360排行数据获取", 4, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("品类-品类360排行数据获取", 4,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        #endif
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/cc/new_cate_archives", ignore_cache=False, load_timeout="20", _block=("品类-品类360排行数据获取", 6, "跳转至新网址"))
        _ = xbot_visual.web.element.wait(browser=web_page, element=package.selector("品类-品类360-品类排行-标准类目标签"), state="appear", iswait=True, timeout="20", _block=("品类-品类360排行数据获取", 7, "等待元素(web)"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("品类-品类360排行数据获取", 8, "等待"))
        #endregion
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("搜索弹窗_close"), _block=("品类-品类360排行数据获取", 10, "IF 元素可见(web)")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("搜索弹窗_close"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-品类360排行数据获取", 11, "点击元素(web)"))
        #endif
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
            "页面统计时间",
        ], _block=("品类-品类360排行数据获取", 13, "品类/流量/内容-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("品类-品类360排行数据获取", 15, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("品类-品类360排行数据获取", 16, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("品类-品类360排行数据获取", 17, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("品类-品类360排行数据获取", 18, "设置变量"))
                return
            #endif
        #endif
        #endregion
        #region 类目选择
        if xbot_visual.workflow.test(operand1=类目选择, operator="==", operand2="标准类目", operator_options="{}", _block=("品类-品类360排行数据获取", 24, "IF 条件")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("品类-品类360-品类排行-标准类目标签"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-品类360排行数据获取", 25, "点击元素(web)"))
        elif xbot_visual.workflow.test(operand1=类目选择, operator="==", operand2="导购类目", operator_options="{}", _block=("品类-品类360排行数据获取", 26, "Else IF")):
            xbot_visual.web.element.click(browser=web_page, element=package.selector("品类-品类360-品类排行-导购类目标签"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="2", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-品类360排行数据获取", 27, "点击元素(web)"))
        #endif
        #endregion
        #region 文件下载
        下载按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"oui-card-header\")]//a", is_related_parent=False, parent=None, timeout="20", _block=("品类-品类360排行数据获取", 31, "获取元素对象(web)"))
        xbot_visual.web.element.click(browser=web_page, element=下载按钮, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-品类360排行数据获取", 32, "点击元素(web)"))
        输出文件路径 = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=保存文件夹, use_custom_filename=True, file_name="品类排行_" + xbot_visual.sh_str(类目选择) + "_" + xbot_visual.sh_str(页面统计时间) + ".xls", save_behavior="overwrite", wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("品类-品类360排行数据获取", 33, "处理下载对话框"))
        xbot_visual.programing.log(type="info", text="文件输出路径: " + xbot_visual.sh_str(输出文件路径), _block=("品类-品类360排行数据获取", 34, "打印日志"))
        #endregion
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
