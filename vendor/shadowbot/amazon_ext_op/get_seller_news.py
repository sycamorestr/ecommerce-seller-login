# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from .utils import get_domain
from .activities_utils import gen_selector,get_shadowroot_element,scroll_and_load
from ._amazon_api import switch_language


class Xpath:
    # 国家地区下拉框
    CountrySelect = '//kat-dropdown[@data-testid="marketplace-picker"]'
    # 国家地区选项
    CountryItem = "//*[@class='divide-y']//kat-option"
    # 日期时间下拉框
    DateSelect = '//kat-dropdown[@data-testid="date-filter"]'
    # 新闻标题
    NewsTitle = '//*[@data-testid="listing-card-layout"]//h5'
    # 新闻项
    NewsItem = '(//*[@data-testid="listing-card-layout"])'
    

class Option:
    # 国家地区列表
    CountryList = ['日本', '美国', '英国', '澳大利亚', '比利时', '巴西', '加拿大', '埃及', '法国', '德国', '印度', '意大利', '墨西哥', '荷兰', '波兰', '沙特阿拉伯', '新加坡', '西班牙', '瑞典', '土耳其', '阿联酋', '南非', '爱尔兰']
    # 日期时间列表
    DateList = ['所有时间', '过去一周', '过去一个月', '过去3个月', '过去一年']


def input_parameter_valid(web_page,country_name,date_name):
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (country_name in Option.CountryList), f"国家地区名称错误：{country_name}"
    assert (date_name in Option.DateList), f"日期时间名称错误：{date_name}"


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标新闻页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(Xpath.DateSelect), timeout=30):
        raise Exception(
            f"进入所有新闻页面失败，未找到日期时间下拉框： {Xpath.DateSelect}"
        )


def set_filter_parameters(web_page:WebBrowser, country_name:str, date_name:str):
    # 设置筛选配置
    # 选择国家地区
    web_page.find_by_xpath(Xpath.CountrySelect).click()
    for option in web_page.find_all_by_xpath(Xpath.CountryItem):
        if option.get_text()==country_name:
            option.click()
            break

    # 选择日期时间
    web_page.find_by_xpath(Xpath.DateSelect).click()
    for option in web_page.find_all(get_shadowroot_element(web_page, "get_seller_news_日期时间选项")):
        if option.get_text().replace(' ', '')==date_name:
            option.click()
            break


def get_deal_data(web_page:WebBrowser):
    # 获取并处理新闻数据
    news_total = ""
    news_title_ele = web_page.find_all_by_xpath(Xpath.NewsTitle)
    for index,item in enumerate(news_title_ele):
        # 获取新闻标题
        news_title_text = item.get_text()
        # 获取新闻标题对应的内容
        news_content_text = ""
        news_content_ele = web_page.find_all_by_xpath(Xpath.NewsItem + '[' + str(index+1) + ']//p')
        for content in news_content_ele:
            news_content_text += content.get_text() + '\n'
        news_content_text = [line for line in news_content_text.split('\n') if line.strip()!=""] # 去除空行
        news_content_text = '\n'.join(news_content_text)
        news_total += f"{index+1}、{news_title_text}\n{news_content_text}\n\n"
    return news_total


def get_seller_news(web_page:WebBrowser,country_name:str,date_name:str):
    # 获取卖家新闻
    # 输入参数校验
    input_parameter_valid(web_page,country_name,date_name)

    # 进入所有新闻页面
    domain = get_domain(web_page)
    url = f"{domain}/seller-news/articles"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置筛选配置
    set_filter_parameters(web_page, country_name, date_name)

    # 模拟滚动页面触发页面的懒加载
    scroll_and_load(web_page)

    # 获取并处理新闻数据
    news_total = get_deal_data(web_page)

    return news_total


def test_get_seller_news():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    country_name = '日本' # 国家地区名称
    date_name = '过去一个月' # 日期时间名称
    news_total = get_seller_news(web_page,country_name,date_name)
    print(news_total)


def main(args):
    # 测试代码入口
    # test_get_seller_news()

    # 业务代码入口
    web_page = args.get('web_page')
    country_name = args.get('country_name') # 国家地区名称
    date_name = args.get('date_name') # 日期时间名称

    result_data = get_seller_news(web_page,country_name,date_name)
    args['result_data'] = result_data
