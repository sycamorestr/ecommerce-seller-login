import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    勾选日期 = ""
    if args is None:
        日期范围或快捷日期 = ""
        quick_select_map = {}
    else:
        日期范围或快捷日期 = args.get("日期范围或快捷日期", "")
        quick_select_map = args.get("quick_select_map", {})
    try:
        # -------检查是否为快捷日期，并对勾选范围校验
        # programing.snippet
        if xbot_visual.workflow.test(operand1=日期范围或快捷日期, operator="in", operand2="快捷日期", operator_options="{\"ignoreCase\":\"False\"}", _block=("快捷日期转换", 3, "IF 条件")):
            勾选天数 = xbot_visual.text.extract_content_from_text(text=日期范围或快捷日期, extract_way="number", regular_pattern="([\\-\\+]?\\d+(\\.\\d+)?)", just_get_first=True, ignore_case=False, _block=("快捷日期转换", 4, "从文本中提取内容"))
            勾选天数 = int(勾选天数)
            if xbot_visual.workflow.test(operand1=lambda: quick_select_map.keys(), operator="not in", operand2=勾选天数, operator_options="{\"ignoreCase\":\"False\"}", _block=("快捷日期转换", 6, "IF 条件")):
                raise Exception("快捷日期可选范围异常，不支持选择：" + xbot_visual.sh_str(日期范围或快捷日期))
            #endif
            勾选日期 = quick_select_map.get(勾选天数)
        else:
            # -------正常的日期区间字符串检查
            if xbot_visual.workflow.multiconditional_judgment(relation="or", conditionals=[{"operand1": 日期范围或快捷日期,"operand2": "~","operator": "not in"},{"operand1": lambda: len(日期范围或快捷日期),"operand2": lambda: 21,"operator": "!="}], _block=("快捷日期转换", 12, "IF 多条件")):
                raise Exception("不合理的日期范围字符串，请使用~分隔开始日期，结束日期。例如 2023-01-01~2023-02-01")
            #endif
            勾选日期 = 日期范围或快捷日期
        #endif
    finally:
        args["勾选日期"] = 勾选日期
