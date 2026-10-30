import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        web_page = xbot_visual.web.get(web_type="superbrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("网络监听", 1, "获取已打开的网页对象"))
        try:
            xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("网络监听", 2, "停止监听网页请求"))
        except Exception as e:
            xbot_visual.programing.log(type='info',text=e,_block=("网络监听", 2,"停止监听网页请求"))
        xbot_visual.web.browser.start_monitor_network(browser=web_page, url="*", use_wildcard=True, resource_type="All", _block=("网络监听", 3, "开始监听网页请求"))
        xbot_visual.web.browser.navigate(browser=web_page, mode="reload", url="", ignore_cache=False, load_timeout="20", _block=("网络监听", 4, "跳转至新网址"))
        # web.element.click
        xbot_visual.web.element.click(browser=web_page, element=package.selector("测试3"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("网络监听", 6, "点击元素(web)"))
        # web.element.click
        # web.element.click
        # web.element.click
        # web.element.click
        # web.element.click
        # web.element.click
        # web.element.click
        # web.element.click
        # web.element.click
        # web.element.click
        # web.element.click
        # dialog.show_custom_message_box
        response_body_list = xbot_visual.web.browser.get_responses(browser=web_page, url="", use_wildcard=False, resource_type="All", _block=("网络监听", 19, "获取网页监听结果"))
        for loop_item in xbot_visual.workflow.list_iterator(list=response_body_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("网络监听", 20, "ForEach列表循环")):
            xbot_visual.programing.log(type="info", text=loop_item, _block=("网络监听", 21, "打印日志"))
        #endloop
        xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("网络监听", 23, "停止监听网页请求"))
    finally:
        pass
