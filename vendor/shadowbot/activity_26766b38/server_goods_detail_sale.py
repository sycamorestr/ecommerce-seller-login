# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv

def select(web_page, xpath, keyword):
    lis = web_page.find_all_by_xpath(xpath)
    for li in lis:
        if li.get_text() == keyword and li.is_displayed():
            li.click()
            break

def select_data(web_page, keyword, value):
    xpath = f"//span[text()='{keyword}']//following-sibling::span"
    web_page.find_by_xpath(xpath).click()
    xpaths = "//ul[contains(@class,'ant-select-dropdown-menu')]/li"
    select(web_page, xpaths, value)

def set_options(web_page, ww_type, ww_group, customer_ww, buier_ww, goods_title, splite_flow, file_folder, file_name, status):

    if '/qos/service/frame' not in web_page.get_url():
        web_page.navigate('https://sycm.taobao.com/qos/service/frame/performance/detail/new#/detail')
    
    xpath = "//*[text()='商品明细']"
    web_page.find_by_xpath(xpath).click()
    
    xpath = "//*[text()='商品销售明细']"
    web_page.find_by_xpath(xpath)
    
    if ww_type !='':
        select_data(web_page, '旺旺类型', ww_type)

    if ww_group !='':
        select_data(web_page, '旺旺分组', ww_group)

    if customer_ww !='':
        select_data(web_page, '客服旺旺', customer_ww)

    if buier_ww!='':
        test_xpath = "//span[text()='买家旺旺']//following-sibling::span//input"
        web_page.find_by_xpath(test_xpath).input(buier_ww)

    if goods_title!='':
        xpath = "//span[text()='商品ID或名称']//following-sibling::span//input"
        web_page.find_by_xpath(xpath).input(goods_title)

    if splite_flow !='':
        select_data(web_page, '分组分流', splite_flow)

    if status != '':
        select_data(web_page, '咨询状态', status)

    web_page.find_by_xpath("//span[text()='下载']").click()
    try:
        web_page.find_by_xpath("//div[@class='ant-modal-content']//tbody/tr[1]//*[text()='下载']", timeout = 5).click()
    except:
        pass
    web.handle_save_dialog(file_folder=file_folder, file_name=file_name, mode='chrome')
    
def test_func():
    if "xbot_extensions" not in __name__:
        web_page = xbot.web.get_active(mode='chrome')
        ww_type = '售前'
        ww_group = '全部'
        customer_ww = '全部'
        buier_ww = ''
        goods_title = ''
        splite_flow = '客服分组'
        status = ''
        file_folder = r'D:\env_text\生意参谋\服务-绩效明细-商品明细'
        file_name = ''
        set_options(web_page, ww_type, ww_group, customer_ww, buier_ww, goods_title, splite_flow, file_folder, file_name, status)
        print(file_folder + '//' + file_name)
        exit()

def main(args):
    test_func()
    web_page = args.get('web_page')
    ww_type = args.get('ww_type')
    ww_group = args.get('ww_group')
    customer_ww = args.get('customer_ww')
    buier_ww = args.get('buier_ww')
    goods_title = args.get("goods_title")
    splite_flow = args.get("splite_flow")
    file_folder = args.get('file_folder')
    file_name = args.get('file_name')
    status = args.get('status')

    set_options(web_page, ww_type, ww_group, customer_ww, buier_ww, goods_title, splite_flow, file_folder, file_name, status)
    args['save_path'] = file_folder + '//' + file_name