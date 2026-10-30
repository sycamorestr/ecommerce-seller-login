# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .utils import handler_feedback, get_domain
from ._amazon_api import switch_language
from xbot.web import WebElement, WebElement
from xbot.selector import Selector

class Xpath:
    search_xpath = '//input[@placeholder="按货件编号搜索"]'
    status_xpath = '//span[contains(@id,"trigger-content") and text()="状态"]'
    Missing_tracking_xpath = '//span[contains(@id,"trigger-content") and text()="缺少追踪"]'
    last_updatetime_xpath = '//span[contains(@id,"trigger-content") and text()="上次更新时间"]'
    store_xpath = '//span[contains(@id,"trigger-content") and text()="店铺"]'
    clear_xpath = '//button[@type="submit" and contains(.,"清除筛选条件")]'
    loading_data = '//td[contains(@class,"awsui_cell-merged") and contains(.,"正在加载资源")]'

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

def download_fba_shipments_data(web_page, status, Missing_tracking, last_updatetime, Store, Preferences, file_folder, file_name):
    '''
    下载FBA货件订单数据
    '''

    # 构建元素
    search_ele_sel  = create_selector([Xpath.search_xpath],"按货件编号搜索")
    loading_sel  = create_selector([Xpath.loading_data],"正在加载资源")

    # 判断当前页面
    domain = get_domain(web_page)
    current_url = web_page.get_url()
    if '/manage/shipments' not in current_url:
        # # 跳转至页面
        web_page.navigate(f'{domain}/manage/shipments')
        
    # 切换语言为简体中文
    switch_language(web_page,'zh_CN')
    web_page.wait_load_completed()
    # search_ele = web_page.find_by_xpath(Xpath.search_xpath,timeout = 10)
    web_page.wait_appear("search_ele_sel")
    sleep(2)

    # 清除筛选
    if len(web_page.find_all_by_xpath(Xpath.clear_xpath, timeout = 3)) > 0:
        web_page.find_by_xpath(Xpath.clear_xpath).click()
        web_page.wait_disappear("loading_sel")
    sleep(2)

    # 设置列首选项
    web_page.find_by_xpath('//button[@title="首选项"]').click()
    for item in Preferences:
        if len(web_page.find_all_by_xpath(f'//div[contains(@class,"awsui_content-display-option-content")]/label[text()="{item}"]/following-sibling::div//input[@checked]')) > 0:
            continue
        else:
            web_page.find_by_xpath(f'//div[contains(@class,"awsui_content-display-option-content")]/label[text()="{item}"]/following-sibling::div//input[not(@checked])').cilck()

    # 筛选状态
    if len(status) > 0:
        web_page.find_by_xpath(Xpath.status_xpath).click()
        for status_name in status:
            status_ele = web_page.find_by_xpath(f'//div[@role="option" and contains(@class,"awsui_selectable-item") and normalize-space(.)="{status_name}"]')
            status_ele.click()

    # 选择是否缺少追踪
    if Missing_tracking != None:
        web_page.find_by_xpath(Xpath.Missing_tracking_xpath).click()
        web_page.find_by_xpath(f'//div[contains(@id,"option-list")]//span[@title="{Missing_tracking}"]').click()

    # 选择上次更新时间
    '''
    最近 7 天
    最近 30 天
    过去 3 个月
    过去 6 个月
    过去 1 年
    '''
    if last_updatetime != None:
        web_page.find_by_xpath(Xpath.last_updatetime_xpath).click()
        web_page.find_by_xpath(f'//div[contains(@id,"option-list")]//span[@title="{last_updatetime}"]').click()

    # 筛选店铺
    if len(Store) > 0:
        web_page.find_by_xpath(Xpath.Missing_tracking_xpath).click()
        for store_name in Store:
            store_ele = web_page.find_by_xpath(f'//div[contains(@id,"option-list")]//span[@title="{store_name}"]')
            store_ele.click()

    # 等待加载完成
    web_page.wait_disappear("loading_sel")

def test():
    if "xbot_extensions" in __file__:
        return
    web_page = xbot.web.get_active('ziniaobrowser')
    status = ['已发货','在途']
    Missing_tracking = None
    last_updatetime = '最近 30 天'
    Store = ['英国', '巴西']
    Preferences = ["状态", "已创建", "上次更新时间", "目的地", "送达时段", "SKU", "商品状态"]
    file_folder = r"C:\Users\yingdao\Desktop"
    file_name = 'test.xlsx'

    file_path = download_fba_shipments_data(web_page,status,Missing_tracking,last_updatetime,Store,Preferences,file_folder,file_name)
    print(file_path)
    exit()

def main(args):
    # 测试代码入口
    test()

    # 业务代码入口
    web_page = args.get("web_page")
    status = args.get("status").split(",") if args.get("status") else []  # 状态List
    Missing_tracking = args.get("Missing_tracking") if args.get("Missing_tracking") else None  # 是否缺少追踪
    last_updatetime = args.get("last_updatetime") if args.get("last_updatetime") else None  # 上次更新时间
    Store = args.get("Store").split(",") if args.get("Store") else []  # StoreList
    Preferences = args.get("Preferences") # 列首选项
    file_folder = args.get("file_folder")  # 保存文件夹路径
    file_name = args.get("file_name")  # 保存文件名

    file_path = download_fba_shipments_data(web_page, status, Missing_tracking, last_updatetime, Store, Preferences, file_folder, file_name)
    args["file_path"] = file_path