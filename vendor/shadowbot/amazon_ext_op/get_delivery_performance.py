# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot  
import re  
from xbot import print, sleep  
from xbot import logging  
from xbot.selector import Selector  
from xbot.web import WebBrowser, WebElement  
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language



class Xpath:
    NavigateMenu = '//*[@data-test-tag="nav-button-container"]'
    PerformanceMenu = '//*[@data-menu-id="performance"]'
    PerformanceItem = '(//*[@class="flyout-menu"])[10]//span'
    DistributionDetail = "//*[@id='shipping-details-section']/a"
    DistributionSpan = '//*[@id="tabs-titles"]//span'
    
    # --- Tab 定义 ---
    LateRateTab = '(//*[@id="tabs-titles"]//div[contains(@class, "sp-tab")])[1]'
    CancelRateTab = '(//*[@id="tabs-titles"]//div[contains(@class, "sp-tab")])[2]'
    TrackingRateTab = '(//*[@id="tabs-titles"]//div[contains(@class, "sp-tab")])[3]'
    DeliveryRateTab = '(//*[@id="tabs-titles"]//div[contains(@class, "sp-tab")])[4]'
    
    # --- 标题定义 (通用) ---
    LateRateSpan = '//h2[@id="late-shipment-target-heading"]'
    CancelRateSpan = '//h2[@id="pre-fulfillment-cancel-rate-target-heading"]'
    TrackingRateSpan = '//h2[@id="valid-tracking-target-heading"]'
    DeliveryRateSpan = '//h2[@id="on-time-delivery-target-heading"]'
    
    # --- 数值定义 ---
    LateRateValue = '//*[@id="lsr-metrics-for-time-window-0"]//span[contains(@class,"late-shipment-metric")]'
    LateRateValue30 = '//div[@id="lsr-metrics-for-time-window-1"]//span[contains(@class, "late-shipment-metric")]'
    CancelRateValue = "(//*[@id='pre-fulfillment-cancellation-summary-slot']//span[contains(@class, 'pre-fulfillment-cancel-rate-metric')])[1]"
    TrackingRateValue = "//*[@class='a-section']//span[contains(@class, 'valid-tracking-metric')]"
    DeliveryRateValue= "//*[@id='otd-metrics-for-time-window-0']//span[contains(@class, 'on-time-delivery-metric')]"
    
    # --- 目标定义 ---
    LateRateGoal = '//*[@class="a-section"]//span[@id="lsr-target-time-window-0"]'
    CancelRateGoal = '//*[@class="a-section"]//span[@id="cr-target-time-window-0"]'
    TrackingRateGoal = '//*[@class="a-section"]//span[@id="vtr-target-time-window-0"]'
    DeliveryRateGoal= '//*[@class="a-section"]//span[@id="otd-target-time-window-0"]'
    
    DownloadButton = "//input[@class='a-button-input' and @type='submit']"
    DeliveryTitle = "//h1[@id='product-detail-heading']"

def gen_selector(xpath):
    xpaths = xpath.split(">>")
    data = {
        "id": "xbot-xpath",
        "name": "动态元素",
        "type": "simple",
        "xpath": {"enable": "true", "segments": xpaths},
    }
    selector = Selector(data)
    return selector

def to_reports_page_if_need(web_page: WebBrowser, url: str):
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(url + "/"):
        return
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)
    if not web_page.wait_appear(gen_selector(Xpath.DeliveryTitle), timeout=30):
        raise Exception(f"进入配送绩效页面失败，未找到配送绩效标题： {Xpath.DeliveryTitle}")

# --- 核心改进：通用数值提取与比较逻辑 ---

def parse_percentage(text: str):
    """提取百分比数值，支持 '4%' 或 '4.5%'，如果提取不到返回 None"""
    if not text or "N/A" in text or "不适用" in text:
        return None
    match = re.search(r'(\d+(?:\.\d+)?)', text) # 只提取数字部分
    if match:
        return float(match.group(1))
    return None

def parse_target_info(text: str):
    """
    解析目标文本，返回 (方向, 目标值)
    支持中文: "目标：低于 4%", "目标：高于 95%"
    支持英文: "Target: under 4%", "Target: over 95%"
    """
    # 1. 提取目标数值
    target_value = parse_percentage(text)
    if target_value is None:
        return None, None # 无法解析目标

    # 2. 判断方向 (低于/高于)
    # 默认方向
    direction = 'unknown' 
    
    # 转换为小写处理
    text_lower = text.lower()
    
    # 关键词库
    keywords_below = ['低于', 'under', 'below', 'less than', '<']
    keywords_above = ['高于', '超过', 'over', 'above', 'greater than', 'more than', '>']
    
    for kw in keywords_below:
        if kw in text_lower:
            direction = 'below'
            break
            
    if direction == 'unknown':
        for kw in keywords_above:
            if kw in text_lower:
                direction = 'above'
                break
                
    return direction, target_value

def is_status(current_text: str, goal_text: str):
    """
    判断当前值是否符合目标
    """
    # 1. 解析当前值
    current_val = parse_percentage(current_text)
    
    # 2. 解析目标值和方向
    direction, goal_val = parse_target_info(goal_text)
    
    # 3. 异常情况处理
    if current_val is None:
        return '' # 当前值不适用 
        
    if goal_val is None or direction == 'unknown':
        # 如果无法解析目标，但有当前值，通常默认视为正常，或者标记为未知
        print(f"警告：无法解析目标文本 '{goal_text}'")
        return '未知'

    # 4. 比较逻辑
    status = '异常'
    
    if direction == 'below':
        # 目标是“低于 X%”，例如 迟发率 < 4%
        if current_val < goal_val:
            status = '正常'
    elif direction == 'above':
        # 目标是“高于 X%”，例如 有效追踪率 > 95%
        if current_val >= goal_val: # 通常包含等于
            status = '正常'
            
    return status

def get_target_text_safe(web_page, xpath):
    """安全获取目标文本，去除 'Target:' 或 '目标:' 前缀"""
    try:
        raw_text = web_page.find_by_xpath(xpath).get_text().strip()
        # 这里的正则兼容中英文冒号，并且只取冒号后面的部分
        match = re.search(r"[:：]\s*(.*)", raw_text)
        if match:
            return match.group(1)
        return raw_text
    except Exception:
        return ""

def get_distribution_performance(web_page: WebBrowser):
    # 检查并获取配送绩效数据
    
    # --- 1. 迟发率 (LSR) ---
    web_page.find_by_xpath(Xpath.LateRateTab).click()
    sleep(0.5)
    lsr_name = web_page.find_by_xpath(Xpath.LateRateSpan).get_text()
    lsr_value = web_page.find_by_xpath(Xpath.LateRateValue).get_text()
    lsr_value30 = web_page.find_by_xpath(Xpath.LateRateValue30).get_text()
    lsr_target = get_target_text_safe(web_page, Xpath.LateRateGoal)
    
    # --- 2. 预配送取消率 (CR) ---
    web_page.find_by_xpath(Xpath.CancelRateTab).click()
    sleep(0.5)
    cr_name = web_page.find_by_xpath(Xpath.CancelRateSpan).get_text()
    cr_value = web_page.find_by_xpath(Xpath.CancelRateValue).get_text()
    cr_target = get_target_text_safe(web_page, Xpath.CancelRateGoal)

    # --- 3. 有效追踪率 (VTR) ---
    web_page.find_by_xpath(Xpath.TrackingRateTab).click()
    sleep(0.5)
    vtr_name = web_page.find_by_xpath(Xpath.TrackingRateSpan).get_text()
    vtr_value = web_page.find_by_xpath(Xpath.TrackingRateValue).get_text()
    vtr_target = get_target_text_safe(web_page, Xpath.TrackingRateGoal)

    # --- 4. 准时交货率 (OTDR) ---
    web_page.find_by_xpath(Xpath.DeliveryRateTab).click()
    sleep(0.5)
    otd_name = web_page.find_by_xpath(Xpath.DeliveryRateSpan).get_text()
    otd_value = web_page.find_by_xpath(Xpath.DeliveryRateValue).get_text()
    otd_target = get_target_text_safe(web_page, Xpath.DeliveryRateGoal)

    # --- 组装数据 ---
    distribution_dict = {}
    
    # 注意：这里直接传入原始文本进行解析和比较
    distribution_dict[lsr_name] = {
        "当前数值": lsr_value, 
        "目标": lsr_target, 
        "状态": is_status(lsr_value, lsr_target)
    }
    distribution_dict['30天' + lsr_name] = {
        "当前数值": lsr_value30, 
        "目标": lsr_target, 
        "状态": is_status(lsr_value30, lsr_target)
    }
    distribution_dict[cr_name] = {
        "当前数值": cr_value, 
        "目标": cr_target, 
        "状态": is_status(cr_value, cr_target)
    }
    distribution_dict[vtr_name] = {
        "当前数值": vtr_value, 
        "目标": vtr_target, 
        "状态": is_status(vtr_value, vtr_target)
    }
    distribution_dict[otd_name] = {
        "当前数值": otd_value, 
        "目标": otd_target, 
        "状态": is_status(otd_value, otd_target)
    }
    
    return distribution_dict

def get_data_account_status(web_page: WebBrowser):
    # 获取账号状态数据
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"

    # 进入配送绩效页面
    domain = get_domain(web_page)
    url = f"{domain}/performance/detail/shipping"
    to_reports_page_if_need(web_page, url)

    # 尝试切换语言，但后续逻辑已兼容英文
    switch_language(web_page, 'zh_CN')
 

    # 6.检查并获取配送绩效数据
    distribution_dict = get_distribution_performance(web_page)
    return distribution_dict

def test_check_account_status():
    if "xbot_extensions" in __file__:
        return

    try:
        web_page = xbot.web.get_active(mode="superbrowser")
        result = get_data_account_status(web_page)
        print("最终结果:", result)
    except Exception as e:
        print(f"测试出错: {e}")
    exit()
def main(args):
    # 测试代码入口
    test_check_account_status()

    # 业务代码入口
    web_page = args.get("web_page")
    distribution_dict = get_data_account_status(web_page)
    args["data"] = distribution_dict