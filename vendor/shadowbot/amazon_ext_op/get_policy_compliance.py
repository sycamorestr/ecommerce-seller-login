# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot  # type: ignore
import re  # type: ignore
from xbot import print, sleep  # type: ignore
from xbot.selector import Selector  # type: ignore
from xbot.web import WebBrowser, WebElement  # type: ignore
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language, login

class Xpath:
    # 导航菜单
    NavigateMenu = '//*[@data-test-tag="nav-button-container"]'
    # 绩效菜单
    PerformanceMenu = '//*[@data-menu-id="performance"]'
    # 绩效选项
    PerformanceItem = '(//*[@class="flyout-menu"])[10]//span'
    # 账户状况评级
    ConditionRating = '//*[contains(@class, "ahr-status-badge")] | //div[contains(@class, "sp-ahd-ahr-indicator")]'
    # 账户状况分数
    ConditionScore = "//*[@class='a-column a-span5 a-spacing-none a-ws-span5 a-span-last a-ws-span-last']/h3"
    # 所有问题名称
    QuestionName = "//*[@id='policies-content-rows-section']//a"
    # 问题对应数量
    QuestionNumber = "//*[@id='policies-content-rows-section']//span"
    # 查看客户服务绩效详情
    ServiceDetail = "//*[@id='customer-satisfaction-details-section']/a"
    # 订单缺陷率tabspan
    OrderDefectTab = '(//*[@id="tabs-titles"]//span)[1]'
    # 发票缺陷率tabspan
    InvoiceDefectTab = '(//*[@id="tabs-titles"]//span)[3]'
    # 订单配送方类型
    OrderCategory = '//*[@id="odr-target-section"]//span[@id="a-autoid-0"]'
    # 卖方类型选项
    SellerItem = "(//*[@role='listbox']//a)[1]"
    # 亚马逊类型选项
    AmazonItem = "(//*[@role='listbox']//a)[2]"
    # 订单缺陷率数值
    OrderDefectVal = '//*[@id="odr-giant-metric-percentage"]/span'
    # 负面反馈行
    NegeedbackLine = '(//*[@id="odr-metric-table"]//tr)[2]'
    # 亚马逊商城交易保障索赔行
    AmazonDealsLine = '(//*[@id="odr-metric-table"]//tr)[3]'
    # 信用卡拒付索赔行
    CreditCardLine = '(//*[@id="odr-metric-table"]//tr)[4]'
    # 订单缺陷率目标
    OrderDefectGoal = "//*[@id='odr-summary-target-section']/span[@id='odr-target']"
    # 查看配送绩效详情
    DistributionDetail = "//*[@id='shipping-details-section']/a"
    # 配送绩效span
    DistributionSpan = '//*[@id="tabs-titles"]//span'
    # 迟发率span
    LateRateSpan = '(//*[@id="tabs-titles"]//span)[1]'
    # 预配送取消率span
    CancelRateSpan = '(//*[@id="tabs-titles"]//span)[8]'
    # 有效追踪率span
    TrackingRateSpan = '(//*[@id="tabs-titles"]//span)[10]'
    # 准时交货率span
    DeliveryRateSpan = '(//*[@id="tabs-titles"]//span)[12]'


def goto_account_status(web_page:WebBrowser):
    # 通过菜单进入账户状况
    # 点击导航菜单
    web_page.find_by_xpath(Xpath.NavigateMenu).click()
    # 悬浮绩效菜单
    web_page.find_by_xpath(Xpath.PerformanceMenu).hover()
    # 点击账户状况选项
    for option in web_page.find_all_by_xpath(Xpath.PerformanceItem):
        if option.get_text() == '账户状况':
            option.click()
            break

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

def to_reports_page_if_need(web_page: WebBrowser, url: str, site_name: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)

    # 进行登录校验
    login(web_page)
    # 进行站点校验
    if site_name:
        if '/account-switcher/default/merchantMarketplace' in web_page.get_url():
            switch_site(web_page, site_name)


    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(Xpath.ConditionRating), timeout=30):
        raise Exception(
            f"进入账户状况页面失败，未找到账户状况评级： {Xpath.ConditionRating}"
        )

# # 旧版本，出错时可还原
# def get_policy_compliance(web_page:WebBrowser):
#     # 检查并获取政策合规性数据
#     # 获取账户状况评级数据
#     condition_rate = web_page.find_by_xpath(Xpath.ConditionRating).get_text()
#     # 获取账户状况分数数据
#     condition_score = web_page.find_by_xpath(Xpath.ConditionScore).get_text()
#     # 获取所有问题名称
#     question_name_list = []
#     for name in web_page.find_all_by_xpath(Xpath.QuestionName):
#         question_name_list.append(name.get_text())
#     # 获取问题对应数量
#     question_num_list = []
#     for number in web_page.find_all_by_xpath(Xpath.QuestionNumber):
#         question_num_list.append(number.get_text())
#     policy_dict = {}
#     policy_dict["账户状况评级"] = condition_rate
#     policy_dict["账户状况分数"] = condition_score
#     for i in range(0, len(question_name_list)):
#         if int(question_num_list[i]) >0:
#             status = '异常'
#         else:
#             status = '正常'
#         policy_dict[question_name_list[i]]={"当前数值":question_num_list[i],"状态":status}
#     # print(policy_dict)
#     return policy_dict

# 新版本，兼容墨西哥
def get_policy_compliance(web_page: WebBrowser):
    """
    检查并获取政策合规性数据 (兼容多站点)
    """
    
    # --- 1. 获取账户状况评级 (兼容逻辑) ---
    condition_rate_text = "未知"
    
    # 尝试找到指示器元素
    indicator_ele = web_page.find_by_xpath(Xpath.ConditionRating)
    
    if indicator_ele:
        # 优先尝试获取文本（常规站点，如 "200", "Good"）
        text = indicator_ele.get_text().strip()
        if text:
            condition_rate_text = text
        else:
            # 如果文本为空（墨西哥站点），则检测 class 颜色
            class_val = indicator_ele.get_attribute("class")
            if "status-green" in class_val or "ahr-green" in class_val:
                condition_rate_text = "良好"
            elif "status-yellow" in class_val or "ahr-yellow" in class_val:
                condition_rate_text = "存在风险"
            elif "status-red" in class_val or "ahr-red" in class_val:
                condition_rate_text = "不佳"
            else:
                condition_rate_text = "未知"
    
    # --- 2. 获取账户状况分数 (兼容逻辑) ---
    condition_score_text = "N/A" # 默认为 N/A，部分站点没有分数
    try:
        score_ele = web_page.find_by_xpath(Xpath.ConditionScore, timeout=2) # 缩短超时，因为可能不存在
        if score_ele:
            condition_score_text = score_ele.get_text().strip()
    except Exception:
        # 没找到分数元素，说明可能是墨西哥站点，保持 N/A 即可
        pass

    # --- 3. 获取所有问题名称和数量 ---
    question_name_list = []
    for name in web_page.find_all_by_xpath(Xpath.QuestionName):
        question_name_list.append(name.get_text())

    question_num_list = []
    for number in web_page.find_all_by_xpath(Xpath.QuestionNumber):
        question_num_list.append(number.get_text())

    # --- 4. 组装结果 ---
    policy_dict = {}
    policy_dict["账户状况评级"] = condition_rate_text
    policy_dict["账户状况分数"] = condition_score_text
    
    # 容错：防止名称和数量长度不一致
    min_len = min(len(question_name_list), len(question_num_list))
    
    for i in range(min_len):
        num_str = question_num_list[i].strip()
        # 处理可能包含非数字字符的情况
        try:
            num = int(re.sub(r'\D', '', num_str)) if num_str else 0
        except:
            num = 0
            
        status = '异常' if num > 0 else '正常'
        policy_dict[question_name_list[i]] = {"当前数值": num_str, "状态": status}
    
    return policy_dict

def get_data_account_status(web_page:WebBrowser, site_name):
    # 获取账号状态数据
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"

    # 进入账户状况页面
    domain = get_domain(web_page)
    url = f"{domain}/performance/dashboard"
    to_reports_page_if_need(web_page, url, site_name)

    # 0.切换语言
    # switch_language(web_page, 'zh_CN')

    # 1.通过菜单进入账户状况
    # goto_account_status(web_page)
    
    # 2.检查并获取政策合规性数据
    policy_dict = get_policy_compliance(web_page)
    return policy_dict

def test_check_account_status():
    if "xbot_extensions" in __file__:
        return

    web_page = xbot.web.get_active(mode="ziniaobrowser")
    site_name = '美国'
    data = get_data_account_status(
        web_page,
        site_name
    )
    print(data)
    exit()

def main(args):

    # 测试代码入口
    # test_check_account_status()

    # # 业务代码入口
    web_page = args.get("web_page")
    site_name = args.get('site_name') or ''
    policy_dict = get_data_account_status(
        web_page,
        site_name
    )
    args["data"] = policy_dict
