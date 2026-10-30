# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from datetime import datetime


def check_format(date_string, foramat_string):
    """
    日期字符串转换为datetime，顺便检验格式是否正确
    """
    try:
        return datetime.strptime(date_string, foramat_string)
    except:
        raise Exception(f"日期校验异常： 日期【{date_string}】不符合格式【{foramat_string}】")


def check_date(start_, end_, format_str):
    """
    检查日期是否格式正确，大小正确
    """
    
    start_date = check_format(start_, format_str)
    end_date = check_format(end_, format_str)

    if start_date > end_date:
        raise Exception(f"日期检验异常：开始日期不能大于结束日期。 参数输入开始日期【{start_}】结束日期【{end_}】")



def main(args):
    """
    检查日期是否格式正确，大小正确
    """


    start_ = args["开始日期"]
    end_ = args["结束日期"]
    format_str = args["日期格式"]

    # 测试用例
    # start_ = "2023-01-01"
    # end_ = "2023-01-01"
    # format_str = "%Y-%m-%d"


    check_date(start_, end_, format_str)
