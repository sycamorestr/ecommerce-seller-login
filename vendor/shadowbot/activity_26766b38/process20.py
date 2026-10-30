import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    输出文件路径 = ""
    if args is None:
        查询日期 = ""
        保存文件夹 = None
        快捷日期 = "日"
    else:
        查询日期 = args.get("查询日期", "")
        保存文件夹 = args.get("保存文件夹", None)
        快捷日期 = args.get("快捷日期", "日")
    try:
        #region 跳转至目标页面
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("交易-交易概况-交易总览数据获取", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("交易-交易概况-交易总览数据获取", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/fa/frame/trade_overview", ignore_cache=False, load_timeout="20", _block=("交易-交易概况-交易总览数据获取", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("交易-交易概况-交易总览数据获取", 4, "等待"))
        #endregion
        # 此处插入时间选择&校验指令
        xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process11", package=__name__, inputs={
            "日期": 查询日期,
            "快捷日期": 快捷日期,
            }, outputs=[
        ], _block=("交易-交易概况-交易总览数据获取", 7, "交易-交易概况时间选择"))
        交易_交易概况_left数据 = xbot_visual.web.element.data_scraping(browser=web_page, table_element=package.selector("数据列表_交易概况_left"), handle_pager=False, page_element=None, scrape_multi_page=False, max_page="0", page_interval="1", simulate_click_page=True, scroll_to_bottom=True, simulate_delay=False, min_time="1", max_time="3", save_to_datasheet=False, _block=("交易-交易概况-交易总览数据获取", 8, "批量数据抓取"))
        交易_交易概况_right数据 = xbot_visual.web.element.data_scraping(browser=web_page, table_element=package.selector("数据列表-交易-交易概况-right"), handle_pager=False, page_element=None, scrape_multi_page=False, max_page="0", page_interval="1", simulate_click_page=True, scroll_to_bottom=True, simulate_delay=False, min_time="1", max_time="3", save_to_datasheet=False, _block=("交易-交易概况-交易总览数据获取", 9, "批量数据抓取"))
        输出数据列表 = xbot_visual.programing.variable(value=lambda: 交易_交易概况_left数据 + 交易_交易概况_right数据
        , _block=("交易-交易概况-交易总览数据获取", 10, "设置变量"))
        # 千位符 & 百分号 处理, 并写入数据表格
        xbot_visual.programing.databook.remove_all_rows(_block=("交易-交易概况-交易总览数据获取", 12, "清空数据表格"))
        for loop_item in xbot_visual.workflow.list_iterator(list=输出数据列表, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("交易-交易概况-交易总览数据获取", 13, "ForEach列表循环")):
            if xbot_visual.workflow.test(operand1=lambda: loop_item[1], operator="in", operand2=",", operator_options="{\"ignoreCase\":\"True\"}", _block=("交易-交易概况-交易总览数据获取", 14, "IF 条件")):
                loop_item[1] = loop_item[1].replace(",","")
            #endif
            if xbot_visual.workflow.test(operand1=lambda: loop_item[1], operator="in", operand2="%", operator_options="{\"ignoreCase\":\"True\"}", _block=("交易-交易概况-交易总览数据获取", 17, "IF 条件")):
                loop_item[1] = str(round(float(loop_item[1].replace("%",""))/100,4))
            #endif
            xbot_visual.programing.databook.write_data_to_workbook(write_range="column", write_way="append", write_column_way="append", row_num="0", column_name=None, begin_row_num="1", begin_column_name="", content=loop_item, _block=("交易-交易概况-交易总览数据获取", 20, "写入内容至数据表格"))
        #endloop
        输出文件路径 = xbot_visual.programing.databook.export_data(folder_source="custom", custom_folder_path=保存文件夹, file_name="交易_交易概况总览数据_.xlsx", export_header=False, _block=("交易-交易概况-交易总览数据获取", 22, "数据表格导出"))
    finally:
        args["输出文件路径"] = 输出文件路径
