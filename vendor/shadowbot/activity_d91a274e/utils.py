# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

def main(args):
    pass
 
def select_datetime(date_time, web_page, current_year_month_element_name, pre_month_element_name, next_month_element_name,date_element_name):
    """
    date_time：待选择的日期【2022-12-12】
    web_page：网页对象
    current_year_month_element_name：当前年月元素名称
    pre_month_element_name：上一月元素名称
    next_month_element_name：下一月元素名称
    date_element_name：目标日期元素名称
    """
    target_year = int(date_time.split('-')[0])
    target_month = int(date_time.split('-')[1]) if date_time.split('-')[1][0] != 0 else int(date_time.split('-')[1][0])
    target_date = int(date_time.split('-')[-1]) if date_time.split('-')[-1][0] != 0 else int(date_time.split('-')[-1][0])
    glv['date'] = target_date
    glv['year_month'] = date_time[:7]
    select_year(target_year,web_page,current_year_month_element_name,pre_month_element_name, next_month_element_name)
    select_month(target_month,web_page,current_year_month_element_name,pre_month_element_name, next_month_element_name)
    select_date(web_page,date_element_name)

def select_year(target_year,web_page,current_year_month_element_name,pre_month_element_name, next_month_element_name):
    pre_month = web_page.find(pre_month_element_name)
    next_month = web_page.find(next_month_element_name)
    while True:
        current_year_month = web_page.find(current_year_month_element_name).get_text()
        current_year = int(current_year_month.split('-')[0])
        if current_year > target_year:
            pre_month.click()
        elif current_year < target_year:
            next_month.click()
        else:
            break
        
def select_month(target_month, web_page,current_year_month_element_name,pre_month_element_name, next_month_element_name):
    pre_month = web_page.find(pre_month_element_name)
    next_month = web_page.find(next_month_element_name)
    while True:
        current_year_month = web_page.find(current_year_month_element_name).get_text()
        current_month = int(current_year_month.split('-')[-1]) if current_year_month.split('-')[-1][0] != 0 else int(current_year_month.split('-')[-1])
        if current_month > target_month:
            pre_month.click()
        elif current_month < target_month:
            next_month.click()
        else:
            break

def select_date(web_page,date_element_name):
    web_page.find(date_element_name).click()


def get_page_data(web_page,similer_element_group):
    result = {}
    similer_elements = web_page.find_all(similer_element_group)
    for element in similer_elements:
        field = element.get_text().replace('','').replace(' \ue7aa','')
        element_parent = element.parent()
        data = element.next_sibling().get_text()
        result[field] = data if ',' not in data else data.replace(',','')
    return result