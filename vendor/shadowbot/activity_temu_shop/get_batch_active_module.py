# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from .import package
from .package import variables as glv
from .utils import Tools

def handle_dropdown(target_text, elem_list):
    """处理横像复选框"""
    for elem in elem_list:
        check_box_elem = elem.find_by_xpath("./..")
        if elem.get_text() == target_text and check_box_elem.get_attribute('data-checked') == 'false':
            elem.click()
            break

def get_active_module(web_page, active_type, active_site, SPU, file_folder, file_name):
    Tools.check_web(web_page, 'activity/marketing-activity')

    web_page.find_by_xpath("//span[text()='批量报名活动']").click()
    sleep(2)
    """选择报名活动类型"""
    elem_list = web_page.find_all_by_xpath("//label[text()='报名活动类型']/../..//following-sibling::div//label/div[2]")
    if active_type != '全部' and active_type != "":
        if isinstance(active_type, str):
            handle_dropdown(active_type, elem_list)
        elif isinstance(active_type, list):
            for text in active_type:
                handle_dropdown(text, elem_list)

    web_page.find_by_xpath("//*[text()='选择活动站点']/../..//following-sibling::div").click()
    flow_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")

    if isinstance(active_site, list):
        for tar_site in active_site:
            Tools.down_select(web_page, tar_site, flow_elems)
    else:
        Tools.down_select(web_page, active_site, flow_elems)

    web_page.find_by_xpath("//*[text()='选择商品']").click(simulative=False)
    
    if isinstance(SPU, list):
        SPU = ",".join(SPU)
    web_page.find_by_xpath("//input[contains(@placeholder,'可通过SPU ID查询')]").input(SPU)
    web_page.find_by_xpath("//*[text()='查询']").click()
    web_page.find_by_xpath("//*[text()='全选']").click()
    web_page.find_by_xpath("//*[text()='确认']").click()
    file_path = web_page.find_by_xpath("//*[text()='生成模板']").download(file_folder=file_folder, file_name=file_name)
    return file_path

def main(args):
    
    web_page = args.get("web_page")
    active_type = args.get("active_type", '清仓甩卖')
    active_site = args.get("active_site", ['美国站', '加拿大站'])
    SPU = args.get("SPU",['105022240', '199744500'])
    file_folder = args.get("file_folder", r"C:\Users\11758\Desktop")
    file_name = args.get("file_name", 'test111.xlsx')
    # web_page = web.get_active(mode='chrome')
    file_path= get_active_module(web_page, active_type, active_site, SPU,file_folder, file_name)
    args['file_path'] = file_path