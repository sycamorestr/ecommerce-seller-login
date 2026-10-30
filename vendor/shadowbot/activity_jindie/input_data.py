import re
from datetime import datetime
import xbot
from xbot import sleep
from .import package
from .package import variables as glv
from xbot.web import WebBrowser
from .utils import gen_selector, get_tag_style, set_datetime_data


def input_data(web_page: WebBrowser, group_name: str, key: str, value: str):
    '''根据字段分组与字段名填写数据。'''
    input_xpath = (
        f'//span[.="{group_name}"]/../../..'
        f'//span[.="{key}"]/../following-sibling::div[1]//*[@class="k-input" or @class="k-textbox"]'
    )
    input_selector = gen_selector(input_xpath, f'{group_name}-{key}-输入框')

    tag_style = get_tag_style(input_xpath, web_page)
    if not tag_style:
        raise Exception(f'无法获取字段属性：{group_name}-{key}，定位：{input_xpath}')

    if tag_style.get('tag') == 'textarea':
        web_page.find(input_selector).input(value)
        return web_page

    if tag_style.get('tag') == 'span':
        web_page.find(input_selector).click()
        sleep(1)
        value_xpath = f'//div[@class="k-list-scroller"]/ul[@aria-hidden="false"]/li[normalize-space(.)="{value}"]'
        value_selector = gen_selector(value_xpath, f'{group_name}-{key}-下拉选项-{value}')
        if not web_page.is_element_displayed(value_selector):
            raise Exception(f'下拉选项不存在：{value}，定位：{value_xpath}')
        web_page.find(value_selector).click()
        return web_page

    if (
        tag_style.get('tag') == 'input'
        and tag_style.get('class') in ['k-input', 'k-textbox']
        and tag_style.get('data_role') != 'datepicker'
    ):
        web_page.find(input_selector).input(value)
        xbot.win32.send_keys('{enter}')
        return web_page

    if (
        tag_style.get('tag') == 'input'
        and tag_style.get('class') == 'k-input'
        and tag_style.get('data_role') == 'datepicker'
    ):
        if not re.fullmatch(r'\d{4}/\d{2}/\d{2}', str(value)):
            raise Exception(f'{group_name}-{key} 仅支持 YYYY/MM/DD，当前输入：{value}')
        try:
            datetime.strptime(str(value), '%Y/%m/%d')
        except ValueError:
            raise Exception(f'{group_name}-{key} 日期非法：{value}')

        set_datetime_data(input_xpath, str(value), web_page)
        web_page.find(input_selector).click()
        xbot.win32.send_keys('{enter}')
        return web_page

    raise Exception(f'暂不支持的字段类型：{tag_style}')


def test_func():
    if 'xbot_extensions' not in __file__:
        web_page = xbot.web.get_active('chrome')
        input_data(web_page, '基本信息', '采购日期', '2026/01/01')
        exit()


def main(args):
    # test_func()
    web_page = args.get('web_page')
    group_name = args.get('group_name')
    key = args.get('key')
    value = args.get('value')
    args['out_web_page'] = input_data(web_page, group_name, key, value)
