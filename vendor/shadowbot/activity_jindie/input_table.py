import json
import xbot
from xbot import print
from .import package
from .package import variables as glv
from xbot.web import WebBrowser
from xbot.web import WebElement
from .utils import gen_selector, get_tag_style, set_datetime_data, set_checkbox_data


def get_table(web_page: WebBrowser, sheet_index: int = 1) -> WebElement:
    '''获取表格对象。'''
    table_xpath = f'(//table//tr/ancestor::table[@class="k-selectable"])[{sheet_index}]'
    table_selector = gen_selector(table_xpath, f'表格{sheet_index}')
    if not web_page.is_element_displayed(table_selector):
        raise Exception(f'表格不存在，定位：{table_xpath}')
    return web_page.find(table_selector)


def get_col_index(table: WebElement, col_name: str) -> int:
    '''根据表头文本获取列索引（1-based）。'''
    if isinstance(col_name, int):
        return col_name

    header_xpath = './preceding::div[@class="k-grid-header"]//th'
    header_cells = table.find_all_by_xpath(header_xpath)
    for index, cell in enumerate(header_cells):
        text = cell.get_text().strip().replace('*', '').replace('\n', '')
        col_name = col_name.strip().replace('*', '').replace('\\n', '')
        if text == str(col_name):
            return index + 1

    raise Exception(f'未找到列名：{col_name}，当前表头：{[c.get_text() for c in header_cells]}')


def get_col_field_by_name(web_page: WebBrowser, col_name: str):
    """根据列名获取 data-field，用于复选框按字段定位。"""
    js_code = '''
        function () {
            function norm(s) { return (s || '').replace(/\s+/g, '').trim(); }
            var headers = Array.from(document.querySelectorAll('.k-content.k-state-active th'));
            var th = headers.find(function (h) {
                return norm(h.textContent) === norm(%s) || norm(h.textContent).indexOf(norm(%s)) >= 0;
            });
            if (!th) return null;
            return {
                field: th.getAttribute('data-field') || null,
                index: th.getAttribute('data-index') || null,
                text: (th.textContent || '').trim()
            };
        }
    ''' % (json.dumps(col_name), json.dumps(col_name))
    return web_page.execute_javascript(js_code, execution_world='MAIN')


def normalize_bool_value(data):
    v = str(data).strip().lower()
    if v in ['1', 'true', '是', 'y', 'yes']:
        return True
    if v in ['0', 'false', '否', 'n', 'no']:
        return False
    return None


def input_table(web_page: WebBrowser, sheet_index: int, col_name: str, row_num: int, data: str):
    '''填写表格单元格数据。'''
    table = get_table(web_page, sheet_index)
    col_index = get_col_index(table, col_name)

    cell_xpath = f'.//tr[{row_num}]/td[{col_index}]'
    cell_ele = table.find_by_xpath(cell_xpath)
    cell_ele.click()

    input_xpath_list = [(
        f'((//table//tr/ancestor::table[@class="k-selectable"])[{sheet_index}]'
        f'//tr[{row_num}]/td[{col_index}]//input)[1]'
    ), 
    (
        f'((//table//tr/ancestor::table[@class="k-selectable"])[{sheet_index}]'
        f'//tr[{row_num}]/td[{col_index}]//textarea)[1]'
    )]
    input_displayed_list = [ele_xpath for ele_xpath in input_xpath_list if web_page.is_element_displayed(gen_selector(ele_xpath, "输入元素"))]
    if len(input_displayed_list) == 0:
        raise Exception("暂未兼容该表格输入元素")
    else:
        input_xpath = input_displayed_list[0]
        input_ele = web_page.find_by_xpath(input_xpath)
    # input_ele = cell_ele.find_by_xpath('.//input')
    input_tag_style = get_tag_style(input_xpath, web_page) or {}

    if input_tag_style.get('tag') == 'input' and input_tag_style.get('type') == 'checkbox':
        target = normalize_bool_value(data)
        if target is None:
            raise Exception(f'复选框仅支持 是/否/true/false/1/0，当前值：{data}')

        checkbox_xpath = input_xpath
        col_field = get_col_field_by_name(web_page, col_name)
        if col_field and col_field.get('field'):
            field = col_field.get('field')
            checkbox_xpath = (
                f'(//div[contains(@class,"k-content") and contains(@class,"k-state-active")]'
                f'//tbody/tr[{row_num}]//*[@data-field="{field}"]//input[@type="checkbox"])[1]'
            )

        result = set_checkbox_data(checkbox_xpath, target, web_page)
        if not result or not result.get('ok'):
            raise Exception(f'复选框设置失败：{result}')
        return web_page

    if (
        (input_tag_style.get('tag') == 'input' or input_tag_style.get('tag') == 'textarea')
        and (input_tag_style.get('type') == 'text' or input_tag_style.get('type') == 'textarea')
        and input_tag_style.get('class') in ['k-input', 'k-textbox', 'k-input kd-editor-input-bound']
        and input_tag_style.get('data_role') != 'datetimepicker'
    ):
        input_ele.input(data)
        xbot.win32.send_keys('{enter}')
        return web_page

    if (
        input_tag_style.get('tag') == 'input'
        and input_tag_style.get('type') == 'text'
        and input_tag_style.get('data_role') == 'datetimepicker'
    ):
        set_datetime_data(input_xpath, data, web_page)
        xbot.win32.send_keys('{enter}')
        return web_page

    raise Exception(f'暂不支持的表格输入类型：{input_tag_style}')


def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        input_table(web_page, 1, '备注', 1, 'cessa')
        exit()


def main(args):
    test_func()
    web_page = args.get('web_page')
    sheet_index = int(args.get('sheet_index', 1))
    col_name = args.get('col_name')
    row_num = int(args.get('row_num', 1))
    data = args.get('data')
    args['out_web_page'] = input_table(web_page, sheet_index, col_name, row_num, data)
