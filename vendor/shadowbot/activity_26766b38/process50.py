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
        保存文件夹 = None
        终端选择 = ""
    else:
        保存文件夹 = args.get("保存文件夹", None)
        终端选择 = args.get("终端选择", "")
    try:
        #region 获取网页进行跳转
        _xbot_retry_time = 0
        while _xbot_retry_time <= 3:
            try:
                web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("实时-实时总览数据获取", 2, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("实时-实时总览数据获取", 2,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/ipoll/index.htm", ignore_cache=False, load_timeout="20", _block=("实时-实时总览数据获取", 3, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("实时-实时总览数据获取", 4, "等待"))
        #endregion
        #region 终端选择
        package.variables['通用终端选择'] = xbot_visual.programing.variable(value=终端选择
        , _block=("实时-实时总览数据获取", 7, "设置变量"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("实时-终端显示div"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("实时-实时总览数据获取", 8, "点击元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("实时-实时总览-终端选择动态元素"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("实时-实时总览数据获取", 9, "点击元素(web)"))
        #endregion
        #region 实时数据统计时间确认
        统计时间文本 = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("实时-统计时间文本"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("实时-实时总览数据获取", 12, "获取元素信息(web)"))
        页面统计时间 = xbot_visual.text.extract_content_from_text(text=统计时间文本, extract_way="custom", regular_pattern="统计时间 (.*)", just_get_first=True, ignore_case=False, _block=("实时-实时总览数据获取", 13, "从文本中提取内容"))
        xbot_visual.programing.log(type="info", text="当前实时数据时间: " + xbot_visual.sh_str(页面统计时间), _block=("实时-实时总览数据获取", 14, "打印日志"))
        统计时间提取数字列表 = xbot_visual.text.extract_content_from_text(text=页面统计时间, extract_way="custom", regular_pattern="[0-9]+", just_get_first=False, ignore_case=False, _block=("实时-实时总览数据获取", 15, "从文本中提取内容"))
        命名后缀时间文本 = xbot_visual.text.join_list_to_text(list_to_join=统计时间提取数字列表, delimiter_way="no", standard_delimiter="space", num_standard_delimiter="1", custom_delimiter="", _block=("实时-实时总览数据获取", 16, "列表聚合成文本"))
        #endregion
        #region 数据下载
        实时总览数据列表 = xbot_visual.web.element.data_scraping(browser=web_page, table_element=package.selector("数据列表-实时-实时总览数据"), handle_pager=False, page_element=None, scrape_multi_page=False, max_page="", page_interval="1", simulate_click_page=True, scroll_to_bottom=True, simulate_delay=False, min_time="1", max_time="3", save_to_datasheet=True, _block=("实时-实时总览数据获取", 19, "批量数据抓取"))
        输出文件路径 = xbot_visual.programing.databook.export_data(folder_source="custom", custom_folder_path=保存文件夹, file_name="实时总览数据_" + xbot_visual.sh_str(命名后缀时间文本) + ".xlsx", export_header=False, _block=("实时-实时总览数据获取", 20, "数据表格导出"))
        #endregion
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
