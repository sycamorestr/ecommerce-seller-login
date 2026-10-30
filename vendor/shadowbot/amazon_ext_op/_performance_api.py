# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

from ._voice_customer_core import VoiceCustomerHandler



def get_voice_customer_data(web_page, site_name, asin_list, ret_type,time_days):
    """获取买家之声数据"""
    voice_customer_handler = VoiceCustomerHandler(web_page)
    return voice_customer_handler.run(site_name, asin_list, ret_type,time_days)




def main(args):
    print("CUSTOMER_RETURNS".lower())
    pass
