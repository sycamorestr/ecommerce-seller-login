import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        店铺ID = ""
        全局超时时间 = "20"
    else:
        网页对象 = args.get("网页对象", None)
        店铺ID = args.get("店铺ID", "")
        全局超时时间 = args.get("全局超时时间", "20")
    try:
        #region 前置流程参数
        web_page = xbot_visual.programing.variable(value=网页对象
        , _block=("抖店店铺切换(ID)(新)", 2, "设置变量"))
        web_page_mode = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_active_by_web_page", params={
            "web_page": 网页对象,
        }, _block=("抖店店铺切换(ID)(新)", 3, "调用模块"))
        if xbot_visual.workflow.test(operand1=web_page, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店店铺切换(ID)(新)", 4, "IF 条件")):
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type=web_page_mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="30", stop_load_if_load_timeout="stopLoad", open_page=False, url=None, _block=("抖店店铺切换(ID)(新)", 5, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("抖店店铺切换(ID)(新)", 5,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        #endif
        shop_name = xbot_visual.programing.variable(value=店铺ID
        , _block=("抖店店铺切换(ID)(新)", 7, "设置变量"))
        # 处于首页时，等待店铺栏出现
        web_page_attribute = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("抖店店铺切换(ID)(新)", 9, "获取网页信息"))
        if xbot_visual.workflow.test(operand1=web_page_attribute, operator="in", operand2="fxg.jinritemai.com/ffa", operator_options="{\"ignoreCase\":\"True\"}", _block=("抖店店铺切换(ID)(新)", 10, "IF 条件")):
            for _ in xbot_visual.workflow.range_iterator(start="1", stop="50", step="1", _block=("抖店店铺切换(ID)(新)", 11, "For次数循环")):
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("抖店店铺切换(ID)(新)", 12, "等待"))
                try:
                    店铺栏 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("抖店_当前店铺名称"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="3", _block=("抖店店铺切换(ID)(新)", 13, "获取元素对象(web)"))
                except Exception as e:
                    pass
                    店铺栏 = None
                if xbot_visual.workflow.test(operand1=店铺栏, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店店铺切换(ID)(新)", 14, "IF 条件")):
                    break
                #endif
            #endloop
        #endif
        try:
            xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_当前店铺名称"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="10", _block=("抖店店铺切换(ID)(新)", 20, "点击元素(web)"))
            web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@label=\"店铺ID\"]", is_related_parent=False, parent=None, timeout="10", _block=("抖店店铺切换(ID)(新)", 21, "获取元素对象(web)"))
            店铺ID信息 = xbot_visual.web.element.get_details(browser=web_page, element=web_element, operation="other", absolute_url=False, attribute_name="value", relative_to="screen", to96dpi=True, timeout="20", _block=("抖店店铺切换(ID)(新)", 22, "获取元素信息(web)"))
            if xbot_visual.workflow.test(operand1=店铺ID信息, operator="==", operand2=shop_name, operator_options="{}", _block=("抖店店铺切换(ID)(新)", 23, "IF 条件")):
                return
            #endif
        except Exception as exception2:
            exception2 = xbot_visual.trace(exception2)
            pass
        #endtry
        time_out = xbot_visual.programing.variable(value=lambda: int(全局超时时间)
        , _block=("抖店店铺切换(ID)(新)", 28, "设置变量"))
        if xbot_visual.workflow.test(operand1=shop_name, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店店铺切换(ID)(新)", 29, "IF 条件")):
            xbot_visual.programing.log(type="info", text="抖店店铺切换：未填写目标店铺ID，无需进行店铺切换 ~", _block=("抖店店铺切换(ID)(新)", 30, "打印日志"))
            return
        #endif
        #endregion
        retry_times = xbot_visual.programing.variable(value=""
        , _block=("抖店店铺切换(ID)(新)", 34, "设置变量"))
        for retry_times in xbot_visual.workflow.range_iterator(start="1", stop="3", step="1", _block=("抖店店铺切换(ID)(新)", 35, "For次数循环")):
            try:
                response_body_list2 = xbot_visual.programing.variable(value=lambda: []
                , _block=("抖店店铺切换(ID)(新)", 37, "设置变量"))
                #region 跳转店铺切换页面
                xbot_visual.web.browser.start_monitor_network(browser=web_page, url="*ecomauth/loginv1/get_login_subject*", use_wildcard=True, resource_type="All", _block=("抖店店铺切换(ID)(新)", 39, "开始监听网页请求"))
                for loop_index4 in xbot_visual.workflow.range_iterator(start="1", stop="5", step="1", _block=("抖店店铺切换(ID)(新)", 40, "For次数循环")):
                    try:
                        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://fxg.jinritemai.com/ffa/multiShop", ignore_cache=False, load_timeout=time_out, _block=("抖店店铺切换(ID)(新)", 41, "跳转至新网址"))
                    except Exception as e:
                        pass
                    xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("抖店店铺切换(ID)(新)", 42, "等待"))
                    response_body_list2 = xbot_visual.web.browser.get_responses(browser=web_page, url="", use_wildcard=False, resource_type="All", _block=("抖店店铺切换(ID)(新)", 43, "获取网页监听结果"))
                    try:
                        all_id_message = xbot_visual.text.extract_content_from_text(text=lambda: response_body_list2[-1]['body'], extract_way="custom", regular_pattern="account_id.*?:.*?\"(.*?)\"", just_get_first=False, ignore_case=False, _block=("抖店店铺切换(ID)(新)", 44, "从文本中提取内容"))
                    except Exception as e:
                        pass
                        all_id_message = None
                    if xbot_visual.workflow.test(operand1="all_id_message", operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店店铺切换(ID)(新)", 45, "IF 条件")):
                        break
                    #endif
                    xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("抖店店铺切换(ID)(新)", 48, "等待"))
                #endloop
                xbot_visual.web.browser.stop_monitor_network(browser=web_page, _block=("抖店店铺切换(ID)(新)", 50, "停止监听网页请求"))
                #endregion
                子店铺相似元素组 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("抖店_店铺切换_子账号_块相似元素组(新)"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout=time_out, output_with_element_count=False, _block=("抖店店铺切换(ID)(新)", 52, "获取相似元素列表(web)"))
                # json.to_text
                all_id_message = xbot_visual.text.extract_content_from_text(text=lambda: response_body_list2[-1]['body'], extract_way="custom", regular_pattern="account_id.*?:.*?\"(.*?)\"", just_get_first=False, ignore_case=False, _block=("抖店店铺切换(ID)(新)", 54, "从文本中提取内容"))
                click_cnt = xbot_visual.programing.variable(value=lambda: 0
                , _block=("抖店店铺切换(ID)(新)", 55, "设置变量"))
                is_click = xbot_visual.programing.variable(value=False
                , _block=("抖店店铺切换(ID)(新)", 56, "设置变量"))
                for click_cnt, loop_item in enumerate(xbot_visual.workflow.list_iterator(list=all_id_message, loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("抖店店铺切换(ID)(新)", 57, "ForEach列表循环"))):
                    if xbot_visual.workflow.test(operand1=lambda: loop_item, operator="==", operand2=shop_name, operator_options="{}", _block=("抖店店铺切换(ID)(新)", 58, "IF 条件")):
                        # 点击目标店铺
                        点击店铺 = xbot_visual.programing.variable(value=lambda: 子店铺相似元素组[click_cnt]
                        , _block=("抖店店铺切换(ID)(新)", 60, "设置变量"))
                        xbot_visual.web.element.click(browser=web_page, element=点击店铺, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店店铺切换(ID)(新)", 61, "点击元素(web)"))
                        is_click = xbot_visual.programing.variable(value=True
                        , _block=("抖店店铺切换(ID)(新)", 62, "设置变量"))
                        break
                    else:
                        # 判断是不是最后一项，如果是最后一项就抛错没找到目标店铺
                        if xbot_visual.workflow.test(operand1=click_cnt, operator="==", operand2=lambda: len(子店铺相似元素组) - 1, operator_options="{}", _block=("抖店店铺切换(ID)(新)", 66, "IF 条件")):
                            raise Exception("未找到目标店铺ID（" + xbot_visual.sh_str(shop_name) + "）")
                        #endif
                    #endif
                #endloop
                if xbot_visual.workflow.test(operand1=is_click, operator="is true", operand2="", operator_options="{}", _block=("抖店店铺切换(ID)(新)", 71, "IF 条件")):
                    break
                #endif
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                xbot_visual.programing.log(type="info", text="抖店店铺切换【" + xbot_visual.sh_str(retry_times) + "】：" + xbot_visual.sh_str(exception), _block=("抖店店铺切换(ID)(新)", 75, "打印日志"))
                if xbot_visual.workflow.test(operand1=retry_times, operator="==", operand2="3", operator_options="{}", _block=("抖店店铺切换(ID)(新)", 76, "IF 条件")):
                    raise Exception("抖店店铺切换：" + xbot_visual.sh_str(exception))
                elif xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": exception,"operand2": "当前店铺已停用","operator": "in"},{"operand1": exception,"operand2": "未找到目标店铺","operator": "in"}], _block=("抖店店铺切换(ID)(新)", 78, "Else IF 多条件")):
                    raise Exception("抖店店铺切换：" + xbot_visual.sh_str(exception))
                #endif
            #endtry
        #endloop
        web_wait_result3 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("抖店_当前店铺名称"), state="appear", iswait=True, timeout="20", _block=("抖店店铺切换(ID)(新)", 83, "等待元素(web)"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("抖店_即时零食"), _block=("抖店店铺切换(ID)(新)", 84, "IF 元素可见(web)")):
            return
        #endif
        xbot_visual.web.element.click(browser=web_page, element=package.selector("抖店_当前店铺名称"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("抖店店铺切换(ID)(新)", 87, "点击元素(web)"))
        web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@label=\"店铺ID\"]", is_related_parent=False, parent=None, timeout="20", _block=("抖店店铺切换(ID)(新)", 88, "获取元素对象(web)"))
        店铺ID信息 = xbot_visual.web.element.get_details(browser=web_page, element=web_element, operation="other", absolute_url=False, attribute_name="value", relative_to="screen", to96dpi=True, timeout="20", _block=("抖店店铺切换(ID)(新)", 89, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=店铺ID信息, operator="!=", operand2=shop_name, operator_options="{}", _block=("抖店店铺切换(ID)(新)", 90, "IF 条件")):
            raise Exception("当前店铺与目标店铺不同，请检查店铺ID")
        #endif
    finally:
        pass
