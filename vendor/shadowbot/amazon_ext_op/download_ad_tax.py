# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser, WebElement  # type: ignore
from pathlib import Path
from .activities_utils import download_handler
from .utils import get_ad_domain
from datetime import datetime
import json
import re


# XPath定义
class Xpath:
    # 已付款按钮
    PaidTab = "//button[@role='tab'][@value='paid']"
    # 日期范围选择器
    DateRangeFilter = "//*[@data-e2e-id='paid-invoices-table:dateRangeFilter:openContainer']"
    # 应用日期按钮
    DateRangeApply = "//*[@data-takt-id='CursorTable-paid-invoices-table-DateRangeFilter-save']"
    # 当前页所有数据行
    DataRows = "//div[contains(@class, 'ag-center-cols-container')][.//div[@col-id='INVOICE']]/div[@role='row'][@row-index]"
    # 下一页按钮（可点击状态）
    NextPage = "//button[@id='bi-nav-table-next-btn'][not(@disabled)]"
    # 下载按钮（相对于行的XPath）
    DownloadBtn = ".//button[@data-takt-id='GBH_SingleDownload']"
    # PDF选项（点击下载后出现的选项）
    PdfOption = '//div[@role="listbox"]//button[@role="option" and contains(., ".pdf")]'
    
    # 日期选择器相关XPath
    # 左日历月份下拉按钮（第一个）
    LeftMonthButton = "(//button[@data-takt-id='storm-ui-dropdown-trigger-button'][@aria-haspopup='listbox'][contains(@aria-label, '月')])[1]"
    # 左日历年份下拉按钮（第一个）
    LeftYearButton = "(//button[@data-takt-id='storm-ui-dropdown-trigger-button'][@aria-haspopup='listbox'][not(contains(@aria-label, '月'))])[1]"
    # 右日历月份下拉按钮（第二个）
    RightMonthButton = "(//button[@data-takt-id='storm-ui-dropdown-trigger-button'][@aria-haspopup='listbox'][contains(@aria-label, '月')])[2]"
    # 右日历年份下拉按钮（第二个）
    RightYearButton = "(//button[@data-takt-id='storm-ui-dropdown-trigger-button'][@aria-haspopup='listbox'][not(contains(@aria-label, '月'))])[2]"
    # 上一月按钮
    PrevMonthButton = "//button[@data-takt-id='CursorTable-paid-invoices-table-DateRangeFilter-calendar-month-previous']"
    # 下一月按钮
    NextMonthButton = "//button[@data-takt-id='CursorTable-paid-invoices-table-DateRangeFilter-calendar-month-next']"
    # 日期按钮（通过data-iso-date定位）
    DateButton = "//button[@data-iso-date='{date}']"
    # 下拉选项（月份或年份）
    DropdownOption = "//div[@role='listbox']//button[@role='option'][normalize-space()='{value}']"

# 表格列字段定义（根据col-id）
COLUMN_FIELDS = [
    'CHECKBOX',      # 复选框（跳过）
    'INVOICE',       # 发票号
    'DATE_SENT',     # 发送日期
    'DUE_DATE',      # 到期日期
    'COUNTRY',       # 国家
    'STATUS',        # 状态
    'PAYMENT_METHOD', # 支付方式
    'AMOUNT_DUE',    # 应付金额
    'ACTIONS'        # 操作列（包含下载按钮）
]

# 中文月份映射
MONTH_MAP = {
    '一月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
    '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}


def see_element(ele):
    script = """
        function (element, input) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center'});
        }
    """
    ele.execute_javascript(script)

# def handle_info(web_page, oper_type, wait_appear=2):
#     """注入js，消除信息框"""
#     dis = """
#     function hideAds(context, args) {
#         document.querySelectorAll('div[id="headerBar"]')
#                 .forEach(el => el.style.display = args);
#     }
#     """
#     web_page.execute_javascript(dis, oper_type)
#     sleep(0.5)


def to_page_if_needed(web_page: WebBrowser, url: str):
    """如果当前页面不是目标页面，则导航到目标页面"""
    current_url = web_page.get_url()
    if not current_url.startswith(url):
        web_page.navigate(url, load_timeout=300)
        web_page.wait_load_completed(timeout=30)

def get_current_month_year(web_page: WebBrowser, is_left: bool = True):
    """获取当前显示的月份和年份"""
    try:
        if is_left:
            month_btn = web_page.find_by_xpath(Xpath.LeftMonthButton, timeout=5)
            year_btn = web_page.find_by_xpath(Xpath.LeftYearButton, timeout=5)
        else:
            month_btn = web_page.find_by_xpath(Xpath.RightMonthButton, timeout=5)
            year_btn = web_page.find_by_xpath(Xpath.RightYearButton, timeout=5)
        
        month_text = month_btn.get_attribute('aria-label') or month_btn.get_text().strip()
        year_text = year_btn.get_attribute('aria-label') or year_btn.get_text().strip()
        
        # 解析月份（例如 "十二月"）
        month_num = MONTH_MAP.get(month_text)
        if month_num is None:
            raise Exception(f"无法识别的月份名称: {month_text}")
        
        # 解析年份（例如 "2025"）
        year_num = int(year_text)
        
        return year_num, month_num
    except Exception as e:
        raise Exception(f"获取当前月份和年份失败: {e}")

def select_month_year(web_page: WebBrowser, target_year: int, target_month: int, is_left: bool = True):
    """选择指定的年份和月份"""
    try:
        # 获取当前显示的月份和年份
        current_year, current_month = get_current_month_year(web_page, is_left)
        
        # 如果已经是目标年月，直接返回
        if current_year == target_year and current_month == target_month:
            return
        
        # 计算需要跳转的月数
        month_diff = (target_year - current_year) * 12 + (target_month - current_month)
        
        # 如果差距太大，先通过下拉选择年份和月份
        if abs(month_diff) > 6:
            # 选择年份
            if is_left:
                year_btn = web_page.find_by_xpath(Xpath.LeftYearButton, timeout=5)
            else:
                year_btn = web_page.find_by_xpath(Xpath.RightYearButton, timeout=5)
            
            year_btn.click()
            sleep(0.5)
            
            # 选择目标年份
            year_option = web_page.find_by_xpath(
                Xpath.DropdownOption.format(value=str(target_year)),
                timeout=5
            )
            year_option.click()
            sleep(0.5)
            
            # 选择月份
            if is_left:
                month_btn = web_page.find_by_xpath(Xpath.LeftMonthButton, timeout=5)
            else:
                month_btn = web_page.find_by_xpath(Xpath.RightMonthButton, timeout=5)
            
            month_btn.click()
            sleep(0.5)
            
            # 获取月份中文名称
            month_name = None
            for name, num in MONTH_MAP.items():
                if num == target_month:
                    month_name = name
                    break
            
            if month_name:
                month_option = web_page.find_by_xpath(
                    Xpath.DropdownOption.format(value=month_name),
                    timeout=5
                )
                month_option.click()
                sleep(0.5)
        else:
            # 使用上一月/下一月按钮导航
            if is_left:
                prev_btn = web_page.find_by_xpath(Xpath.PrevMonthButton, timeout=5)
            else:
                # 右日历的下一月按钮在第二个位置
                next_btns = web_page.find_all_by_xpath(Xpath.NextMonthButton, timeout=5)
                if len(next_btns) >= 2:
                    prev_btn = next_btns[1]  # 使用第二个下一月按钮（右日历的）
                else:
                    prev_btn = next_btns[0] if next_btns else None
            
            if month_diff < 0:
                # 需要往前翻
                for _ in range(abs(month_diff)):
                    if is_left:
                        prev_btn = web_page.find_by_xpath(Xpath.PrevMonthButton, timeout=5)
                    else:
                        next_btns = web_page.find_all_by_xpath(Xpath.NextMonthButton, timeout=5)
                        prev_btn = next_btns[1] if len(next_btns) >= 2 else next_btns[0]
                    prev_btn.click()
                    sleep(0.5)
            else:
                # 需要往后翻
                next_btns = web_page.find_all_by_xpath(Xpath.NextMonthButton, timeout=5)
                if is_left:
                    next_btn = next_btns[0] if next_btns else None
                else:
                    next_btn = next_btns[1] if len(next_btns) >= 2 else next_btns[0] if next_btns else None
                
                for _ in range(month_diff):
                    if next_btn:
                        next_btn.click()
                        sleep(0.5)
                        # 重新查找按钮（可能DOM更新）
                        next_btns = web_page.find_all_by_xpath(Xpath.NextMonthButton, timeout=5)
                        if is_left:
                            next_btn = next_btns[0] if next_btns else None
                        else:
                            next_btn = next_btns[1] if len(next_btns) >= 2 else next_btns[0] if next_btns else None
        
        # 验证是否成功切换到目标年月
        final_year, final_month = get_current_month_year(web_page, is_left)
        if final_year != target_year or final_month != target_month:
            raise Exception(f"切换月份失败，当前: {final_year}-{final_month}, 目标: {target_year}-{target_month}")
            
    except Exception as e:
        raise Exception(f"选择月份和年份失败: {e}")

def select_single_date(web_page: WebBrowser, target_date_str: str):
    """选择单个日期"""
    # 解析目标日期
    target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
    target_year = target_dt.year
    target_month = target_dt.month
    
    max_attempts = 3  # 最多尝试3次
    
    for attempt in range(max_attempts):
        try:
            # 尝试直接查找日期按钮
            date_xpath = Xpath.DateButton.format(date=target_date_str)
            date_buttons = web_page.find_all_by_xpath(date_xpath, timeout=2)
            
            if date_buttons:
                # 找到日期按钮，检查是否可点击
                clicked = False
                for date_btn in date_buttons:
                    # 检查是否被禁用
                    disabled_attr = date_btn.get_attribute('disabled')
                    class_attr = date_btn.get_attribute('class') or ''
                    
                    # 如果按钮有disabled属性或者class包含禁用样式，跳过
                    if disabled_attr == 'true' or 'gvgeEw' in class_attr:
                        continue
                    date_btn.click()
                    sleep(0.5)
                    clicked = True
                    break
                
                if clicked:
                    return  # 成功点击，退出函数
                else:
                    raise Exception(f"日期 {target_date_str} 不可用（已被禁用）")
            
            # 如果找不到日期按钮，说明不在当前显示的日历中，需要切换月份
            # 先尝试切换到左日历
            select_month_year(web_page, target_year, target_month, is_left=True)
            sleep(0.5)
            
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"尝试 {attempt + 1} 失败，重试: {e}")
                sleep(0.5)
                continue
            else:
                raise Exception(f"选择日期失败: {e}")
    
    # 如果所有尝试都失败，抛出异常
    raise Exception(f"无法选择日期 {target_date_str}，已尝试 {max_attempts} 次")

def select_tax_date_range(web_page: WebBrowser, start_date_str: str, end_date_str: str):
    """选择日期范围（类似get_advertising_history.py的逻辑）"""
    # 等待日历出现
    sleep(1)
    
    # 选择开始日期
    try:
        select_single_date(web_page, start_date_str)
        sleep(0.5)
    except Exception as e:
        raise Exception(f"选择开始日期失败: {e}")
    
    # 选择结束日期
    try:
        select_single_date(web_page, end_date_str)
        sleep(0.5)
    except Exception as e:
        raise Exception(f"选择结束日期失败: {e}")
    
    # 点击应用按钮
    try:
        sleep(0.5)  # 等待一下确保日期已选择
        save_button = web_page.find_by_xpath(Xpath.DateRangeApply, timeout=10)
        save_button.click()
        sleep(1)
    except Exception as e:
        raise Exception(f"点击保存按钮失败: {e}")

def setup_page_and_filter(web_page: WebBrowser, start_date: str, end_date: str):
    """设置页面和筛选条件"""
    # 1. 打开广告网页
    domain = get_ad_domain(web_page)
    url = f"{domain}/ads-bg/billing/history"
    to_page_if_needed(web_page, url)
    sleep(2)
    # handle_info(web_page, 'none')
    # 2. 点击发票已付款项
    try:
        web_page.find_by_xpath(Xpath.PaidTab, timeout=10).click()
        sleep(3)
    except Exception as e:
        print(f"点击'发票已付款项'失败: {e}")
        raise
    
    # 3. 点击日期范围选择器
    try:
        date_filter = web_page.find_by_xpath(Xpath.DateRangeFilter, timeout=10)
        # 将日期选择器元素滚动到屏幕中间，确保智能日期选择功能正常工作
        scroll_to_center_script = '''
        function (ele, _) {
            ele.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
        }
        '''
        date_filter.execute_javascript(scroll_to_center_script)
        sleep(0.5)  # 等待滚动完成
        date_filter.click()
        sleep(1)
    except Exception as e:
        print(f"打开日期范围选择器失败: {e}")
        raise
    
    # 4. 选择日期范围并应用（使用新的自定义函数，内部已包含点击应用按钮）
    try:
        select_tax_date_range(web_page, start_date, end_date)
        sleep(3)  # 等待数据加载
    except Exception as e:
        print(f"选择日期范围失败: {e}")
        raise

def extract_row_data(row_element: WebElement) -> dict:
    """从一行中提取所有字段数据"""
    row_data = {}
    
    for col_id in COLUMN_FIELDS:
        if col_id == 'CHECKBOX' or col_id == 'ACTIONS':
            continue  # 跳过复选框和操作列
        
        try:
            # 定位该列的单元格
            cell = row_element.find_by_xpath(f".//div[@col-id='{col_id}']", timeout=1)
            
            # 提取文本内容
            text = cell.get_text().strip()
            
            # 对于某些字段，可能需要特殊处理
            if col_id == 'INVOICE':
                # 发票号可能在button中
                try:
                    invoice_btn = cell.find_by_xpath(".//button", timeout=0.5)
                    btn_text = invoice_btn.get_text().strip()
                    if btn_text:
                        text = btn_text
                except:
                    pass
            
            # 如果文本为空，尝试从title属性获取
            if not text:
                try:
                    text = cell.get_attribute('title') or ""
                except:
                    pass
            
            row_data[col_id] = text if text else ""
        except Exception as e:
            # 如果某个字段提取失败，设置为空字符串
            row_data[col_id] = ""
    
    return row_data

def download_invoice_pdf(web_page: WebBrowser, row_element: WebElement, download_folder: str, file_name: str) -> str:
    """下载单张发票的PDF文件"""
    try:
        # 1. 点击该行的下载按钮
        download_btn = row_element.find_by_xpath(Xpath.DownloadBtn, timeout=5)
        see_element(download_btn)
        sleep(3)
        download_btn.click()
        # 等待菜单出现
        
        # 2. 点击PDF选项（使用新的XPath）
        pdf_option = web_page.find_by_xpath(Xpath.PdfOption, timeout=60)
        sleep(3)
        pdf_option.click()

        
        # 3. 处理下载弹窗
        file_path = download_handler(web_page, download_folder, file_name)
        return file_path
        
    except Exception as e:
        print(f"下载发票PDF失败: {e}")
        raise

def scrape_and_download(web_page: WebBrowser, action_type: str, download_folder: str = '', file_name_prefix: str = '') -> dict:
    """抓取数据和/或下载文件"""
    data = []  # 统一的数据列表
    total_count = 0
    success_count = 0
    error_count = 0
    
    page_num = 1
    
    while True:
        print(f"正在处理第 {page_num} 页...")
        
        # 获取当前页的所有数据行
        try:
            rows = web_page.find_all_by_xpath(Xpath.DataRows, timeout=10)
            if not rows:
                print("未找到数据行，可能已到达最后一页或数据为空")
                break
            
            print(f"第 {page_num} 页找到 {len(rows)} 条记录")
            
            # 遍历每一行
            for row_index, row in enumerate(rows):
                total_count += 1
                row_data = {}
                
                try:
                    # 如果需要抓取数据或下载文件，都需要先提取数据（至少需要发票号用于文件名）
                    if action_type in ['scrape', 'both', 'download']:
                        row_data = extract_row_data(row)
                    
                    # 如果需要下载文件
                    download_path = None
                    if action_type in ['download', 'both']:
                        # 生成文件名（优先使用发票号，如果没有则使用行号）
                        invoice_no = row_data.get('INVOICE', '').strip() if row_data else ''
                        if invoice_no:
                            # 使用发票号作为文件名
                            file_name = f"{file_name_prefix}_{invoice_no}.pdf" if file_name_prefix else f"invoice_{invoice_no}.pdf"
                        else:
                            # 如果没有发票号，使用行号
                            file_name = f"{file_name_prefix}_{total_count}.pdf" if file_name_prefix else f"invoice_{total_count}.pdf"
                        
                        # 下载PDF
                        download_path = download_invoice_pdf(web_page, row, download_folder, file_name)
                        # 等待文件下载完成（检查文件是否存在）
                        if download_path:
                            file_path_obj = Path(download_path)
                            max_wait_time = 300  # 最大等待时间（秒）
                            wait_interval = 0.5  # 检查间隔（秒）
                            waited_time = 0
                            
                            while not file_path_obj.exists() and waited_time < max_wait_time:
                                sleep(wait_interval)
                                waited_time += wait_interval
                            
                            if file_path_obj.exists():
                                print(f"成功下载: {file_name} -> {download_path}")
                            else:
                                print(f"警告: 文件下载超时，文件可能未完全下载: {download_path}")
                        else:
                            print(f"警告: 下载路径为空: {file_name}")
                    
                    # 将下载路径添加到数据中（如果有）
                    if download_path:
                        row_data['download_path'] = download_path
                    
                    # 添加到统一的数据列表
                    data.append(row_data)
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"处理第 {total_count} 条记录时出错: {e}")
                    # 如果出错，至少添加一个空记录（包含错误信息）
                    error_data = row_data.copy() if row_data else {}
                    error_data['error'] = str(e)
                    data.append(error_data)
                    continue
            
            # 检查是否有下一页
            try:
                next_btn = web_page.find_by_xpath(Xpath.NextPage, timeout=3)
                if next_btn:
                    next_btn.click()
                    sleep(3)  # 等待下一页加载
                    page_num += 1
                else:
                    print("已到达最后一页")
                    break
            except:
                print("未找到下一页按钮，已处理完所有数据")
                break
                
        except Exception as e:
            print(f"处理第 {page_num} 页时出错: {e}")
            break
    
    # 等待所有下载完成（特别是最后一个文件），避免切换店铺时出现状态冲突
    if action_type in ['download', 'both']:
        print("等待所有文件下载完成...")
        download_paths = [item.get('download_path') for item in data if item.get('download_path')]
        if download_paths:
            max_wait_time = 120  # 最大等待时间（秒）
            wait_interval = 1  # 检查间隔（秒）
            waited_time = 0
            
            # 检查所有下载的文件是否都存在
            while waited_time < max_wait_time:
                all_exist = True
                for file_path in download_paths:
                    if file_path:
                        file_path_obj = Path(file_path)
                        if not file_path_obj.exists():
                            all_exist = False
                            break
                
                if all_exist:
                    print("所有文件下载完成")
                    break
                
                sleep(wait_interval)
                waited_time += wait_interval
            
            # 最终检查，报告未完成的下载
            if waited_time >= max_wait_time:
                missing_files = [fp for fp in download_paths if fp and not Path(fp).exists()]
                if missing_files:
                    print(f"警告: 以下文件可能未完全下载: {missing_files}")
        else:
            print("没有需要等待的下载文件")
        

        sleep(2)
    # handle_info(web_page, 'block')
    return {
        'data': data
    }

def download_ad_tax(
    web_page: WebBrowser,
    start_date: str,
    end_date: str,
    action_type: str = 'both',
    download_folder: str = '',
    file_name_prefix: str = ''
) -> dict:
    # 参数校验
    assert isinstance(web_page, WebBrowser), "web_page 必须是 WebBrowser 实例"
    assert action_type in ['scrape', 'download', 'both'], f"action_type 必须是 'scrape', 'download' 或 'both'"
    
    if action_type in ['download', 'both']:
        assert download_folder, "下载操作需要提供 download_folder 参数"
        download_folder = Path(download_folder)
        download_folder.mkdir(parents=True, exist_ok=True)
    
    # 1. 设置页面和筛选条件
    setup_page_and_filter(web_page, start_date, end_date)
    
    # 2. 抓取数据和/或下载文件
    result = scrape_and_download(web_page, action_type, str(download_folder), file_name_prefix)
    
    return result

def test_download_ad_tax():
    """测试函数"""
    if "xbot_extensions" in __file__:
        return
    
    web_page = xbot.web.get_active(mode="superbrowser")
    start_date = '2025-01-01'
    end_date = '2025-12-05'
    desktop = os.path.join(os.path.expanduser('~'),'Desktop')
    download_folder = desktop
    file_name_prefix = "1209"
    
    result = download_ad_tax(
        web_page=web_page,
        start_date=start_date,
        end_date=end_date,
        action_type='both',
        download_folder=download_folder,
        file_name_prefix=file_name_prefix
    )
    
    print(f"处理完成:")
    print(f"数据条数: {len(result['data'])}")
    
    # 统计下载文件数
    download_count = sum(1 for item in result['data'] if item.get('download_path'))
    print(f"下载文件数: {download_count}")

    print(result)
    
    exit()

def main(args):
    """主函数入口"""
    # 测试代码入口
    test_download_ad_tax()
    
    # 业务代码入口
    web_page = args.get('web_page')
    start_date = args.get('开始日期')
    end_date = args.get('结束日期')
    action_type = args.get('操作类型', 'both')  # 'scrape' | 'download' | 'both'
    download_folder = args.get('下载文件夹路径', '')
    file_name_prefix = args.get('文件名前缀', '')
    
    result = download_ad_tax(
        web_page=web_page,
        start_date=start_date,
        end_date=end_date,
        action_type=action_type,
        download_folder=download_folder,
        file_name_prefix=file_name_prefix
    )
    
    # 将结果保存到args中
    args['data'] = result['data']

