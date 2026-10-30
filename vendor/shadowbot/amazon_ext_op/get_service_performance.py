import xbot  
import re  
from xbot import print, sleep  
from xbot.selector import Selector  
from xbot.web import WebBrowser, WebElement 
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language, login

TRANS_MAP = {
    # 指标名称
    "Order Defect Rate": "订单缺陷率",
    "Invoice Defect Rate": "发票缺陷率",
    "Negative Feedback": "负面反馈",
    "Negative Feedback Rate": "负面反馈",
    "A-to-z Guarantee claims": "亚马逊商城交易保障索赔",
    "Credit Card Chargeback claims": "信用卡拒付索赔",
    "Late Shipment Rate": "迟发率",
    "Pre-fulfillment Cancel Rate": "预配送取消率",
    "Valid Tracking Rate": "有效追踪率",
    "On-Time Delivery Rate": "准时交货率",
    # 配送方
    "Seller": "卖家",
    "Amazon": "亚马逊",
    "Fulfilled by": "订单配送方",
    # 状态
    "Target": "目标",
    "under": "低于",
    "over": "高于",
    "N/A": "不适用",
}

class Xpath:
    # 导航菜单
    NavigateMenu = '//*[@data-test-tag="nav-button-container"]'
    PerformanceMenu = '//*[@data-menu-id="performance"]'
    # 兼容中英文的绩效菜单链接
    PerformanceItem = '(//*[@class="flyout-menu"])[10]//span | //a[contains(@href, "/performance/dashboard")]'
    
    # 账户状况评级
    ConditionRating = '//*[contains(@class, "ahr-status-badge")]'
    ConditionScore = "//*[@class='a-column a-span5 a-spacing-none a-ws-span5 a-span-last a-ws-span-last']/h3"
    
    # 问题列表
    QuestionName = "//*[@id='policies-content-rows-section']//a"
    QuestionNumber = "//*[@id='policies-content-rows-section']//span"
    
    # 详情链接
    ServiceDetail = "//*[@id='customer-satisfaction-details-section']/a"
    
    # Tabs (保持索引，通常位置固定)
    OrderDefectTab = '(//*[@id="tabs-titles"]//span)[1]'
    InvoiceDefectTab = '(//*[@id="tabs-titles"]//span)[3]'
    
    # 订单配送方下拉框 (兼容中英文按钮文本)
    OrderCategory = '//*[@id="odr-target-section"]//span[contains(@class, "a-button-text")]'
    # 下拉选项 (保持索引，通常固定)
    SellerItem = "(//*[@role='listbox']//a)[1]"
    AmazonItem = "(//*[@role='listbox']//a)[2]"
    
    # 订单缺陷率数值
    OrderDefectVal = '//*[@id="odr-giant-metric-percentage"]/span'
    
    # 表格行 (保持索引)
    NegeedbackLine = '(//*[@id="odr-metric-table"]//tr)[2]'
    AmazonDealsLine = '(//*[@id="odr-metric-table"]//tr)[3]'
    CreditCardLine = '(//*[@id="odr-metric-table"]//tr)[4]'
    
    # 目标区域 (使用ID模糊匹配增强稳定性)
    OrderDefectGoal = "//*[@id='odr-summary-target-section']//*[contains(@id, 'odr-target')]"
    
    # 其他指标
    DistributionDetail = "//*[@id='shipping-details-section']/a"
    DistributionSpan = '//*[@id="tabs-titles"]//span'
    LateRateSpan = '(//*[@id="tabs-titles"]//span)[1]'
    CancelRateSpan = '(//*[@id="tabs-titles"]//span)[8]'
    TrackingRateSpan = '(//*[@id="tabs-titles"]//span)[10]'
    DeliveryRateSpan = '(//*[@id="tabs-titles"]//span)[12]'
    DownloadButton = "//input[@class='a-button-input' and @type='submit']"
    ServiceTitle= "//h1[@id='customer-service-heading']"
    
    # 发票缺陷率
    InvoiceDefectValue = '(//*[@id="idr-metric-overview-col"]//span)[1]'
    InvoiceDefectGoal = '(//*[@id="invoice-defect-rate-summary-target-section"]//span)[1]'


def to_reports_page_if_need(web_page: WebBrowser, url: str, site_name: str):
    # 导航逻辑保持不变
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(url + "/"):
        return
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)

    # 进行登录校验
    login(web_page)
    # 进行站点校验
    if site_name:
        if '/account-switcher/default/merchantMarketplace' in web_page.get_url():
            switch_site(web_page, site_name)
    
    # 使用 gen_selector 或直接 xpath 等待
    # 这里为了代码简洁，假设 gen_selector 已定义或直接使用 find
    try:
        if not web_page.wait_appear(Xpath.ServiceTitle, timeout=30): # 简化调用
             pass 
    except:
        pass # 允许部分超时异常

def trans(text: str) -> str:
    """
    通用翻译函数：将英文短语转换为中文
    模糊匹配：如果 text 包含字典里的 key，则替换
    """
    clean_text = text.strip()
    # 1. 精确匹配
    if clean_text in TRANS_MAP:
        return TRANS_MAP[clean_text]
    
    # 2. 包含匹配 (例如 "Negative Feedback Rate" -> "负面反馈")
    for en_key, cn_val in TRANS_MAP.items():
        if en_key in clean_text:
            return cn_val
            
    # 3. 没找到则返回原文
    return clean_text

def match_number(text:str):
    """提取数字，支持百分比"""
    if not text: return 0.0
    if "不适用" in text or "N/A" in text: return 0.0
    
    # 匹配数字，支持小数点
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    if match:
        return float(match.group(1))
    return 0.0

def standardize_goal_str(goal_text: str) -> str:
    """
    将目标字符串标准化为 '目标：低于 X%'
    输入可能是: 'Target: under 1%', '目标：低于 1%', '< 1%'
    """
    # 先清理输入文本，移除可能已存在的"目标："前缀，避免重复
    clean_text = goal_text.strip()
    # 移除可能的中文前缀
    if clean_text.startswith('目标：') or clean_text.startswith('目标:'):
        clean_text = re.sub(r'^目标[：:]\s*', '', clean_text)
    # 移除可能的英文前缀
    if 'Target:' in clean_text or 'target:' in clean_text:
        clean_text = re.sub(r'^[Tt]arget:\s*', '', clean_text)
    
    num = match_number(clean_text)
    # 默认假设是低于，除非有明显的大于关键词
    # 格式化数字：如果是整数则显示整数，否则显示小数
    if num == int(num):
        return f"目标：低于 {int(num)}%"
    else:
        return f"目标：低于 {num}%"

def is_status(current_num_str:str, goal_str:str):
    """
    判断状态
    规则：'不适用'/'N/A' -> 状态为空字符串
    """
    # 1. 处理不适用
    if not current_num_str: return ''
    if any(x in current_num_str for x in ['不适用', 'N/A', '-']):
        return ''
    
    current_num = match_number(current_num_str)
    goal_num = match_number(goal_str)
    
    # 2. 判断方向 (支持英文关键词)
    is_lower_better = True
    if any(x in goal_str.lower() for x in ['高于', 'over', '>', 'exceed']):
        is_lower_better = False
        
    status = '异常'
    if is_lower_better:
        if current_num < goal_num:
            status = '正常'
    else:
        if current_num > goal_num:
            status = '正常'
            
    return status

def process_row_data(raw_text: str):
    """
    核心解析逻辑：
    1. 分离 Label 和 Value
    2. 处理 N/A -> 不适用
    3. 翻译 Label -> 中文
    """
    # 1. 统一处理所有空白字符：将 \n, \t, 多个空格等统一替换为单个空格
    clean_text = re.sub(r'\s+', ' ', raw_text.strip())
    
    # 2. 强制处理不适用
    if '不适用' in clean_text or 'N/A' in clean_text:
        val = "不适用"
        # 移除干扰词以提取 Label
        temp_text = clean_text.replace('不适用', '').replace('N/A', '')
        # 移除可能的 (0) 或 (0.0%) 等括号内容
        temp_text = re.sub(r'\(.*?\)', '', temp_text)
        label_raw = temp_text.strip()
    else:
        # 3. 优先提取百分比格式的数值（如 "0%", "2.04%"）
        # 匹配模式：标签 + 百分比 + 可选的括号数字
        # 例如："负面反馈 0% (0)" 或 "负面反馈0%" 或 "负面反馈 2.04% (1)"
        percent_match = re.search(r'(\d+(?:\.\d+)?%)', clean_text)
        
        if percent_match:
            # 找到百分比数值
            val = percent_match.group(1)
            # 提取百分比之前的部分作为标签
            label_raw = clean_text[:percent_match.start()].strip()
            # 如果标签为空，尝试从整个文本中提取（处理无空格的情况）
            if not label_raw:
                # 处理 "负面反馈0%" 这种情况
                label_match = re.search(r'^(.+?)(\d+(?:\.\d+)?%)', clean_text)
                if label_match:
                    label_raw = label_match.group(1).strip()
        else:
            # 如果没有找到百分比，尝试找最后一个非空白字符块
            match = re.search(r"^(.*?)\s+([^\s]+)$", clean_text)
            if match:
                label_raw = match.group(1).strip()
                val = match.group(2).strip()
            else:
                # 如果都匹配不到，使用默认值
                label_raw = clean_text
                val = "0%"
    
    # 4. 清理标签：移除可能残留的数字、百分比、括号等
    # 移除末尾可能残留的百分比或数字
    label_raw = re.sub(r'\s*\d+(?:\.\d+)?%\s*$', '', label_raw)
    label_raw = re.sub(r'\s*\(\d+\)\s*$', '', label_raw)
    label_raw = label_raw.strip()
    
    # 5. 翻译 Label
    label_cn = trans(label_raw)
    
    # 6. 确保 label_cn 不包含任何特殊字符（作为键名使用）
    label_cn = re.sub(r'[\n\t\r]+', '', label_cn).strip()
    
    return label_cn, val

def get_service_performance(web_page:WebBrowser, xpath_category:str):
    # --- 1. 切换配送方 ---
    web_page.find_by_xpath(Xpath.OrderCategory).click()
    sleep(1) # 等待动画
    web_page.find_by_xpath(xpath_category).click()
    sleep(2) # 等待数据加载

    # --- 2. 获取配送方名称并转中文 (用于Key后缀) ---
    raw_category = web_page.find_by_xpath(xpath_category).get_text()
    # 判断包含 "Amazon" 还是 "Seller"
    if "Amazon" in raw_category or "亚马逊" in raw_category:
        category_cn = "亚马逊"
    else:
        category_cn = "卖家" # 默认为卖家
        
    suffix_field = f'（{category_cn}）'

    # --- 3. 获取目标 (统一格式) ---
    raw_goal = web_page.find_by_xpath(Xpath.OrderDefectGoal).get_text()
    std_goal = standardize_goal_str(raw_goal)

    service_dict = {}

    # --- 4. 获取 ODR (订单缺陷率) ---
    odr_tab_raw = web_page.find_by_xpath(Xpath.OrderDefectTab).get_text()
    odr_name_cn = trans(odr_tab_raw) # 翻译 "Order Defect Rate" -> "订单缺陷率"
    
    odr_val_ele = web_page.find_all_by_xpath(Xpath.OrderDefectVal)
    odr_val = odr_val_ele[0].get_text().strip() if odr_val_ele else "0%"
    
    service_dict[odr_name_cn + suffix_field] = {
        "当前数值": odr_val,
        "目标": std_goal,
        "状态": is_status(odr_val, std_goal)
    }

    # --- 5. 获取子项 (负面反馈等) ---
    # 定义需要抓取的行的XPath列表
    lines_xpath = [Xpath.NegeedbackLine, Xpath.AmazonDealsLine, Xpath.CreditCardLine]
    
    for line_xp in lines_xpath:
        # 获取整行文本
        full_text = ""
        elements = web_page.find_all_by_xpath(line_xp)
        if not elements: continue
        
        # 拼接 td 文本 (防止表格分列)
        for td in elements:
            full_text += td.get_text() + " "
            
        # 解析并翻译
        label_cn, val_cn = process_row_data(full_text)
        
        service_dict[label_cn + suffix_field] = {
            "当前数值": val_cn,
            "目标": std_goal,
            "状态": is_status(val_cn, std_goal) # 如果是 "不适用"，这里返回 ''
        }

    return service_dict


def get_invoice_data(web_page: WebBrowser):
    try:
        # 获取数值
        vals = web_page.find_all_by_xpath(Xpath.InvoiceDefectValue, timeout=5)
        if vals != []:
            val = vals[0].get_text().strip()
        else:
            val = ''

        # 处理可能的 N/A
        if "N/A" in val: val = "不适用"

        # 获取目标
        raw_goal = web_page.find_all_by_xpath(Xpath.InvoiceDefectGoal, timeout=5)
        if raw_goal != []:
            raw_goal = raw_goal[0].get_text()
            std_goal = standardize_goal_str(raw_goal)
        else:
            std_goal = ''

        # 获取并翻译 Tab 名称
        raw_tab = web_page.find_by_xpath(Xpath.InvoiceDefectTab).get_text()
        tab_cn = trans(raw_tab) # "Invoice Defect Rate" -> "发票缺陷率"

        invoice_dict = {}
        invoice_dict[tab_cn] = {
            "当前数值": val,
            "目标": std_goal,
            "状态": is_status(val, std_goal)
        }
        return invoice_dict
    except Exception as e:
        print(f"获取发票缺陷率失败: {e}")
        return {}


def get_data_account_status(web_page:WebBrowser, site_name: str):
    # 业务主入口
    
    # 1. 验证对象
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"

    # 2. 导航 (假设你已经处理好登录)
    domain = get_domain(web_page)
    url = f"{domain}/performance/detail/customer-service"
    to_reports_page_if_need(web_page, url, site_name)

    # 3. 移除强制中文切换，改为自适应
    # switch_language(web_page, 'zh_CN') 
    
    # 4. 点击 ODR Tab
    web_page.find_by_xpath(Xpath.OrderDefectTab).click()
    sleep(1)

    # 5. 获取卖家配送数据
    service_dict_seller = get_service_performance(web_page, Xpath.SellerItem)
    
    # 6. 获取亚马逊配送数据
    service_dict_amazon = get_service_performance(web_page, Xpath.AmazonItem)
    
    # 7. 获取发票缺陷率
    web_page.find_by_xpath(Xpath.InvoiceDefectTab).click()
    sleep(1)
    invoice_dict = get_invoice_data(web_page)
    
    # 8. 合并
    merged_dict = {**service_dict_seller, **service_dict_amazon, **invoice_dict}
    return merged_dict

def test_check_account_status():
    if "xbot_extensions" in __file__:
        return

    web_page = xbot.web.get_active(mode="superbrowser")
    site_name = '美国'
    merged_dict = get_data_account_status(
        web_page,site_name
    )
    print(merged_dict)
    exit()

def main(args):

    # 测试代码入口
    # test_check_account_status()

    # 业务代码入口
    web_page = args.get("web_page")
    site_name = args.get('site_name')
    merged_dict = get_data_account_status(
        web_page,
        site_name
    )
    args["data"] = merged_dict
