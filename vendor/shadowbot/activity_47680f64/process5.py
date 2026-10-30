import xbot
import xbot_visual
from . import package
from .package import variables as glv
import time

def main(args):
    if args is None:
        传入值 = ""
        可选项列表 = []
        是否多选 = False
        分隔符 = ","
    else:
        传入值 = args.get("传入值", "")
        可选项列表 = args.get("可选项列表", [])
        是否多选 = args.get("是否多选", False)
        分隔符 = args.get("分隔符", ",")
    try:
        # ------做下清洗，清理两边空格
        if isinstance(传入值, str):
            传入值 = 传入值.strip()
        # ------多选参数校验-----
        if xbot_visual.workflow.test(operand1=是否多选, operator="is true", operand2="", operator_options="{}", _block=("入参校验", 4, "IF 条件")):
            传入值_list = [s.strip() for s in 传入值.split(分隔符)]
            for 传入_item in xbot_visual.workflow.list_iterator(list=传入值_list, loop_start_index="0", loop_end_index="-1", output_with_index=False, _block=("入参校验", 6, "ForEach列表循环")):
                if xbot_visual.workflow.test(operand1=可选项列表, operator="not in", operand2=传入_item, operator_options="{\"ignoreCase\":\"False\"}", _block=("入参校验", 7, "IF 条件")):
                    raise Exception("运维异常：参数校验异常，多选参数内不包含【" + xbot_visual.sh_str(传入_item) + "】，全部可选参数为：" + xbot_visual.sh_str(可选项列表))
                #endif
            #endloop
        else:
            # ------单选参数校验-----
            if xbot_visual.workflow.test(operand1=可选项列表, operator="not in", operand2=传入值, operator_options="{\"ignoreCase\":\"False\"}", _block=("入参校验", 13, "IF 条件")):
                raise Exception("运维异常：参数校验异常，单选参数内不包含【" + xbot_visual.sh_str(传入值) + "】，全部可选参数为：" + xbot_visual.sh_str(可选项列表))
            #endif
        #endif
    finally:
        pass
