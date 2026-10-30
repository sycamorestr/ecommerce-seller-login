import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    表格地址列表 = []
    if args is None:
        网页对象 = None
        开始时间 = "2023-01-01"
        结束时间 = "2023-01-05"
        账户类型 = "全部"
        存放文件夹路径 = r"C:\Users\SHADOWBOT\Desktop\新建文件夹"
    else:
        网页对象 = args.get("网页对象", None)
        开始时间 = args.get("开始时间", "2023-01-01")
        结束时间 = args.get("结束时间", "2023-01-05")
        账户类型 = args.get("账户类型", "全部")
        存放文件夹路径 = args.get("存放文件夹路径", r"C:\Users\SHADOWBOT\Desktop\新建文件夹")
    try:
        # 1.基础变量校验
        web_page = xbot_visual.programing.variable(value=lambda: 网页对象
        , _block=("抖店资金日账单下载", 2, "设置变量"))
        if xbot_visual.dir.if_exist(path=存放文件夹路径, expect_exist="no_exist", _block=("抖店资金日账单下载", 3, "IF 文件夹存在")):
            raise Exception("该文件夹不存在，" + xbot_visual.sh_str(存放文件夹路径))
        #endif
        # 2.时间周期划分
        当前循环日期时间_str = xbot_visual.programing.variable(value=""
        , _block=("抖店资金日账单下载", 7, "设置变量"))
        开始时间_datetime_instance = xbot_visual.datetime.from_string(text=开始时间, is_custom_format=False, format=None, _block=("抖店资金日账单下载", 8, "转换到日期时间"))
        结束时间_datetime_instance = xbot_visual.datetime.from_string(text=结束时间, is_custom_format=False, format=None, _block=("抖店资金日账单下载", 9, "转换到日期时间"))
        loop_index = -1
        while True:
            loop_index += 1
            datetime_instance, _ = xbot_visual.datetime.add(datetime=开始时间_datetime_instance, timeway="increase", duration=loop_index, unit="day", output_text=False, _block=("抖店资金日账单下载", 11, "增加/减少时间"))
            if xbot_visual.workflow.test(operand1=datetime_instance, operator=">=", operand2=结束时间_datetime_instance, operator_options="{}", _block=("抖店资金日账单下载", 12, "IF 条件")):
                break
            #endif
            当前循环日期时间_str = xbot_visual.datetime.to_string(datetime=datetime_instance, format="%Y-%m-%d", _block=("抖店资金日账单下载", 15, "日期时间转换为文本"))
            # 3.网页判断
            # web.get
            #region 网页跳转
            web_page_attribute = xbot_visual.web.browser.get_details(browser=网页对象, operation="url", _block=("抖店资金日账单下载", 19, "获取网页信息"))
            if xbot_visual.workflow.test(operand1=web_page_attribute, operator="not in", operand2="https://fxg.jinritemai.com/ffa/p/v2onlineBill?", operator_options="{\"ignoreCase\":\"False\"}", _block=("抖店资金日账单下载", 20, "IF 条件")):
                xbot_visual.web.browser.navigate(browser=网页对象, mode="url", url="https://fxg.jinritemai.com/ffa/p/v2onlineBill?", ignore_cache=False, load_timeout="20", _block=("抖店资金日账单下载", 21, "跳转至新网址"))
            #endif
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("抖店资金账单下载_日账单_按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店资金日账单下载", 23, "点击元素(web)"))
            #endregion
            # 4.时间填写
            #region 时间填写
            for loop_index2 in xbot_visual.workflow.range_iterator(start="1", stop="3", step="1", _block=("抖店资金日账单下载", 27, "For次数循环")):
                xbot_visual.web.element.input(browser=网页对象, element=package.selector("抖店资金账单下载_开始日期_输入框"), text=当前循环日期时间_str, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店资金日账单下载", 28, "填写输入框(web)"))
                xbot_visual.web.element.input(browser=网页对象, element=package.selector("抖店资金账单下载_结束日期_输入框"), text=当前循环日期时间_str, append=False, input_check=False, check_value=None, retry_times="3", simulate=True, driver_input=False, save_to_clipboard=False, input_type="simulate", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店资金日账单下载", 29, "填写输入框(web)"))
                开始日期_element_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("抖店资金账单下载_开始日期_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店资金日账单下载", 30, "获取元素信息(web)"))
                结束日期_element_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=package.selector("抖店资金账单下载_结束日期_输入框"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店资金日账单下载", 31, "获取元素信息(web)"))
                if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 开始日期_element_attribute,"operand2": 当前循环日期时间_str,"operator": "=="},{"operand1": 结束日期_element_attribute,"operand2": 当前循环日期时间_str,"operator": "=="}], _block=("抖店资金日账单下载", 32, "IF 多条件")):
                    break
                #endif
            #endloop
            #endregion
            # 5.账户类型选择
            #region 账户类别选择
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("抖店资金账单下载_账号类型_下拉框点击"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店资金日账单下载", 39, "点击元素(web)"))
            if xbot_visual.web.browser.element_display(browser=网页对象, content_type="undisplay", selector=package.selector("抖店资金账单下载_账户类型_类别相似元素组"), _block=("抖店资金日账单下载", 40, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("抖店资金账单下载_账号类型_下拉框点击"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店资金日账单下载", 41, "点击元素(web)"))
            #endif
            for 账户类型_类别_element in xbot_visual.web.element.iter_all_elements(browser=网页对象, selector=package.selector("抖店资金账单下载_账户类型_类别相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抖店资金日账单下载", 43, "循环相似元素(web)")):
                账户类型_类别_attribute = xbot_visual.web.element.get_details(browser=网页对象, element=账户类型_类别_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店资金日账单下载", 44, "获取元素信息(web)"))
                if xbot_visual.workflow.test(operand1=账户类型_类别_attribute, operator="==", operand2=账户类型, operator_options="{}", _block=("抖店资金日账单下载", 45, "IF 条件")):
                    xbot_visual.web.element.click(browser=网页对象, element=账户类型_类别_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店资金日账单下载", 46, "点击元素(web)"))
                    break
                #endif
            #endloop
            #endregion
            # 6.下载报表
            if xbot_visual.web.browser.contains_element_or_text(browser=网页对象, content_type="contains_element", selector=package.selector("抖店资金账单下载_暂无数据"), text="", _block=("抖店资金日账单下载", 52, "IF 网页包含")):
                xbot_visual.programing.log(type="info", text="类别：" + xbot_visual.sh_str(账户类型) + "   时间：" + xbot_visual.sh_str(当前循环日期时间_str) + " ----无数据", _block=("抖店资金日账单下载", 53, "打印日志"))
                xbot_visual.list.append_or_insert(lst=表格地址列表, insert_way="append", index="0", elem=lambda: None, _block=("抖店资金日账单下载", 54, "列表插入一项"))
                continue
            #endif
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("抖店资金账单下载_生成报表_第一个"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店资金日账单下载", 57, "点击元素(web)"))
            if xbot_visual.web.browser.contains_element_or_text(browser=网页对象, content_type="not_contains_element", selector=package.selector("抖店资金账单下载_生成_显示元素"), text="", _block=("抖店资金日账单下载", 58, "IF 网页包含")):
                xbot_visual.web.element.click(browser=网页对象, element=package.selector("抖店资金账单下载_生成报表_第一个"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店资金日账单下载", 59, "点击元素(web)"))
            #endif
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("抖店资金账单下载_生成_显示元素"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店资金日账单下载", 61, "点击元素(web)"))
            # web.get
            xbot_visual.web.element.click(browser=网页对象, element=package.selector("抖店资金账单下载_下载按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店资金日账单下载", 63, "点击元素(web)"))
            download_file_name = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=存放文件夹路径, use_custom_filename=False, file_name=None, save_behavior="overwrite", wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("抖店资金日账单下载", 64, "处理下载对话框"))
            xbot_visual.list.append_or_insert(lst=表格地址列表, insert_way="append", index="0", elem=download_file_name, _block=("抖店资金日账单下载", 65, "列表插入一项"))
            xbot_visual.programing.log(type="info", text="类别：" + xbot_visual.sh_str(账户类型) + "   时间：" + xbot_visual.sh_str(当前循环日期时间_str) + " ----下载完成", _block=("抖店资金日账单下载", 66, "打印日志"))
            datetime_instance, _ = xbot_visual.datetime.add(datetime=开始时间_datetime_instance, timeway="increase", duration=lambda: loop_index+1, unit="day", output_text=False, _block=("抖店资金日账单下载", 67, "增加/减少时间"))
            if xbot_visual.workflow.test(operand1=datetime_instance, operator="<", operand2=结束时间_datetime_instance, operator_options="{}", _block=("抖店资金日账单下载", 68, "IF 条件")):
                xbot_visual.programing.sleep(random_number=False, seconds="60", start_number="1", stop_number="5", _block=("抖店资金日账单下载", 69, "等待"))
            #endif
        #endloop
    finally:
        args["表格地址列表"] = 表格地址列表
