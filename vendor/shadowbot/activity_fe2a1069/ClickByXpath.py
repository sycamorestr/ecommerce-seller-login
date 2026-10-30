# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot.errors import UIAError
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from xbot_extensions.activity_ea8fd401.iframeElement import main as GetElementAcrossDomains

def test(xpath):
    element = GetElementAcrossDomains({"web_page":None, "xpathSelector": xpath})
    element.click()


def main(args):
    xpath = args.get("xpathSelector")
    time_out = args.get("获取元素超时")
    refresh = args.get("refresh")
    retry_cnt = args.get("retry_count")
    simulative = args.get("是否模拟人工")
    button = args.get("按钮")
    delay_after = args.get("执行成功后等待")
    is_iframe_element = args.get("是否为iframe对象")

    
    browser = args.get("web_page") or web.get_active(mode="chrome")

    # 跨iframe查找
    if is_iframe_element:
        element = GetElementAcrossDomains({"web_page":browser, "xpathSelector": xpath})
    else:

        # 尝试查找元素
        while retry_cnt > 0:
            try:
                list_web_element = browser.find_all_by_xpath(xpath, timeout=time_out)
                element = list_web_element[0]
                break
            except:
                # 查找元素超时
                if refresh:
                    browser.reload()
                retry_cnt -= 1
                print(f"查找元素【{xpath}】超时, 剩余重试次数【{retry_cnt}】")

        if len(list_web_element) != 1:
            raise Exception(f"xpath不正确，找到了{len(list_web_element)}个元素！")
    
    # 点击元素
    element.click(button=button, simulative=simulative, delay_after=delay_after)
    