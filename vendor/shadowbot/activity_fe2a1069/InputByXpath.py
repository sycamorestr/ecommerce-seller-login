# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
import xbot_visual
import time
from xbot.errors import UIAError
from xbot_extensions.activity_ea8fd401.iframeElement import main as GetElementAcrossDomains


def do_press(key="{ENTER}"):
    """键盘输入事件"""
    xbot_visual.win32.send_keys(keys=key, hardware_driver_input=False, force_ime_eng=False, contains_hotkey=True, send_key_delay="50", delay_after="1", _block=("order", 1, "键盘输入"))


def main(args):
    page = args.get("web_page") or web.get_active(mode="chrome")
    xpath = args.get("xpath")
    text = args.get("输入内容")
    input_type = args.get("输入方式")
    time_out = args.get("等待元素存在")
    press_key = args.get("追加按键")
    is_append = args.get("追加输入")
    delay_after = args.get("操作完成后等待")

    is_iframe = args.get("iframe跨域元素")
    # 获取输入元素
    if is_iframe:
        element = GetElementAcrossDomains({"web_page":page, "xpathSelector": xpath})
    else:
        element = page.find_by_xpath(xpath_selector=xpath, timeout=time_out)

    # 确定是否模拟人工使用对应的方法
    input_func = {
        "剪切板": element.clipboard_input,
        "模拟人工": element.input
    }.get(input_type)

    # 不管怎么样先点一下
    element.click(simulative=False, delay_after=0.5)

    # 输入
    input_func(text, append=is_append, delay_after=delay_after)

    # 追加按键
    if press_key:
        do_press(press_key)
