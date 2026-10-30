# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep,win32
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from .utils import get_domain, handler_container
from ._amazon_api import switch_site, switch_language
from xbot import logging
from .create_element import create_selector

class ReviewFilterOptions:
    
    # 订单类型选项（中文 -> 英文）orderStatus=
    ORDER_STATUS_OPTIONS = {
        '由我销售': 'soldByMe',
        '由其他卖家销售':'soldByOthers',
        '未验证': 'notVerified',
        '未找到订单':'unknown'
        
    }
    
    # 联系状态选项（中文 -> 英文）可多选,contactStatus=
    CONTACT_STATUS_OPTIONS = {
        '已联系': 'contacted',
        '未联系': 'notContacted'
    }
    
    # 星级评定选项（中文 -> 英文）可多选 stars=
    STAR_OPTIONS = {
        '1星': '1',
        '2星': '2',
        '3星': '3',
        '4星': '4',
        '5星': '5',
    }
    
    # 时间段选项（中文 -> 英文）timePeriod=
    TIME_PERIOD_OPTIONS = {
        '本周': 'thisWeek',
        '上周': 'lastWeek',
        '更早以前': 'older'
    }

    #标记为已完成的包含在内  includeDone = true  不包含则是 false


# --- 1. 定义所有需要用到的 XPath 路径 ---
class Xpath:
    """XPath 常量集中管理"""
    
    # 数据
    ReviewContainer = '//div[@data-testid and starts-with(@data-testid, "review-")]'
    
    # 数据提取
    AsinDetailContainer = './/div[contains(@class, "asinDetail")]'
    
    # 父ASIN
    ParentAsin = './/div[contains(@class, "asinDetail")]//div[contains(@class, "css-yyccc7")][1]//div[not(@class)]'
    
    # 子ASIN
    ChildAsin = './/div[contains(@class, "asinDetail")]//div[contains(@class, "css-yyccc7")][2]//div[not(@class)]'
    
    # 评论链接
    ReviewLink = './/*[local-name()="kat-link"][contains(@href, "customer-reviews")]'

    # 商品评论星级
    ReviewStar = './/*[@class="reviewRating"]'

    # 商品评论时间
    ReviewTime = './/*[@class="reviewRating"]/following-sibling::*'

    # 商品评论
    ProductComment = './/*[contains(@id,"review-content")]'
    
    # 翻页元素（跨域）
    NextPageButton = '//*[local-name()="kat-pagination"]/xbotShadowRoot//span[@part="pagination-nav-right" and not(contains(@class, "end"))]'
    

# --- 2. 构建跨域元素 ---
class Element:
    next_page_button = create_selector(Xpath.NextPageButton, name = '下一页按钮')

# --- 3.业务操作

def get_product_data(web_page: WebBrowser) -> list:
    """
    获取当前页面的所有评论数据
    """
    result_list = []
    
    try:
        # 判断是否有数据：检查是否存在评论容器元素
        review_containers = web_page.find_all_by_xpath(Xpath.ReviewContainer, timeout=10)
        
        if not review_containers or len(review_containers) == 0:
            print("当前页面没有评论数据")
            return result_list
        
        # 遍历每个评论项，提取数据
        for index, container in enumerate(review_containers, 1):
            try:
                
                # 获取商品星级
                product_star = ""
                try:
                    product_star = container.find_by_xpath(Xpath.ReviewStar).get_attribute('value')
                except Exception as e:
                    print(f"第 {index} 条评论获取星级失败: {e}")
                
                # 获取评论发布时间
                review_time = ""
                try:
                    review_time = container.find_by_xpath(Xpath.ReviewTime).get_text()
                    if '于' in review_time:
                        review_time = review_time.split('于')[1].split('发')[0].strip()
                    elif 'on' in review_time:
                        review_time = review_time.split('on')[1].strip()
                except Exception as e:
                    print(f"第 {index} 条评论获取评论时间: {e}")
                
                # 获取评论
                comment_review = ""
                try:
                    comment_review = container.find_by_xpath(Xpath.ProductComment).get_text()
                except Exception as e:
                    print(f"第 {index} 条评论获取失败: {e}")

                # 提取父ASIN
                parent_asin = ""
                try:
                    parent_asin_elem = container.find_by_xpath(Xpath.ParentAsin, timeout=2)
                    parent_asin = parent_asin_elem.get_text().strip() if parent_asin_elem else ""
                except Exception as e:
                    print(f"第 {index} 条评论提取父ASIN失败: {e}")
                
                # 提取子ASIN
                child_asin = ""
                try:
                    child_asin_elem = container.find_by_xpath(Xpath.ChildAsin, timeout=2)
                    child_asin = child_asin_elem.get_text().strip() if child_asin_elem else ""
                except Exception as e:
                    print(f"第 {index} 条评论提取子ASIN失败: {e}")
                
                # 提取评论链接
                review_link = ""
                try:
                    link_elem = container.find_by_xpath(Xpath.ReviewLink, timeout=2)
                    if link_elem:
                        review_link = link_elem.get_attribute('href') or ""
                except Exception as e:
                    print(f"第 {index} 条评论提取评论链接失败: {e}")
                
                # 构建数据字典
                data_dict = {
                    '商品星级': product_star,
                    '评论时间': review_time,
                    '评论内容': comment_review,
                    '父ASIN': parent_asin,
                    '子ASIN': child_asin,
                    '评论链接': review_link
                }
                
                result_list.append(data_dict)
                print(f"第 {index} 条评论提取成功: 商品星级={product_star}, 评论时间={review_time}, 评论内容={comment_review}, 父ASIN={parent_asin}, 子ASIN={child_asin}，链接={review_link}")
                
            except Exception as e:
                print(f"第 {index} 条评论处理失败: {e}")
                continue
        
    except Exception as e:
        print(f"获取评论数据失败: {e}")
        logging.error(f"获取评论数据失败: {e}")
    
    return result_list






# --- 4.拼接url
def build_reviews_filter_url(
    domain: str,
    orderclass: str = None,
    connectstatus: list = None,
    stars: list = None,
    timeselect: str = None,
    isincludeDone: bool = None
) -> str:
    """
    构建买家评论筛选页面的完整URL
    """
    # 基础路径
    base_path = "/brand-customer-reviews/"
    
    # 构建查询参数
    query_params = []
    
    # 订单类型（单选）
    if orderclass and orderclass.strip():
        if orderclass in ReviewFilterOptions.ORDER_STATUS_OPTIONS:
            query_params.append(f"orderStatus={ReviewFilterOptions.ORDER_STATUS_OPTIONS[orderclass]}")
    
    # 联系状态（多选）
    if connectstatus and isinstance(connectstatus, list) and len(connectstatus) > 0:
        contact_values = []
        for status in connectstatus:
            if status and status.strip() and status in ReviewFilterOptions.CONTACT_STATUS_OPTIONS:
                contact_values.append(ReviewFilterOptions.CONTACT_STATUS_OPTIONS[status])
        if contact_values:
            query_params.append(f"contactStatus={','.join(contact_values)}")
    
    # 星级评定（多选）
    if stars and isinstance(stars, list) and len(stars) > 0:
        star_values = []
        for star in stars:
            if star and str(star).strip() and str(star) in ReviewFilterOptions.STAR_OPTIONS:
                star_values.append(ReviewFilterOptions.STAR_OPTIONS[str(star)])
        if star_values:
            # 去重并排序
            star_values = sorted(set(star_values), key=lambda x: int(x))
            query_params.append(f"stars={','.join(star_values)}")
    
    # 时间段（单选）
    if timeselect and timeselect.strip():
        if timeselect in ReviewFilterOptions.TIME_PERIOD_OPTIONS:
            query_params.append(f"timePeriod={ReviewFilterOptions.TIME_PERIOD_OPTIONS[timeselect]}")
    
    # 标记为已完成
    if isincludeDone is not None:
        query_params.append(f"includeDone={'true' if isincludeDone else 'false'}")
    
    # 拼接完整URL
    if query_params:
        url = f"{domain}{base_path}?{'&'.join(query_params)}"
    else:
        url = f"{domain}{base_path}"
    
    return url


# --- 5. 整体业务流程 ---
def process_method(web_page: WebBrowser,orderclass,connectstatus,stars,timeselect,isincludeDone) -> list:
    # 步骤1: 准备目标URL并确保在目标页面
    domain = get_domain(web_page)

    #需要补充 url拼接函数,调用函数4
    url = build_reviews_filter_url(
        domain=domain,
        orderclass=orderclass,
        connectstatus=connectstatus,
        stars=stars,
        timeselect=timeselect,
        isincludeDone=isincludeDone
    )
    # 如果不是，要导航到的报告页面URL

    #跳转
    web_page.navigate(url,load_timeout=100)
    handler_container(web_page)
    #切换语言
    switch_language(web_page, 'zh_CN')
    sleep(3)

    # 存储所有数据
    all_data = []
    
    # 当前页码（用于日志显示）
    current_page = 1
    
    # 循环抓取所有页面的数据
    while True:
        print(f"\n开始抓取第 {current_page} 页数据...")
        
        # 获取当前页数据
        page_data = get_product_data(web_page)
        
        if page_data:
            all_data.extend(page_data)
            print(f"第 {current_page} 页抓取完成，共 {len(page_data)} 条数据")
        else:
            print(f"第 {current_page} 页没有数据")
        
        # 尝试点击右箭头翻到下一页
        # 处理翻页
        try:
            if web_page.wait_appear(Element.next_page_button,timeout = 2):
                web_page.find(Element.next_page_button).click()
                web_page.wait_load_completed(timeout = 20)
                current_page += 1
                sleep(1)
            else:
                print("已到达最后一页。")
                break
        except Exception as e:
            print(f"查找'下一页'按钮时出错或未找到:{e}")
            break
        
    
    print(f"\n所有页面抓取完成，共 {len(all_data)} 条数据")
    return all_data

def test_return_processing_report():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    #模拟参数
    orderclass = ''  # 订单类型（单选）
    connectstatus = ['已联系', '未联系']  # 联系状态（多选，列表）
    stars = ['4星', '5星']  # 星级评定（多选，列表）
    timeselect = '更早以前'  # 时间段（单选）
    isincludeDone = ''  # 标记为已完成（布尔值）
    
    data = process_method(web_page, orderclass, connectstatus, stars, timeselect, isincludeDone)
    print(data)

    exit()


def main(args):
    test_return_processing_report()
    # 业务代码入口
    web_page = args.get('web_page')
    #用户传入参数
    orderclass = args.get('订单类型')  # 单选，str
    connectstatus = args.get('联系状态')  # 多选，list
    stars = args.get('星级评定')  # 多选，list
    timeselect = args.get('时间段')  # 单选，str
    isincludeDone = args.get('标记为已完成')  # 布尔值，bool
    
    data = process_method(web_page, orderclass, connectstatus, stars, timeselect, isincludeDone)
    args['data'] = data
