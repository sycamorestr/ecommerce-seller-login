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
                web_page = xbot_visual.web.get(web_type="superbrowser", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("TEST E1 优惠券", 1, "获取已打开的网页对象"))
                _xbot_retry_time = 5
            except Exception as e:
                if _xbot_retry_time == 3:
                    raise e
                else:
                    xbot_visual.programing.log(type='info',text=e,_block=("TEST E1 优惠券", 1,"获取已打开的网页对象"))
                _xbot_retry_time += 1
                time.sleep(3)
        xbot_visual.web.browser.start_monitor_network(browser=web_page, url="*", use_wildcard=True, resource_type="All", _block=("TEST E1 优惠券", 2, "开始监听网页请求"))
        xbot_visual.web.browser.navigate(browser=web_page, mode="reload", url="", ignore_cache=False, load_timeout="20", _block=("TEST E1 优惠券", 3, "跳转至新网址"))
        # web.element.get_element
        # web.element.click
        xbot_visual.web.browser.wait_load_completed(browser=web_page, load_timeout="20", action_after_load_timeout="handleExcept", _block=("TEST E1 优惠券", 6, "等待网页加载完成"))
        xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("TEST E1 优惠券", 7, "等待"))
        response_body_list = xbot_visual.web.browser.get_responses(browser=web_page, url="", use_wildcard=False, resource_type="All", _block=("TEST E1 优惠券", 8, "获取网页监听结果"))
        for loop_item in xbot_visual.workflow.list_iterator(list=response_body_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("TEST E1 优惠券", 9, "ForEach列表循环")):
            body = xbot_visual.programing.variable(value=lambda: loop_item['body']
            , _block=("TEST E1 优惠券", 10, "设置变量"))
            xbot_visual.programing.log(type="info", text=lambda: loop_item['url'], _block=("TEST E1 优惠券", 11, "打印日志"))
            xbot_visual.programing.log(type="info", text=body, _block=("TEST E1 优惠券", 12, "打印日志"))
            if xbot_visual.workflow.test(operand1=body, operator="in", operand2="Save 5% on 24 Themed Christmas Tree DIY Ornament", operator_options="{\"ignoreCase\":\"False\"}", _block=("TEST E1 优惠券", 13, "IF 条件")):
                xbot_visual.programing.log(type="info", text=lambda: "=="*200, _block=("TEST E1 优惠券", 14, "打印日志"))
                xbot_visual.programing.log(type="info", text=lambda: loop_item['url'], _block=("TEST E1 优惠券", 15, "打印日志"))
                xbot_visual.file.write(path="C:\\Users\\yd\\Desktop\\日志.txt", content=body, write_way="overwrite", is_text=True, new_line=False, encoding="UTF-8", _block=("TEST E1 优惠券", 16, "写入文件"))
                content = xbot_visual.text.extract_content_from_text(text=body, extract_way="custom", regular_pattern="(?<=var coupons = ).+", just_get_first=True, ignore_case=False, _block=("TEST E1 优惠券", 17, "从文本中提取内容"))
                xbot_visual.programing.log(type="info", text=content, _block=("TEST E1 优惠券", 18, "打印日志"))
                json_instance = xbot_visual.json.to_json(text=content, _block=("TEST E1 优惠券", 19, "转换成Json对象"))
                xbot_visual.programing.log(type="info", text=json_instance, _block=("TEST E1 优惠券", 20, "打印日志"))
            #endif
        #endloop
        xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("TEST E1 优惠券", 23, "停止监听网页请求"))
        response_body_list = xbot_visual.web.browser.get_responses(browser=web_page, url="", use_wildcard=False, resource_type="All", _block=("TEST E1 优惠券", 24, "获取网页监听结果"))
        xbot_visual.programing.log(type="info", text=response_body_list, _block=("TEST E1 优惠券", 25, "打印日志"))
    finally:
        pass
