# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep, web, win32
from .import package
from .package import variables as glv
from .utils import select_click
from xbot_extensions.web_action.select_date import select_date
from .activities_utils import download_handler
from .create_element import create_selector
from .utils import handler_container


def configure(web_page, report_type, month, year, file_fold, file_name, account_type='标准订单'):

    sign = web_page.find_all('所有商城', timeout=5)
    if len(sign) > 0:
        try:
            web_page.find('report_lib_account_type_new').click()
            account_type_list = web_page.find_all("report_lib_account_type_list_new", timeout=3)
            keyword_list = ['全部', '标准订单', '发票支付订单']
            select_click(account_type, keyword_list, account_type_list)
        except:
            pass
    else:
        try:
            web_page.find("report_lib_account_type").click()
            account_type_list = web_page.find_all("report_lib_account_type_list", timeout=3)
            keyword_list = ['全部', '标准订单', '发票支付订单']
            select_click(account_type, keyword_list, account_type_list)
        except:
            pass

    if len(sign) > 0:
        #查看类型选择
        web_page.find("report_lib_report_type_click_new").click()
        report_type_list = web_page.find_all("report_lib_report_type_list_new")
        keyword_list = ['汇总', '交易', '延迟交易']
        select_click(report_type, keyword_list, report_type_list)
    else:
        #查看类型选择
        web_page.find("report_lib_report_type_click").click()
        report_type_list = web_page.find_all("report_lib_report_type_list")
        keyword_list = ['汇总', '交易', '延迟交易']
        select_click(report_type, keyword_list, report_type_list)

    #月选择
    if month != '':
        web_page.find("report_lib_month").click()
        web_page.find("report_lib_month_select").click()
        month_elem_list = web_page.find_all("report_lib_month_list")
        keyword_list = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
        select_click(month, keyword_list, month_elem_list)

    #年选择
    if year != '':
        web_page.find("report_lib_year_select").click()
        year_elem_list = web_page.find_all("report_lib_year_list")
        for year_elem in year_elem_list:
            if year_elem.get_text() == year:
                year_elem.click()
                break
    
    #点击请求报告
    web_page.find("res_report").click()
    
    #验证是否可下载
    # for retry in range(100):
    #     try:
    #         web_page.find("report_lib_download_mark",timeout=5)
    #         break
    #     except:
    #         web_page.find("report_lib_download").click()
    #         continue
    # # web_page.find("report_lib_download").click()  

    # download_handler(web_page, web_page.find("report_lib_download"), file_fold, file_name, 300)
    #新版
    download_button = None
    has_modify_button_in_last_retry = False  # 记录最后一次循环是否检测到修改按钮
    
    for retry in range(20): # 最多尝试20次
        print(f"开始第 {retry + 1}/20 次检查...")
        
        # 状态1: 先检查"一分钟后重试"的特定错误，若有则刷新网页 
        try:
            error_locator = create_selector('//*[local-name()="kat-alert"][@variant="danger" and @size="small" and not(@dismissed)]',name = '异常情况')
            error_message = web_page.find(error_locator, timeout=1)
            if web_page.wait_appear(error_message,timeout = '3'):
                print("检测到'一分钟后重试'错误。将等待60秒...")
                sleep(60) # 等待一分多钟
                web_page.reload()
                sleep(2)  # 等待页面加载
                continue 
        except:
            pass
        
        # 状态2: 每两次循环检查一次修改按钮（第2、4、6、8、10次）
        # 如果存在修改按钮，刷新网页；最后一次刷新后仍存在则抛出异常
        if (retry + 1) % 2 == 0:  # 第2、4、6、8、10次循环
            try:
                modify_button_selector = create_selector(
                    '//*[local-name()="kat-table-body"]/*[local-name()="kat-table-row"][1]//*[contains(@class, "header-cell-report-action")]//*[local-name()="kat-dropdown-button"]',
                    name='修改按钮'
                )
                modify_button = web_page.find(modify_button_selector, timeout=2)
                if modify_button:
                    print(f"第 {retry + 1} 次检查：检测到修改按钮，刷新网页...")
                    web_page.reload()
                    sleep(3)  # 等待页面加载
                    
                    # 如果是最后一次循环（第10次），刷新后再次检查
                    if retry == 19:
                        try:
                            modify_button_after_reload = web_page.find(modify_button_selector, timeout=2)
                            if modify_button_after_reload:
                                has_modify_button_in_last_retry = True
                                print("最后一次检查：刷新后仍检测到修改按钮，报告尚未完全生成。")
                            else:
                                print("最后一次检查：刷新后修改按钮已消失，报告可能已准备好。")
                        except:
                            print("最后一次检查：刷新后修改按钮已消失，报告可能已准备好。")
            except:
                pass  # 如果找不到修改按钮，说明报告可能已准备好
        
        # 状态3: 检查是否成功（找到下载按钮）
        try:
            # 尝试查找已就绪的"下载"按钮
            download_status = web_page.find("report_lib_download_mark", timeout=2)
            download_button = web_page.find("report_lib_download", timeout=2)
            print("报告已生成！准备下载。")
            break  # 找到下载按钮，退出循环
        except:
            pass

        # 状态4: 尝试点击"刷新"按钮
        try:
            refresh_button = web_page.find("report_lib_download", timeout=2)
            refresh_button.click()
            print("报告未就绪，已点击'刷新'按钮。")
            sleep(2)  # 等待刷新后的页面加载
        except:
            print("警告：'刷新'按钮无法点击或正在加载中。")
            pass

        # 如果还没找到下载按钮，等待后继续下一次循环
        if download_button is None:
            print("等待10秒后进行下一次检查...")
            sleep(10)

    # 循环结束后，检查结果
    if has_modify_button_in_last_retry:
        error_msg = "报告尚未完全生成：检测到修改按钮仍存在，报告未生成。"
        print(f"警告：{error_msg}")
        raise Exception(error_msg)  # 抛出异常提醒客户
    
    if download_button is None:
        error_msg = "经过10次检查后，仍未找到可下载的报告。"
        print(f"错误：{error_msg}")
        raise Exception(error_msg)
    
    # 找到下载按钮，执行下载
    print("开始下载报告...")
    download_button.click()
    sleep(1)
    
    # 使用 download_handler 处理下载和紫鸟弹窗
    download_file_path = download_handler(web_page, file_fold, file_name)
    print(f"报告下载完成：{download_file_path}")


    
    # web.handle_save_dialog(file_folder = file_fold, mode=web_page.product_name, file_name=file_name, wait_complete=False)
    # sleep(2)
    # for retry in range(2):      
    #     try:
    #         win = win32.get(class_name='Chrome_WidgetWin_1',timeout=5)
    #         win.find('send_post_confirm').click()
    #     except:
    #         pass


def run(web_page, report_type, start_time, end_time, file_fold, file_name, account_type):
    current_url = web_page.get_url()
    domin_url_list = current_url.split('/')
    domin_url = domin_url_list[0] + '//' + domin_url_list[2]
    web_page.navigate(f"{domin_url}/payments/reports-repository/ref=xx_rrepo_dnav_xx")
    handler_container(web_page)
    configure(web_page, report_type, start_time, end_time, file_fold, file_name, account_type)
    return file_fold + '\\' + file_name


def main(args):
    test_run()
    web_page = args.get("web_page")
    account_type = args.get("account_type",'标准订单')
    report_type = args.get("report_type",'汇总')
    month = args.get('month','二月')
    year = args.get('year','2025')
    file_fold = args.get("file_fold", r"C:\Users\67504\Desktop\文件下载\测试文件夹啊")
    file_name = args.get("file_name", r"测试.pdf")

    # web_page = web.get_active(mode='superbrowser')
    file_path = run(web_page, report_type, month, year, file_fold, file_name, account_type)
    args["file_path"] = file_path

def test_run():
    if "xbot_extensions" in __file__:
        return
    
    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    web_page.reload()
    file_path = run(web_page, '汇总', '十一月', '2025', r'D:', '测试.pdf', '标准订单')
    print(file_path)
    exit()
