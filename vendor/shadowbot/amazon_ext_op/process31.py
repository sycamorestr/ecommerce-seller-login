import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    try:
        web_page = xbot_visual.web.get(web_type="superbrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("网络监听(副本)1", 1, "获取已打开的网页对象"))
        try:
            xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("网络监听(副本)1", 2, "停止监听网页请求"))
        except Exception as e:
            xbot_visual.programing.log(type='info',text=e,_block=("网络监听(副本)1", 2,"停止监听网页请求"))
        xbot_visual.web.browser.start_monitor_network(browser=web_page, url="*", use_wildcard=True, resource_type="All", _block=("网络监听(副本)1", 3, "开始监听网页请求"))
        pressed_button = xbot_visual.dialog.show_message_box(title="1", message="1", buttons="确定", default_button="确定", use_wait_timeout=False, wait_seconds=None, _block=("网络监听(副本)1", 4, "打开信息对话框"))
        response_body_list = xbot_visual.web.browser.get_responses(browser=web_page, url="", use_wildcard=False, resource_type="All", _block=("网络监听(副本)1", 5, "获取网页监听结果"))
        xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("网络监听(副本)1", 6, "停止监听网页请求"))
        for loop_item in xbot_visual.workflow.list_iterator(list=response_body_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("网络监听(副本)1", 7, "ForEach列表循环")):
            xbot_visual.programing.log(type="info", text=lambda: loop_item['url'], _block=("网络监听(副本)1", 8, "打印日志"))
            xbot_visual.programing.log(type="info", text=lambda: loop_item['body'], _block=("网络监听(副本)1", 9, "打印日志"))
        #endloop
    finally:
        pass
