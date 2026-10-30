import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    输出文件路径 = ""
    执行状态 = "成功"
    数据集对象列表 = []
    if args is None:
        保存文件夹 = "C:\\Users\\Administrator\\Desktop"
        查询日期 = "日"
        开启页面统计时间校验 = True
        网页对象 = None
        选择视角 = "整体"
        文件名 = ""
    else:
        保存文件夹 = args.get("保存文件夹", "C:\\Users\\Administrator\\Desktop")
        查询日期 = args.get("查询日期", "日")
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
        网页对象 = args.get("网页对象", None)
        选择视角 = args.get("选择视角", "整体")
        文件名 = args.get("文件名", "")
    try:
        # xbot_extensions.activity_fe2a1069.GetDownloadPath
        # programing.log
        #region 获取网页进行跳转
        if xbot_visual.workflow.test(operand1=网页对象, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("品类-商品排行-全部商品", 4, "IF 条件")):
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    网页对象 = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("品类-商品排行-全部商品", 5, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("品类-商品排行-全部商品", 5,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        #endif
        xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.process2", package=__name__, inputs={
            "web_page": 网页对象,
            "url": "https://sycm.taobao.com/cc/item_rank",
            "跳转最大次数": lambda: 5,
            }, outputs=[
        ], _block=("品类-商品排行-全部商品", 7, "URL检查"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("品类-商品排行-全部商品", 8, "等待"))
        #endregion
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process10", package=__name__, inputs={
            "日期": 查询日期,
            }, outputs=[
            "页面统计时间",
        ], _block=("品类-商品排行-全部商品", 10, "品类/流量/内容-通用时间选择"))
        #region 功能模块 : 开启页面统计时间校验 
        if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("品类-商品排行-全部商品", 12, "IF 条件")):
            _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                "查询日期": 查询日期,
                "页面统计时间": 页面统计时间,
                }, outputs=[
                "判断结果",
            ], _block=("品类-商品排行-全部商品", 13, "调用流程"))
            if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("品类-商品排行-全部商品", 14, "IF 条件")):
                执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                , _block=("品类-商品排行-全部商品", 15, "设置变量"))
                # process.return
                raise Exception(执行状态)
            #endif
        #endif
        #endregion
        xbot_visual.programing.sleep(random_number=False, seconds="5", start_number="1", stop_number="5", _block=("品类-商品排行-全部商品", 21, "等待"))
        if 选择视角:
            text_list = xbot_visual.web.element.get_all_elements(
                browser=网页对象,
                select_type="selector",
                selector=package.selector("选择视角_相似元素组"),
                operation="text",
                is_related_parent=False,
                timeout="20"
            )
            match_index = None
            for i, text in enumerate(text_list):
                if 选择视角 in text:
                    match_index = i
                    break
            if match_index is not None:
                element_list = xbot_visual.web.element.get_all_elements(
                    browser=网页对象,
                    select_type="selector",
                    selector=package.selector("选择视角_相似元素组"),
                    operation="element",
                    is_related_parent=False,
                    timeout="20"
                )
                xbot_visual.web.element.click(
                    browser=网页对象,
                    element=element_list[match_index],
                    simulate=True,
                    move_mouse=False,
                    clicks="click",
                    button="left",
                    keys="null",
                    delay_after="1",
                    anchor_type="center",
                    sudoku_part="MiddleCenter",
                    offset_x="0",
                    offset_y="0",
                    timeout="20"
                )
        try:
            xbot_visual.web.browser.navigate(browser=网页对象, mode="reload", url="", ignore_cache=False, load_timeout="60", _block=("品类-商品排行-全部商品", 23, "跳转至新网址"))
        except Exception as e:
            pass
        #region 数据下载
        # web.element.click
        数据集 = xbot_visual.programing.variable(value="生意参谋_品类_商品排行_全部商品"
        , _block=("品类-商品排行-全部商品", 26, "设置变量"))
        current_date = xbot_visual.datetime.to_string(datetime=None, format="%Y_%m_%d_%H_%M_%S", _block=("品类-商品排行-全部商品", 27, "日期时间转换为文本"))
        if xbot_visual.workflow.test(operand1=文件名, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("品类-商品排行-全部商品", 28, "IF 条件")):
            文件名 = xbot_visual.programing.variable(value=xbot_visual.sh_str(数据集) + "_" + xbot_visual.sh_str(页面统计时间) + "_" + xbot_visual.sh_str(current_date) + ".xlsx"
            , _block=("品类-商品排行-全部商品", 29, "设置变量"))
        #endif
        店铺名 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetShopName", package=__name__, inputs={
            "平台名称": "生意参谋",
            "web_page": 网页对象,
            }, outputs=[
            "店铺名",
        ], _block=("品类-商品排行-全部商品", 31, "获取店铺名"))
        xbot_visual.web.element.hover(browser=网页对象, element=package.selector("下载"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-商品排行-全部商品", 32, "鼠标悬停在元素上(web)"))
        xbot_visual.web.element.click(browser=网页对象, element=package.selector("下载"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("品类-商品排行-全部商品", 33, "点击元素(web)"))
        输出文件路径 = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=保存文件夹, use_custom_filename=True, file_name=文件名, save_behavior="overwrite", wait_complete=False, wait_complete_timeout="", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("品类-商品排行-全部商品", 34, "处理下载对话框"))
        for loop_index in xbot_visual.workflow.range_iterator(start="1", stop="3", step="1", _block=("品类-商品排行-全部商品", 35, "For次数循环")):
            if xbot_visual.file.if_exist(path=输出文件路径, expect_exist="exist", _block=("品类-商品排行-全部商品", 36, "IF 文件存在")):
                break
            #endif
            xbot_visual.programing.sleep(random_number=False, seconds="5", start_number="1", stop_number="5", _block=("品类-商品排行-全部商品", 39, "等待"))
        #endloop
        # -----输出
        xbot_visual.programing.log(type="info", text="文件输出路径: " + xbot_visual.sh_str(输出文件路径), _block=("品类-商品排行-全部商品", 42, "打印日志"))
        待插入字段 = xbot_visual.programing.variable(value=lambda: [["RPA店铺名_页面", "RPA统计日期"], [店铺名, 页面统计时间]]
        , _block=("品类-商品排行-全部商品", 43, "设置变量"))
        xbot_visual.list.append_or_insert(lst=数据集对象列表, insert_way="append", index="0", elem=lambda: {"数据集": 数据集, "文件路径": 输出文件路径, "待插入字段": 待插入字段, "去重主键": ["统计日期", "商品ID"]}, _block=("品类-商品排行-全部商品", 44, "列表插入一项"))
        #endregion
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
        args["数据集对象列表"] = 数据集对象列表
