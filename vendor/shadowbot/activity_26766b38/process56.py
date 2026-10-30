import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    文件路径 = ""
    数据集对象列表 = []
    if args is None:
        查询日期 = ""
        保存文件夹 = None
        选择新版or旧版 = ""
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", None)
        选择新版or旧版 = args.get("选择新版or旧版", "")
    try:
        # ------日期参数校验
        默认下载路径 = xbot_visual.programing.variable(value=保存文件夹
        , _block=("流量_店铺来源_流量来源构成", 2, "设置变量"))
        if xbot_visual.workflow.test(operand1=默认下载路径, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("流量_店铺来源_流量来源构成", 3, "IF 条件")):
            默认下载路径, 是否弹窗下载, 下载路径下已存在文件数 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetDownloadPath", package=__name__, inputs={
                }, outputs=[
                "默认下载路径",
                "是否弹窗下载",
                "下载路径下已存在文件数",
            ], _block=("流量_店铺来源_流量来源构成", 4, "获取当前下载保存路径"))
        #endif
        日期 = xbot_visual.datetime.to_string(datetime=查询日期, format="%Y-%m-%d", _block=("流量_店铺来源_流量来源构成", 6, "日期时间转换为文本"))
        url = xbot_visual.programing.variable(value="https://sycm.taobao.com/flow/monitor/shopsource/construction?belong=all&dateRange=" + xbot_visual.sh_str(日期) + "%7C" + xbot_visual.sh_str(日期) + "&dateType=day&device=2&rivalUser1Id="
        , _block=("流量_店铺来源_流量来源构成", 7, "设置变量"))
        web_page = xbot_visual.web.create(web_type="chrome", value=url, silent_running=False, wait_load_completed=True, load_timeout="120", stop_load_if_load_timeout="handleExcept", chrome_file_name=None, edge_file_name=None, bro360_file_name=None, firefox_file_name=None, arguments=None, _block=("流量_店铺来源_流量来源构成", 8, "打开网页"))
        xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("流量_店铺来源_流量来源构成", 9, "等待"))
        #region 数据下载
        # ------获取页面信息
        流量_店铺来源_下载按钮_旧 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("流量_店铺来源_下载按钮(旧)"), state="appear", iswait=True, timeout="3", _block=("流量_店铺来源_流量来源构成", 12, "等待元素(web)"))
        店铺名 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetShopName", package=__name__, inputs={
            "平台名称": "生意参谋",
            "web_page": web_page,
            }, outputs=[
            "店铺名",
        ], _block=("流量_店铺来源_流量来源构成", 13, "获取店铺名"))
        页面统计时间 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetElementInnerText", package=__name__, inputs={
            "web_page": web_page,
            "xpath": "//*[contains(text(), \"统计时间\")]",
            "等待元素存在": lambda: 20,
            }, outputs=[
            "元素内部文本",
        ], _block=("流量_店铺来源_流量来源构成", 14, "获取元素String"))
        if xbot_visual.workflow.test(operand1=选择新版or旧版, operator="==", operand2="新版", operator_options="{}", _block=("流量_店铺来源_流量来源构成", 15, "IF 条件")):
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("返回旧版"), _block=("流量_店铺来源_流量来源构成", 16, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("前往新版"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_店铺来源_流量来源构成", 17, "点击元素(web)"))
            #endif
            try:
                xbot_visual.web.element.click(browser=web_page, element=package.selector("流量_店铺来源_下载按钮(新)1"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="3", _block=("流量_店铺来源_流量来源构成", 20, "点击元素(web)"))
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                xbot_visual.web.element.click(browser=web_page, element=package.selector("流量_店铺来源_下载（包含下拉框）"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="3", _block=("流量_店铺来源_流量来源构成", 22, "点击元素(web)"))
                xbot_visual.web.element.click(browser=web_page, element=package.selector("流量_店铺来源_下载（包含下拉框）_下载数据表格"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_店铺来源_流量来源构成", 23, "点击元素(web)"))
            #endtry
        else:
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=package.selector("前往新版"), _block=("流量_店铺来源_流量来源构成", 26, "IF 元素可见(web)")):
                xbot_visual.web.element.click(browser=web_page, element=package.selector("返回旧版"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_店铺来源_流量来源构成", 27, "点击元素(web)"))
            #endif
            try:
                xbot_visual.web.element.click(browser=web_page, element=package.selector("店铺来源_流量来源构成_旧版(新)_下载按钮"), simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="3", _block=("流量_店铺来源_流量来源构成", 30, "点击元素(web)"))
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                xbot_visual.web.element.hover(browser=web_page, element=package.selector("流量_店铺来源_下载（包含下拉框）_旧"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("流量_店铺来源_流量来源构成", 32, "鼠标悬停在元素上(web)"))
                xbot_visual.web.element.click(browser=web_page, element=package.selector("流量_店铺来源_下载（包含下拉框）_旧"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="3", _block=("流量_店铺来源_流量来源构成", 33, "点击元素(web)"))
                xbot_visual.web.element.click(browser=web_page, element=package.selector("流量_店铺来源_下载（包含下拉框）_下载数据表格_旧"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="3", _block=("流量_店铺来源_流量来源构成", 34, "点击元素(web)"))
            #endtry
        #endif
        # programing.try
        # web.element.click
        # programing.catch
        # web.element.click
        # programing.endtry
        数据集 = xbot_visual.programing.variable(value="生意参谋_流量_流量来源_流量来源构成"
        , _block=("流量_店铺来源_流量来源构成", 42, "设置变量"))
        文件名 = xbot_visual.programing.variable(value=xbot_visual.sh_str(数据集) + "_" + xbot_visual.sh_str(日期) + ".xls"
        , _block=("流量_店铺来源_流量来源构成", 43, "设置变量"))
        文件路径 = xbot_visual.web.handle_save_dialog(web_type="chrome", dialog_result="OK", file_folder=默认下载路径, use_custom_filename=True, file_name=文件名, save_behavior="overwrite", wait_complete=False, wait_complete_timeout="", simulate=False, clipboard_input=False, input_type="automatic", wait_appear_timeout="20", force_ime_ENG=False, send_key_delay="50", focus_timeout="1000", _block=("流量_店铺来源_流量来源构成", 44, "处理下载对话框"))
        # xbot_extensions.activity_47680f64.下载一个文件
        待插入字段 = xbot_visual.programing.variable(value=lambda: [["RPA店铺名_页面", "RPA日期", "RPA页面统计日期"] , [店铺名, 日期, 页面统计时间]]
        , _block=("流量_店铺来源_流量来源构成", 46, "设置变量"))
        xbot_visual.list.append_or_insert(lst=数据集对象列表, insert_way="append", index="0", elem=lambda: {"数据集": 数据集, "文件路径": 文件路径, "待插入字段": 待插入字段, "去重主键": ["RPA日期", "二级来源", "三级来源", "访客数"]}, _block=("流量_店铺来源_流量来源构成", 47, "列表插入一项"))
        #endregion
        xbot_visual.web.browser.close(operation="close_specified", browser=web_page, web_type="cef", task_kill=False, ignore_beforeunload=False, _block=("流量_店铺来源_流量来源构成", 49, "关闭网页"))
    finally:
        args["文件路径"] = 文件路径
        args["数据集对象列表"] = 数据集对象列表
