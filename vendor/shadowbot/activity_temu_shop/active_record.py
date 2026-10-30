# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import re
import math
import xbot
from xbot import print, sleep, web
from xbot_extensions.lazy_loading import get_lazy_element_list_by_xpath
from xbot.app import databook
from .import package
from .package import variables as glv
from .utils import Tools
from xbot_extensions.web_action.select_date import select_date

def set_params(web_page, active_category, active_type, start_time, end_time, SPU, 
            goods_num, active_status, end_status):

    Tools.check_web(web_page, 'activity/marketing-activity/log')
    if active_category == '长期活动':
        web_page.find_by_xpath("//*[text()='长期活动']").click()
    elif active_category == '专题活动':
        web_page.find_by_xpath("//*[text()='专题活动']").click()
        
    if active_type != '':
        web_page.find_by_xpath("//*[text()='活动类型']//ancestor::div[@data-testid='beast-core-grid-col-wrapper']/div/div[2]").click()
        flow_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")
        Tools.down_select(web_page, active_type, flow_elems)

    if start_time != '':
        web_page.find_by_xpath("//*[text()='活动时间']//ancestor::div[@data-testid='beast-core-grid-col-wrapper']/div/div[2]").click()
        date_iframe = web_page.find_by_xpath('//div[@data-testid="beast-core-portal-main"]')
        select_date(web_page, date_iframe, start_time, end_time)
        web_page.find_by_xpath("//div[@data-testid='beast-core-portal-main']//*[text()='确认']").click()

    if SPU != '':
        web_page.find_by_xpath("//*[text()='ID查询']//ancestor::div[@data-testid='beast-core-grid-col-wrapper']//input[contains(@placeholder,'请输入')]").input(SPU)

    if goods_num != '':
        web_page.find_by_xpath("//*[text()='货号']//ancestor::div[@data-testid='beast-core-grid-col-wrapper']//input[contains(@placeholder,'请输入')]").input(goods_num)

    if active_status != '':
        web_page.find_by_xpath("//*[text()='活动状态']//ancestor::div[@data-testid='beast-core-grid-col-wrapper']/div/div[2]").click()
        flow_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")
        Tools.down_select(web_page, active_status, flow_elems)

    if end_status != '':
        web_page.find_by_xpath("//*[text()='到期状态']//ancestor::div[@data-testid='beast-core-grid-col-wrapper']/div/div[2]").click()
        flow_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")
        Tools.down_select(web_page, end_status, flow_elems)
    
    web_page.find_by_xpath("//*[text()='查询']").click()


def get_data(web_page):

    try:
        web_page.find_by_xpath("//*[text()='暂无数据']",timeout=2)
        return "当前条件下无数据"
    except:
        web_page.find_by_xpath("//*[text()='每页']//following-sibling::div[@data-testid='beast-core-select']").click()
        elems = web_page.find_all_by_xpath("//ul//li//*[text()='40']")
       
        for elem in elems:
            if elem.is_displayed():
                elem.click()
       
        max_page = web_page.find_by_xpath("(//ul/li)[1]").get_text()
        max_page = re.search(r'\d+', max_page)
        if max_page:
            max_page = max_page.group()
            max_page = math.ceil(int(max_page) / 40)
        else:
            max_page = 1
       
        for page in range(int(max_page)):
            lazy_list = get_lazy_element_list_by_xpath(web_page, "//tbody/tr", timeout=3, 跨域全局查找='全局查找', 每次获取数量=-1)
            for index, tr in enumerate(lazy_list):
                data_list = []
                tds = tr.find_all_by_xpath("./td")
                try:
                    if len(tds)>4:
                        title_list = tds[1].find_by_xpath(".//div[contains(@class, 'oods-info_info')]").get_text()
                        title = title_list.split('\n')[0]
                        spu_id = re.search(r'\n(.*?)\n', title_list, re.S).group(1)
                        spu_id = re.search(r'\d+', spu_id, re.S).group()
                        data_list.append(title)
                        tds_data = [td.get_text() for td in tds[2:] if '共1张' not in tds[3].get_text()]
                        data_list.extend(tds_data)
                        data_list.append(spu_id)
                        databook.append_row(data_list, begin_column_name = 'A')
                    else:
                        current_row = databook.get_row_count()
                        data = databook.get_row(current_row)
                        databook.set_row(current_row+1, data,'A')
                        tds_data = [td.get_text() for td in tds]
                        databook.set_row(current_row+1, tds_data, 'C')
                except:
                    pass
            if int(max_page) > 1 and page < int(max_page) - 1:
                web_page.find_by_xpath("//ul/li[last()]").click(simulative=False)
            sleep(2)
            # 报名记录元素
            record_xpath = '//div[@id="sca-container-root"]//*[contains(@class,"index-module__routeName")][contains(text(),"报名记录")]'
            web_page.find_by_xpath(record_xpath, timeout=3).click()
            
            

def run(web_page, active_category, active_type, start_time, end_time, SPU, 
            goods_num, active_status, end_status):

    set_params(web_page, active_category, active_type, start_time, end_time, SPU, 
                goods_num, active_status, end_status)
    get_data(web_page)



def main(args):

    web_page = args.get("web_page")
    active_category = args.get("active_category", "专题活动")
    active_type = args.get("active_type", "限时秒杀")
    start_time = args.get("start_time", "2025-02-01")
    end_time = args.get("end_time", "2025-02-03")
    SPU = args.get("SPU", "")
    goods_num = args.get("goods_num", "")
    active_status = args.get("active_status", "")
    end_status = args.get("end_status", "")
    databook.clear()
    databook.set_row(1, ['商品信息', 'SKC信息', 'SKU属性集', '报名站点','日常申报价', '活动申报价/折扣率', '提交时间', '活动类型', '报名结果', '场次共用活动库存', 'SPU ID'], begin_column_name = 'A')
    # web_page = web.get_active(mode='chrome')

    run(web_page, active_category, active_type, start_time, end_time, SPU, 
            goods_num, active_status, end_status)

    
