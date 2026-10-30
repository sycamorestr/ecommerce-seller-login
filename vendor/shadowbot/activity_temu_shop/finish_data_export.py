# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
import xbot_visual
from xbot import print, sleep, web
from .import package
from xbot.selector import Selector
from .package import variables as glv
from .utils import Tools
from xbot_extensions.web_action.select_date import select_date

from urllib.parse import urlparse
from .download_utils import download_handler

def remove_path(url):
    u = urlparse(url)
    return f"{u.scheme}://{u.netloc}"

def export_data(web_page: xbot.web.WebBrowser, bill_type, start_time, end_time, file_path, file_name, clear_create_time=False):

    browser_mode = Tools.get_web_page_product_name(web_page)

    Tools.check_target_web(web_page,'labor/settle')
    sleep(2)
    
    # 等待网页加载完毕
    web_page.wait_load_completed()
    # 等待数据加载完毕
    Tools.wait_loading(web_page)

    # 点击已到账款项
    query_xpath = '//span[text()="查询"]'
    query_sel = Tools.gen_selector(query_xpath)
    if web_page.wait_appear(query_sel, timeout=4):
        web_page.find_by_xpath('//div[@id="step6"]').click()
        web_page.find_by_xpath(f'//div[.="{bill_type}" and not (div)]').click()

    # 清除弹窗
    Tools.handle_info(web_page)
    if '聚合账单' not in bill_type:

        # 进行时间选择
        web_page.find_by_xpath("//span[.='到账时间' or .='到账日期']/../../../../..//input[contains(@placeholder,'请选择') or contains(@placeholder,'开始时间')]").hover()
        web_page.find_by_xpath("//span[.='到账时间' or .='到账日期']/../../../../..//input[contains(@placeholder,'请选择') or contains(@placeholder,'开始时间')]").click()

        date_frame = web_page.find_by_xpath('//*[@data-testid="beast-core-rangePicker-dropdown-contentRoot"]')

        if start_time[:7] == end_time[:7]:
            select_date(web_page, date_frame, start_time, "")
            select_date(web_page, date_frame, end_time, "")
        else:
            select_date(web_page, date_frame, start_time, end_time)
    
        # 判断是否有确认出现
        confirm_xpath = '//footer[contains(@class,"RPR_footerWrapper")]//span[text()="确认"]'
        confirm_sel = web_page.find_all_by_xpath(confirm_xpath,timeout=1)
        confirm_dis = [_ for _ in confirm_sel if _.get_bounding(to96dpi=False)[2] != 0]
        if len(confirm_dis) > 0:
            confirm_dis[0].click()
            sleep(3)

        if web_page.wait_appear(query_sel, timeout=0.5):
            # 新页面
            if clear_create_time is True:
                # 清空订单创建时间
                web_page.find_by_xpath('(//input[@placeholder="请选择"])[1]').hover()
                web_page.find_by_xpath('(//input[@placeholder="请选择"])[1]/following-sibling::div//*[name()="path"]').hover()
                web_page.find_by_xpath('(//input[@placeholder="请选择"])[1]/following-sibling::div//*[name()="path"]').click()
            web_page.find_by_xpath('//span[text()="查询"]').click()
            web_page.find_by_xpath('//div[@data-testid="beast-core-box"]//span[text()="导出数据"]').click()
            web_page.find_by_xpath('//div[contains(text(),"确认导出")]/../../../..//span[.="确认"]').click()
        else:
            # 旧页面
            # web_page.find_by_xpath('//footer[@class="RPR_footerWrapper_5-120-1"]/button[contains(@class, "primary")]', timeout=2).click()
            web_page.find_by_xpath("//*[text()='已到账款项']/..//following-sibling::a/span", timeout=1).click(delay_after = 2)#点击导出数据
            next_xpath = '//span[contains(text(),"下一条")]'
            next_sel = Tools.gen_selector(next_xpath)

            # 点击下一条
            while web_page.wait_appear(next_sel, timeout=1):
                web_page.find_by_xpath(next_xpath).click(delay_after=1)
            
            confirm_export_xpath = '//span[contains(text(),"确认导出并继续")]'
            confirm_export_sel   = Tools.gen_selector(confirm_export_xpath)
            if web_page.wait_appear(confirm_export_sel, timeout=1):
                web_page.find_by_xpath(confirm_export_xpath).click(delay_after=1)
    
    for retry in range(100):
        target_report = web_page.find_by_xpath("//div[contains(@class,'exportHistoryList')]/div[1]//button//span[1]")
        if '生成中' in target_report.get_text():
            sleep(3)
            web_page.find_by_xpath("//span[text()='刷新']").click()
            continue
        else:
            target_report.click()
            download_handler(
                web_page=web_page,
                file_folder=file_path, 
                file_name=file_name, 
                )
            break
    return file_path + '\\' + file_name

def main(args):
    
    web_page = args.get("web_page")
    bill_type = args.get('bill_type', 'PO明细账单')
    start_time = args.get("start_time" ,'2025-08-12')
    end_time = args.get("end_time" ,'2025-08-14')
    folder_path = args.get("folder_path", r"C:\Users\11758\Desktop\test")
    file_name = args.get("file_name", 'test.xlsx')
    clear_create_time = args.get('clear_create_time', False)

    # web_page = web.get_active(mode='chrome')

    file_path = export_data(web_page, bill_type, start_time, end_time, folder_path, file_name, clear_create_time=clear_create_time)
    args["file_path"] = file_path

