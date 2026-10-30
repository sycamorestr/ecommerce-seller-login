# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web
from xbot_extensions.web_action.select_date import select_date
from .import package
from .package import variables as glv
from .utils import Tools
from .download_utils import download_handler

def export_data(web_page, hosted_type, time_select, file_path, file_name):
    Tools.check_target_web(web_page, 'labor/settle')
    if hosted_type == '全托':
        web_page.find_by_xpath("//div[contains(@class,'container')]/div[1]//*[text()='导出数据']").click() #点击导出数据
        print('进行了点击导出数据')

        next_xpath = '//span[text()="下一条"]'# 下一条元素
        next_sel   = Tools.gen_selector(next_xpath)
        confirm_export_xpath = '//span[text()="确认导出并继续"]'    # 确认导出元素
        confirm_export_sel   = Tools.gen_selector(confirm_export_xpath)

        if web_page.wait_appear(next_sel, timeout=2):
            # 循环匹配出现的元素并进行点击
            while True:

                # 点击下一条
                if web_page.wait_appear(next_sel, timeout=1):
                    web_page.find_by_xpath(next_xpath).click()
                    continue
                # 点击确认导出并继续
                if web_page.wait_appear(confirm_export_sel, timeout=1):
                    web_page.find_by_xpath(confirm_export_xpath).click()
                    break
    elif hosted_type == '半托':
        if time_select:
            # 获取开始时间与结束时间
            start_time = time_select.split('~')[0]
            end_time = time_select.split('~')[1]

            # 点击时间框，展开时间选择
            web_page.find_by_xpath('//input[@placeholder="请选择"]', timeout=30).click()

            # 进行时间选择
            time_frame_xpath = '//section[contains(@class,"RPR_contentPickerWrapper")]/div[1]'
            time_frame_sel = web_page.find_by_xpath(time_frame_xpath)
            select_date(web_page, time_frame_sel, start_time, end_time)
        
        # 点击查询
        web_page.find_by_xpath('//div[@data-testid="beast-core-grid-col-wrapper"]/button/*[text()="查询"]').click()

        # 点击导出按钮
        export_button_xpath =  '//div[@data-testid="beast-core-box"]//span[text()="导出数据"]'
        web_page.find_by_xpath(export_button_xpath).click()

        # 点击确认
        web_page.find_by_xpath("//div[contains(@class,'body-module__footer')]/button/*[text()='确认']").click()
    
    for retry in range(100):
        target_report = web_page.find_by_xpath("//div[contains(@class,'exportHistoryList')]/div[1]//button//span[1]")
        if '生成中' in target_report.get_text():
            sleep(2)
            web_page.find_by_xpath("//span[text()='刷新']").click()
            continue
        else:
            target_report.click()
            download_handler(web_page=web_page, file_folder=file_path, file_name=file_name)
            break
    return file_path + '\\' + file_name

def main(args):
    
    web_page = args.get("web_page")
    hosted_type = args.get('hosted_type') or '全托'
    print(hosted_type)                  
    time_select = args.get('time_select') or None
    folder_path = args.get("folder_path")
    file_name = args.get("file_name", 'test.xlsx')

    # web_page = web.get_active(mode='chrome')

    file_path = export_data(web_page, hosted_type, time_select, folder_path, file_name)
    args["file_path"] = file_path

