# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
from datetime import datetime

import xbot
import xbot_visual
from xbot import print, sleep, web
from xbot_extensions.web_action import select_date 

from .import package
from .package import variables as glv
from .utils import Tools
from xbot._core.retry import Retry
from .download_utils import download_handler


def order_export(web_page, time_select, order_type, order_state, cancled, export_fields, file_folder, file_name, over_time: int = 300):
    """订单导出"""
    # 获取浏览器名称
    web_type = Tools.get_web_page_product_name(web_page)

    # 判断是否为目标页面
    url = web_page.get_url()
    if 'mmsos/export-order.html' not in url:
        # 获取域名
        domain_url = Tools.get_domain_from_url(url)
        # 进行网页跳转
        web_page.navigate(f'{domain_url}/mmsos/export-order.html')

    # 点击时间框展开时间
    time_frame_xpath = '//div[contains(@class,"IPT_inputBlockCell")]/input[@placeholder="开始时间  ~  结束时间"]'
    web_page.find_by_xpath(time_frame_xpath).click()

    if time_select:

        # 对时间进行分割
        start_time = time_select.split('~')[0]
        end_time = time_select.split('~')[1]

        # 使用智能日期进行时间选择
        time_xpath = '//div[contains(@class,"RPR_outerPickerWrapper")]'
        time_sel = web_page.find_by_xpath(time_xpath)
        select_date.select_date(web_page, time_sel, start_time, end_time)
        
        # 点击确定
        web_page.find_by_xpath('//span[text()="确认"]').click()
    
    # 订单类型
    for _ in Retry(timeout=20, ignore_exception=True):
        if order_type:
            # 点击展开订单类型选择
            order_type_frame_xpath = '//div[contains(@class,"IPT_autosizeWrapper")]'
            web_page.find_by_xpath(order_type_frame_xpath, timeout=3).click(anchor=('middleRight', 0, 0))
            
            all_check_xpath = '//ul[@role="listbox"]/li[contains(.,"全选")]'
            all_check_state = web_page.find_by_xpath(all_check_xpath).get_attribute('data-checked')
            if '全选' in order_type:
                if all_check_state == 'false':
                    web_page.find_by_xpath(all_check_xpath).click()
            else:
                if all_check_state == 'true':
                    web_page.find_by_xpath(all_check_xpath).click()
                elif all_check_state == 'false':
                    web_page.find_by_xpath(all_check_xpath).click()
                    sleep(1)
                    web_page.find_by_xpath(all_check_xpath).click()
                # 获取所有li的信息
                lis = web_page.find_all_by_xpath('//ul[contains(@class,"ST_dropdownPanel")]/li')
                for li in lis:
                    
                    # 获取文本信息,进行匹配点击
                    li_text = li.find_by_xpath('.//span').get_text()
                    li_class = li.get_attribute('data-checked')

                    # 没被选中则点击
                    if li_text in order_type and 'true' not in li_class:
                        li.click()
                        if li_text == '全选':
                            break
                    
                    # 没在参数中但被选中的则取消
                    if li_text not in order_type and 'true' in li_class:
                        li.click()
            web_page.find_by_xpath('(//*[contains(text(),"订单类型")])[1]').click()
            break
        
                
    # 订单状态选择
    if order_state:
        # 点击打开订单状态下拉框
        order_state_xpath = '(//div[contains(@class,"IPT_inputBlockCell")]/input[@placeholder="请选择"])[1]'
        web_page.find_by_xpath(order_state_xpath).click()

        # 进行状态选择
        order_xpath = f'//ul[contains(@class,"ST_dropdownPanel")]//span[text()="{order_state}"]'
        web_page.find_by_xpath(order_xpath).click()

    # 已取消商品选择
    if cancled:
        cancled_xpath = f'//div[text()="{cancled}"]'
        web_page.find_by_xpath(cancled_xpath).click()

    # 获取任务编号
    tast_num_xpath = '//tbody/tr[1]/td[1]'
    tast_num_sel = web_page.find_all_by_xpath(tast_num_xpath, timeout=1)
    if len(tast_num_sel) > 0:
        tast_num = tast_num_sel[0].get_text()
    else:
        tast_num = None
    print('导出前文件的任务编码:', tast_num)

    # 导出字段
    if export_fields:
        # 获取全部label信息
        label_info_xpath = '//div[@data-testid="beast-core-grid-col-wrapper" and contains(.,"导出字段")]/following-sibling::div//label'
        label_info_sel = web_page.find_all_by_xpath(label_info_xpath)[1:]
        if "全选" in export_fields:
            for label_sel in label_info_sel:
                if label_sel.get_attribute('data-checked') == 'false':
                    label_sel.click()
        else:
            for label_sel in label_info_sel:
                if label_sel.get_text() in export_fields:
                    if label_sel.get_attribute('data-checked') == 'false':
                        label_sel.click()
                else:
                    if label_sel.get_attribute('data-checked') == 'true':
                        label_sel.click()

    # 点击导出
    export_button_xpath = '//span[text()="确认导出"]'
    web_page.find_by_xpath(export_button_xpath).click()

    # 等待下载任务生成
    Tools.wait_loading(web_page)

    # 判断是否生成了下载任务
    for _ in range(120):
        current_num_sel = web_page.find_all_by_xpath(tast_num_xpath, timeout=1)
        if len(current_num_sel) > 0:
            current_num = current_num_sel[0].get_text()
            if current_num != tast_num:
                break
        sleep(1)
    print('下载的文件任务编码:', current_num)

    # 进行匹配下载订单报表
    trs = web_page.find_all_by_xpath('//tbody/tr')

    for _ in Retry(timeout=over_time, ignore_exception=True):
        # 等待下载状态为已完成
        download_state = trs[0].find_by_xpath('./td[5]').get_text()

        #  状态为已完成
        if download_state == '已完成':
            
            # 进行下载
            trs[0].find_by_xpath('./td[6]//span[text()="下载"]').click()
            break
        sleep(1)
    
    file_path = download_handler(
        web_page,
        file_folder,
        file_name
    )

    return file_path
       

def test():
    """测试模块"""
    if 'xbot_extensions' in __file__:
        return 
    
    web_page = web.get_active(mode='ziniaobrowser')
    time_select = '2025-08-12~2025-09-13'
    order_type = ['卖家履约订单']
    order_state = '全部'
    cancled = '过滤'
    export_fields = ['全选']
    file_folder = os.path.join(os.path.expanduser('~'), 'Desktop')
    file_folder = r'C:\Users\Administrator\Desktop\店铺数据下载'
    file_name = '收支明细.xlsx'

    order_export(web_page, time_select, order_type, order_state, cancled, export_fields, file_folder, file_name)
    exit()


def main(args):

    # 测试模块
    test()

    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')

    # 功能模块
    web_page = args.get('web_page')
    time_select = args.get('time_select')
    order_type = args.get('order_type', ['全选'])
    order_state = args.get('order_state', '')
    cancled = args.get('cnacled', '')
    export_fields = args.get('export_fields', '')
    file_folder = args.get('file_folder', desktop)
    file_name = args.get("file_name")
    over_time = args.get('over_time') or 300
    if isinstance(over_time, str):
        over_time = int(over_time)

    file_path = order_export(
        web_page, time_select, order_type, order_state, cancled, export_fields, file_folder, file_name
        )
    args['file_path'] = file_path