import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    输出文件路径 = ""
    执行状态 = "成功"
    数据集对象列表 = []
    if args is None:
        查询日期 = "2026-01-02"
        保存文件夹 = ""
        开启页面统计时间校验 = True
        web_page = None
    else:
        查询日期 = args.get("查询日期", "2026-01-02")
        保存文件夹 = args.get("保存文件夹", "")
        开启页面统计时间校验 = args.get("开启页面统计时间校验", True)
        web_page = args.get("web_page", None)
    try:
        #region 获取当前页进行目标页面跳转
        if xbot_visual.workflow.test(operand1=web_page, operator="empty value", operand2="", operator_options="{\"values\":\"None,Empty,Blank\"}", _block=("首页-运营视窗整体看板数据获取", 2, "IF 条件")):
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("首页-运营视窗整体看板数据获取", 3, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("首页-运营视窗整体看板数据获取", 3,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
        #endif
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url="https://sycm.taobao.com/portal/home.htm?activeKey=operator", ignore_cache=False, load_timeout="20", _block=("首页-运营视窗整体看板数据获取", 5, "跳转至新网址"))
        xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("首页-运营视窗整体看板数据获取", 6, "等待"))
        # xbot_extensions.activity_fe2a1069.PopupBlocker
        #endregion
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("运营视窗整体看板数据获取_返回旧版"), _block=("首页-运营视窗整体看板数据获取", 9, "IF 元素可见(web)")):
            #region 新版
            if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 查询日期,"operand2": "日","operator": "in"},{"operand1": 查询日期,"operand2": "周","operator": "in"},{"operand1": 查询日期,"operand2": "月","operator": "in"}], _block=("首页-运营视窗整体看板数据获取", 11, "IF 多条件")):
                web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=lambda: f'(//span[text()="{查询日期}"])[1]', is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 12, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=web_page, element=web_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 13, "点击元素(web)"))
            else:
                自定义日 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="(//span[text()=\"日\"])[1]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 15, "获取元素对象(web)"))
                xbot_visual.web.element.hover(browser=web_page, element=自定义日, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 16, "鼠标悬停在元素上(web)"))
                xbot_visual.process.run(process="xbot_extensions.web_action.select_date", package=__name__, inputs={
                    "web_page": web_page,
                    "date_elem": package.selector("运营视窗整体看板数据获取_日期框"),
                    "date_start": 查询日期,
                    "date_end": "",
                    "simulative": False,
                    }, outputs=[
                ], _block=("首页-运营视窗整体看板数据获取", 17, "智能日期选择器"))
            #endif
            #region 页面统计时间校验 
            # web.element.get_element
            # web.element.get_element
            # web.element.get_element
            首页_统计时间文本_定位后 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"pro-layout-card-header__ft\"]//div[@class=\"oui-date-picker-menu-v2  oui-date-picker-current-date\"]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 23, "获取元素对象(web)"))
            xbot_visual.web.element.hover(browser=web_page, element=首页_统计时间文本_定位后, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 24, "鼠标悬停在元素上(web)"))
            统计时间文本信息 = xbot_visual.web.element.get_details(browser=web_page, element=首页_统计时间文本_定位后, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("首页-运营视窗整体看板数据获取", 25, "获取元素信息(web)"))
            页面统计时间 = xbot_visual.text.extract_content_from_text(text=统计时间文本信息, extract_way="custom", regular_pattern="统计时间 (.*)", just_get_first=True, ignore_case=False, _block=("首页-运营视窗整体看板数据获取", 26, "从文本中提取内容"))
            # text.split_text_to_list
            # programing.variable
            xbot_visual.programing.log(type="info", text="当前页面统计时间为 : " + xbot_visual.sh_str(页面统计时间), _block=("首页-运营视窗整体看板数据获取", 29, "打印日志"))
            if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 30, "IF 条件")):
                _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                    "查询日期": 查询日期,
                    "页面统计时间": 页面统计时间,
                    }, outputs=[
                    "判断结果",
                ], _block=("首页-运营视窗整体看板数据获取", 31, "调用流程"))
                if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("首页-运营视窗整体看板数据获取", 32, "IF 条件")):
                    执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                    , _block=("首页-运营视窗整体看板数据获取", 33, "设置变量"))
                    return
                #endif
            #endif
            #endregion
            #region 数据批量抓取
            # xbot_extensions.activity_fe2a1069.ClickByXpath
            # xbot_extensions.activity_fe2a1069.ClickByXpath
            表格元素 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_select", params={
                "xpath": "//span[.=\"表格\"]",
                "name": "表格元素",
            }, _block=("首页-运营视窗整体看板数据获取", 41, "调用模块"))
            for loop_index2 in xbot_visual.workflow.range_iterator(start="0", stop="10", step="1", _block=("首页-运营视窗整体看板数据获取", 42, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=表格元素, _block=("首页-运营视窗整体看板数据获取", 43, "IF 元素可见(web)")):
                    xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                        "web_page": web_page,
                        "xpathSelector": "//span[.=\"查看所有指标\"]",
                        "获取元素超时": lambda: 5,
                        "执行成功后等待": lambda: 1,
                        "是否模拟人工": True,
                        "按钮": "left",
                        "retry_count": lambda: 1,
                        "refresh": False,
                        "是否为iframe对象": False,
                        }, outputs=[
                    ], _block=("首页-运营视窗整体看板数据获取", 44, "点击Xpath元素"))
                else:
                    break
                #endif
            #endloop
            xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                "web_page": web_page,
                "xpathSelector": "//span[.=\"表格\"]",
                "获取元素超时": lambda: 5,
                "执行成功后等待": lambda: 1,
                "是否模拟人工": False,
                "按钮": "left",
                "retry_count": lambda: 1,
                "refresh": False,
                "是否为iframe对象": False,
                }, outputs=[
            ], _block=("首页-运营视窗整体看板数据获取", 49, "点击Xpath元素"))
            # ---------------获取数据
            result = xbot_visual.programing.variable(value=lambda: []
            , _block=("首页-运营视窗整体看板数据获取", 51, "设置变量"))
            for loop_index in xbot_visual.workflow.range_iterator(start="0", stop="5", step="1", _block=("首页-运营视窗整体看板数据获取", 52, "For次数循环")):
                try:
                    if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 查询日期,"operand2": "日","operator": "in"},{"operand1": 查询日期,"operand2": "周","operator": "in"},{"operand1": 查询日期,"operand2": "月","operator": "in"}], _block=("首页-运营视窗整体看板数据获取", 54, "IF 多条件")):
                        web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=lambda: f'(//span[text()="{查询日期}"])[1]', is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 55, "获取元素对象(web)"))
                        xbot_visual.web.element.click(browser=web_page, element=web_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 56, "点击元素(web)"))
                    else:
                        自定义日 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="(//span[text()=\"日\"])[1]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 58, "获取元素对象(web)"))
                        xbot_visual.web.element.hover(browser=web_page, element=自定义日, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 59, "鼠标悬停在元素上(web)"))
                        xbot_visual.process.run(process="xbot_extensions.web_action.select_date", package=__name__, inputs={
                            "web_page": web_page,
                            "date_elem": package.selector("运营视窗整体看板数据获取_日期框"),
                            "date_start": 查询日期,
                            "date_end": "",
                            "simulative": False,
                            }, outputs=[
                        ], _block=("首页-运营视窗整体看板数据获取", 60, "智能日期选择器"))
                    #endif
                    break
                except Exception as exception:
                    exception = xbot_visual.trace(exception)
                    xbot_visual.programing.log(type="info", text=exception, _block=("首页-运营视窗整体看板数据获取", 64, "打印日志"))
                #endtry
            #endloop
            xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("首页-运营视窗整体看板数据获取", 67, "等待"))
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("首页-运营视窗整体看板数据获取", 68, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("首页-运营视窗整体看板数据获取", 68,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
            表格按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"layout-card-header\")]//span[text()=\"表格\"]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 69, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=表格按钮, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 70, "点击元素(web)"))
            列字段_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"ant-table-fixed-left\"]//tr/td[last()]/div[@class=\"leading columnTd\"]", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 71, "获取相似元素列表(web)"))
            总计字段个数 = len(列字段_数据列表)
            temp_列字段_数据列表 = []
            temp_列字段_数据列表 = [v + "_增长率" for v in 列字段_数据列表]
            
            new_列字段_数据列表 = []
            for x, y in zip(列字段_数据列表, temp_列字段_数据列表):
                new_列字段_数据列表.append(x)
                new_列字段_数据列表.append(y)
            
            列字段_数据列表 = new_列字段_数据列表
            日期_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@class=\"numberTableTh\"]/span[1]", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 73, "获取相似元素列表(web)"))
            总计日期个数 = len(日期_数据列表)
            数据cell_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class='ant-table-body']//tr[contains(@class,'ant-table-row')]/td[@class='']", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 74, "获取相似元素列表(web)"))
            总计指标个数 = len(数据cell_数据列表)
            if xbot_visual.workflow.test(operand1=总计指标个数, operator="!=", operand2=lambda: 总计字段个数 * 总计日期个数, operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 75, "IF 条件")):
                raise Exception("指标获取异常，请检查相似元素是否正确")
            #endif
            xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {"日期": 日期_数据列表}, _block=("首页-运营视窗整体看板数据获取", 78, "列表插入一项"))
            for idx in xbot_visual.workflow.range_iterator(start="0", stop=lambda: 总计字段个数 - 1, step=lambda: 1, _block=("首页-运营视窗整体看板数据获取", 79, "For次数循环")):
                start = xbot_visual.programing.variable(value=lambda: idx*总计日期个数
                , _block=("首页-运营视窗整体看板数据获取", 80, "设置变量"))
                end = xbot_visual.programing.variable(value=lambda: start+总计日期个数
                , _block=("首页-运营视窗整体看板数据获取", 81, "设置变量"))
                # programing.log
                行数据 = xbot_visual.programing.variable(value=lambda: 数据cell_数据列表[start: end]
                , _block=("首页-运营视窗整体看板数据获取", 83, "设置变量"))
                xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {列字段_数据列表[idx * 2]: 行数据}, _block=("首页-运营视窗整体看板数据获取", 84, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {列字段_数据列表[idx * 2 + 1]: []}, _block=("首页-运营视窗整体看板数据获取", 85, "列表插入一项"))
            #endloop
            # programing.log
            #endregion
            # --------------输出
            店铺名 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetShopName", package=__name__, inputs={
                "平台名称": "生意参谋",
                "web_page": web_page,
                }, outputs=[
                "店铺名",
            ], _block=("首页-运营视窗整体看板数据获取", 90, "获取店铺名"))
            数据集 = xbot_visual.programing.variable(value="生意参谋_首页_运营视窗_整体看板"
            , _block=("首页-运营视窗整体看板数据获取", 91, "设置变量"))
            输出文件路径 = xbot_visual.programing.variable(value=xbot_visual.sh_str(保存文件夹) + "\\" + xbot_visual.sh_str(数据集) + "_" + xbot_visual.sh_str(页面统计时间) + ".xlsx"
            , _block=("首页-运营视窗整体看板数据获取", 92, "设置变量"))
            # ---------------保存为文件
            import pandas as pd
            
            v_list = []
            
            pre = []
            for dic in result:
                for k, v in dic.items():
                    line = [k]
                    if not v:
                        line += pre
                        pre = []
                    else:
                        line += [i.split('\n')[0] for i in v]
                        pre = [i.split('\n')[1] for i in v if len(i.split('\n')) > 1]
                    v_list.append(line)
            print(v_list)
            df = pd.DataFrame(v_list).T
            
            
            df.to_excel(输出文件路径, index=False, header=False, encoding="utf-8")
            待插入字段 = xbot_visual.programing.variable(value=lambda: [["RPA店铺名_页面", "RPA页面统计日期"], [店铺名, 页面统计时间]]
            , _block=("首页-运营视窗整体看板数据获取", 95, "设置变量"))
            输出数据字典 = xbot_visual.programing.variable(value=lambda: {}
            , _block=("首页-运营视窗整体看板数据获取", 96, "设置变量"))
            xbot_visual.programing.log(type="info", text=result, _block=("首页-运营视窗整体看板数据获取", 97, "打印日志"))
            if xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="周", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 98, "IF 条件")):
                import datetime
                
                start_date, end_date = 页面统计时间.split(" ~ ")
                
                year_start,month_start,day_start = start_date.split("-")
                
                year_end,month_end,day_end = end_date.split("-")
                
                if year_start != year_end:
                  end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                  end_week = end_date_obj.isocalendar()[1]  # 获取ISO周数
                  页面统计时间 = f"{year_end} 第{end_week}周"
                else:
                  start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                  start_week = start_date_obj.isocalendar()[1]  # 获取ISO周数
                  页面统计时间 = f"{year_start} 第{start_week}周"
            #endif
            if xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="月", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 101, "IF 条件")):
                start,end= 页面统计时间.split(" ~ ")
                
                year,month,day = start.split("-")
                
                页面统计时间 = f"{year}-{month}"
            #endif
            # programing.log
            xbot_visual.programing.log(type="info", text=页面统计时间, _block=("首页-运营视窗整体看板数据获取", 105, "打印日志"))
            for i in result:
              if '日期' in i.keys():
                print(i['日期'])
                need_index = i['日期'].index(页面统计时间)
            for i in result:
              key = list(i.keys())[0]
              if need_index < len(i[key]):
                输出数据字典[key] = i[key][need_index]
            xbot_visual.list.append_or_insert(lst=数据集对象列表, insert_way="append", index="0", elem=lambda: {"数据集": 数据集, "文件路径": 输出文件路径, "待插入字段": 待插入字段, "去重主键": ["日期", "支付金额", "客单价"], "输出数据字典": 输出数据字典}, _block=("首页-运营视窗整体看板数据获取", 107, "列表插入一项"))
            return
            #endregion
        #endif
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("运营视窗_体验新版"), _block=("首页-运营视窗整体看板数据获取", 111, "IF 元素可见(web)")):
            #region 旧版
            xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process4", package=__name__, inputs={
                "web_page": web_page,
                "日期": 查询日期,
                }, outputs=[
            ], _block=("首页-运营视窗整体看板数据获取", 113, "通用时间选择-URL跳转"))
            xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("首页-运营视窗整体看板数据获取", 114, "等待"))
            #region 页面统计时间校验 
            首页_运营视窗标签 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("首页-运营视窗div"), css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("首页-运营视窗整体看板数据获取", 116, "获取元素对象(web)"))
            首页_统计时间文本_定位后 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("首页-统计时间文本"), css_selector="", xpath_selector="", is_related_parent=True, parent=首页_运营视窗标签, timeout="20", _block=("首页-运营视窗整体看板数据获取", 117, "获取元素对象(web)"))
            xbot_visual.web.element.hover(browser=web_page, element=首页_统计时间文本_定位后, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 118, "鼠标悬停在元素上(web)"))
            统计时间文本信息 = xbot_visual.web.element.get_details(browser=web_page, element=首页_统计时间文本_定位后, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("首页-运营视窗整体看板数据获取", 119, "获取元素信息(web)"))
            页面统计时间 = xbot_visual.text.extract_content_from_text(text=统计时间文本信息, extract_way="custom", regular_pattern="统计时间 (.*)", just_get_first=True, ignore_case=False, _block=("首页-运营视窗整体看板数据获取", 120, "从文本中提取内容"))
            xbot_visual.programing.log(type="info", text="当前页面统计时间为 : " + xbot_visual.sh_str(页面统计时间), _block=("首页-运营视窗整体看板数据获取", 121, "打印日志"))
            if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 122, "IF 条件")):
                _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                    "查询日期": 查询日期,
                    "页面统计时间": 页面统计时间,
                    }, outputs=[
                    "判断结果",
                ], _block=("首页-运营视窗整体看板数据获取", 123, "调用流程"))
                if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("首页-运营视窗整体看板数据获取", 124, "IF 条件")):
                    执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                    , _block=("首页-运营视窗整体看板数据获取", 125, "设置变量"))
                    return
                #endif
            #endif
            #endregion
            #region 数据批量抓取
            表格元素 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_select", params={
                "xpath": "(//*[text()=\"表格\"])[1]",
                "name": "表格元素",
            }, _block=("首页-运营视窗整体看板数据获取", 131, "调用模块"))
            for loop_index2 in xbot_visual.workflow.range_iterator(start="0", stop="10", step="1", _block=("首页-运营视窗整体看板数据获取", 132, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=表格元素, _block=("首页-运营视窗整体看板数据获取", 133, "IF 元素可见(web)")):
                    xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                        "web_page": web_page,
                        "xpathSelector": "//li/a[text()=\"整体\"]",
                        "获取元素超时": lambda: 5,
                        "执行成功后等待": lambda: 1,
                        "是否模拟人工": False,
                        "按钮": "left",
                        "retry_count": lambda: 1,
                        "refresh": False,
                        "是否为iframe对象": False,
                        }, outputs=[
                    ], _block=("首页-运营视窗整体看板数据获取", 134, "点击Xpath元素"))
                else:
                    break
                #endif
            #endloop
            xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                "web_page": web_page,
                "xpathSelector": "(//*[text()=\"表格\"])[1]",
                "获取元素超时": lambda: 5,
                "执行成功后等待": lambda: 1,
                "是否模拟人工": False,
                "按钮": "left",
                "retry_count": lambda: 1,
                "refresh": False,
                "是否为iframe对象": False,
                }, outputs=[
            ], _block=("首页-运营视窗整体看板数据获取", 139, "点击Xpath元素"))
            # ---------------获取数据
            result = xbot_visual.programing.variable(value=lambda: []
            , _block=("首页-运营视窗整体看板数据获取", 141, "设置变量"))
            _xbot_retry_time = 0
            while _xbot_retry_time <= 3:
                try:
                    web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("首页-运营视窗整体看板数据获取", 142, "获取已打开的网页对象"))
                    _xbot_retry_time = 5
                except Exception as e:
                    if _xbot_retry_time == 3:
                        raise e
                    else:
                        xbot_visual.programing.log(type='info',text=e,_block=("首页-运营视窗整体看板数据获取", 142,"获取已打开的网页对象"))
                    _xbot_retry_time += 1
                    time.sleep(3)
            表格按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"layout-card-header\")]//span[text()=\"表格\"]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 143, "获取元素对象(web)"))
            xbot_visual.web.element.click(browser=web_page, element=表格按钮, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 144, "点击元素(web)"))
            列字段_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"ant-table-fixed-left\"]//tr/td[last()]/div", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 145, "获取相似元素列表(web)"))
            总计字段个数 = len(列字段_数据列表)
            temp_列字段_数据列表 = []
            temp_列字段_数据列表 = [v + "_增长率" for v in 列字段_数据列表]
            
            new_列字段_数据列表 = []
            for x, y in zip(列字段_数据列表, temp_列字段_数据列表):
                new_列字段_数据列表.append(x)
                new_列字段_数据列表.append(y)
            
            列字段_数据列表 = new_列字段_数据列表
            日期_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@class=\"numberTableTh\"]/span[1]", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 147, "获取相似元素列表(web)"))
            总计日期个数 = len(日期_数据列表)
            数据cell_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@id=\"sycm-home-operator-window-core-index\"]//div[@class='ant-table-body']//tr[contains(@class,'ant-table-row')]/td[@class='']", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 148, "获取相似元素列表(web)"))
            总计指标个数 = len(数据cell_数据列表)
            if xbot_visual.workflow.test(operand1=总计指标个数, operator="!=", operand2=lambda: 总计字段个数 * 总计日期个数, operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 149, "IF 条件")):
                raise Exception("指标获取异常，请检查相似元素是否正确")
            #endif
            xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {"日期": 日期_数据列表}, _block=("首页-运营视窗整体看板数据获取", 152, "列表插入一项"))
            for idx in xbot_visual.workflow.range_iterator(start="0", stop=lambda: 总计字段个数 - 1, step=lambda: 1, _block=("首页-运营视窗整体看板数据获取", 153, "For次数循环")):
                start = xbot_visual.programing.variable(value=lambda: idx*总计日期个数
                , _block=("首页-运营视窗整体看板数据获取", 154, "设置变量"))
                end = xbot_visual.programing.variable(value=lambda: start+总计日期个数
                , _block=("首页-运营视窗整体看板数据获取", 155, "设置变量"))
                # programing.log
                行数据 = xbot_visual.programing.variable(value=lambda: 数据cell_数据列表[start: end]
                , _block=("首页-运营视窗整体看板数据获取", 157, "设置变量"))
                xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {列字段_数据列表[idx * 2]: 行数据}, _block=("首页-运营视窗整体看板数据获取", 158, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {列字段_数据列表[idx * 2 + 1]: []}, _block=("首页-运营视窗整体看板数据获取", 159, "列表插入一项"))
            #endloop
            # programing.log
            #endregion
            # --------------输出
            店铺名 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetShopName", package=__name__, inputs={
                "平台名称": "生意参谋",
                "web_page": web_page,
                }, outputs=[
                "店铺名",
            ], _block=("首页-运营视窗整体看板数据获取", 164, "获取店铺名"))
            数据集 = xbot_visual.programing.variable(value="生意参谋_首页_运营视窗_整体看板"
            , _block=("首页-运营视窗整体看板数据获取", 165, "设置变量"))
            输出文件路径 = xbot_visual.programing.variable(value=xbot_visual.sh_str(保存文件夹) + "\\" + xbot_visual.sh_str(数据集) + "_" + xbot_visual.sh_str(页面统计时间) + ".xlsx"
            , _block=("首页-运营视窗整体看板数据获取", 166, "设置变量"))
            # ---------------保存为文件
            import pandas as pd
            
            v_list = []
            
            pre = []
            for dic in result:
                for k, v in dic.items():
                    line = [k]
                    if not v:
                        line += pre
                        pre = []
                    else:
                        line += [i.split('\n')[0] for i in v]
                        pre = [i.split('\n')[1] for i in v if len(i.split('\n')) > 1]
                    v_list.append(line)
            print(v_list)
            df = pd.DataFrame(v_list).T
            
            
            df.to_excel(输出文件路径, index=False, header=False, encoding="utf-8")
            待插入字段 = xbot_visual.programing.variable(value=lambda: [["RPA店铺名_页面", "RPA页面统计日期"], [店铺名, 页面统计时间]]
            , _block=("首页-运营视窗整体看板数据获取", 169, "设置变量"))
            输出数据字典 = xbot_visual.programing.variable(value=lambda: {}
            , _block=("首页-运营视窗整体看板数据获取", 170, "设置变量"))
            # programing.log
            if xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="周", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 172, "IF 条件")):
                import datetime
                
                start_date, end_date = 页面统计时间.split(" ~ ")
                
                year_start,month_start,day_start = start_date.split("-")
                
                year_end,month_end,day_end = end_date.split("-")
                
                if year_start != year_end:
                  end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                  end_week = end_date_obj.isocalendar()[1]  # 获取ISO周数
                  页面统计时间 = f"{year_end} 第{end_week}周"
                else:
                  start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                  start_week = start_date_obj.isocalendar()[1]  # 获取ISO周数
                  页面统计时间 = f"{year_start} 第{start_week}周"
            #endif
            if xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="月", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 175, "IF 条件")):
                start,end= 页面统计时间.split(" ~ ")
                
                year,month,day = start.split("-")
                
                页面统计时间 = f"{year}-{month}"
            #endif
            xbot_visual.programing.log(type="info", text=result, _block=("首页-运营视窗整体看板数据获取", 178, "打印日志"))
            xbot_visual.programing.log(type="info", text=页面统计时间, _block=("首页-运营视窗整体看板数据获取", 179, "打印日志"))
            for i in result:
              if '日期' in i.keys():
                print(i['日期'])
                need_index = i['日期'].index(页面统计时间)
            for i in result:
              key = list(i.keys())[0]
              if need_index < len(i[key]):
                输出数据字典[key] = i[key][need_index]
            xbot_visual.list.append_or_insert(lst=数据集对象列表, insert_way="append", index="0", elem=lambda: {"数据集": 数据集, "文件路径": 输出文件路径, "待插入字段": 待插入字段, "去重主键": ["日期", "支付金额", "客单价"], "输出数据字典": 输出数据字典}, _block=("首页-运营视窗整体看板数据获取", 181, "列表插入一项"))
            return
            #endregion
        #endif
        if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("视窗_切换按钮"), _block=("首页-运营视窗整体看板数据获取", 185, "IF 元素可见(web)")):
            xbot_visual.web.element.hover(browser=web_page, element=package.selector("视窗_切换按钮"), simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 186, "鼠标悬停在元素上(web)"))
            if xbot_visual.web.browser.element_display(browser=web_page, content_type="display", selector=package.selector("视窗_切换旧版(新版)"), _block=("首页-运营视窗整体看板数据获取", 187, "IF 元素可见(web)")):
                #region 新-新版
                if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 查询日期,"operand2": "日","operator": "in"},{"operand1": 查询日期,"operand2": "周","operator": "in"},{"operand1": 查询日期,"operand2": "月","operator": "in"}], _block=("首页-运营视窗整体看板数据获取", 189, "IF 多条件")):
                    web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=lambda: f'(//span[text()="{查询日期}"])[1]', is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 190, "获取元素对象(web)"))
                    xbot_visual.web.element.click(browser=web_page, element=web_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 191, "点击元素(web)"))
                else:
                    自定义日 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="(//span[text()=\"日\"])[1]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 193, "获取元素对象(web)"))
                    xbot_visual.web.element.hover(browser=web_page, element=自定义日, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 194, "鼠标悬停在元素上(web)"))
                    xbot_visual.process.run(process="xbot_extensions.web_action.select_date", package=__name__, inputs={
                        "web_page": web_page,
                        "date_elem": package.selector("运营视窗整体看板数据获取_日期框"),
                        "date_start": 查询日期,
                        "date_end": "",
                        "simulative": False,
                        }, outputs=[
                    ], _block=("首页-运营视窗整体看板数据获取", 195, "智能日期选择器"))
                #endif
                # web.element.hover
                # xbot_extensions.web_action.select_date
                #region 页面统计时间校验 
                # web.element.get_element
                # web.element.get_element
                首页_统计时间文本_定位后 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("首页-统计时间文本_新版_新版"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 202, "获取元素对象(web)"))
                xbot_visual.web.element.hover(browser=web_page, element=首页_统计时间文本_定位后, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 203, "鼠标悬停在元素上(web)"))
                统计时间文本信息 = xbot_visual.web.element.get_details(browser=web_page, element=首页_统计时间文本_定位后, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("首页-运营视窗整体看板数据获取", 204, "获取元素信息(web)"))
                页面统计时间 = xbot_visual.text.extract_content_from_text(text=统计时间文本信息, extract_way="custom", regular_pattern="统计时间 (.*)", just_get_first=True, ignore_case=False, _block=("首页-运营视窗整体看板数据获取", 205, "从文本中提取内容"))
                # text.split_text_to_list
                # programing.variable
                xbot_visual.programing.log(type="info", text="当前页面统计时间为 : " + xbot_visual.sh_str(页面统计时间), _block=("首页-运营视窗整体看板数据获取", 208, "打印日志"))
                if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 209, "IF 条件")):
                    _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                        "查询日期": 查询日期,
                        "页面统计时间": 页面统计时间,
                        }, outputs=[
                        "判断结果",
                    ], _block=("首页-运营视窗整体看板数据获取", 210, "调用流程"))
                    if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("首页-运营视窗整体看板数据获取", 211, "IF 条件")):
                        执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                        , _block=("首页-运营视窗整体看板数据获取", 212, "设置变量"))
                        return
                    #endif
                #endif
                #endregion
                #region 数据批量抓取
                # xbot_extensions.activity_fe2a1069.ClickByXpath
                # xbot_extensions.activity_fe2a1069.ClickByXpath
                表格元素 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_select", params={
                    "xpath": "//span[.=\"表格\"]",
                    "name": "表格元素",
                }, _block=("首页-运营视窗整体看板数据获取", 220, "调用模块"))
                for loop_index2 in xbot_visual.workflow.range_iterator(start="0", stop="10", step="1", _block=("首页-运营视窗整体看板数据获取", 221, "For次数循环")):
                    if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=表格元素, _block=("首页-运营视窗整体看板数据获取", 222, "IF 元素可见(web)")):
                        xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                            "web_page": web_page,
                            "xpathSelector": "(//div[@class=\"pro-layout-card-header__action-bar\"]/button)[1]",
                            "获取元素超时": lambda: 5,
                            "执行成功后等待": lambda: 1,
                            "是否模拟人工": True,
                            "按钮": "left",
                            "retry_count": lambda: 1,
                            "refresh": False,
                            "是否为iframe对象": False,
                            }, outputs=[
                        ], _block=("首页-运营视窗整体看板数据获取", 223, "点击Xpath元素"))
                    else:
                        break
                    #endif
                #endloop
                xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                    "web_page": web_page,
                    "xpathSelector": "//span[.=\"表格\"]",
                    "获取元素超时": lambda: 5,
                    "执行成功后等待": lambda: 1,
                    "是否模拟人工": False,
                    "按钮": "left",
                    "retry_count": lambda: 1,
                    "refresh": False,
                    "是否为iframe对象": False,
                    }, outputs=[
                ], _block=("首页-运营视窗整体看板数据获取", 228, "点击Xpath元素"))
                # ---------------获取数据
                result = xbot_visual.programing.variable(value=lambda: []
                , _block=("首页-运营视窗整体看板数据获取", 230, "设置变量"))
                if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 查询日期,"operand2": "日","operator": "in"},{"operand1": 查询日期,"operand2": "周","operator": "in"},{"operand1": 查询日期,"operand2": "月","operator": "in"}], _block=("首页-运营视窗整体看板数据获取", 231, "IF 多条件")):
                    web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=lambda: f'(//span[text()="{查询日期}"])[1]', is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 232, "获取元素对象(web)"))
                    xbot_visual.web.element.click(browser=web_page, element=web_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 233, "点击元素(web)"))
                else:
                    自定义日 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="(//span[text()=\"日\"])[1]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 235, "获取元素对象(web)"))
                    xbot_visual.web.element.hover(browser=web_page, element=自定义日, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 236, "鼠标悬停在元素上(web)"))
                    xbot_visual.process.run(process="xbot_extensions.web_action.select_date", package=__name__, inputs={
                        "web_page": web_page,
                        "date_elem": package.selector("运营视窗整体看板数据获取_日期框"),
                        "date_start": 查询日期,
                        "date_end": "",
                        "simulative": False,
                        }, outputs=[
                    ], _block=("首页-运营视窗整体看板数据获取", 237, "智能日期选择器"))
                #endif
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("首页-运营视窗整体看板数据获取", 239, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("首页-运营视窗整体看板数据获取", 239,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
                表格按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"layout-card-header\")]//span[text()=\"表格\"]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 240, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=web_page, element=表格按钮, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 241, "点击元素(web)"))
                列字段_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"ant-table-fixed-left\"]//tr/td[last()]/div", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 242, "获取相似元素列表(web)"))
                总计字段个数 = len(列字段_数据列表)
                列字段_数据列表_增长率 = xbot_visual.programing.variable(value=lambda: [v + "_增长率" for v in 列字段_数据列表]
                , _block=("首页-运营视窗整体看板数据获取", 243, "设置变量"))
                new_列字段_数据列表 = []
                for x, y in zip(列字段_数据列表, 列字段_数据列表_增长率):
                    new_列字段_数据列表.append(x)
                    new_列字段_数据列表.append(y)
                列字段_数据列表 = new_列字段_数据列表
                日期_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@class=\"numberTableTh\"]/span[1]", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 245, "获取相似元素列表(web)"))
                总计日期个数 = len(日期_数据列表)
                xbot_visual.programing.sleep(random_number=False, seconds="5", start_number="1", stop_number="5", _block=("首页-运营视窗整体看板数据获取", 246, "等待"))
                数据cell_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class='ant-table-body']//tr[contains(@class,'ant-table-row')]/td[@class='']", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 247, "获取相似元素列表(web)"))
                总计指标个数 = len(数据cell_数据列表)
                xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("首页-运营视窗整体看板数据获取", 248, "等待"))
                if xbot_visual.workflow.test(operand1=总计指标个数, operator="!=", operand2=lambda: 总计字段个数 * 总计日期个数, operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 249, "IF 条件")):
                    raise Exception("指标获取异常，请检查相似元素是否正确")
                #endif
                xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {"日期": 日期_数据列表}, _block=("首页-运营视窗整体看板数据获取", 252, "列表插入一项"))
                for idx in xbot_visual.workflow.range_iterator(start="0", stop=lambda: 总计字段个数 - 1, step=lambda: 1, _block=("首页-运营视窗整体看板数据获取", 253, "For次数循环")):
                    start = xbot_visual.programing.variable(value=lambda: idx*总计日期个数
                    , _block=("首页-运营视窗整体看板数据获取", 254, "设置变量"))
                    end = xbot_visual.programing.variable(value=lambda: start+总计日期个数
                    , _block=("首页-运营视窗整体看板数据获取", 255, "设置变量"))
                    # programing.log
                    行数据 = xbot_visual.programing.variable(value=lambda: 数据cell_数据列表[start: end]
                    , _block=("首页-运营视窗整体看板数据获取", 257, "设置变量"))
                    xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {列字段_数据列表[idx * 2]: 行数据}, _block=("首页-运营视窗整体看板数据获取", 258, "列表插入一项"))
                    xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {列字段_数据列表[idx * 2 + 1]: []}, _block=("首页-运营视窗整体看板数据获取", 259, "列表插入一项"))
                #endloop
                xbot_visual.programing.log(type="info", text=result, _block=("首页-运营视窗整体看板数据获取", 261, "打印日志"))
                #endregion
                # --------------输出
                店铺名 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetShopName", package=__name__, inputs={
                    "平台名称": "生意参谋",
                    "web_page": web_page,
                    }, outputs=[
                    "店铺名",
                ], _block=("首页-运营视窗整体看板数据获取", 264, "获取店铺名"))
                数据集 = xbot_visual.programing.variable(value="生意参谋_首页_运营视窗_整体看板"
                , _block=("首页-运营视窗整体看板数据获取", 265, "设置变量"))
                输出文件路径 = xbot_visual.programing.variable(value=xbot_visual.sh_str(保存文件夹) + "\\" + xbot_visual.sh_str(数据集) + "_" + xbot_visual.sh_str(页面统计时间) + ".xlsx"
                , _block=("首页-运营视窗整体看板数据获取", 266, "设置变量"))
                # ---------------保存为文件
                import pandas as pd
                
                v_list = []
                
                pre = []
                for dic in result:
                    for k, v in dic.items():
                        line = [k]
                        if not v:
                            line += pre
                            pre = []
                        else:
                            line += [i.split('\n')[0] for i in v]
                            pre = [i.split('\n')[1] for i in v if len(i.split('\n')) > 1]
                        v_list.append(line)
                print(v_list)
                df = pd.DataFrame(v_list).T
                
                
                df.to_excel(输出文件路径, index=False, header=False, encoding="utf-8")
                待插入字段 = xbot_visual.programing.variable(value=lambda: [["RPA店铺名_页面", "RPA页面统计日期"], [店铺名, 页面统计时间]]
                , _block=("首页-运营视窗整体看板数据获取", 269, "设置变量"))
                输出数据字典 = xbot_visual.programing.variable(value=lambda: {}
                , _block=("首页-运营视窗整体看板数据获取", 270, "设置变量"))
                # programing.log
                if xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="周", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 272, "IF 条件")):
                    import datetime
                    
                    start_date, end_date = 页面统计时间.split(" ~ ")
                    
                    year_start,month_start,day_start = start_date.split("-")
                    
                    year_end,month_end,day_end = end_date.split("-")
                    
                    if year_start != year_end:
                      end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                      end_week = end_date_obj.isocalendar()[1]  # 获取ISO周数
                      页面统计时间 = f"{year_end} 第{end_week}周"
                    else:
                      start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                      start_week = start_date_obj.isocalendar()[1]  # 获取ISO周数
                      页面统计时间 = f"{year_start} 第{start_week}周"
                #endif
                if xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="月", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 275, "IF 条件")):
                    start,end= 页面统计时间.split(" ~ ")
                    
                    year,month,day = start.split("-")
                    
                    页面统计时间 = f"{year}-{month}"
                #endif
                xbot_visual.programing.log(type="info", text=result, _block=("首页-运营视窗整体看板数据获取", 278, "打印日志"))
                xbot_visual.programing.log(type="info", text=页面统计时间, _block=("首页-运营视窗整体看板数据获取", 279, "打印日志"))
                for i in result:
                  if '日期' in i.keys():
                    print(i['日期'])
                    need_index = i['日期'].index(页面统计时间)
                for i in result:
                  key = list(i.keys())[0]
                  if need_index < len(i[key]):
                    输出数据字典[key] = i[key][need_index]
                xbot_visual.list.append_or_insert(lst=数据集对象列表, insert_way="append", index="0", elem=lambda: {"数据集": 数据集, "文件路径": 输出文件路径, "待插入字段": 待插入字段, "去重主键": ["日期", "支付金额", "客单价"], "输出数据字典": 输出数据字典}, _block=("首页-运营视窗整体看板数据获取", 281, "列表插入一项"))
                #endregion
                return
            else:
                #region 新-旧版
                xbot_visual.process.run(process="xbot_extensions.activity_c80700f1.process4", package=__name__, inputs={
                    "web_page": web_page,
                    "日期": 查询日期,
                    }, outputs=[
                ], _block=("首页-运营视窗整体看板数据获取", 286, "通用时间选择-URL跳转"))
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("首页-运营视窗整体看板数据获取", 287, "等待"))
                #region 页面统计时间校验 
                首页_运营视窗标签 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("首页-运营视窗div"), css_selector="", xpath_selector="", is_related_parent=False, parent="", timeout="20", _block=("首页-运营视窗整体看板数据获取", 289, "获取元素对象(web)"))
                首页_统计时间文本_定位后 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("首页-统计时间文本"), css_selector="", xpath_selector="", is_related_parent=True, parent=首页_运营视窗标签, timeout="20", _block=("首页-运营视窗整体看板数据获取", 290, "获取元素对象(web)"))
                xbot_visual.web.element.hover(browser=web_page, element=首页_统计时间文本_定位后, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 291, "鼠标悬停在元素上(web)"))
                统计时间文本信息 = xbot_visual.web.element.get_details(browser=web_page, element=首页_统计时间文本_定位后, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("首页-运营视窗整体看板数据获取", 292, "获取元素信息(web)"))
                页面统计时间 = xbot_visual.text.extract_content_from_text(text=统计时间文本信息, extract_way="custom", regular_pattern="统计时间 (.*)", just_get_first=True, ignore_case=False, _block=("首页-运营视窗整体看板数据获取", 293, "从文本中提取内容"))
                xbot_visual.programing.log(type="info", text="当前页面统计时间为 : " + xbot_visual.sh_str(页面统计时间), _block=("首页-运营视窗整体看板数据获取", 294, "打印日志"))
                if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 295, "IF 条件")):
                    _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                        "查询日期": 查询日期,
                        "页面统计时间": 页面统计时间,
                        }, outputs=[
                        "判断结果",
                    ], _block=("首页-运营视窗整体看板数据获取", 296, "调用流程"))
                    if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("首页-运营视窗整体看板数据获取", 297, "IF 条件")):
                        执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                        , _block=("首页-运营视窗整体看板数据获取", 298, "设置变量"))
                        return
                    #endif
                #endif
                #endregion
                #region 数据批量抓取
                表格元素 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_select", params={
                    "xpath": "(//*[text()=\"表格\"])[1]",
                    "name": "表格元素",
                }, _block=("首页-运营视窗整体看板数据获取", 304, "调用模块"))
                for loop_index2 in xbot_visual.workflow.range_iterator(start="0", stop="10", step="1", _block=("首页-运营视窗整体看板数据获取", 305, "For次数循环")):
                    if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=表格元素, _block=("首页-运营视窗整体看板数据获取", 306, "IF 元素可见(web)")):
                        xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                            "web_page": web_page,
                            "xpathSelector": "//li/a[text()=\"整体\"]",
                            "获取元素超时": lambda: 5,
                            "执行成功后等待": lambda: 1,
                            "是否模拟人工": False,
                            "按钮": "left",
                            "retry_count": lambda: 1,
                            "refresh": False,
                            "是否为iframe对象": False,
                            }, outputs=[
                        ], _block=("首页-运营视窗整体看板数据获取", 307, "点击Xpath元素"))
                    else:
                        break
                    #endif
                #endloop
                xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                    "web_page": web_page,
                    "xpathSelector": "(//*[text()=\"表格\"])[1]",
                    "获取元素超时": lambda: 5,
                    "执行成功后等待": lambda: 1,
                    "是否模拟人工": False,
                    "按钮": "left",
                    "retry_count": lambda: 1,
                    "refresh": False,
                    "是否为iframe对象": False,
                    }, outputs=[
                ], _block=("首页-运营视窗整体看板数据获取", 312, "点击Xpath元素"))
                # ---------------获取数据
                result = xbot_visual.programing.variable(value=lambda: []
                , _block=("首页-运营视窗整体看板数据获取", 314, "设置变量"))
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("首页-运营视窗整体看板数据获取", 315, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("首页-运营视窗整体看板数据获取", 315,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
                表格按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"layout-card-header\")]//span[text()=\"表格\"]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 316, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=web_page, element=表格按钮, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 317, "点击元素(web)"))
                列字段_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"ant-table-fixed-left\"]//tr/td[last()]/div", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 318, "获取相似元素列表(web)"))
                总计字段个数 = len(列字段_数据列表)
                temp_列字段_数据列表 = []
                temp_列字段_数据列表 = [v + "_增长率" for v in 列字段_数据列表]
                
                new_列字段_数据列表 = []
                for x, y in zip(列字段_数据列表, temp_列字段_数据列表):
                    new_列字段_数据列表.append(x)
                    new_列字段_数据列表.append(y)
                
                列字段_数据列表 = new_列字段_数据列表
                日期_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@class=\"numberTableTh\"]/span[1]", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 320, "获取相似元素列表(web)"))
                总计日期个数 = len(日期_数据列表)
                数据cell_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@id=\"sycm-home-operator-window-core-index\"]//div[@class='ant-table-body']//tr[contains(@class,'ant-table-row')]/td[@class='']", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 321, "获取相似元素列表(web)"))
                总计指标个数 = len(数据cell_数据列表)
                if xbot_visual.workflow.test(operand1=总计指标个数, operator="!=", operand2=lambda: 总计字段个数 * 总计日期个数, operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 322, "IF 条件")):
                    raise Exception("指标获取异常，请检查相似元素是否正确")
                #endif
                xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {"日期": 日期_数据列表}, _block=("首页-运营视窗整体看板数据获取", 325, "列表插入一项"))
                for idx in xbot_visual.workflow.range_iterator(start="0", stop=lambda: 总计字段个数 - 1, step=lambda: 1, _block=("首页-运营视窗整体看板数据获取", 326, "For次数循环")):
                    start = xbot_visual.programing.variable(value=lambda: idx*总计日期个数
                    , _block=("首页-运营视窗整体看板数据获取", 327, "设置变量"))
                    end = xbot_visual.programing.variable(value=lambda: start+总计日期个数
                    , _block=("首页-运营视窗整体看板数据获取", 328, "设置变量"))
                    # programing.log
                    行数据 = xbot_visual.programing.variable(value=lambda: 数据cell_数据列表[start: end]
                    , _block=("首页-运营视窗整体看板数据获取", 330, "设置变量"))
                    xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {列字段_数据列表[idx * 2]: 行数据}, _block=("首页-运营视窗整体看板数据获取", 331, "列表插入一项"))
                    xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {列字段_数据列表[idx * 2 + 1]: []}, _block=("首页-运营视窗整体看板数据获取", 332, "列表插入一项"))
                #endloop
                # programing.log
                #endregion
                # --------------输出
                店铺名 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetShopName", package=__name__, inputs={
                    "平台名称": "生意参谋",
                    "web_page": web_page,
                    }, outputs=[
                    "店铺名",
                ], _block=("首页-运营视窗整体看板数据获取", 337, "获取店铺名"))
                数据集 = xbot_visual.programing.variable(value="生意参谋_首页_运营视窗_整体看板"
                , _block=("首页-运营视窗整体看板数据获取", 338, "设置变量"))
                输出文件路径 = xbot_visual.programing.variable(value=xbot_visual.sh_str(保存文件夹) + "\\" + xbot_visual.sh_str(数据集) + "_" + xbot_visual.sh_str(页面统计时间) + ".xlsx"
                , _block=("首页-运营视窗整体看板数据获取", 339, "设置变量"))
                # ---------------保存为文件
                import pandas as pd
                
                v_list = []
                
                pre = []
                for dic in result:
                    for k, v in dic.items():
                        line = [k]
                        if not v:
                            line += pre
                            pre = []
                        else:
                            line += [i.split('\n')[0] for i in v]
                            pre = [i.split('\n')[1] for i in v if len(i.split('\n')) > 1]
                        v_list.append(line)
                print(v_list)
                df = pd.DataFrame(v_list).T
                
                
                df.to_excel(输出文件路径, index=False, header=False, encoding="utf-8")
                待插入字段 = xbot_visual.programing.variable(value=lambda: [["RPA店铺名_页面", "RPA页面统计日期"], [店铺名, 页面统计时间]]
                , _block=("首页-运营视窗整体看板数据获取", 342, "设置变量"))
                输出数据字典 = xbot_visual.programing.variable(value=lambda: {}
                , _block=("首页-运营视窗整体看板数据获取", 343, "设置变量"))
                # programing.log
                if xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="周", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 345, "IF 条件")):
                    import datetime
                    
                    start_date, end_date = 页面统计时间.split(" ~ ")
                    
                    year_start,month_start,day_start = start_date.split("-")
                    
                    year_end,month_end,day_end = end_date.split("-")
                    
                    if year_start != year_end:
                      end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                      end_week = end_date_obj.isocalendar()[1]  # 获取ISO周数
                      页面统计时间 = f"{year_end} 第{end_week}周"
                    else:
                      start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                      start_week = start_date_obj.isocalendar()[1]  # 获取ISO周数
                      页面统计时间 = f"{year_start} 第{start_week}周"
                #endif
                if xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="月", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 348, "IF 条件")):
                    start,end= 页面统计时间.split(" ~ ")
                    
                    year,month,day = start.split("-")
                    
                    页面统计时间 = f"{year}-{month}"
                #endif
                xbot_visual.programing.log(type="info", text=result, _block=("首页-运营视窗整体看板数据获取", 351, "打印日志"))
                xbot_visual.programing.log(type="info", text=页面统计时间, _block=("首页-运营视窗整体看板数据获取", 352, "打印日志"))
                for i in result:
                  if '日期' in i.keys():
                    print(i['日期'])
                    need_index = i['日期'].index(页面统计时间)
                for i in result:
                  key = list(i.keys())[0]
                  if need_index < len(i[key]):
                    输出数据字典[key] = i[key][need_index]
                xbot_visual.list.append_or_insert(lst=数据集对象列表, insert_way="append", index="0", elem=lambda: {"数据集": 数据集, "文件路径": 输出文件路径, "待插入字段": 待插入字段, "去重主键": ["日期", "支付金额", "客单价"], "输出数据字典": 输出数据字典}, _block=("首页-运营视窗整体看板数据获取", 354, "列表插入一项"))
                #endregion
                return
            #endif
        else:
            # 切换按钮和体验新旧版的版本
            #region 啥都没有版本
            #region 数据批量抓取
            xbot_visual.win32.move_mouse(point_x="656", point_y="298", relative_to="screen", move_speed="middle", delay_after="2", _block=("首页-运营视窗整体看板数据获取", 362, "移动鼠标"))
            try:
                xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                    "web_page": web_page,
                    "xpathSelector": "(//div[@class=\"pro-layout-card-header__action-bar\"]/button)[1]",
                    "获取元素超时": lambda: 5,
                    "执行成功后等待": lambda: 1,
                    "是否模拟人工": True,
                    "按钮": "left",
                    "retry_count": lambda: 1,
                    "refresh": False,
                    "是否为iframe对象": False,
                    }, outputs=[
                ], _block=("首页-运营视窗整体看板数据获取", 363, "点击Xpath元素"))
            except Exception as e:
                pass
            表格元素 = xbot_visual.process.invoke_module(module="utils", package=__name__, function="get_select", params={
                "xpath": "//span[.=\"表格\"]",
                "name": "表格元素",
            }, _block=("首页-运营视窗整体看板数据获取", 364, "调用模块"))
            for loop_index2 in xbot_visual.workflow.range_iterator(start="0", stop="10", step="1", _block=("首页-运营视窗整体看板数据获取", 365, "For次数循环")):
                if xbot_visual.web.browser.element_display(browser=web_page, content_type="undisplay", selector=表格元素, _block=("首页-运营视窗整体看板数据获取", 366, "IF 元素可见(web)")):
                    for _xbot_retry_time in range(4):
                        try:
                            xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                                "web_page": web_page,
                                "xpathSelector": "(//div[@class=\"pro-layout-card-header__action-bar\"]/button)[1]",
                                "获取元素超时": lambda: 5,
                                "执行成功后等待": lambda: 1,
                                "是否模拟人工": True,
                                "按钮": "left",
                                "retry_count": lambda: 1,
                                "refresh": False,
                                "是否为iframe对象": False,
                                }, outputs=[
                            ], _block=("首页-运营视窗整体看板数据获取", 367, "点击Xpath元素"))
                            break
                        except Exception as e:
                            if _xbot_retry_time == 3:
                                raise e
                            else:
                                xbot_visual.programing.log(type='info',text=e,_block=("首页-运营视窗整体看板数据获取", 367,"点击Xpath元素"))
                        time.sleep(2)
                else:
                    break
                #endif
            #endloop
            xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.ClickByXpath", package=__name__, inputs={
                "web_page": web_page,
                "xpathSelector": "//span[.=\"表格\"]",
                "获取元素超时": lambda: 5,
                "执行成功后等待": lambda: 1,
                "是否模拟人工": True,
                "按钮": "left",
                "retry_count": lambda: 1,
                "refresh": False,
                "是否为iframe对象": False,
                }, outputs=[
            ], _block=("首页-运营视窗整体看板数据获取", 372, "点击Xpath元素"))
            # ---------------获取数据
            result = xbot_visual.programing.variable(value=lambda: []
            , _block=("首页-运营视窗整体看板数据获取", 374, "设置变量"))
            if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 查询日期,"operand2": "日","operator": "in"},{"operand1": 查询日期,"operand2": "周","operator": "in"},{"operand1": 查询日期,"operand2": "月","operator": "in"}], _block=("首页-运营视窗整体看板数据获取", 375, "IF 多条件")):
                web_element = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector=lambda: f'(//span[text()="{查询日期}"])[1]', is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 376, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=web_page, element=web_element, simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 377, "点击元素(web)"))
            else:
                自定义日 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="(//span[text()=\"日\"])[1]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 379, "获取元素对象(web)"))
                xbot_visual.web.element.hover(browser=web_page, element=自定义日, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 380, "鼠标悬停在元素上(web)"))
                invoke_result = xbot_visual.process.invoke_module(module="jx_test", package=__name__, function="select_date_in_picker", params={
                    "web_page": web_page,
                    "target_date": 查询日期,
                }, _block=("首页-运营视窗整体看板数据获取", 381, "调用模块"))
                # xbot_extensions.web_action.select_date
            #endif
            #region 页面统计时间校验 
            首页_统计时间文本_定位后 = xbot_visual.web.element.get_element(browser=web_page, select_type="selector", selector=package.selector("视窗_日期校验_4"), css_selector="", xpath_selector="", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 385, "获取元素对象(web)"))
            xbot_visual.web.element.hover(browser=web_page, element=首页_统计时间文本_定位后, simulate=True, delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 386, "鼠标悬停在元素上(web)"))
            统计时间文本信息 = xbot_visual.web.element.get_details(browser=web_page, element=首页_统计时间文本_定位后, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("首页-运营视窗整体看板数据获取", 387, "获取元素信息(web)"))
            页面统计时间 = xbot_visual.text.extract_content_from_text(text=统计时间文本信息, extract_way="custom", regular_pattern="统计时间 (.*)", just_get_first=True, ignore_case=False, _block=("首页-运营视窗整体看板数据获取", 388, "从文本中提取内容"))
            xbot_visual.programing.log(type="info", text="当前页面统计时间为 : " + xbot_visual.sh_str(页面统计时间), _block=("首页-运营视窗整体看板数据获取", 389, "打印日志"))
            if xbot_visual.workflow.test(operand1=开启页面统计时间校验, operator="is true", operand2="", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 390, "IF 条件")):
                _Res = xbot_visual.process.run(process="process46", package=__name__, inputs={
                    "查询日期": 查询日期,
                    "页面统计时间": 页面统计时间,
                    }, outputs=[
                    "判断结果",
                ], _block=("首页-运营视窗整体看板数据获取", 391, "调用流程"))
                if xbot_visual.workflow.test(operand1=_Res.判断结果, operator="in", operand2="异常", operator_options="{\"ignoreCase\":\"False\"}", _block=("首页-运营视窗整体看板数据获取", 392, "IF 条件")):
                    执行状态 = xbot_visual.programing.variable(value=_Res.判断结果
                    , _block=("首页-运营视窗整体看板数据获取", 393, "设置变量"))
                    return
                #endif
            #endif
            #endregion
            for loop_index3 in xbot_visual.workflow.range_iterator(start="0", stop="3", step="1", _block=("首页-运营视窗整体看板数据获取", 398, "For次数循环")):
                _xbot_retry_time = 0
                while _xbot_retry_time <= 3:
                    try:
                        web_page = xbot_visual.web.get(web_type="chrome", mode="activated", value="", use_wildcard=False, silent_running=False, wait_load_completed=True, load_timeout="20", stop_load_if_load_timeout="handleExcept", open_page=False, url=None, _block=("首页-运营视窗整体看板数据获取", 399, "获取已打开的网页对象"))
                        _xbot_retry_time = 5
                    except Exception as e:
                        if _xbot_retry_time == 3:
                            raise e
                        else:
                            xbot_visual.programing.log(type='info',text=e,_block=("首页-运营视窗整体看板数据获取", 399,"获取已打开的网页对象"))
                        _xbot_retry_time += 1
                        time.sleep(3)
                # 切换至表格页面
                表格按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"layout-card-header\")]//span[text()=\"表格\"]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 401, "获取元素对象(web)"))
                xbot_visual.web.element.click(browser=web_page, element=表格按钮, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 402, "点击元素(web)"))
                列字段_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class=\"ant-table-fixed-left\"]//tr/td[last()]/div[@class=\"leading columnTd\"]", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 403, "获取相似元素列表(web)"))
                总计字段个数 = len(列字段_数据列表)
                temp_列字段_数据列表 = []
                temp_列字段_数据列表 = [v + "_增长率" for v in 列字段_数据列表]
                
                new_列字段_数据列表 = []
                for x, y in zip(列字段_数据列表, temp_列字段_数据列表):
                    new_列字段_数据列表.append(x)
                    new_列字段_数据列表.append(y)
                
                列字段_数据列表 = new_列字段_数据列表
                日期_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//*[@class=\"numberTableTh\"]/span[1]", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 405, "获取相似元素列表(web)"))
                总计日期个数 = len(日期_数据列表)
                xbot_visual.programing.sleep(random_number=False, seconds="5", start_number="1", stop_number="5", _block=("首页-运营视窗整体看板数据获取", 406, "等待"))
                数据cell_数据列表 = xbot_visual.web.element.get_all_elements(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[@class='ant-table-body']//tr[contains(@class,'ant-table-row')]/td[@class='']", is_related_parent=False, parent=None, operation="text", absolute_url=False, attribute_name=None, timeout="20", output_with_element_count=True, _block=("首页-运营视窗整体看板数据获取", 407, "获取相似元素列表(web)"))
                总计指标个数 = len(数据cell_数据列表)
                xbot_visual.programing.sleep(random_number=False, seconds="3", start_number="1", stop_number="5", _block=("首页-运营视窗整体看板数据获取", 408, "等待"))
                if xbot_visual.workflow.test(operand1=总计指标个数, operator="!=", operand2=lambda: 总计字段个数 * 总计日期个数, operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 409, "IF 条件")):
                    # programing.raise
                    xbot_visual.programing.log(type="info", text=lambda: f'列字段值为---{列字段_数据列表}', _block=("首页-运营视窗整体看板数据获取", 411, "打印日志"))
                    xbot_visual.programing.log(type="info", text="总计个数为" + xbot_visual.sh_str(总计指标个数) + "，列字段个数为" + xbot_visual.sh_str(总计字段个数) + "，日期个数为" + xbot_visual.sh_str(总计日期个数), _block=("首页-运营视窗整体看板数据获取", 412, "打印日志"))
                else:
                    break
                #endif
                xbot_visual.programing.sleep(random_number=False, seconds="2", start_number="1", stop_number="5", _block=("首页-运营视窗整体看板数据获取", 416, "等待"))
            #endloop
            xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {"日期": 日期_数据列表}, _block=("首页-运营视窗整体看板数据获取", 418, "列表插入一项"))
            for idx in xbot_visual.workflow.range_iterator(start="0", stop=lambda: 总计字段个数 - 1, step=lambda: 1, _block=("首页-运营视窗整体看板数据获取", 419, "For次数循环")):
                start = xbot_visual.programing.variable(value=lambda: idx*总计日期个数
                , _block=("首页-运营视窗整体看板数据获取", 420, "设置变量"))
                end = xbot_visual.programing.variable(value=lambda: start+总计日期个数
                , _block=("首页-运营视窗整体看板数据获取", 421, "设置变量"))
                # programing.log
                行数据 = xbot_visual.programing.variable(value=lambda: 数据cell_数据列表[start: end]
                , _block=("首页-运营视窗整体看板数据获取", 423, "设置变量"))
                xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {列字段_数据列表[idx * 2]: 行数据}, _block=("首页-运营视窗整体看板数据获取", 424, "列表插入一项"))
                xbot_visual.list.append_or_insert(lst=result, insert_way="append", index="0", elem=lambda: {列字段_数据列表[idx * 2 + 1]: []}, _block=("首页-运营视窗整体看板数据获取", 425, "列表插入一项"))
                # list.append_or_insert
            #endloop
            xbot_visual.programing.log(type="info", text=result, _block=("首页-运营视窗整体看板数据获取", 428, "打印日志"))
            #endregion
            # --------------输出
            店铺名 = xbot_visual.process.run(process="xbot_extensions.activity_fe2a1069.GetShopName", package=__name__, inputs={
                "平台名称": "生意参谋",
                "web_page": web_page,
                }, outputs=[
                "店铺名",
            ], _block=("首页-运营视窗整体看板数据获取", 431, "获取店铺名"))
            数据集 = xbot_visual.programing.variable(value="生意参谋_首页_运营视窗_整体看板"
            , _block=("首页-运营视窗整体看板数据获取", 432, "设置变量"))
            输出文件路径 = xbot_visual.programing.variable(value=xbot_visual.sh_str(保存文件夹) + "\\" + xbot_visual.sh_str(数据集) + "_" + xbot_visual.sh_str(页面统计时间) + ".xlsx"
            , _block=("首页-运营视窗整体看板数据获取", 433, "设置变量"))
            # ---------------保存为文件
            import pandas as pd
            
            v_list = []
            
            pre = []
            for dic in result:
                for k, v in dic.items():
                    line = [k]
                    if not v:
                        line += pre
                        pre = []
                    else:
                        line += [i.split('\n')[0] for i in v]
                        pre = [i.split('\n')[1] for i in v if len(i.split('\n')) > 1]
                    v_list.append(line)
            print(v_list)
            df = pd.DataFrame(v_list).T
            
            
            df.to_excel(输出文件路径, index=False, header=False, encoding="utf-8")
            待插入字段 = xbot_visual.programing.variable(value=lambda: [["RPA店铺名_页面", "RPA页面统计日期"], [店铺名, 页面统计时间]]
            , _block=("首页-运营视窗整体看板数据获取", 436, "设置变量"))
            输出数据字典 = xbot_visual.programing.variable(value=lambda: {}
            , _block=("首页-运营视窗整体看板数据获取", 437, "设置变量"))
            # programing.log
            if xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="周", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 439, "IF 条件")):
                import datetime
                
                start_date, end_date = 页面统计时间.split(" ~ ")
                
                year_start,month_start,day_start = start_date.split("-")
                
                year_end,month_end,day_end = end_date.split("-")
                
                if year_start != year_end:
                  end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                  end_week = end_date_obj.isocalendar()[1]  # 获取ISO周数
                  页面统计时间 = f"{year_end} 第{end_week}周"
                else:
                  start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                  start_week = start_date_obj.isocalendar()[1]  # 获取ISO周数
                  页面统计时间 = f"{year_start} 第{start_week}周"
            #endif
            if xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="月", operator_options="{}", _block=("首页-运营视窗整体看板数据获取", 442, "IF 条件")):
                start,end= 页面统计时间.split(" ~ ")
                
                year,month,day = start.split("-")
                
                页面统计时间 = f"{year}-{month}"
            #endif
            xbot_visual.programing.log(type="info", text=result, _block=("首页-运营视窗整体看板数据获取", 445, "打印日志"))
            xbot_visual.programing.log(type="info", text=页面统计时间, _block=("首页-运营视窗整体看板数据获取", 446, "打印日志"))
            for i in result:
              if '日期' in i.keys():
                print(i['日期'])
                need_index = i['日期'].index(页面统计时间)
            for i in result:
              key = list(i.keys())[0]
              if need_index < len(i[key]):
                输出数据字典[key] = i[key][need_index]
            xbot_visual.list.append_or_insert(lst=数据集对象列表, insert_way="append", index="0", elem=lambda: {"数据集": 数据集, "文件路径": 输出文件路径, "待插入字段": 待插入字段, "去重主键": ["日期", "支付金额", "客单价"], "输出数据字典": 输出数据字典}, _block=("首页-运营视窗整体看板数据获取", 448, "列表插入一项"))
            #endregion
        #endif
        表格按钮 = xbot_visual.web.element.get_element(browser=web_page, select_type="xpath_selector", selector=None, css_selector="", xpath_selector="//div[contains(@class, \"layout-card-header\")]//span[text()=\"表格\"]", is_related_parent=False, parent=None, timeout="20", _block=("首页-运营视窗整体看板数据获取", 451, "获取元素对象(web)"))
        xbot_visual.web.element.click(browser=web_page, element=表格按钮, simulate=False, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("首页-运营视窗整体看板数据获取", 452, "点击元素(web)"))
    finally:
        args["输出文件路径"] = 输出文件路径
        args["执行状态"] = 执行状态
        args["数据集对象列表"] = 数据集对象列表
