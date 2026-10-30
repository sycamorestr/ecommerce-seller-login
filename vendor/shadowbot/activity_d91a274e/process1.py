import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    data = {}
    if args is None:
        报表类型 = ""
        转化周期 = ""
        日期 = ""
        web_page = None
    else:
        报表类型 = args.get("报表类型", "")
        转化周期 = args.get("转化周期", "")
        日期 = args.get("日期", "")
        web_page = args.get("web_page", None)
    try:
        #region 参数设定
        #region 参数设定
        报表类型_url_dict = xbot_visual.programing.variable(value=lambda: {'账户报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/index','计划报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/campaign/index','单元报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/adgroup/index','关键词报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/keyword/index','人群报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/crowd/index','创意报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/creative/index','权益报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/coupon/index','地域报表':'https://subway.simba.taobao.com/index.jsp#!/report/bpreport/area/index'}
        , _block=("A1 直通车", 3, "设置变量"))
        #endregion
        if xbot_visual.workflow.test(operand1=lambda: 报表类型_url_dict.keys(), operator="not in", operand2=报表类型, operator_options="{\"ignoreCase\":\"False\"}", _block=("A1 直通车", 5, "IF 条件")):
            raise Exception("当前版本指令仅支持以下报表类型中的一种报表类型【'账户报表','计划报表','单元报表','关键词报表','人群报表','创意报表','权益报表','地域报表'】")
            return
        #endif
        package.variables['table_type'] = xbot_visual.programing.variable(value=报表类型
        , _block=("A1 直通车", 9, "设置变量"))
        package.variables['select_time'] = xbot_visual.programing.variable(value=日期
        , _block=("A1 直通车", 10, "设置变量"))
        package.variables['conversion_cycle'] = xbot_visual.programing.variable(value=转化周期
        , _block=("A1 直通车", 11, "设置变量"))
        #endregion
        #region 网页操作
        xbot_visual.web.browser.navigate(browser=web_page, mode="url", url=lambda: 报表类型_url_dict.get(报表类型), ignore_cache=False, load_timeout="20", _block=("A1 直通车", 14, "跳转至新网址"))
        #endregion
        #region 周期选择
        xbot_visual.web.element.click(browser=web_page, element=package.selector("阿里妈妈_直通车_店铺基础报表_转化周期"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A1 直通车", 17, "点击元素(web)"))
        xbot_visual.web.element.click(browser=web_page, element=package.selector("阿里妈妈_直通车_店铺基础报表_转化周期选择"), simulate=True, move_mouse=False, clicks="click", button="left", keys="null", delay_after="1", anchor_type="center", sudoku_part="MiddleCenter", offset_x="0", offset_y="0", timeout="20", _block=("A1 直通车", 18, "点击元素(web)"))
        #endregion
        #region 时间选择
        xbot_visual.process.run(process="xbot_extensions.activity_d65f9fd7.process3", package=__name__, inputs={
            "日期": 日期,
            "web_page": web_page,
            }, outputs=[
        ], _block=("A1 直通车", 21, "直通车汇总数据日期选择"))
        #endregion
        #region 数据获取
        for web_loop_element in xbot_visual.web.element.iter_all_elements(browser=web_page, selector=package.selector("天猫直通车_报表_数据汇总_数据字段相似元素组"), operation="element", absolute_url=False, attribute_name=None, timeout="20", loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("A1 直通车", 24, "循环相似元素(web)")):
            字段名 = xbot_visual.web.element.get_details(browser=web_page, element=web_loop_element, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("A1 直通车", 25, "获取元素信息(web)"))
            web_element_result = xbot_visual.web.element.get_associated_elements(browser=web_page, element=web_loop_element, associated_kind="parent", child_access_kind="index", child_index="0", sibling_direction="next", timeout="20", _block=("A1 直通车", 26, "获取关联元素(web)"))
            web_element_next = xbot_visual.web.element.get_associated_elements(browser=web_page, element=web_element_result, associated_kind="sibling", child_access_kind="index", child_index="0", sibling_direction="next", timeout="20", _block=("A1 直通车", 27, "获取关联元素(web)"))
            数据 = xbot_visual.web.element.get_details(browser=web_page, element=web_element_next, operation="text", absolute_url=False, attribute_name=None, relative_to="screen", to96dpi=True, timeout="20", _block=("A1 直通车", 28, "获取元素信息(web)"))
            字段名 = xbot_visual.programing.variable(value=lambda: 字段名 if '' not in 字段名 else 字段名.replace('','')
            , _block=("A1 直通车", 29, "设置变量"))
            数据 = xbot_visual.programing.variable(value=lambda: 数据 if ',' not in 数据 else 数据.replace(',','')
            , _block=("A1 直通车", 30, "设置变量"))
            xbot_visual.dictionary.set(dict=data, key=字段名, value=数据, _block=("A1 直通车", 31, "设置键值对"))
        #endloop
        #endregion
    finally:
        args["data"] = data
