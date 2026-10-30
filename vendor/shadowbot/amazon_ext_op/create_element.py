# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot import web
from xbot.selector import Selector

def create_selector(*xpath_segments, name='dynamic_selector'):
    """
    一个灵活的函数，接收任意数量的XPath字符串作为参数，
    并将它们组合成一个分段式的Selector对象。

    Args:
        *xpath_segments: 一个或多个XPath字符串。每个字符串代表一级层级路径。
        name (str, optional): 为这个元素在影刀日志中起一个名字。 
                                     Defaults to 'dynamic_selector'.

    Returns:
        一个可供 browser.find() 使用的 Selector 对象。
    
    Raises:
        ValueError: 如果没有提供任何XPath字符串。
    """
    if not xpath_segments:
        raise ValueError("至少需要提供一个XPath字符串片段！")
    # 构建与影刀元素库兼容的data字典
    # 核心：直接将所有传入的字符串参数(*xpath_segments)组合成 'segments' 列表
    data = {
        'id': name,
        'name': name,
        'type': 'simple',
        'framework': 'chromium', 
        'version': '2', 
        'xpath': {
            'enable': 'true',
            'segments': list(xpath_segments)  # 直接使用传入的参数列表
        }
    }
    # 使用data字典实例化并返回Selector对象
    return Selector(data)

def create_selector_shadow(*xpath_segments, name='dynamic_selector'):
    """
    一个灵活的函数，接收任意数量的XPath字符串作为参数，
    并将它们组合成一个分段式的Selector对象。

    Args:
        *xpath_segments: 一个或多个XPath字符串。每个字符串代表一级层级路径。
        name (str, optional): 为这个元素在影刀日志中起一个名字。 
                                     Defaults to 'dynamic_selector'.

    Returns:
        一个可供 browser.find() 使用的 Selector 对象。
    
    Raises:
        ValueError: 如果没有提供任何XPath字符串。
    """
    if not xpath_segments:
        raise ValueError("至少需要提供一个XPath字符串片段！")
    # 构建与影刀元素库兼容的data字典
    # 核心：直接将所有传入的字符串参数(*xpath_segments)组合成 'segments' 列表
    separator = '/xbotShadowRoot'
    
    joined_xpath_string = separator.join(xpath_segments)
    data = {
        'id': name,
        'name': name,
        'type': 'simple',
        'framework': 'chromium', 
        'version': '2', 
        'xpath': {
            'enable': 'true',
            'segments': [joined_xpath_string]  
        }
    }
    # 使用data字典实例化并返回Selector对象
    return Selector(data)

def create_frame(*xpath_segments, name='dynamic_selector'):

    if not xpath_segments:
        raise ValueError("至少需要提供一个XPath字符串片段！")
    # 构建与影刀元素库兼容的data字典
    # 核心：直接将所有传入的字符串参数(*xpath_segments)组合成 'segments' 列表
    data = {
        'id': name,
        'name': name,
        'type': 'simple',
        'xpath': {
            'enable': 'true',
            'segments': list(xpath_segments)  # 直接使用传入的参数列表
        }
    }
    # 使用data字典实例化并返回Selector对象
    return Selector(data)

def main(args):
    browser = xbot.web.get_active(mode='ziniaobrowser')

    # --- 场景1：传入一个str，构建简单元素 ---
    # print("--- 场景1：传入一个参数 ---")
    # submit_button_xpath = '//*[local-name()="kat-filter-bar"]/xbotShadowRoot//*[local-name()="kat-button"][@type="button"]/xbotShadowRoot/button[@type="button"]'
    # selector1 = create_selector(
    #     submit_button_xpath, 
    #     name='提交按钮'
    # )
    # browser.find(selector1).click()
    # print("创建的Selector结构:", selector1)


    # --- 场景2：传入两个str，组合起来 [str1, str2] ---
    print("\n--- 场景2：传入两个参数 ---")
    # StarteDate= '//*[local-name()="kat-date-picker"][@name="startDatePicker"]/xbotShdowRoot'
    # EndDate = '//*[local-name()="kat-input"][@type="text"]'
    StarteDate= '//*[local-name()="kat-checkbox"]/xbotShadowRoot//*[local-name()="kat-label"][contains(@class, "label-text")]/xbotShadowRoot//span[@part="label-text"]'
    # EndDate = '//div[contains(@class,"actions-content")]/kat-button'
    selector2 = create_selector(
        StarteDate,
        # EndDate, 
        name='日期'
    )
    browser.find(selector2).click()
    # browser.find(selector2).input('09/12/2025')
    print("创建的Selector结构:", selector2.value)


    # --- 场景3：传入三个str，再加一个 [str1, str2, str3] ---
    # print("\n--- 场景3：传入三个参数 ---")
    # host_A_xpath = '//*[local-name()="kat-filter-bar"]'
    # host_B_xpath = '/div/div/div/*[local-name()="kat-button"]'
    # target_C_xpath = '/button[@type="button"]'
    # selector3 = create_selector(
    #     host_A_xpath, 
    #     host_B_xpath, 
    #     target_C_xpath, 
    #     name='深层嵌套输入框'
    # )
    # # browser.find(selector3).click()
    # print(browser.find(selector3).get_text())
    # print(package.selector('筛选按钮').value)
    # data={'id': 'name', 
    # 'name': '筛选按钮1', 'type': 'simple', 'framework': 'chromium', 
    # 'version': '2', 
    # 'xpath': {'enable': 'true', 'segments': ['//*[local-name()="kat-filter-bar"]/xbotShadowRoot/div/div/div/*[local-name()="kat-button"]/xbotShadowRoot/button[@type="button"]']}}
    # data1 = Selector(data)
    # browser.find(data1).click()

        