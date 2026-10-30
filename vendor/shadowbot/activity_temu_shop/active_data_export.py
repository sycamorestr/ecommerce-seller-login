# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
import re
import math

import xbot
from xbot import print, sleep
from xbot_extensions.web_action import select_date
import xbot_visual

from .import package
from .package import variables as glv
from .utils import Tools
from .download_utils import download_handler

def active_data_export(web_page, time_range, file_folder, file_name):
    """活动数据导出"""
    
    # 获取浏览器类型
    web_type = Tools.get_web_page_product_name(web_page)

    # 判断页面是否在目标页面
    for _ in range(3):
        url = web_page.get_url()
        if 'main/act/data-full' not in url:
            # 获取页面域名
            domain_url = Tools.get_domain_from_url(url)
            #  跳转目标页面
            web_page.navigate(f'{domain_url}/main/act/data-full')
        
            # 等待页面加载完毕
            Tools.wait_loading(web_page)
        else:
            break
    
    confirm_xpath = '//button[contains(@class,"BTN_outerWrapper")]/span[text()="确认"]'

    Tools.handle_info(web_page)
    # 若时间范围存在
    if time_range:
        # 点击统计时间，展开时间框
        total_time_xpath = '//input[@placeholder="请选择日期"]'
        web_page.find_by_xpath(total_time_xpath).click()

        # 分割时间
        start = time_range.split('~')[0]
        end = time_range.split('~')[1]

        # 使用智能日期选择，进行时间选择
        time_frame_xpath = '(//div[contains(@class,"RPR_tableWrapper")])[1]'
        time_frame_ele = web_page.find_by_xpath(time_frame_xpath)
        select_date.select_date(web_page, time_frame_ele, start, end)
        # 点击确认
        confirm_sel = web_page.find_all_by_xpath(confirm_xpath)
        confirm_display = [_ for _ in confirm_sel if _.get_bounding(to96dpi=False)[2] !=0 ][0]
        confirm_display.click()

    # 点击查询
    query_xpath = '//button[contains(@class,"BTN_outerWrapper")]/span[text()="查询"]'
    web_page.find_by_xpath(query_xpath).click()

    # 等待数据加载完毕
    Tools.wait_loading(web_page)

    # 点击条数 每页显示40条
    select_num_xpath = '//li[contains(@class,"PGT_sizeChanger")]//div[@data-testid="beast-core-select-header"]'
    # 点击所选数量
    num_xpath = f'//ul[contains(@class,"ST_dropdownPanel")]/li/span[text()="500"]'

    web_page.find_by_xpath(select_num_xpath).click()
    web_page.find_by_xpath(num_xpath).click()

    # 等待数据加载完毕
    Tools.wait_loading(web_page)

    # 获取总共的商品数量
    goods_num_xpath = '//li[contains(@class,"PGT_totalText")]'
    goods_num_text = web_page.find_by_xpath(goods_num_xpath).get_text()
    # 通过正则去获取数字
    goods_num = re.search(r'(\d+)',goods_num_text).group(1)

    if int(goods_num) == 0:
        print('数据为空')
        return []

    # 判断商品页数, 向上取整
    page = math.ceil(int(goods_num) / 500)
    
    # 创建空列表
    file_paths = []

    #进行循环导出
    for p in range(page):

        # 勾选全部信息
        all_info_xpath = '//thead/tr//div[@data-testid="beast-core-checkbox-checkIcon"]'
        web_page.find_by_xpath(all_info_xpath).click()

        Tools.handle_info(web_page)

        # 进行数据导出
        data_export_xpath = '//button[contains(@class,"BTN_outerWrapper")]/span[text()="批量导出数据"]'
        web_page.find_by_xpath(data_export_xpath).click()

        # 获取信息条数
        info_xpath = '//div[contains(@class,"body-module__title")]'
        info_text = web_page.find_by_xpath(info_xpath).get_text()
        info = re.search(r'(\d+)', info_text, re.S).group(1)
        # 如果信息数量为0，则点击取消
        if info == '0':
            cancle_xpath = '//button[contains(@class,"BTN_outerWrapper")]/span[text()="取消"]'
            web_page.find_by_xpath(cancle_xpath).click()
            return []
        
        # 点击确认
        confirm_sel = web_page.find_all_by_xpath(confirm_xpath)
        confirm_display = [_ for _ in confirm_sel if _.get_bounding(to96dpi=False)[2] !=0 ][0]
        confirm_display.click()

        if p == 0:
            files_name = f'{file_name}.xlsx'
        else:
            files_name = f'{file_name}({p}).xlsx'
        # 配置下载文件
        file_path = download_handler(
            web_page=web_page,
            file_folder=file_folder,
            file_name=files_name,
        )
        file_paths.append(file_path)

        # 4. 翻页（非最后一页）
        if page > 1 and p != page - 1:
            web_page.find_by_xpath('//li[@data-testid="beast-core-pagination-next"]').click()

        return file_path
    

def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return 
    web_page = xbot.web.get_active(mode='ziniaobrowser')
    time_range = '2026-01-18~2026-01-18'
    file_folder = os.path.join(os.path.expanduser('~'), 'Desktop')
    file_name = 'xiaobu'
    active_data_export(web_page, time_range, file_folder, file_name)

    exit()


def main(args):
    # 测试模块
    test()

    # 桌面路径
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')

    # 功能模块
    web_page = args.get('web_page')
    time_range = args.get('time_range', ' ')
    file_folder = args.get('file_folder', desktop)
    file_name = args.get('file_name', '活动数据报表')

    file_path = active_data_export(web_page, time_range, file_folder, file_name)
    args['file_path'] = file_path
    