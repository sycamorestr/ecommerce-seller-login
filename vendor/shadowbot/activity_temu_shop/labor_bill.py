# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os

import xbot  # type: ignore
from xbot import print, sleep, web  # type: ignore
from xbot_extensions.web_action import select_date
from . import package
from .package import variables as glv
from .utils import Tools
from xbot.selector import Selector
from .download_utils import download_handler
import threading

def gen_selector(xpath):
    xpaths = xpath.split(">>")
    data =  {'id': 'ifream-xpath', 'name': 'ifream-xpath', 'type': 'simple', 'xpath': {'enable': 'true', 'segments': xpaths}}
    selector = Selector(data)
    return selector


def download_labor_bill(
    web_page,
    start_time,
    end_time,
    capital_flow,
    financial_type,
    fund_mix,
    fund_max,
    file_folder,
    report_type,
    file_name,
    time_out=120
) -> list:
    """/labor/bill 下载账单
    :param web_page:
    :param start_time: str, 开始时间, 格式为 'YYYY-MM-DD'
    :param end_time: str, 结束时间, 格式为 'YYYY-MM-DD'
    :param capital_flow: str, 资金流向
    :param financial_type: list, 账务类型
    :param fund_mix: str, 收入金额, 资金下限
    :param fund_max: str, 收入金额, 资金上限
    :param file_folder: str, 文件保存夹
    :param report_type: str, 报表类型, "全球,美国,欧区,卖家中心"
    """

    # 获取店铺名称
    shop_name_xpath = '(//div[contains(@class, "account-info_accountInfo")]//span)[1]'
    shop_name = web_page.find_by_xpath(shop_name_xpath).get_text().strip()

    if report_type.strip() == "":
        report_type = ["卖家中心", "全球", "欧区", "美国"]
    else:
        report_type = [item.strip() for item in report_type.strip().split(",")]

    # 判断页面是否正常
    Tools.check_web(web_page, "labor/bill")

    # 消除弹窗
    Tools.handle_info(web_page)
    
    # 点击时间框
    time_xpath = '//input[@placeholder="请选择"]'
    time_display = web_page.find_all_by_xpath(time_xpath)
    time_display = [_ for _ in time_display if _.get_bounding(to96dpi=False)[2] != 0][0]
    time_display.click()

    # 选择时间
    date_frame = web_page.find_by_xpath('//*[@data-testid="beast-core-rangePicker-dropdown-contentRoot"]')
    select_date.select_date(web_page, date_frame, start_time, end_time)
    web_page.find_by_xpath("//span[text()='确认']").click()

    # 选择资金流向
    if capital_flow:
        web_page.find_by_xpath(
            "//*[text()='资金流向']//ancestor::div[@data-testid='beast-core-grid-col-wrapper'][2]/div[1]/div[2]"
        ).click()
        capital_flow_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")
        Tools.click_dropdown(web_page, capital_flow, capital_flow_elems)

    # 选择账务类型
    if financial_type:
        web_page.find_by_xpath(
            "//*[text()='账务类型']//ancestor::div[@data-testid='beast-core-grid-col-wrapper'][2]/div[1]/div[2]"
        ).click()
        financial_type_elems = web_page.find_all_by_xpath("//ul[@role='listbox']//span")
        Tools.click_dropdown(web_page, financial_type, financial_type_elems)

    # 选择收入金额
    fund_input_list = web_page.find_all_by_xpath("//input[@placeholder='请输入']")

    if fund_mix != "":
        fund_input_list[0].input(fund_mix)
    if fund_max != "":
        fund_input_list[1].input(fund_max)

    # 执行导出动作
    web_page.find_by_xpath("//span[text()='查询']").click()
    web_page.find_by_xpath("//span[text()='导出']").click()
    web_page.find_by_xpath('//*[text()="导出列表 + 账务详情"]').click()
    web_page.find_by_xpath("//span[text()='确认']").click()

    # 判断是否重复导出
    flag_xpath = '//div[1][normalize-space(.)="当前筛选条件的导出任务已创建, 请勿重复创建"]'
    flag = web_page.wait_appear(gen_selector(flag_xpath), timeout=2)
    if flag:
        web_page.wait_disappear(gen_selector(flag_xpath), timeout=4)
        export_history_xpath = '//span[text()="导出历史"]'
        web_page.find_by_xpath(export_history_xpath, timeout=2).click()

    # 等待导出完成, 并下载文件
    sleep(2)

    save_path_list = []

    for _ in range(100):
        target_report: list = web_page.find_all_by_xpath(
            "//div[contains(@class,'exportHistoryList')]/div[1]//button//span[1]"
        )
        if any("生成中" in elem.get_text() for elem in target_report):
            sleep(2)
            web_page.find_by_xpath("//span[text()='刷新']").click()
            continue

        # 找到目标导出的大框依次遍历
        export_history_export_parent_xpath = f'(//div[contains(@class, "export-history_list") and contains(., "{start_time} 00:00:00 ~ {end_time} 23:59:59") and contains(., "列表数据、财务明细")])[1]'
        export_history_export_parent_element = web_page.find_by_xpath(export_history_export_parent_xpath)
              

        for report_item in report_type:
            try:
                download_btn = export_history_export_parent_element.find_by_xpath(f'.//*[contains(text(), "{report_item}")]', timeout=3)
                report_name = download_btn.get_text()
                if file_name == '':
                    save_name = f"{shop_name}-{report_name}-{start_time}-{end_time}.xlsx"
                    file_path = file_folder + '\\' + save_name
                else:
                    save_name = file_name.replace('.xlsx','') + '-' + report_name + '.xlsx'
                    file_path = file_folder + '\\' + save_name

                download_btn.click()

                # 下载 当前页面下载, 其他的需要跳转到temu下载
                if report_item != "卖家中心":
                    temu_web_page = xbot.web.get_active(mode=web_page.product_name)
                    temu_web_page.wait_load_completed()

                    # 判断是否需要勾选授权
                    core_box_xpath = '//label//*[@data-testid="beast-core-box"]'
                    core_box_sel = temu_web_page.find_all_by_xpath(core_box_xpath, timeout=3)
                    core_box_dis = [_ for _ in core_box_sel if _.get_bounding(to96dpi=False)[2] != 0]

                    confirm_to_xpath = '//button//*[text()="确认授权并前往"]'
                    confirm_to_sel = temu_web_page.find_all_by_xpath(confirm_to_xpath)
                    
                    if len(confirm_to_sel) > 0:
                        if len(core_box_dis) > 0:
                            core_box_dis[0].click()

                        # 进行点击确认授权并前往
                        confirm_to_sel = temu_web_page.find_all_by_xpath(confirm_to_xpath)
                        confirm_to_dis = [_ for _ in confirm_to_sel if _.get_bounding(to96dpi=False)[2] != 0][0]
                        confirm_to_dis.click()

                    # 判断是否要切换店铺
                    if len(temu_web_page.find_all_by_xpath('//span[text()="确认切换"]', timeout=15)) > 0:
                        temu_web_page.find_by_xpath('//span[text()="确认切换"]').click()
                    time_out = int(time_out)
                    download_handler(
                        web_page, file_folder, save_name
                    )
                    temu_web_page.close()
                else:
                    time_out = int(time_out)
                    download_handler(
                        web_page, file_folder, save_name
                    )
                    
                save_path_list.append(file_path)
            except Exception as e:
                print(e)
                print(f"导出 {report_item} 账单失败")

        break
    web_page.find_by_xpath('//div[text()="账务明细"]').click()
    return save_path_list


def check_saler_center(
        web_page,
        start_time,
        end_time,
        capital_flow,
        financial_type,
        fund_mix,
        fund_max,
        file_folder,
        report_type,
        file_name,
        time_out=120
    ):
    # 设置子线程停止标志
    is_completed = False

    def wait_saler_center(
        url: str,
        interval: float = 0.3
    ):
        """
        循环判断当前页面是否为卖家中心页面，如果是，则进行验证

        参数：
            url: 卖家中心验证url标识
            interval: 检查间隔
        """

        nonlocal is_completed

        while not is_completed:
            target_url = web_page.get_url()
            if url in target_url:
                Tools.check_saler_center(web_page)

            sleep(interval) # 间隔等待
    
    confirm_thread = threading.Thread(
        target=wait_saler_center,
        kwargs={
            "url": 'authentication',
        },
        daemon=True
    )
    confirm_thread.start()

    file_path = download_labor_bill(
            web_page,
            start_time,
            end_time,
            capital_flow,
            financial_type,
            fund_mix,
            fund_max,
            file_folder,
            report_type,
            file_name,
            time_out
        )

    # 设置线程完成标志
    is_completed =True
    confirm_thread.join()

    return file_path


def main(args):
    
    web_page = args.get("web_page", "")
    start_time = args.get("start_time", "2025-04-01")
    end_time = args.get("end_time", "2025-04-30")
    capital_flow = args.get("capital_flow", "流出")
    financial_type = args.get("financial_type", ["提现", "结算"])
    fund_mix = args.get("fund_mix", "10")
    fund_max = args.get("fund_max", "100")
    file_folder = args.get("file_folder", r"C:\Users\wangkai\Downloads\新建文件夹2")
    report_type = args.get("report_type", "")
    file_name = args.get('file_name') or ''
    time_out = args.get('time_out') or 120

    # web_page = web.get_active(mode='superbrowser')
    save_path_list = check_saler_center(
        web_page,
        start_time,
        end_time,
        capital_flow,
        financial_type,
        fund_mix,
        fund_max,
        file_folder,
        report_type,
        file_name,
        time_out
    )
    args["save_path_list"] = save_path_list
