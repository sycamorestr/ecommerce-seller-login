# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import math
import os
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement
from pathlib import Path
from .utils import get_domain
from ._amazon_api import switch_language
from .activities_utils import gen_selector,get_shadowroot_element,scroll_and_load
from PIL import Image

class Xpath:
    # 订单配送方下拉框
    OrderDeliverSelect = "//kat-popover[1]/kat-button[@class='filter-button']"
    # 买家满意度状况下拉框
    SellerStatusSelect = "//kat-popover[2]/kat-button[@class='filter-button']"
    # 上次更新时间下拉框
    LastTimeSelect = "//kat-popover[3]/kat-button[@class='filter-button']"
    # 订单配送方下拉选项
    OrderDeliverItems = "//kat-popover[1]//kat-radiobutton"
    # 买家满意度状况下拉选项
    SellerStatusItems = "//kat-popover[2]//kat-checkbox"
    # 上次更新时间下拉选项
    LastTimeItems = "//kat-popover[3]//kat-radiobutton"
    # 已显示退货标记列
    ShowedFlagCol = '//table/tbody/tr/td[13]//div[@class="listing-table-cta"]'
    # 表格内容行
    TableContentRow = '//table/tbody/tr'
    # 分页导航组
    PageNavigation = "//*[@id='root']//kat-pagination"
    # 搜索输入框
    SearchInput = "//*[@id='root']//kat-input-group[@id='listing-search']/kat-input"
    # 搜索按钮
    SearchButton = "//*[@id='filter-bar']/div[1]/kat-button"
    

class Option:
    # 订单配送方选项
    DeliverItems = ['亚马逊', '卖家', '']
    # 买家满意度状况选项
    StatusItems = ['极差', '不合格', '一般', '良好', '极好', '反馈不足', '']
    # 上次更新时间选项
    TimeItems = ['7天', '30天', '90天', '1年', '全部', '']
    # 截图标志文本
    FlagTexts = ['是', '存在风险']


def input_parameter_valid(web_page:WebBrowser,order_deliver:str,seller_status:list,last_time:str,flag_text:list):
    # TODO: 用断言检测数据类型
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert (order_deliver in Option.DeliverItems), f"订单配送方错误：{order_deliver}"
    assert all(item in Option.StatusItems for item in seller_status), f"买家满意度状况错误：{seller_status}"
    assert (last_time in Option.TimeItems), f"上次更新时间错误：{last_time}"
    assert all(item in Option.FlagTexts for item in flag_text), f"截图标志文本错误：{flag_text}"


def to_reports_page_if_need(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标报告页面（且不是子页面），直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
        url + "/"
    ):
        return
    # 如果不是，要导航到的报告页面URL
    web_page.navigate(url, load_timeout=300)
    # 使用构建 selector 的方式来等待元素
    if not web_page.wait_appear(gen_selector(Xpath.OrderDeliverSelect), timeout=30):
        raise Exception(
            f"进入买家之声页面失败，未找到订单配送方下拉框： {Xpath.OrderDeliverSelect}"
        )


def set_filter_parameters(web_page:WebBrowser,order_deliver:str,seller_status:list,last_time:str,product_name:str):
    # 设置筛选配置
    # 设置输入框
    if product_name == '':
        pass
    else:
        web_page.find_by_xpath(Xpath.SearchInput).input(product_name)
        web_page.find_by_xpath(Xpath.SearchButton).click()
    # 选择订单配送方
    web_page.find_by_xpath(Xpath.OrderDeliverSelect).click()
    for option in web_page.find_all_by_xpath(Xpath.OrderDeliverItems):
        if option.get_attribute('label') == order_deliver:
            option.click()
            break
    # 选择买家满意度状况
    for item in seller_status:
        web_page.find_by_xpath(Xpath.SellerStatusSelect).click()
        for option in web_page.find_all(get_shadowroot_element(web_page,"screenshot_return_mark_买家满意度状况")):
            if option.get_text() == item:
                option.click()
                break
    # 选择上次更新时间
    web_page.find_by_xpath(Xpath.LastTimeSelect).click()
    for option in web_page.find_all_by_xpath(Xpath.LastTimeItems):
        if option.get_attribute('label').replace(' ', '') == last_time:
            option.click(anchor=('middleCenter', -10, 0))
            break


def screenshot_pages(web_page:WebBrowser,file_name:str,file_folder:str,flag_text:list):
    try:
        # 获取总行数
        total_items = web_page.find_by_xpath(Xpath.PageNavigation).get_attribute('total-items')
        # 获取每页总行数
        page_items = web_page.find_by_xpath(Xpath.PageNavigation).get_attribute('items-per-page')
        pages = math.ceil(int(total_items)/int(page_items))
    except:
        pages = 1
    result_list = []
    for index1 in range(pages):
        items = web_page.find_all_by_xpath(Xpath.ShowedFlagCol)
        for index, item in enumerate(items):
            if item.child_at(0) != None and item.child_at(0).child_at(0).get_attribute('label') in flag_text:
                web_page.find_by_xpath(Xpath.TableContentRow+'['+str(index+1)+']').screenshot(str(file_folder), filename=file_name + '_第' + str(index1+1) + '页'+'_第'+str(index+1)+'条.png')
                result_list.append(str(file_folder)+'\\'+file_name + '_第' + str(index1+1) + '页'+'_第'+str(index+1)+'条.png')
            index += 1
        # 点击下一页
        scroll_and_load(web_page) # 滚动到屏幕底部
        sleep(1)
        if pages > 1:
            web_page.find("screenshot_return_mark_下一页按钮").click()
        index1 += 1
    if len(result_list)>=2:
        # 合并截图（纵向拼接，图片大小一致）
        save_path = str(file_folder)+'\\'+file_name+'.png'
        first_img = Image.open(result_list[0])
        img_width, img_height = first_img.size
        total_height = img_height * len(result_list)
        new_image = Image.new('RGB', (img_width, total_height))
        y_offset = 0
        for img_path in result_list:
            img = Image.open(img_path)
            new_image.paste(img, (0, y_offset))
            y_offset += img_height
        new_image.save(save_path)
        file_path = save_path
        # 删除子图
        for pic in result_list:
            if os.path.exists(pic):
                os.remove(pic)
    elif len(result_list)==1:
        file_path = result_list[0]
    else:
        file_path = ''
    return file_path


def screenshot_return_mark(web_page:WebBrowser,order_deliver:str,seller_status:str,last_time:str,flag_text:str,product_name:str,file_folder:str,file_name:str):
    # 退货标记截图
    # 输入参数转换
    seller_status = [item.strip() for item in seller_status.split(';')]
    flag_text = [item.strip() for item in flag_text.split(';')]
    file_folder = Path(file_folder)
    file_folder.mkdir(parents=True, exist_ok=True)

    # 输入参数校验
    input_parameter_valid(web_page,order_deliver,seller_status,last_time,flag_text)

    # 进入买家之声页面
    domain = get_domain(web_page)
    url = f"{domain}/voice-of-the-customer"
    to_reports_page_if_need(web_page, url)

    # 切换语言
    switch_language(web_page, 'zh_CN')

    # 设置筛选配置
    web_page.wait_load_completed(timeout=30) # 等待网页加载完毕
    set_filter_parameters(web_page,order_deliver,seller_status,last_time,product_name)

    # 截图已显示退货标记不为--的行
    file_path = screenshot_pages(web_page,file_name,file_folder,flag_text)
    return file_path


def test_screenshot_return_mark():
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="auto")
    order_deliver = '亚马逊' # 订单配送方
    seller_status = '极好' # 买家满意度状况
    last_time = '7天' # 上次更新时间
    flag_text = '是;存在风险' # 截图标志文本
    product_name = '' # 商品名称
    file_folder = r"C:\Users\58204\Desktop\test" # 截图文件夹路径
    file_name = "test" # 截图文件名
    file_path = screenshot_return_mark(web_page,order_deliver,seller_status,last_time,flag_text,product_name,file_folder,file_name)
    print(file_path)
    exit()

def main(args):
    # 测试代码入口
    test_screenshot_return_mark()

    # 业务代码入口
    web_page = args.get('web_page')
    order_deliver = args.get('order_deliver') # 订单配送方
    seller_status = args.get('seller_status') # 买家满意度状况
    last_time = args.get('last_time') # 上次更新时间
    flag_text = args.get('flag_text') # 截图标志文本
    product_name = args.get('product_name') # 商品名称
    file_folder = args.get('file_folder') # 截图文件夹路径
    file_name = args.get('file_name') # 截图文件名

    file_path = screenshot_return_mark(web_page,order_deliver,seller_status,last_time,flag_text,product_name,file_folder,file_name)
    args['file_path'] = file_path
