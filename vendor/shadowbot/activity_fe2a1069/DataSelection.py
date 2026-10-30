# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
import re
import time
from .GetElementInnerText import main as get_element_string

def is_current_month(args, page, target_date, like_person):
    # 查找需要的元素
    # page = web.get_active(mode="chrome")
    last_month = page.find_by_xpath(args.get("上一月_xpath"))
    next_month = page.find_by_xpath(args.get("下一月_xpath"))
    # 判断当前面板是否为目标选择的年月

    # 先获取选择面板的当前年月的文本内容
    current_year_string = get_element_string({"web_page": page, "xpath": args.get("当前年_xpath")})
    current_month_string = get_element_string({"web_page": page, "xpath": args.get("当前月_xpath")})

    # 匹配出当前年月
    # print(f"当前面板年月信息: {current_year_string}; {current_month_string}")
    try:
        dict_={
            "一":1, "二":2, "三":3, "四":4, "五":5, "六":6, "七":7, "八":8, "九":9, "十":10, "十一":11, "十二":12
        }
        current_year = int(re.findall(args.get("年正则"), current_year_string)[0])
        current_month = re.findall(args.get("月正则"), current_month_string)[0]
        current_month = int(dict_.get(current_month,current_month) )

    except Exception as e:
        raise Exception("勾选日期框架：匹配年月信息异常，请检查高级参数【年月正则】是否正确。")

    if current_year < target_date.tm_year:
        next_month.click(simulative=like_person, delay_after=0.5)
    elif current_year > target_date.tm_year:
        last_month.click(simulative=like_person, delay_after=0.5)
    elif current_month < target_date.tm_mon:
        next_month.click(simulative=like_person, delay_after=0.5)
    elif current_month > target_date.tm_mon:
        last_month.click(simulative=like_person, delay_after=0.5)
    else:
        return True


def main(args):
    page = args.get("web_page") or web.get_active(mode="chrome")
    target_date = time.strptime(args.get("日期"), "%Y-%m-%d")
    is_check = args.get("仅切换选择面板")
    like_person = args.get("模拟人工点击", False)

    # 面板切换
    for i in range(20):
        if is_current_month(args, page, target_date, like_person):
            break
    else:
        raise Exception("循环20次仍未找到目标年月")
    
    if is_check:
        return

    # 勾选目标日期
    target_elements = page.find_all_by_xpath(args.get("目标日期_xpath"))
    if len(target_elements) == 1:
        target_elements[0].click(simulative=like_person)
    elif len(target_elements) == 0:
        raise Exception("目标日期xpath 异常，没有找到目标对象")
    else:
        target_elements[target_date.tm_mday-1].click(simulative=like_person)
