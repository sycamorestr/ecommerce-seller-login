# 模板

import xbot
import re
from xbot import print, sleep
from xbot import print
from xbot.web import WebBrowser
from xbot.selector import Selector
from .utils import get_domain
from .utils import handler_container
from ._amazon_api import switch_site, switch_language
from .create_element import create_selector
from datetime import datetime

class Xpath:
    """集中管理所有XPath定位器，便于维护和调试"""
    
    # 搜索相关元素
    SEARCH_INPUT = '//*[local-name()="kat-input"][@type="search"]'
    SEARCH_BUTTON = '//*[local-name()="kat-input"][@type="search"]/following-sibling::*[local-name()="kat-button"]'
    
    # 数据表格相关
    TABLE_ROWS = '//*[@id="fixed-table-data"]/kat-table//kat-table-body/kat-table-row'
    SKU_ELEMENT = './/span[@class="value"]/*[local-name()="kat-link"]'
    
    # 历史供货详情 
    HISTORY_DETAIL_LINK = './/*[local-name()="kat-table-cell"][@data-column-id="historical_dos" and .//*[local-name()="ipv2-details-popover"]]'
    
    # 数据字段定位
    SHORT_TERM_INVENTORY = '//div[contains(@class, "historical-days-of-supply-table")]//*[local-name()="kat-table-body"]/*[local-name()="kat-table-row"][2]/*[local-name()="kat-table-cell"][2]'
    SHORT_TERM_SHIPPED = '//div[contains(@class, "historical-days-of-supply-table")]//*[local-name()="kat-table-body"]/*[local-name()="kat-table-row"][3]/*[local-name()="kat-table-cell"][2]'
    LONG_TERM_INVENTORY = '//div[contains(@class, "historical-days-of-supply-table")]//*[local-name()="kat-table-body"]/*[local-name()="kat-table-row"][2]/*[local-name()="kat-table-cell"][3]'
    LONG_TERM_SHIPPED = '//div[contains(@class, "historical-days-of-supply-table")]//*[local-name()="kat-table-body"]/*[local-name()="kat-table-row"][3]/*[local-name()="kat-table-cell"][3]'

def to_page_if_needed(web_page: WebBrowser, url: str):
    # 如果当前页面已经是目标页面，直接返回
    if web_page.get_url().startswith(url) and not web_page.get_url().startswith(
            url + "/"
    ):
        return
    # 如果不是，则导航到目标URL
    web_page.navigate(url, load_timeout=300)
    handler_container(web_page)

# =============================
# 5. Excel操作函数
# =============================
def read_msku_list_from_excel(excel_file_path: str, sheet_name: str , start_row: int = 2) -> list:

    msku_list = []
    
    try:
        # 打开Excel文件
        workbook = xbot.excel.open(excel_file_path, visible=True)
        worksheet = workbook.get_sheet_by_name(sheet_name)
        
        # 读取A列数据
        row = start_row
        while True:
            try:
                cell_value = worksheet.get_cell(row, 'A')
                if not cell_value or str(cell_value).strip() == '':
                    break
                
                msku = str(cell_value).strip()

                msku_list.append(msku)

                row += 1
                
            except Exception as e:
                print(f"[Excel读取] 第{row}行读取失败: {e}")
                break
        
        workbook.close()
        
    except Exception as e:
        print(f"[Excel读取] 文件操作失败: {e}")
        raise
    print(msku_list)
    return msku_list

def write_data_to_excel(excel_file_path: str, data_list: list, sheet_name: str, start_row: int = 2):
    """
    将数据写入Excel文件的B-E列
    """
    try:
        workbook = xbot.excel.open(excel_file_path, visible=False)
        worksheet = workbook.get_sheet_by_name(sheet_name)
        
        
        for i, data in enumerate(data_list):
            row = start_row + i
            
            # B列：短期每日平均现有商品数量
            worksheet.set_cell(row, 'B',(data.get('short_term_inventory', 0)))
            # C列：短期平均每日配送商品数量
            worksheet.set_cell(row, 'C',(data.get('short_term_shipped', 0)))
            # D列：长期每日平均现有商品数量
            worksheet.set_cell(row, 'D',(data.get('long_term_inventory', 0)))
            # E列：长期平均每日配送商品数量
            worksheet.set_cell(row, 'E',(data.get('long_term_shipped', 0)))
            
        
        workbook.save()
        workbook.close()
        
    except Exception as e:
        print(f"[Excel写入] 失败: {e}")
        raise


# =============================
# 6. 网页数据抓取函数
# =============================
def search_msku(web_page: WebBrowser, msku: str, max_retry: int = 3) -> bool:

    for attempt in range(max_retry):
        try:
            
            # 查找搜索框
            search_input = web_page.find_by_xpath(Xpath.SEARCH_INPUT, timeout=5)
            
            # 清空并输入MSKU
            search_input.click()
            sleep(0.5)
            search_input.clipboard_input(msku)
            sleep(1)
            
            # 查找搜索按钮并点击
            search_button = web_page.find_by_xpath(Xpath.SEARCH_BUTTON, timeout=3)
            search_button.click()
            
            # 等待搜索结果
            sleep(3)
            return True
            
        except Exception as e:
            print(f"[MSKU搜索] 第{attempt + 1}次尝试失败: {e}")
            sleep(2)
    
    return False

def extract_msku_data(web_page: WebBrowser, msku: str) -> dict:

    data = {
        'msku': msku,
        'short_term_inventory': 0.0,
        'short_term_shipped': 0.0,
        'long_term_inventory': 0.0,
        'long_term_shipped': 0.0,
        'success': False
    }
    
    try:
        
        # 查找表格行
        table_rows = web_page.find_all_by_xpath(Xpath.TABLE_ROWS, timeout=5)
        if not table_rows:
            print(f"[数据提取] 未找到数据表格行")
            return data
        
        # 在第一行中查找历史详情链接
        for row in table_rows:
            try:
                try:
                    row_msku_el = row.find_by_xpath(Xpath.SKU_ELEMENT, timeout=2)
                    row_msku_text = (row_msku_el.get_text() or '').strip()
                except Exception:
                    row_msku_text = ''
                
                if row_msku_text != msku:
                    continue

                history_link = row.find_by_xpath(Xpath.HISTORY_DETAIL_LINK, timeout=2)
                
                # 点击详情链接
                # history_link.click()              
                # 提取数据
                
                short_inventory_elem = web_page.find_by_xpath(Xpath.SHORT_TERM_INVENTORY, timeout=3)
                
                data['short_term_inventory'] = short_inventory_elem.get_text()
                short_shipped_elem = web_page.find_by_xpath(Xpath.SHORT_TERM_SHIPPED, timeout=3)
                data['short_term_shipped'] = short_shipped_elem.get_text()
                
                long_inventory_elem = web_page.find_by_xpath(Xpath.LONG_TERM_INVENTORY, timeout=3)
                data['long_term_inventory'] = long_inventory_elem.get_text()
                
                long_shipped_elem = web_page.find_by_xpath(Xpath.LONG_TERM_SHIPPED, timeout=3)
                data['long_term_shipped'] = long_shipped_elem.get_text()
                           
                data['success'] = True
                break
                
            except Exception as e:
                print(f"[数据提取] 当前行数据提取失败，尝试下一行: {e}")
                continue
        
    except Exception as e:
        print(f"[数据提取] {msku} 数据提取失败: {e}")
        return data
    return data

# =============================
# 7. 主业务流程
# =============================
def process_method(web_page: WebBrowser, excel_file_path: str, sheet_name: str, start_row: int = 2, max_retry: int = 3):

    domain = get_domain(web_page)
    account_health_url = f"{domain}/inventoryplanning/manageinventoryhealth"
    to_page_if_needed(web_page, account_health_url)
    switch_language(web_page, 'zh_CN')
    try:
        # 1. 读取MSKU列表
        msku_list = read_msku_list_from_excel(excel_file_path, sheet_name, start_row)
        if not msku_list:
            return {
                'success': False,
                'message': 'Excel中未找到有效的MSKU',
                'total_count': 0,
                'success_count': 0,
                'failed_count': 0
            }       
        
        # 3. 循环处理每个MSKU
        results = []
        success_count = 0
        failed_count = 0
        
        for i, msku in enumerate(msku_list, 1):
            try:
                # 搜索MSKU
                if search_msku(web_page, msku, max_retry):
                    # 提取数据
                    msku_data = extract_msku_data(web_page, msku)
                    results.append(msku_data)
                    
                    if msku_data['success']:
                        success_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
                    # 添加失败记录
                    results.append({
                        'msku': msku,
                        'short_term_inventory': 0.0,
                        'short_term_shipped': 0.0,
                        'long_term_inventory': 0.0,
                        'long_term_shipped': 0.0,
                        'success': False
                    })
                
                # 间隔等待
                if i < len(msku_list):
                    sleep(2)
                    
            except Exception as e:
                failed_count += 1
                print(f"{msku} 处理异常: {e}")
                results.append({
                    'msku': msku,
                    'short_term_inventory': 0.0,
                    'short_term_shipped': 0.0,
                    'long_term_inventory': 0.0,
                    'long_term_shipped': 0.0,
                    'success': False
                })
        
        # 4. 写入Excel
        write_data_to_excel(excel_file_path, results, sheet_name, start_row)
        
        # 5. 返回结果统计
        result_summary = {
            'success': True,
            'message': f'处理完成：成功 {success_count} 个，失败 {failed_count} 个',
            'total_count': len(msku_list),
            'data': results
        }
        
        print(result_summary)
        
        return result_summary
        
    except Exception as e:
        error_msg = f"主流程执行失败: {e}"
        print(f"[错误] {error_msg}")
        return {
            'success': False,
            'message': error_msg,
            'total_count': 0,
            'success_count': 0,
            'failed_count': 0
        }

def test_run():
    if "xbot_extensions" in __file__:
        return
    print("--- 开始测试 ---")
    web_page = xbot.web.get_active(mode="ziniaobrowser")
    # search_msku(web_page,'CB-WTIM-U2JF')
    # read_msku_list_from_excel(r'C:\Users\58204\Desktop\test\历史供货天数模板.xlsx','Sheet1')
    # extract_msku_data(web_page,'CB-WTIM-U2JF')
    process_method(web_page,r'C:\Users\58204\Desktop\test\历史供货天数模板.xlsx','Sheet1')
    exit()


def main(args):
    test_run()
    web_page = args.get("web_page")
    file_path = args.get("file_path")
    sheet_name = args.get("sheet_name", "Sheet1")
    result_dict = process_method(web_page, file_path, sheet_name)
    args["data"] = result_dict

