import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    if args is None:
        网页对象 = None
        目标店铺名称 = ""
        全局超时时间 = ""
    else:
        网页对象 = args.get("网页对象", None)
        目标店铺名称 = args.get("目标店铺名称", "")
        全局超时时间 = args.get("全局超时时间", "")
    try:
        #region 前置流程参数
        web_page = xbot_visual.programing.variable(value=网页对象
        , _block=("抖店店铺切换（新）", 2, "设置变量"))
        web_page_mode = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_active_by_web_page", params={
            "web_page": 网页对象,
        }, _block=("抖店店铺切换（新）", 3, "调用模块"))
        if xbot_visual.workflow.test(operand1=web_page, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店店铺切换（新）", 4, "IF 条件")):
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type=web_page_mode, mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="30", stop_load_if_load_timeout="stopLoad", open_page=False, url=None, _block=("抖店店铺切换（新）", 5, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("抖店店铺切换（新）", 5,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        #endif
        shop_name = xbot_visual.programing.variable(value=目标店铺名称
        , _block=("抖店店铺切换（新）", 7, "设置变量"))
        # 处于首页时，等待店铺栏出现
        web_page_attribute = xbot_visual.web.browser.get_details(browser=web_page, operation="url", _block=("抖店店铺切换（新）", 9, "获取网页信息"))
        if xbot_visual.workflow.test(operand1=web_page_attribute, operator="in", operand2="fxg.jinritemai.com/ffa", operator_options="{\"ignoreCase\":\"True\"}", _block=("抖店店铺切换（新）", 10, "IF 条件")):
            for _ in xbot_visual.workflow.range_iterator(start="1", stop="50", step="1", _block=("抖店店铺切换（新）", 11, "For次数循环")):
                xbot_visual.programing.sleep(random_number=False, seconds="1", start_number="1", stop_number="5", _block=("抖店店铺切换（新）", 12, "等待"))
                try:
                    店铺栏 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"headerShopName\")]", is_related_parent=False, parent=None, timeout="3", _block=("抖店店铺切换（新）", 13, "获取元素对象(web)"))
                except Exception as e:
                    pass
                    店铺栏 = None
                if xbot_visual.workflow.test(operand1=店铺栏, operator="not empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店店铺切换（新）", 14, "IF 条件")):
                    break
                #endif
            #endloop
        #endif
        try:
            web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"headerShopName\")]", is_related_parent=False, parent=None, timeout="6", _block=("抖店店铺切换（新）", 20, "获取元素对象(web)"))
            web_element_attribute = xbot_visual.web.element.get_details(browser=web_page, element=web_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店店铺切换（新）", 21, "获取元素信息(web)"))
            if xbot_visual.workflow.test(operand1=web_element_attribute, operator="==", operand2=shop_name, operator_options="{}", _block=("抖店店铺切换（新）", 22, "IF 条件")):
                return
            #endif
        except Exception as exception2:
            exception2 = xbot_visual.trace(exception2)
            pass
        #endtry
        time_out = xbot_visual.programing.variable(value=lambda: int(全局超时时间)
        , _block=("抖店店铺切换（新）", 27, "设置变量"))
        if xbot_visual.workflow.test(operand1=shop_name, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("抖店店铺切换（新）", 28, "IF 条件")):
            xbot_visual.programing.log(type="info", text="抖店店铺切换：未填写目标店铺名称，无需进行店铺切换 ~", _block=("抖店店铺切换（新）", 29, "打印日志"))
            return
        #endif
        #endregion
        retry_times = xbot_visual.programing.variable(value=""
        , _block=("抖店店铺切换（新）", 33, "设置变量"))
        for retry_times in xbot_visual.workflow.range_iterator(start="1", stop="3", step="1", _block=("抖店店铺切换（新）", 34, "For次数循环")):
            try:
                #region 跳转店铺切换页面
                try:
                    xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://fxg.jinritemai.com/ffa/multiShop", ignore_cache=False, load_timeout=time_out, _block=("抖店店铺切换（新）", 37, "跳转至新网址"))
                except Exception as e:
                    pass
                xbot_visual.programing.sleep(random_number=False, seconds=lambda: max(time_out // 4 + 1, 5), start_number="1", stop_number="5", _block=("抖店店铺切换（新）", 38, "等待"))
                #endregion
                #region 判断走新旧流程
                # programing.log
                旧_wait_result = xbot_visual.programing.variable(value=False
                , _block=("抖店店铺切换（新）", 42, "设置变量"))
                新_wait_result = xbot_visual.programing.variable(value=False
                , _block=("抖店店铺切换（新）", 43, "设置变量"))
                single_result = xbot_visual.programing.variable(value=False
                , _block=("抖店店铺切换（新）", 44, "设置变量"))
                for loop_index2 in xbot_visual.workflow.range_iterator(start="1", stop=lambda: time_out // 2, step="1", _block=("抖店店铺切换（新）", 45, "For次数循环")):
                    旧_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("抖店_店铺切换_子账号_块相似元素组"), state="appear", iswait=True, timeout="2", _block=("抖店店铺切换（新）", 46, "等待元素(web)"))
                    新_wait_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("抖店_店铺切换_子账号_块相似元素组(新)"), state="appear", iswait=True, timeout="2", _block=("抖店店铺切换（新）", 47, "等待元素(web)"))
                    single_result = xbot_visual.web.element.wait(browser=web_page, element=package.selector("店铺名称"), state="appear", iswait=True, timeout="2", _block=("抖店店铺切换（新）", 48, "等待元素(web)"))
                    if xbot_visual.workflow.test(operand1=single_result, operator="is true", operand2="", operator_options="{}", _block=("抖店店铺切换（新）", 49, "IF 条件")):
                        return
                    #endif
                    if xbot_visual.workflow.test(operand1=lambda: bool(旧_wait_result) or bool(新_wait_result), operator="is true", operand2="", operator_options="{}", _block=("抖店店铺切换（新）", 52, "IF 条件")):
                        break
                    #endif
                #endloop
                #endregion
                if xbot_visual.workflow.test(operand1=旧_wait_result, operator="is true", operand2="", operator_options="{}", _block=("抖店店铺切换（新）", 57, "IF 条件")):
                    子店铺相似元素组 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=package.selector("抖店_店铺切换_子账号_块相似元素组"), css_selector="", xpath_selector="//div[contains(@class, \"index_roleItem\")]", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout=time_out, output_with_element_count=False, _block=("抖店店铺切换（新）", 58, "获取相似元素列表(web)"))
                    if xbot_visual.workflow.test(operand1=lambda: 目标店铺名称.isnumeric(), operator="is false", operand2="", operator_options="{}", _block=("抖店店铺切换（新）", 59, "IF 条件")):
                        #region 通过店铺名称选择店铺
                        # 循环子店铺
                        for 当前子店铺_index, 当前子店铺 in enumerate(xbot_visual.workflow.list_iterator(list=子店铺相似元素组, loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("抖店店铺切换（新）", 62, "ForEach列表循环"))):
                            当前子店铺名称 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=".//div[contains(@class, \"index_introName\")]", is_related_parent=True, parent=当前子店铺, timeout=time_out, _block=("抖店店铺切换（新）", 63, "获取元素对象(web)"))
                            # programing.log
                            if xbot_visual.workflow.test(operand1=当前子店铺名称.get_text(), operator="==", operand2=shop_name, operator_options="{}", _block=("抖店店铺切换（新）", 65, "IF 条件")):
                                # programing.log
                                # 判断当前子店铺状态
                                # web.element.get_element
                                # workflow.if
                                # workflow.multiple_conditions_if
                                # programing.raise
                                # workflow.endif
                                # workflow.endif
                                # 找到店铺就找子元素“进入店铺”按钮，去点击
                                # web.element.get_element
                                xbot_visual.web.element.click(browser=web_page, element=当前子店铺, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("抖店店铺切换（新）", 76, "点击元素(web)"))
                                break
                            else:
                                # 判断是不是最后一项，如果是最后一项就抛错没找到目标店铺
                                if xbot_visual.workflow.test(operand1=当前子店铺_index, operator="==", operand2=lambda: len(子店铺相似元素组) - 1, operator_options="{}", _block=("抖店店铺切换（新）", 80, "IF 条件")):
                                    raise Exception("未找到目标店铺（" + xbot_visual.sh_str(shop_name) + "）")
                                #endif
                            #endif
                        #endloop
                        #endregion
                    else:
                        #region 通过店铺索引选择店铺
                        shop_index = xbot_visual.programing.variable(value=lambda: int(shop_name) - 1
                        , _block=("抖店店铺切换（新）", 88, "设置变量"))
                        if xbot_visual.workflow.test(operand1=shop_index, operator=">=", operand2=len(子店铺相似元素组), operator_options="{}", _block=("抖店店铺切换（新）", 89, "IF 条件")):
                            raise Exception("抖店店铺切换：您提供的索引大于店铺总数量，无法选择店铺 ~")
                        #endif
                        目标子店铺 = xbot_visual.programing.variable(value=lambda: 子店铺相似元素组[shop_index]
                        , _block=("抖店店铺切换（新）", 92, "设置变量"))
                        # 获取索引对应店铺名，用于后续切换校验
                        店铺标题元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=".//div[contains(@class,'index_introName')]", is_related_parent=True, parent=目标子店铺, timeout="20", _block=("抖店店铺切换（新）", 94, "获取元素对象(web)"))
                        shop_name = xbot_visual.web.element.get_details(browser=web_page, element=店铺标题元素, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店店铺切换（新）", 95, "获取元素信息(web)"))
                        # 点击目标店铺
                        # web.element.get_element
                        xbot_visual.web.element.click(browser=web_page, element=店铺标题元素, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("抖店店铺切换（新）", 98, "点击元素(web)"))
                        #endregion
                    #endif
                elif xbot_visual.workflow.test(operand1=新_wait_result, operator="is true", operand2="", operator_options="{}", _block=("抖店店铺切换（新）", 101, "Else IF")):
                    子店铺相似元素组 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("抖店_店铺切换_子账号_块相似元素组(新)"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout=time_out, output_with_element_count=False, _block=("抖店店铺切换（新）", 102, "获取相似元素列表(web)"))
                    # workflow.if
                    if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": lambda: len(目标店铺名称),"operand2": "3","operator": ">"},{"operand1": lambda: 目标店铺名称[0].isdigit(),"operand2": "","operator": "is false"}], _block=("抖店店铺切换（新）", 104, "IF 多条件")):
                        #region 通过店铺名称选择店铺
                        # 循环子店铺
                        for 当前子店铺_index, 当前子店铺 in enumerate(xbot_visual.workflow.list_iterator(list=子店铺相似元素组, loop_start_index="0", loop_end_index="-1", output_with_index=True, _block=("抖店店铺切换（新）", 107, "ForEach列表循环"))):
                            当前子店铺名称 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("抖店_店铺切换_子账号名称_块相似元素组(新)"), css_selector="", xpath_selector="", is_related_parent=True, parent=当前子店铺, timeout=time_out, _block=("抖店店铺切换（新）", 108, "获取元素对象(web)"))
                            if xbot_visual.workflow.test(operand1=当前子店铺名称.get_text(), operator="==", operand2=shop_name, operator_options="{}", _block=("抖店店铺切换（新）", 109, "IF 条件")):
                                # programing.comment
                                # 找到店铺就去点击
                                xbot_visual.web.element.click(browser=web_page, element=当前子店铺, simulate=True, move_mouse=True, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("抖店店铺切换（新）", 112, "点击元素(web)"))
                                break
                            else:
                                # 判断是不是最后一项，如果是最后一项就抛错没找到目标店铺
                                if xbot_visual.workflow.test(operand1=当前子店铺_index, operator="==", operand2=lambda: len(子店铺相似元素组) - 1, operator_options="{}", _block=("抖店店铺切换（新）", 116, "IF 条件")):
                                    raise Exception("未找到目标店铺（" + xbot_visual.sh_str(shop_name) + "）")
                                #endif
                            #endif
                        #endloop
                        #endregion
                    else:
                        #region 通过店铺索引选择店铺
                        子店铺相似元素组 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="selector", selector=package.selector("抖店_店铺切换_子账号_块相似元素组(新)"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, operation="element", absolute_url=False, attribute_name=None, timeout=time_out, output_with_element_count=False, _block=("抖店店铺切换（新）", 124, "获取相似元素列表(web)"))
                        shop_index = xbot_visual.programing.variable(value=lambda: int(shop_name) - 1
                        , _block=("抖店店铺切换（新）", 125, "设置变量"))
                        if xbot_visual.workflow.test(operand1=shop_index, operator=">=", operand2=len(子店铺相似元素组), operator_options="{}", _block=("抖店店铺切换（新）", 126, "IF 条件")):
                            raise Exception("抖店店铺切换：您提供的索引大于店铺总数量，无法选择店铺 ~")
                        #endif
                        目标子店铺 = xbot_visual.programing.variable(value=lambda: 子店铺相似元素组[shop_index]
                        , _block=("抖店店铺切换（新）", 129, "设置变量"))
                        # 获取索引对应店铺名，用于后续切换校验
                        店铺标题元素 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=".//div[contains(@class,'index_introName')]", is_related_parent=True, parent=目标子店铺, timeout="20", _block=("抖店店铺切换（新）", 131, "获取元素对象(web)"))
                        shop_name = xbot_visual.web.element.get_details(browser=web_page, element=店铺标题元素, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店店铺切换（新）", 132, "获取元素信息(web)"))
                        # 点击目标店铺
                        xbot_visual.web.element.click(browser=web_page, element=目标子店铺, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout=time_out, _block=("抖店店铺切换（新）", 134, "点击元素(web)"))
                        #endregion
                    #endif
                    # workflow.endif
                #endif
                break
            except Exception as exception:
                exception = xbot_visual.trace(exception)
                xbot_visual.programing.log(type="info", text="抖店店铺切换【" + xbot_visual.sh_str(retry_times) + "】：" + xbot_visual.sh_str(exception), _block=("抖店店铺切换（新）", 141, "打印日志"))
                if xbot_visual.workflow.test(operand1=retry_times, operator="==", operand2="3", operator_options="{}", _block=("抖店店铺切换（新）", 142, "IF 条件")):
                    raise Exception("抖店店铺切换：" + xbot_visual.sh_str(exception))
                elif xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": exception,"operand2": "当前店铺已停用","operator": "in"},{"operand1": exception,"operand2": "未找到目标店铺","operator": "in"}], _block=("抖店店铺切换（新）", 144, "Else IF 多条件")):
                    raise Exception("抖店店铺切换：" + xbot_visual.sh_str(exception))
                #endif
            #endtry
        #endloop
        web_wait_result3 = xbot_visual.web.element.wait(browser=web_page, element=package.selector("抖店_当前店铺名称"), state="appear", iswait=True, timeout="20", _block=("抖店店铺切换（新）", 149, "等待元素(web)"))
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("抖店_即时零食"), _block=("抖店店铺切换（新）", 150, "IF 元素可见(web)")):
            return
        #endif
        当前店铺名称 = xbot_visual.web.element.get_details(browser=web_page, element=package.selector("抖店_当前店铺名称"), operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("抖店店铺切换（新）", 153, "获取元素信息(web)"))
        if xbot_visual.workflow.test(operand1=shop_name, operator="!=", operand2=当前店铺名称, operator_options="{}", _block=("抖店店铺切换（新）", 154, "IF 条件")):
            raise Exception("当前店铺与目标店铺不同，请检查店铺名")
        #endif
    finally:
        pass
