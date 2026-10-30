import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time
from xbot import print

def main(args):
    判断结果 = ""
    if args is None:
        查询日期 = ""
        页面统计时间 = ""
    else:
        查询日期 = args.get("查询日期", "")
        页面统计时间 = args.get("页面统计时间", "")
    try:
        if xbot_visual.workflow.test(operand1=查询日期, operator="in", operand2="~", operator_options="{\"ignoreCase\":\"False\"}", _block=("_页面数据统计时间校验", 1, "IF 条件")):
            if xbot_visual.workflow.test(operand1=页面统计时间, operator="!=", operand2=查询日期, operator_options="{}", _block=("_页面数据统计时间校验", 2, "IF 条件")):
                判断结果 = xbot_visual.programing.variable(value="异常, 日期选择未生效, 页面统计时间为 :  " + xbot_visual.sh_str(页面统计时间)
                , _block=("_页面数据统计时间校验", 3, "设置变量"))
                xbot_visual.programing.log(type="info", text=判断结果, _block=("_页面数据统计时间校验", 4, "打印日志"))
                return
            #endif
        elif xbot_visual.workflow.test(operand1=查询日期, operator="in", operand2="-", operator_options="{\"ignoreCase\":\"False\"}", _block=("_页面数据统计时间校验", 7, "Else IF")):
            if xbot_visual.workflow.test(operand1=查询日期, operator="in", operand2="周", operator_options="{\"ignoreCase\":\"False\"}", _block=("_页面数据统计时间校验", 8, "IF 条件")):
                return
            #endif
            if xbot_visual.workflow.test(operand1=页面统计时间, operator="!=", operand2=查询日期, operator_options="{}", _block=("_页面数据统计时间校验", 11, "IF 条件")):
                判断结果 = xbot_visual.programing.variable(value="异常, 日期选择未生效, 页面统计时间为 :  " + xbot_visual.sh_str(页面统计时间)
                , _block=("_页面数据统计时间校验", 12, "设置变量"))
                xbot_visual.programing.log(type="info", text=判断结果, _block=("_页面数据统计时间校验", 13, "打印日志"))
                return
            #endif
        elif xbot_visual.workflow.test(operand1=查询日期, operator="==", operand2="日", operator_options="{}", _block=("_页面数据统计时间校验", 16, "Else IF")):
            当天日期 = xbot_visual.datetime.to_string(datetime=None, format="%Y-%m-%d", _block=("_页面数据统计时间校验", 17, "日期时间转换为文本"))
            _, 目标日期 = xbot_visual.datetime.add(datetime=当天日期, timeway="decrease", duration="1", unit="day", output_text=True, _block=("_页面数据统计时间校验", 18, "增加/减少时间"))
            if xbot_visual.workflow.test(operand1=页面统计时间, operator="!=", operand2=目标日期, operator_options="{}", _block=("_页面数据统计时间校验", 19, "IF 条件")):
                判断结果 = xbot_visual.programing.variable(value="异常 , 页面数据未更新  页面统计时间为 :  " + xbot_visual.sh_str(页面统计时间)
                , _block=("_页面数据统计时间校验", 20, "设置变量"))
                xbot_visual.programing.log(type="info", text=判断结果, _block=("_页面数据统计时间校验", 21, "打印日志"))
                return
            #endif
        #endif
    finally:
        args["判断结果"] = 判断结果
