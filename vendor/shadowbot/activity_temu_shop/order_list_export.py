# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
import re
import math
from datetime import datetime

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from .utils import Tools
from .download_utils import download_handler


def time_select(web_page, start_time, end_time):
    """进行日期选择。

    页面约定：
    1. 开始时间与结束时间在同一大容器下的两个子容器（section[1] 为开始，section[2] 为结束）。
    2. 同一年且连续月份（如 1-2、2-3）时：开始时间只有左箭头，结束时间只有右箭头；任一方等于输入即停止，再进入第三步。
    2.1 开始月与结束月相同时：只需任一面板出现该月即停止，不进行第三步；开始日、结束日均在显示该月的同一子容器内点击。
    3. 开始/结束月份独立：点开始箭头只改开始月份，点结束箭头只改结束月份。
    4. 开始日期用第一个日期选择框(div[1])，结束日期用第二个(div[2])；同月时两者在同一子容器内点击。
    """

    # 处理日期，分别获取开始时间和结束时间的年月日
    start_dt = datetime.strptime(start_time.strip(), '%Y-%m-%d')
    end_dt = datetime.strptime(end_time.strip(), '%Y-%m-%d')

    start_year, start_month, start_day = start_dt.year, start_dt.month, start_dt.day
    end_year, end_month, end_day = end_dt.year, end_dt.month, end_dt.day

    # 同一容器内：第一个子容器为开始时间，第二个为结束时间
    # 开始时间左/右箭头（连续月份时开始只有左箭头）
    start_left_arrow_xpath = '((//section[contains(@class,"RPR_panelHeader")])[1]/*[local-name()="svg"])[1]'
    start_right_arrow_xpath = '((//section[contains(@class,"RPR_panelHeader")])[1]/*[local-name()="svg"])[last()]'
    # 结束时间左/右箭头（连续月份时结束只有右箭头）
    end_left_arrow_xpath = '((//section[contains(@class,"RPR_panelHeader")])[2]/*[local-name()="svg"])[1]'
    end_right_arrow_xpath = '((//section[contains(@class,"RPR_panelHeader")])[2]/*[local-name()="svg"])[last()]'

    # 年份：同一容器下两个子输入
    start_year_frame_xpath = '(//div[@data-testid="beast-core-rangePicker-dropdown-contentRoot"]//input[@data-testid="beast-core-select-htmlInput"])[1]'
    end_year_frame_xpath = '(//div[@data-testid="beast-core-rangePicker-dropdown-contentRoot"]//input[@data-testid="beast-core-select-htmlInput"])[2]'
    start_year_dropdown_xpath = f'//ul[contains(@class,"ST_dropdownPanel")]/li/span[contains(text(),"{start_year}")]'
    end_year_dropdown_xpath = f'//ul[contains(@class,"ST_dropdownPanel")]/li/span[contains(text(),"{end_year}")]'

    start_year_frame = web_page.find_by_xpath(start_year_frame_xpath)
    end_year_frame = web_page.find_by_xpath(end_year_frame_xpath)

    if str(start_year) not in start_year_frame.get_text():
        start_year_frame.click()
        sleep(0.2)
        web_page.find_by_xpath(start_year_dropdown_xpath).click()
        sleep(0.2)

    if str(end_year) not in end_year_frame.get_text():
        end_year_frame.click()
        sleep(0.2)
        web_page.find_by_xpath(end_year_dropdown_xpath).click()
        sleep(0.2)

    # 月份显示：第一个子容器为开始月份，第二个为结束月份
    start_month_xpath = '(//span[contains(@class,"RPR_dateText")])[1]'
    end_month_xpath = '(//span[contains(@class,"RPR_dateText")])[2]'

    def _parse_web_month(text):
        m = re.search(r'(\d+)\s*月', str(text))
        return int(m.group(1)) if m else None

    def _read_months():
        ws = web_page.find_by_xpath(start_month_xpath).get_text()
        we = web_page.find_by_xpath(end_month_xpath).get_text()
        return _parse_web_month(ws), _parse_web_month(we)

    # 同一年且开始月与结束月相同（同一个月内选区间）
    same_month = start_year == end_year and start_month == end_month
    # 同一年且连续月份（如 1-2、2-3）时：开始只有左箭头，结束只有右箭头
    same_year_consecutive = (
        start_year == end_year and (end_month - start_month) == 1
    )

    web_start_month_num, web_end_month_num = _read_months()
    max_steps = 24

    if same_month or same_year_consecutive:
        # 连续/同月：只点开始左箭头或结束右箭头，直到有一方（开始月或结束月）等于输入即停止
        for _ in range(max_steps):
            if web_start_month_num is None or web_end_month_num is None:
                break
            if web_start_month_num == start_month or web_end_month_num == end_month:
                break
            if web_start_month_num > start_month:
                web_page.find_by_xpath(start_left_arrow_xpath).click()
                sleep(0.3)
                web_start_month_num, web_end_month_num = _read_months()
                continue
            if web_end_month_num < end_month:
                web_page.find_by_xpath(end_right_arrow_xpath).click()
                sleep(0.3)
                web_start_month_num, web_end_month_num = _read_months()
                continue
            break

    if same_month:
        # 同月：只需任一面板出现该月即可，不进行第三步；开始日、结束日都在显示该月的子容器内点击
        web_start_month_num, web_end_month_num = _read_months()
        day_panel = 1 if web_start_month_num == start_month else 2
        start_day_cell_xpath = (
            '//section[contains(@class,"RPR_contentPickerWrapper")]/div[{}]//table//td'
            '[not(contains(@class,"outOfMonth")) and normalize-space()="{}"]'
        ).format(day_panel, start_day)
        web_page.find_by_xpath(start_day_cell_xpath).click()
        sleep(0.2)
        end_day_cell_xpath = (
            '//section[contains(@class,"RPR_contentPickerWrapper")]/div[{}]//table//td'
            '[not(contains(@class,"outOfMonth")) and normalize-space()="{}"]'
        ).format(day_panel, end_day)
        web_page.find_by_xpath(end_day_cell_xpath).click()
        return

    # 第三步：不连续的时间选择月份（用各自面板箭头把开始月、结束月都调到目标）
    web_start_month_num, web_end_month_num = _read_months()
    _steps = 0
    while web_start_month_num is not None and web_start_month_num != start_month and _steps < max_steps:
        _steps += 1
        if web_start_month_num < start_month:
            web_page.find_by_xpath(start_right_arrow_xpath).click()
        else:
            web_page.find_by_xpath(start_left_arrow_xpath).click()
        sleep(0.3)
        web_start_month_num, web_end_month_num = _read_months()

    _steps = 0
    while web_end_month_num is not None and web_end_month_num != end_month and _steps < max_steps:
        _steps += 1
        if web_end_month_num < end_month:
            web_page.find_by_xpath(end_right_arrow_xpath).click()
        else:
            web_page.find_by_xpath(end_left_arrow_xpath).click()
        sleep(0.3)
        web_start_month_num, web_end_month_num = _read_months()

    # 日期选择：开始日期在第一个日期框(div[1])，结束日期在第二个(div[2])
    start_day_cell_xpath = (
        '//section[contains(@class,"RPR_contentPickerWrapper")]/div[1]//table//td'
        '[not(contains(@class,"outOfMonth")) and normalize-space()="{}"]'
    ).format(start_day)
    web_page.find_by_xpath(start_day_cell_xpath).click()
    sleep(0.2)

    end_day_cell_xpath = (
        '//section[contains(@class,"RPR_contentPickerWrapper")]/div[2]//table//td'
        '[not(contains(@class,"outOfMonth")) and normalize-space()="{}"]'
    ).format(end_day)
    web_page.find_by_xpath(end_day_cell_xpath).click()

def order_list_export(web_page, order_type, order_state, time_range, file_folder, file_name):
    """订单列表导出"""

    # 检查网页是否在订单列表页面
    Tools.check_target_web(web_page, 'mmsos/orders.html')

    # 检测是否进入商家页面
    Tools.check_saler_center(web_page)

    # 消除弹窗信息
    Tools.handle_info(web_page)

    # 点击订单列表类型
    order_type_xpath = f'//div[contains(@class,"TAB_tabContentInnerContainer")]//div[text()="{order_type}"]'
    web_page.find_by_xpath(order_type_xpath).click()

    # 点击订单状态
    order_state = order_state + '('
    order_state_xpath = f'//div[contains(@class,"TAB_tabContentInnerContainer")]//div[contains(text(),"{order_state}")]'
    order_state_sel = web_page.find_by_xpath(order_state_xpath)
    Tools.see_element(order_state_sel, 'center')
    sleep(2)
    order_state_sel.click()

    # 是否有时间参数填入
    if time_range:

        # 取得开始时间和结束时间
        start_time = time_range.split('~')[0]
        end_time = time_range.split('~')[1]
        
        # 点击时间框展开时间选择
        time_frame_xpath = '//input[@placeholder="开始时间  ~  结束时间"]'
        web_page.find_by_xpath(time_frame_xpath).click()
        # 进行时间选择
        time_select(web_page, start_time, end_time)

        # 点击确认
        confirm_xpath = '//footer[contains(@class,"RPR_footerWrapper")]//span[text()="确认"]'
        web_page.find_by_xpath(confirm_xpath).click()

        # 点击查询
        query_xpath = '//button/span[text()="查询"]'
        web_page.find_by_xpath(query_xpath).click()

        # 等待数据加载完毕
        Tools.wait_loading(web_page,appear_time=1)

    # 进行页码选择
    page_frame_xpath = '//li[contains(text(),"共有 ")]/following-sibling::li/div'
    web_page.find_by_xpath(page_frame_xpath).click()

    # 切换页码显示500条数据""
    page_num_xpath = '//ul[@role="listbox"]/li/span[text()="500"]'
    page_num = web_page.find_by_xpath(page_num_xpath).click()

    # 获取总数
    total_data_text = web_page.find_by_xpath('//li[contains(text(),"共有 ")]').get_text()
    total_data = int(re.search(r'\d+', total_data_text, re.S).group(0))

    # 数据为0则退出
    if total_data == 0:
        print('暂无订单信息')
        return

    # 获取页码
    page = math.ceil(total_data / 500)

    # 处理小于等于1000条数据的情况
    if total_data <= 1000:
        for i in range(page):

            # 点击勾选全部数据框
            all_data_frame_xpath = '//thead/tr[1]/th[1]//input/following-sibling::div'
            web_page.find_by_xpath(all_data_frame_xpath).click(simulative=False)

            # 进行换页
            if page > 1 and i != page-1:
                web_page.find_by_xpath('//li[@data-testid="beast-core-pagination-next"]').click()

        # 点击导出订单
        oreder_export_button_xpath = '//span[text()="导出订单"]'
        web_page.find_by_xpath(oreder_export_button_xpath, timeout=5).click()

        # 进行订单确认
        confirm_export_xpath = '//button/span[text()="确认导出"]'
        web_page.find_by_xpath(confirm_export_xpath).click()

        # 进行下载
        file_path = download_handler(
            web_page=web_page,
            file_folder=file_folder,
            file_name=file_name
        )

        return [file_path]
    elif total_data > 1000:

        # 取消跨页勾选
        web_page.find_by_xpath('//*[text()="跨页勾选"]/following-sibling::div').click()

        file_path_list = []

        for i in range(page):

            # 点击勾选全部数据框
            all_data_frame_xpath = '//thead/tr[1]/th[1]//input/following-sibling::div'
            web_page.find_by_xpath(all_data_frame_xpath).click()

            # 点击导出订单
            oreder_export_button_xpath = '//span[text()="导出订单"]'
            web_page.find_by_xpath(oreder_export_button_xpath, timeout=5).click()

            # 进行订单确认
            confirm_export_xpath = '//button/span[text()="确认导出"]'
            web_page.find_by_xpath(confirm_export_xpath).click()

            j = i + 1
            current_file_name = file_name + '-' + str(j)
            # 进行下载
            file_path = download_handler(
                web_page=web_page,
                file_folder=file_folder,
                file_name=current_file_name
            )

            file_path_list.append(file_path)

            # 进行换页
            if page > 1 and i != page-1:
                web_page.find_by_xpath('//li[@data-testid="beast-core-pagination-next"]').click()

        return file_path_list


def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return

    web_page = xbot.web.get_active(mode='chrome')
    order_type = '卖家履约订单'
    order_state = '全部'
    time_range = '2025-10-01~2026-3-10'
    file_folder = os.path.join(os.path.expanduser('~'), 'Desktop')
    file_name = '订单列表'

    file_path = order_list_export(web_page, order_type, order_state, time_range, file_folder, file_name)
    print(file_path)
    exit()

def main(args):
    # 测试功能
    test()

    # 获取桌面路径
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    # 功能模块
    web_page = args.get('web_page')
    order_type = args.get('order_type')
    order_state = args.get('order_state')
    time_range = args.get('time_range','')
    file_folder = args.get('file_folder', desktop)
    file_name = args.get('file_name')

    file_path = order_list_export(web_page, order_type, order_state, time_range, file_folder, file_name)
    args['file_path'] = file_path
