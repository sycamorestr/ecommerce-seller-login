import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        转化周期 = ""
        时间选择 = ""
        数据维度 = ""
        文件名称 = ""
        报表类型 = ""
        web_page = None
        数据内容 = ""
        文件存储路径 = ""
        浏览器类型 = ""
    else:
        转化周期 = args.get("转化周期", "")
        时间选择 = args.get("时间选择", "")
        数据维度 = args.get("数据维度", "")
        文件名称 = args.get("文件名称", "")
        报表类型 = args.get("报表类型", "")
        web_page = args.get("web_page", None)
        数据内容 = args.get("数据内容", "")
        文件存储路径 = args.get("文件存储路径", "")
        浏览器类型 = args.get("浏览器类型", "")
    try:
        #region 参数设定
        报表类型_url_dict = xbot_visual.programing.variable(value=lambda: {'账户报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/index','计划报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/campaign/index','单元报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/adgroup/index','关键词报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/keyword/index','人群报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/crowd/index','创意报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/creative/index','权益报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/coupon/index','地域报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/area/index'}
        , _block=("C1 直通车_数据列表获取", 2, "设置变量"))
        if xbot_visual.workflow.test(operand1=lambda: 报表类型_url_dict.keys(), operator="not in", operand2=报表类型, operator_options="{\"ignoreCase\":\"False\"}", _block=("C1 直通车_数据列表获取", 3, "IF 条件")):
            raise Exception("当前版本指令仅支持以下报表类型中的一种报表类型【'账户报表','计划报表','单元报表','关键词报表','人群报表','创意报表','权益报表','地域报表'】")
            return
        #endif
        #endregion
        #region 跳转至目标页面
        if xbot_visual.workflow.test(operand1=lambda: 报表类型_url_dict.keys(), operator="not in", operand2=报表类型, operator_options="{\"ignoreCase\":\"False\"}", _block=("C1 直通车_数据列表获取", 9, "IF 条件")):
            raise Exception("当前版本指令仅支持以下类型的数据报表下载【’账户报表','计划报表','单元报表','关键词报表','人群报表','创意报表','地域报表','权益报表'】")
            return
        #endif
        xbot_visual.programing.log(type="info", text=lambda: 报表类型_url_dict.get(报表类型), _block=("C1 直通车_数据列表获取", 13, "打印日志"))
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url=lambda: 报表类型_url_dict.get(报表类型), ignore_cache=False, load_timeout="20", _block=("C1 直通车_数据列表获取", 14, "跳转至新网址"))
        xbot_visual.web.browser.wait_load_completed(browser=web_page, load_timeout="20", action_after_load_timeout="handleExcept", _block=("C1 直通车_数据列表获取", 15, "等待网页加载完成"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("天猫直通车_报表_店铺基础报表_数据列表_下载按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("C1 直通车_数据列表获取", 16, "点击元素(web)"))
        web_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("天猫直通车_报表_店铺基础报表_数据列表_确认下载按钮"), state="appear", iswait=True, timeout="20", _block=("C1 直通车_数据列表获取", 17, "等待元素(web)"))
        #endregion
        #region 报表名称填写
        current_datetime = xbot_visual.datetime.now(_block=("C1 直通车_数据列表获取", 20, "获取当前日期时间"))
        current_datetime = xbot_visual.datetime.to_string(datetime=current_datetime, format="%Y%m%d", _block=("C1 直通车_数据列表获取", 21, "日期时间转换为文本"))
        默认报表名称 = xbot_visual.programing.variable(value=lambda: current_datetime+报表类型
        , _block=("C1 直通车_数据列表获取", 22, "设置变量"))
        if xbot_visual.workflow.test(operand1=文件名称, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("C1 直通车_数据列表获取", 23, "IF 条件")):
            报表名称 = xbot_visual.programing.variable(value=默认报表名称
            , _block=("C1 直通车_数据列表获取", 24, "设置变量"))
        #endif
        xbot_visual.web.element.input(browser=web_page, element=package.selector("天猫直通车_报表_店铺基础报表_数据列表_报表名称输入框"), text=文件名称, append=False, input_check=False, check_value=None, retry_times="3", simulate=False, driver_input=False, save_to_clipboard=True, input_type="clipboard", contains_hotkey=False, force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", delay_after="1", click_before_input=True, anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("C1 直通车_数据列表获取", 26, "填写输入框(web)"))
        #endregion
        #region 报表时间选择
        if xbot_visual.workflow.multiconditional_judgment(relation="and", conditionals=[{"operand1": 时间选择,"operand2": "","operator": "not empty"},{"operand1": 时间选择,"operand2": "~","operator": "in"}], _block=("C1 直通车_数据列表获取", 29, "IF 多条件")):
            start_time = xbot_visual.programing.variable(value=lambda: 时间选择.split('~')[0]
            , _block=("C1 直通车_数据列表获取", 30, "设置变量"))
            end_time = xbot_visual.programing.variable(value=lambda: 时间选择.split('~')[-1]
            , _block=("C1 直通车_数据列表获取", 31, "设置变量"))
            xbot_visual.process.run(process="xbot_extensions.activity_7daccc.process5", package=__name__, inputs={
                "web_page": web_page,
                "begin_time": start_time,
                "end_time": end_time,
                }, outputs=[
            ], _block=("C1 直通车_数据列表获取", 32, "直通车_报表下载详情_时间选择"))
        else:
            package.variables['select_time'] = xbot_visual.programing.variable(value=时间选择
            , _block=("C1 直通车_数据列表获取", 34, "设置变量"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("天猫直通车_店铺基础报表_数据列表_数据下载_时间选择下拉框"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("C1 直通车_数据列表获取", 35, "点击元素(web)"))
            xbot_visual.web.element.click(browser=web_page, element=package.selector("天猫直通车_报表_店铺基础报表_数据列表_快捷日期选择"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("C1 直通车_数据列表获取", 36, "点击元素(web)"))
        #endif
        #endregion
        #region 数据维度选择
        维度列表 = xbot_visual.programing.variable(value=lambda: ['汇总','分天']
        , _block=("C1 直通车_数据列表获取", 40, "设置变量"))
        if xbot_visual.workflow.test(operand1=维度列表, operator="not in", operand2=数据维度, operator_options="{\"ignoreCase\":\"False\"}", _block=("C1 直通车_数据列表获取", 41, "IF 条件")):
            raise Exception("当前版本指令仅支持汇总和分天两个维度的数据下载")
            return
        #endif
        package.variables['data_dimension'] = xbot_visual.programing.variable(value=数据维度
        , _block=("C1 直通车_数据列表获取", 45, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("天猫直通车_报表_基础报表_数据列表_报表下载_数据维度"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("C1 直通车_数据列表获取", 46, "点击元素(web)"))
        #endregion
        #region 转化周期选择
        转化周期列表 = xbot_visual.programing.variable(value=lambda: ['15天累计','30天累计','1天转化','3天转化','7天转化','15天转化']
        , _block=("C1 直通车_数据列表获取", 49, "设置变量"))
        if xbot_visual.workflow.test(operand1=转化周期列表, operator="not in", operand2=转化周期, operator_options="{\"ignoreCase\":\"False\"}", _block=("C1 直通车_数据列表获取", 50, "IF 条件")):
            raise Exception("当前版本指令仅支持以下转化周期的数据下载【'15天累计','30天累计','1天转化','3天转化','7天转化','15天转化'】")
            return
        #endif
        package.variables['conversion_cycle'] = xbot_visual.programing.variable(value=转化周期
        , _block=("C1 直通车_数据列表获取", 54, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("天猫直通车_报表_基础报表_数据列表_报表下载_转化周期"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("C1 直通车_数据列表获取", 55, "点击元素(web)"))
        #endregion
        #region 数据内容选择
        数据内容列表 = xbot_visual.programing.variable(value=lambda: ['账户','计划','单元','关键词','人群','创意','地域','市级别地域','权益']
        , _block=("C1 直通车_数据列表获取", 58, "设置变量"))
        if xbot_visual.workflow.test(operand1=数据内容列表, operator="not in", operand2=数据内容, operator_options="{\"ignoreCase\":\"False\"}", _block=("C1 直通车_数据列表获取", 59, "IF 条件")):
            raise Exception("当前版本指令仅支持以下数据内容的数据下载【'账户','计划','单元','关键词','人群','创意','地域','市级别地域','权益'】")
            return
        #endif
        package.variables['data_content'] = xbot_visual.programing.variable(value=数据内容
        , _block=("C1 直通车_数据列表获取", 63, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("天猫直通车_报表_基础报表_数据列表_报表下载_数据内容"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("C1 直通车_数据列表获取", 64, "点击元素(web)"))
        #endregion
        #region 报表下载确认
        xbot_visual.web.element.click(browser=web_page, element=package.selector("天猫直通车_报表_店铺基础报表_数据列表_确认下载按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("C1 直通车_数据列表获取", 67, "点击元素(web)"))
        xbot_visual.programing.sleep(random_number=True, seconds="1", start_number="3", stop_number="5", _block=("C1 直通车_数据列表获取", 68, "等待"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("天猫直通车_报表_店铺基础报表_数据列表_确定前往下载按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("C1 直通车_数据列表获取", 69, "点击元素(web)"))
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://subway.simba.taobao.com/index.jsp#!/report/bpreport/download-manage", ignore_cache=False, load_timeout="20", _block=("C1 直通车_数据列表获取", 70, "跳转至新网址"))
        for web_loop_element_index, web_loop_element in enumerate(xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("天猫直通车_报表_店铺基础报表_管理导出报表_报表名称相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("C1 直通车_数据列表获取", 71, "循环相似元素(web)"))):
            web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=web_loop_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("C1 直通车_数据列表获取", 72, "获取元素信息(web)"))
            if xbot_visual.workflow.test(operand1=web_element_attribute, operator="in", operand2=glv['table_name'], operator_options="{\"ignoreCase\":\"False\"}", _block=("C1 直通车_数据列表获取", 73, "IF 条件")):
                package.variables['table_index'] = xbot_visual.programing.variable(value=web_loop_element_index
                , _block=("C1 直通车_数据列表获取", 74, "设置变量"))
                xbot_visual.web.element.click(browser=web_page, element=package.selector("天猫直通车_报表_店铺寄出报表_管理导出报表_下载按钮"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("C1 直通车_数据列表获取", 75, "点击元素(web)"))
                if xbot_visual.workflow.test(operand1=浏览器类型, operator="==", operand2="chrome浏览器", operator_options="{}", _block=("C1 直通车_数据列表获取", 76, "IF 条件")):
                    download_file_name = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=文件存储路径, use_custom_filename=True, file_name=文件名称, save_behavior="overwrite", wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("C1 直通车_数据列表获取", 77, "处理下载对话框"))
                elif xbot_visual.workflow.test(operand1=浏览器类型, operator="==", operand2="edge浏览器", operator_options="{}", _block=("C1 直通车_数据列表获取", 78, "Else IF")):
                    download_file_name = xbot_visual.web.handle_save_dialog(web_type="edge", dialog_result="OK", file_folder=文件存储路径, use_custom_filename=True, file_name=文件名称, save_behavior="overwrite", wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("C1 直通车_数据列表获取", 79, "处理下载对话框"))
                elif xbot_visual.workflow.test(operand1=浏览器类型, operator="==", operand2="影刀浏览器", operator_options="{}", _block=("C1 直通车_数据列表获取", 80, "Else IF")):
                    download_file_name = xbot_visual.web.handle_save_dialog(web_type="cef", dialog_result="OK", file_folder=文件存储路径, use_custom_filename=True, file_name=文件名称, save_behavior="overwrite", wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("C1 直通车_数据列表获取", 81, "处理下载对话框"))
                elif xbot_visual.workflow.test(operand1=浏览器类型, operator="==", operand2="ie浏览器", operator_options="{}", _block=("C1 直通车_数据列表获取", 82, "Else IF")):
                    download_file_name = xbot_visual.web.handle_save_dialog(web_type="ie", dialog_result="OK", file_folder=文件存储路径, use_custom_filename=True, file_name=文件名称, save_behavior="overwrite", wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("C1 直通车_数据列表获取", 83, "处理下载对话框"))
                elif xbot_visual.workflow.test(operand1=浏览器类型, operator="==", operand2="firefox浏览器", operator_options="{}", _block=("C1 直通车_数据列表获取", 84, "Else IF")):
                    download_file_name = xbot_visual.web.handle_save_dialog(web_type="firefox", dialog_result="OK", file_folder=文件存储路径, use_custom_filename=True, file_name=文件名称, save_behavior="overwrite", wait_complete=True, wait_complete_timeout="300", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("C1 直通车_数据列表获取", 85, "处理下载对话框"))
                else:
                    raise Exception("暂不支持您输入的浏览器类型~")
                #endif
            #endif
        #endloop
        #endregion
    finally:
        pass
