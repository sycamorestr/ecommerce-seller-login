# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .utils_uia import  Version, get_version
from .ziniao_v6_uia import ZiNiao
from .ziniao_v5_uia import SuperBrowser


def open_store(store_name, match_type, *, privacy=False, is_open="点击", timeout=20):
    if get_version() == Version.V5:
        sb = SuperBrowser()
        return sb.open_store(store_name, privacy=privacy, match_type=match_type, is_open=is_open, timeout=timeout)
    else:
        ziniao = ZiNiao()
        return ziniao.open_store(store_name, privacy=privacy, match_type=match_type, is_open=is_open, timeout=timeout)

def main(args):
    open_store('美国亚马逊', '相等')
