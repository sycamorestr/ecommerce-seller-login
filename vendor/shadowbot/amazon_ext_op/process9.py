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
                web_page = xbot_visual.web.get(web_type="superbrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("抓取url", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("抓取url", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("抓取url", 2, "停止监听网页请求"))
        xbot_visual.web.browser.start_monitor_network(browser=web_page, url="*", use_wildcard=True, resource_type="All", _block=("抓取url", 3, "开始监听网页请求"))
        # web.create
        # web.browser.navigate
        xbot_visual.web.element.click(browser=web_page, element=package.selector("斜体文本"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抓取url", 6, "点击元素(web)"))
        # web.browser.wait_load_completed
        xbot_visual.programing.sleep(random_number=False, seconds="4", start_number="1", stop_number="5", _block=("抓取url", 8, "等待"))
        response_body_list = xbot_visual.web.browser.get_responses(browser=web_page, url="", use_wildcard=False, resource_type="All", _block=("抓取url", 9, "获取网页监听结果"))
        for loop_item in xbot_visual.workflow.list_iterator(list=response_body_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("抓取url", 10, "ForEach列表循环")):
            url = xbot_visual.programing.variable(value=lambda: loop_item['url']
            , _block=("抓取url", 11, "设置变量"))
            xbot_visual.programing.log(type="info", text=url, _block=("抓取url", 12, "打印日志"))
            body = xbot_visual.programing.variable(value=lambda: loop_item['body']
            , _block=("抓取url", 13, "设置变量"))
            # json.to_text
            if xbot_visual.workflow.test(operand1=body, operator="in", operand2="Save 5% on Gold V Designer Earring Personalize", operator_options="{\"ignoreCase\":\"False\"}", _block=("抓取url", 15, "IF 条件")):
                xbot_visual.programing.log(type="info", text=url, _block=("抓取url", 16, "打印日志"))
                xbot_visual.programing.log(type="info", text=body, _block=("抓取url", 17, "打印日志"))
                xbot_visual.file.write(path="C:\\Users\\yd\\Desktop\\日志.txt", content=body, write_way="overwrite", is_text=True, new_line=False, encoding="UTF-8", _block=("抓取url", 18, "写入文件"))
                xbot_visual.programing.log(type="info", text=lambda: "="*200, _block=("抓取url", 19, "打印日志"))
            #endif
        #endloop
        xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("抓取url", 22, "停止监听网页请求"))
    finally:
        pass
