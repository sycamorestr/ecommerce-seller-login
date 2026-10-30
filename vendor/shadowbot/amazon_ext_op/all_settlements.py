# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块
import os
import xbot
import random
from xbot import print, sleep
from .utils import get_domain_from_url
from .create_element import create_selector_shadow
from .download_utils import download_handler


class Xpath:
    # 账户类型点击框
    account_frame_xpath = '//kat-dropdown[@name="accountType"]'
    # 账户类型选择
    account_option_xpath = '//kat-dropdown[@name="accountType"]/xbotShadowRoot//slot[@role="listbox"]/*[@value="{}"]'

    # 开始时间输入框
    start_input_xpath = '//*[@name="startDate"]/xbotShadowRoot//*[@name="startDate"]/xbotShadowRoot//input[@name="startDate"]'
    # 结束时间输入框
    end_input_xpath = '//*[@name="endDate"]/xbotShadowRoot//*[@name="endDate"]/xbotShadowRoot//input[@name="endDate"]'

    # 搜索按钮xpath
    search_button_xpath = '//kat-button[@class="form-search-button"]/xbotShadowRoot//button[@type="submit"]'

    # 所有下载文件按钮
    all_download_button_xpath = '//tbody/tr/td[last()]'

    # 模板文件下载按钮
    template_download_button_xpath = '//tbody/tr/td[last()]//kat-dropdown-button'

    # 展开下载文件类型选择按钮
    download_type_option_xpath = '//tbody/tr/td[last()]/kat-dropdown-button/xbotShadowRoot//button[@part="dropdown-button-toggle-button"]'
    
    # XML文件下载按钮
    xml_download_button_xpath = '//tbody/tr/td[last()]/kat-dropdown-button/xbotShadowRoot//button[@part="dropdown-button-button-1"]'

    # 进行中
    in_progress_xpath = '//tbody/tr/td[last()]//p[text()="进行中" or text()="In Progress"]'
    # 每行第一个单元格中的时间文本
    row_time_text_xpath = '//div[@class="group-timerange"]'
    # 页面标题（用于判断中英文）
    app_title_xpath = '//h1[@class="app-title"]'


def _normalize_date(value):
    value = '' if value is None else str(value).strip()
    return value.replace('-', '/')


def _split_date_parts(value):
    """解析日期字符串，返回(year, month, day)。支持 YYYY/MM/DD、YYYY-MM-DD、MM/DD/YYYY、MM-DD-YYYY。"""
    text = _normalize_date(value)
    if text == '':
        return None, None, None
    parts = text.split('/')
    if len(parts) != 3:
        raise Exception(f'日期格式错误：{value}')
    p1, p2, p3 = parts
    # 年在首位：YYYY/MM/DD
    if len(p1) == 4:
        return int(p1), int(p2), int(p3)
    # 年在末位：MM/DD/YYYY
    return int(p3), int(p1), int(p2)


def _get_page_language_by_title(web_page):
    """根据页面标题文本判断语言：中文返回zh，其他返回en。"""
    title_list = web_page.find_all_by_xpath(Xpath.app_title_xpath, timeout=5)
    if len(title_list) == 0:
        return 'en'
    try:
        title_text = title_list[0].get_text().strip()
    except Exception:
        title_text = ''
    # 只要包含中文字符，就判定为中文页面
    if any('\u4e00' <= ch <= '\u9fff' for ch in title_text):
        return 'zh'
    return 'en'


def _format_date_by_page_language(page_language, value):
    """根据页面语言格式化日期：en->MM/DD/YYYY，zh->YYYY/MM/DD。"""
    year, month, day = _split_date_parts(value)
    if year is None:
        return ''

    if page_language == 'en':
        return f'{month:02d}/{day:02d}/{year:04d}'
    if page_language == 'zh':
        return f'{year:04d}/{month:02d}/{day:02d}'
    # 默认使用中文格式
    return f'{year:04d}/{month:02d}/{day:02d}'


def _normalize_account_type(account_type):
    text = '' if account_type is None else str(account_type).strip()
    if '发票支付订单' in text:
        return 'INVOICING'
    return 'PAYABLE'


def _random_wait_5_10s():
    sleep(random.randint(5, 10))


def _adaptive_wait_seconds(round_idx):
    """
    进行中轮询的渐进等待时长（秒）：
    2 -> 3 -> 5 -> 8，附带0-1秒随机抖动。
    """
    base_steps = [2, 3, 5, 8]
    base = base_steps[min(round_idx, len(base_steps) - 1)]
    jitter = random.randint(0, 1)
    return base + jitter


def _wait_page_ready(web_page, timeout=8):
    """刷新后等待搜索按钮可见，避免固定长等待。"""
    search_button_sel = create_selector_shadow(Xpath.search_button_xpath)
    web_page.find(search_button_sel, timeout=timeout)


def _set_account_type_if_need(web_page, account_type_value):
    # 标准订单(PAYABLE)与发票支付订单(INVOICING)都显式选择，保证筛选条件一致
    account_frame_sel = create_selector_shadow(Xpath.account_frame_xpath)
    web_page.find(account_frame_sel, timeout=10).click()
    account_option_sel = create_selector_shadow(Xpath.account_option_xpath.format(account_type_value))
    web_page.find(account_option_sel, timeout=10).click()


def _input_date_and_search(web_page, start_time, end_time):
    start_input_sel = create_selector_shadow(Xpath.start_input_xpath)
    end_input_sel = create_selector_shadow(Xpath.end_input_xpath)
    search_button_sel = create_selector_shadow(Xpath.search_button_xpath)
    page_language = _get_page_language_by_title(web_page)
    start_input_text = _format_date_by_page_language(page_language, start_time)
    end_input_text = _format_date_by_page_language(page_language, end_time)

    web_page.find(start_input_sel, timeout=10).click()
    web_page.find(start_input_sel, timeout=10).input(start_input_text)
    web_page.find(end_input_sel, timeout=10).click()
    web_page.find(end_input_sel, timeout=10).input(end_input_text)
    web_page.find(search_button_sel, timeout=10).click()
    sleep(2)


def _click_request_report_buttons(web_page):
    row_list = web_page.find_all_by_xpath('//tbody/tr', timeout=10)
    click_count = 0
    for idx in range(1, len(row_list) + 1):
        row_request_xpath = f'(//tbody/tr)[{idx}]//kat-button[@label="请求报告" or @label="Request Report"]'
        row_request_buttons = web_page.find_all_by_xpath(row_request_xpath, timeout=2)
        if len(row_request_buttons) == 0:
            continue
        try:
            row_request_buttons[0].click()
            click_count += 1
            sleep(0.3)
        except Exception:
            pass
    return click_count


def _has_in_progress(web_page):
    in_progress_list = web_page.find_all_by_xpath(Xpath.in_progress_xpath, timeout=5)
    return len(in_progress_list) > 0


def _has_download_buttons(web_page, download_type):
    """判断当前页是否存在可用下载按钮。"""
    download_type_text = '' if download_type is None else str(download_type)
    if 'XML' in download_type_text.upper():
        # XML模式至少要有类型展开按钮
        expand_sel = create_selector_shadow(Xpath.download_type_option_xpath)
        return len(web_page.find_all(expand_sel, timeout=3)) > 0
    # 模板文件和默认模式都依赖dropdown按钮
    return len(web_page.find_all_by_xpath(Xpath.template_download_button_xpath, timeout=3)) > 0


def _wait_until_no_in_progress(web_page, start_time, end_time, max_round=60):
    for _ in range(max_round):
        if not _has_in_progress(web_page):
            return
        web_page.reload()
        _random_wait_5_10s()
        _input_date_and_search(web_page, start_time, end_time)
    raise Exception('等待报告生成超时，页面仍存在进行中状态')


def _refresh_and_research(web_page, account_type_value, start_time, end_time):
    """刷新页面后重新设置条件并搜索。"""
    web_page.reload()
    _random_wait_5_10s()
    _set_account_type_if_need(web_page, account_type_value)
    _input_date_and_search(web_page, start_time, end_time)


def _sanitize_filename_part(text):
    text = '' if text is None else str(text).strip()
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        text = text.replace(ch, '_')
    text = text.replace(' ', '_')
    return text


def _get_file_stem_and_suffix(raw_name):
    raw_name = str(raw_name).strip()
    if '.' not in raw_name:
        return raw_name, ''
    stem, suffix = raw_name.rsplit('.', 1)
    return stem, f'.{suffix}'


def _get_row_time_text(web_page, row_index):
    row_time_xpath = f'(//tbody/tr)[{row_index}]//div[@class="group-timerange"]'
    row_time_eles = web_page.find_all_by_xpath(row_time_xpath, timeout=2)
    if len(row_time_eles) == 0:
        return ''
    try:
        return row_time_eles[0].get_text().strip()
    except Exception:
        return ''


def _build_download_name(file_name, row_time_text, index):
    if file_name is None or str(file_name).strip() == '':
        raw = 'all_settlements'
    else:
        raw = str(file_name).strip()

    prefix, suffix = _get_file_stem_and_suffix(raw)
    if row_time_text == '':
        row_time_text = str(index)
    safe_prefix = _sanitize_filename_part(prefix)
    safe_time_text = _sanitize_filename_part(row_time_text)
    return f'{safe_prefix}-{safe_time_text}{suffix}'


def _download_all_files(web_page, download_type, file_folder, file_name):
    download_type_text = '' if download_type is None else str(download_type)
    file_path_list = []

    # 逐行处理下载：没有下载按钮就跳过
    row_list = web_page.find_all_by_xpath('//tbody/tr', timeout=10)
    if len(row_list) == 0:
        return file_path_list

    for idx in range(1, len(row_list) + 1):
        row_time_text = _get_row_time_text(web_page, idx)
        if row_time_text:
            print(f'[下载命名] 第{idx}行时间文本：{row_time_text}')
        else:
            print(f'[下载命名] 第{idx}行未获取到时间文本，回退使用行号')
        # 模板文件下载：直接点模板文件按钮
        if '模板文件' in download_type_text:
            row_template_xpath = f'(//tbody/tr)[{idx}]/td[last()]//kat-dropdown-button'
            print(f'[模板下载] 第{idx}行开始定位，xpath={row_template_xpath}')
            row_template_buttons = web_page.find_all_by_xpath(row_template_xpath, timeout=2)
            print(f'[模板下载] 第{idx}行定位结果：{len(row_template_buttons)} 个按钮')
            if len(row_template_buttons) == 0:
                print(f'[模板下载] 第{idx}行跳过：未找到模板下载按钮')
                continue
            try:
                btn_text = row_template_buttons[0].get_text()
            except Exception:
                btn_text = ''
            try:
                btn_label = row_template_buttons[0].get_attribute('label')
            except Exception:
                btn_label = ''
            print(f'[模板下载] 第{idx}行按钮信息：text={btn_text}, label={btn_label}')
            save_name = _build_download_name(file_name, row_time_text, idx)
            print(f'[模板下载] 第{idx}行开始下载，save_name={save_name}')
            try:
                file_path = download_handler(web_page, row_template_buttons[0], file_folder, save_name)
                file_path_list.append(file_path)
                print(f'[模板下载] 第{idx}行下载成功：{file_path}')
            except Exception as e:
                print(f'[模板下载] 第{idx}行下载失败：{e}')
            continue

        # XML下载：先点类型选择，再点XML
        if 'XML' in download_type_text.upper():
            row_expand_xpath = f'(//tbody/tr)[{idx}]/td[last()]//kat-dropdown-button/xbotShadowRoot//button[@part="dropdown-button-toggle-button"]'
            row_xml_xpath = f'(//tbody/tr)[{idx}]/td[last()]//kat-dropdown-button/xbotShadowRoot//button[@part="dropdown-button-button-1"]'
            row_expand_sel = create_selector_shadow(row_expand_xpath)
            row_xml_sel = create_selector_shadow(row_xml_xpath)

            row_expand_buttons = web_page.find_all(row_expand_sel, timeout=2)
            if len(row_expand_buttons) == 0:
                continue
            row_expand_buttons[0].click()
            sleep(0.2)
            row_xml_buttons = web_page.find_all(row_xml_sel, timeout=2)
            if len(row_xml_buttons) == 0:
                continue
            save_name = _build_download_name(file_name, row_time_text, idx)
            file_path = download_handler(web_page, row_xml_buttons[0], file_folder, save_name)
            file_path_list.append(file_path)
            continue

        # 其他类型：按默认下载按钮处理
        row_default_xpath = f'(//tbody/tr)[{idx}]/td[last()]/kat-dropdown-button'
        row_default_buttons = web_page.find_all_by_xpath(row_default_xpath, timeout=2)
        if len(row_default_buttons) == 0:
            continue
        save_name = _build_download_name(file_name, row_time_text, idx)
        file_path = download_handler(web_page, row_default_buttons[0], file_folder, save_name)
        file_path_list.append(file_path)
    return file_path_list


def download_all_settlements(web_page, account_type, start_time, end_time, download_type, file_folder, file_name):
    """下载所有结算的订单数据"""

    # 判断页面是否为目标页面
    if "/payments/past-settlements" not in web_page.get_url():
        domain_url = get_domain_from_url(web_page.get_url())
        url = domain_url + "/payments/past-settlements"
        for _ in range(3):
            web_page.navigate(url)
            break
        else:
            raise Exception('跳转页面失败')

    account_type_value = _normalize_account_type(account_type)

    # 账户类型仅在发票支付订单时切换
    _set_account_type_if_need(web_page, account_type_value)

    # 首次搜索
    _input_date_and_search(web_page, start_time, end_time)

    # 搜索后逐行点击请求报告按钮，直到当前页可点击的请求按钮都处理完成
    request_count = _click_request_report_buttons(web_page)
    print(f'请求报告点击完成，本轮共点击：{request_count}')

    # 无请求报告时，先判断是否有进行中；无进行中再判断是否有下载按钮，有则直接下载
    if request_count == 0:
        if not _has_in_progress(web_page):
            if _has_download_buttons(web_page, download_type):
                print('当前页无请求报告、无进行中，检测到下载按钮，开始下载')
                return _download_all_files(web_page, download_type, file_folder, file_name)
            print('当前页无请求报告、无进行中，且无下载按钮')
        else:
            print('当前页无请求报告，但存在进行中，进入刷新轮询')

    # 都点击完成后（或存在进行中），先刷新一次重新搜索
    web_page.reload()
    _wait_page_ready(web_page, timeout=8)
    _set_account_type_if_need(web_page, account_type_value)
    _input_date_and_search(web_page, start_time, end_time)

    # 判断进行中：仅在存在进行中时，使用渐进等待后刷新，直到进行中消失
    for i in range(60):
        if not _has_in_progress(web_page):
            break
        wait_seconds = _adaptive_wait_seconds(i)
        print(f'检测到进行中，等待{wait_seconds}s后刷新页面')
        sleep(wait_seconds)
        web_page.reload()
        _wait_page_ready(web_page, timeout=8)
        _set_account_type_if_need(web_page, account_type_value)
        _input_date_and_search(web_page, start_time, end_time)
    else:
        raise Exception('等待进行中状态结束超时')

    # 批量下载并返回文件路径列表
    return _download_all_files(web_page, download_type, file_folder, file_name)


def test_download_all_settlements():
    """本地直接运行该文件时的测试入口。"""
    if 'xbot_extensions' in __file__:
        return

    web_page = xbot.web.get_active(mode='superbrowser')
    account_type = '标准订单'
    start_time = '2024-04-01'
    end_time = '2024-04-30'
    download_type = 'XML文件'
    Desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    file_folder = Desktop
    file_name = 'all_settlements'

    file_path_list = download_all_settlements(
        web_page=web_page,
        account_type=account_type,
        start_time=start_time,
        end_time=end_time,
        download_type=download_type,
        file_folder=file_folder,
        file_name=file_name
    )
    print(file_path_list)
    exit()

def main(args):
    test_download_all_settlements()
    
    web_page = args.get('web_page')
    account_type = args.get('account_type') or '标准订单'
    start_time = args.get('start_time') or ''
    end_time = args.get('end_time') or ''
    download_type = args.get('download_type') or ''
    file_folder = args.get('file_folder')
    file_name = args.get('file_name') or 'all_settlements.txt'

    file_path_list = download_all_settlements(
        web_page=web_page,
        account_type=account_type,
        start_time=start_time,
        end_time=end_time,
        download_type=download_type,
        file_folder=file_folder,
        file_name=file_name
    )
    args['file_path'] = file_path_list
